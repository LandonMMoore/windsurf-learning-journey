import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
import requests
from loguru import logger
from redis import Redis

from src.celery_app import database
from src.core.config import configs
from src.repository.workflow_repository import WorkflowRepository
from src.schema.workflow_schema import (
    ExcelSheetName,
    FileProcessingInfo,
    FileProcessingStatus,
    LogLevel,
    WorkflowStateUpdate,
    WorkflowStatus,
    WorkflowStepEnum,
)
from src.services.workflow_crud_service import WorkflowCrudService
from src.services.workflow_redis_manager import WorkflowRedisSchema
from src.services.workflow_service import ExcelDataMigrationService, MigrationResult
from src.schema.workflow_master_data_schema import WorkflowFundSchema, WorkflowProgramSchema,  WorkflowCostCenterSchema, WorkflowAccountSchema, WorkflowAwardSchema, WorkflowSponsorSchema, WorkflowParentTaskSchema
from src.schema.workflow_master_data_schema import WorkflowProjectSchemaForValidation, WorkflowTransactionSchemaForValidation
from openpyxl import Workbook
import shutil
class CeleryWorkflowManager:
    """Synchronous workflow manager for Celery tasks"""

    def __init__(
        self,
        redis_client: Redis,
        schema: WorkflowRedisSchema,
        workflow_service: WorkflowCrudService,
    ):
        self.redis_client = redis_client
        self.schema = schema
        self.workflow_service = workflow_service

    def update_workflow_status_sync(
        self, workflow_id: str, data: WorkflowStateUpdate
    ) -> bool:
        """Generic Redis workflow state updater"""
        try:
            redis_key = self.schema.workflow_state_key(workflow_id)
            workflow_data = self.redis_client.get(redis_key)
            if not workflow_data:
                return False

            workflow_dict = json.loads(workflow_data.decode())

            update_dict = data.model_dump(exclude_unset=True)

            # Handle top-level updates
            for key, value in update_dict.items():
                if key == "files" and isinstance(value, dict):
                    # Update nested files
                    for file_id, file_update in value.items():
                        if file_id not in workflow_dict["files"]:
                            workflow_dict["files"][file_id] = {}
                        for f_key, f_value in file_update.items():
                            if f_value is not None:
                                workflow_dict["files"][file_id][f_key] = f_value
                elif value is not None:
                    workflow_dict[key] = value

            now = datetime.now(timezone.utc).isoformat()

            # Auto-set timestamps
            if update_dict.get(
                "status"
            ) == WorkflowStatus.DOWNLOADING.value and not workflow_dict.get(
                "started_at"
            ):
                workflow_dict["started_at"] = now
            if update_dict.get("status") in [
                WorkflowStatus.COMPLETED.value,
                WorkflowStatus.FAILED.value,
                WorkflowStatus.CANCELLED.value,
            ]:
                workflow_dict["completed_at"] = now

            self.redis_client.set(
                redis_key, json.dumps(workflow_dict), ex=86400 * 7  # 7-day expiry
            )

            # Emit workflow update via Redis Pub/Sub
            self.emit_workflow_update_sync(
                workflow_id, update_dict.get("status", "updated"), workflow_dict
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to update workflow {workflow_id}: {e}")
            return False

    def emit_workflow_update_sync(
        self, workflow_id: str, status: str, workflow_data: Dict[str, Any]
    ):
        """Emit workflow update via Redis Pub/Sub (Celery pushes to Redis, server emits via Socket.IO)"""
        try:
            # Create the message to publish to Redis
            message = {
                "workflow_id": workflow_id,
                "status": status,
                "data": workflow_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Publish to Redis channel (synchronous operation)
            self.redis_client.publish(configs.WORKFLOW_UPDATES, json.dumps(message))

        except Exception as e:
            logger.error(f"Failed to publish workflow update to Redis: {e}")

    def get_workflow_progress(self, workflow_id: str) -> float:
        redis_key = self.schema.workflow_state_key(workflow_id)
        workflow_data = self.redis_client.get(redis_key)
        if not workflow_data:
            return 0.0
        workflow_dict = json.loads(workflow_data.decode())
        return workflow_dict.get("progress_percentage", 0.0)

    def add_log_sync(
        self,
        workflow_id: str,
        workflow_db_id: int,
        level: LogLevel,
        message: str,
        file_name: Optional[str] = None,
        step: Optional[str] = None,
    ):
        """Synchronous log addition for Celery tasks"""
        log_entry = {
            "workflow_id": workflow_db_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.value,
            "message": message,
            "file_name": file_name,
            "step": step,
        }
        # Use the actual redis_client instance
        self.redis_client.lpush(
            self.schema.workflow_logs_key(workflow_id), json.dumps(log_entry)
        )

    def set_workflow_result(self, workflow_id: str, result: Dict[str, Any]):
        """Synchronous version for Celery tasks"""
        self.redis_client.set(
            self.schema.workflow_result_key(workflow_id),
            json.dumps(result),
            ex=86400 * 7,
        )

    # TODO: Update this to use the new workflow state
    def download_sharepoint_files(
        self, workflow_id: str, items: List[Dict[str, Any]], workflow_db_id: int
    ) -> List[Dict[str, Any]]:
        """Downloads files from SharePoint and updates workflow state in Redis"""
        files = []

        # Mark overall status as DOWNLOADING
        self.update_workflow_status_sync(
            workflow_id, WorkflowStateUpdate(status=WorkflowStatus.DOWNLOADING.value)
        )

        for item in items:
            file_id = item.get("id")
            file_name = item.get("name", "unknown")
            file_download_url = item.get("@microsoft.graph.downloadUrl", "")

            if not file_id or not file_download_url:
                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.ERROR,
                    f"Missing ID or download URL for {file_name}",
                    file_name=file_name,
                    step=WorkflowStepEnum.DOWNLOAD.value,
                )
                continue

            # Set file state: downloading
            self.update_workflow_status_sync(
                workflow_id,
                WorkflowStateUpdate(
                    files={
                        file_id: FileProcessingInfo(
                            file_id=file_id,
                            file_name=file_name,
                            download_url=file_download_url,
                            status=FileProcessingStatus.DOWNLOADING.value,
                            progress_percentage=10.0,
                        ).model_dump(exclude_unset=True)
                    }
                ),
            )

            self.add_log_sync(
                workflow_id,
                workflow_db_id,
                LogLevel.INFO,
                f"Downloading {file_name}",
                file_name=file_name,
                step=WorkflowStepEnum.DOWNLOAD.value,
            )

            try:
                response = requests.get(file_download_url, timeout=30)
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    for chunk in response.iter_content(
                        chunk_size=configs.FILE_DOWNLOAD_CHUNK_SIZE
                    ):
                        if chunk:
                            tmp.write(chunk)
                logger.info("Downloaded file")
                files.append(
                    {
                        "id": file_id,
                        "name": file_name,
                        "content": tmp.name,
                        "metadata": item,
                    }
                )

                # Set file state: downloaded
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.DOWNLOADED.value,
                                progress_percentage=30.0,
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )

                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.INFO,
                    f"{file_name} downloaded successfully",
                    file_name=file_name,
                    step=WorkflowStepEnum.DOWNLOAD.value,
                )

            except Exception as e:
                logger.exception(f"Download failed for {file_name}")

                # Set file state: failed
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.FAILED.value,
                                progress_percentage=0.0,
                                error_messages=[str(e)],
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )

                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.ERROR,
                    f"Failed to download {file_name}: {str(e)}",
                    file_name=file_name,
                    step=WorkflowStepEnum.DOWNLOAD.value,
                )
        # Calculate percentage
        files_failed = len(items) - len(files)
        current_progress = self.get_workflow_progress(workflow_id)
        scaled_progress = self.calculate_scaled_progress(
            workflow_id, len(items), len(files), current_progress, 30.0
        )
        self.update_workflow_status_sync(
            workflow_id,
            WorkflowStateUpdate(
                progress_percentage=scaled_progress, files_failed=files_failed
            ),
        )

        return files, files_failed, scaled_progress

    def validate_downloaded_files(
        self, workflow_id: str, files: List[Dict[str, Any]], workflow_db_id: int
    ) -> List[Dict[str, Any]]:
        # Mark overall status as VALIDATING
        self.update_workflow_status_sync(
            workflow_id, WorkflowStateUpdate(status=WorkflowStatus.VALIDATING.value)
        )

        valid_files = []
        for file in files:
            file_id = file["id"]
            name = file["name"]
            file_path = file["content"]
            self.add_log_sync(
                workflow_id,
                workflow_db_id,
                LogLevel.INFO,
                f"Validating {name}",
                file_name=name,
                step=WorkflowStepEnum.VALIDATION.value,
            )
            try:
                # Set file state: validating
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.VALIDATING.value,
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )

                # Validate the headers and sheets
                is_valid, errors = self.validate_excel_file(file_path)
                if is_valid:
                    valid_files.append(file)
                    self.update_workflow_status_sync(
                        workflow_id,
                        WorkflowStateUpdate(
                            files={
                                file_id: FileProcessingInfo(
                                    status=FileProcessingStatus.VALID.value,
                                ).model_dump(exclude_unset=True)
                            }
                        ),
                    )
                    self.add_log_sync(
                        workflow_id,
                        workflow_db_id,
                        LogLevel.INFO,
                        f"{name} validation passed",
                        file_name=name,
                        step=WorkflowStepEnum.VALIDATION.value,
                    )
                else:
                    self.update_workflow_status_sync(
                        workflow_id,
                        WorkflowStateUpdate(
                            files={
                                file_id: FileProcessingInfo(
                                    status=FileProcessingStatus.INVALID.value,
                                    error_messages=errors,
                                ).model_dump(exclude_unset=True)
                            }
                        ),
                    )
                    self.add_log_sync(
                        workflow_id,
                        workflow_db_id,
                        LogLevel.WARNING,
                        f"{name} validation failed",
                        file_name=name,
                        step=WorkflowStepEnum.VALIDATION.value,
                    )
            except Exception as e:
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.FAILED.value,
                                error_messages=[str(e)],
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )
                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.ERROR,
                    f"Validation error for {name}: {str(e)}",
                    file_name=name,
                    step=WorkflowStepEnum.VALIDATION.value,
                )

        # Calculate percentage
        files_failed = len(files) - len(valid_files)
        current_progress = self.get_workflow_progress(workflow_id)
        scaled_progress = self.calculate_scaled_progress(
            workflow_id, len(files), len(valid_files), current_progress, 30.0
        )
        self.update_workflow_status_sync(
            workflow_id,
            WorkflowStateUpdate(
                progress_percentage=scaled_progress, files_failed=files_failed
            ),
        )
        return valid_files, files_failed, scaled_progress

    def process_valid_files(
        self, workflow_id: str, files: List[Dict[str, Any]], workflow_db_id: int
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        results = []

        # Mark overall status as PROCESSING
        self.update_workflow_status_sync(
            workflow_id, WorkflowStateUpdate(status=WorkflowStatus.PROCESSING.value)
        )

        for file in files:
            name = file["name"]
            path = file["content"]
            file_id = file["id"]
            self.add_log_sync(
                workflow_id,
                workflow_db_id,
                LogLevel.INFO,
                f"Processing {name}",
                file_name=name,
                step=WorkflowStepEnum.PROCESSING.value,
            )

            start_time = datetime.utcnow()

            # Set file state: processing
            self.update_workflow_status_sync(
                workflow_id,
                WorkflowStateUpdate(
                    files={
                        file_id: FileProcessingInfo(
                            status=FileProcessingStatus.PROCESSING.value,
                        ).model_dump(exclude_unset=True)
                    }
                ),
            )

            try:
                with database.session() as session:
                    workflow_repository = WorkflowRepository(session)
                    workflow_service = ExcelDataMigrationService(workflow_repository)
                    result = workflow_service.migrate_excel_file(path)
                    logger.info(f"{name} migration result")

            except Exception as e:
                logger.error(f"Migration failed for {name}: {e}")
                duration = (datetime.utcnow() - start_time).total_seconds()
                result = MigrationResult(
                    success=False,
                    total_records=0,
                    inserted_records=0,
                    failed_records=0,
                    errors=[str(e)],
                    duration_seconds=duration,
                    details={},
                )
                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.ERROR,
                    f"Processing failed for {name}: {e}",
                    file_name=name,
                    step=WorkflowStepEnum.PROCESSING.value,
                )
                # Set file state: failed
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.FAILED.value,
                                progress_percentage=0.0,
                                error_messages=[str(e)],
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )
            else:
                self.add_log_sync(
                    workflow_id,
                    workflow_db_id,
                    LogLevel.INFO,
                    f"{name} processed successfully",
                    file_name=name,
                    step=WorkflowStepEnum.PROCESSING.value,
                )
                # Set file state: processed
                self.update_workflow_status_sync(
                    workflow_id,
                    WorkflowStateUpdate(
                        files={
                            file_id: FileProcessingInfo(
                                status=FileProcessingStatus.PROCESSED.value,
                                progress_percentage=100.0,
                                processed_at=datetime.now(timezone.utc).isoformat(),
                            ).model_dump(exclude_unset=True)
                        }
                    ),
                )

            results.append(result)

        # Calculate percentage
        files_failed = len(files) - len(results)
        current_progress = self.get_workflow_progress(workflow_id)
        scaled_progress = self.calculate_scaled_progress(
            workflow_id, len(files), len(results), current_progress, 40.0
        )
        self.update_workflow_status_sync(
            workflow_id,
            WorkflowStateUpdate(
                status=WorkflowStatus.COMPLETED.value,
                progress_percentage=scaled_progress,
                files_processed=len(results),
                files_failed=files_failed,
                completed_at=datetime.now(timezone.utc).isoformat(),
            ),
        )

        return results, files_failed, scaled_progress

    def clear_workflow_status(self, workflow_id: str):
        self.redis_client.delete(self.schema.workflow_status_key(workflow_id))

    def clear_workflow_state(self, workflow_id: str):
        self.redis_client.delete(self.schema.workflow_state_key(workflow_id))

    def clear_workflow_logs(self, workflow_id: str):
        self.redis_client.delete(self.schema.workflow_logs_key(workflow_id))

    def calculate_scaled_progress(
        self,
        workflow_id: str,
        files_count: int,
        results_count: int,
        current_progress: float,
        scale_range: float,
    ) -> float:
        """Calculate scaled progress based on number of processed files."""
        if files_count == 0:
            return current_progress

        raw_percent = (results_count / files_count) * 100
        scaled_progress = (raw_percent / 100) * scale_range
        return current_progress + scaled_progress

    def validate_excel_headers(
        self, file_path: Path, expected_headers: Set[str], sheet_name: str = "Sheet"
    ) -> List[str]:
        """
        Validates an Excel sheet's DataFrame against schema rules:
        - Required headers present
        - No duplicate headers
        - Case sensitivity match

        Args:
            file_path (Path): Path to the Excel file.
            expected_headers (Set[str]): Set of valid/required headers.
            sheet_name (str): Name of the Excel sheet.

        Returns:
            List[str]: List of validation error messages. Empty if valid.
        """
        errors = []

        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str, header=0)
        df.columns = df.columns.str.strip()

        # 1. Detect duplicate columns
        duplicates = df.columns[df.columns.duplicated()].tolist()
        if duplicates:
            errors.append(
                f"{sheet_name} Duplicate column(s) found: {', '.join(duplicates)}"
            )

        # 2. Required headers check
        missing = expected_headers - set(df.columns)

        if missing:
            errors.append(
                f"{sheet_name} Missing required column(s): {', '.join(missing)}"
            )

        # 3. Case sensitivity check
        lowercase_expected = {col.lower() for col in expected_headers}
        mismatched_case = [
            col
            for col in df.columns
            if col.lower() in lowercase_expected and col not in expected_headers
        ]
        if mismatched_case:
            errors.append(
                f"{sheet_name} Column name case mismatch: {', '.join(mismatched_case)}"
            )

        return errors

    def validate_excel_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        start_time = datetime.utcnow()
        try:
            logger.info("Starting Excel validation")

            # Validate file exists
            excel_file = Path(file_path)
            if not excel_file.exists():
                return False, ["Excel file not found"]

            # Validate sheets
            is_valid, missing_sheets = self.validate_excel_sheets(excel_file)
            if not is_valid:
                logger.warning(
                    f"Missing required sheets: {', '.join(missing_sheets)}. Please ensure the file contains all required sheets."
                )
                return False, [f"Missing required sheets: {', '.join(missing_sheets)}"]

            # Validate each sheets headers in order
            results = {}

            # 1. Chart of Accounts Master Data
            results["coa_master"] = self.validate_excel_headers(
                excel_file,
                configs.COA_MASTER_DATA_VALID_HEADERS,
                sheet_name=ExcelSheetName.COA_MASTER_DATA.value,
            )

            # 2. Award & Project Master Data
            results["award_project"] = self.validate_excel_headers(
                excel_file,
                configs.AWARD_PROJECT_MASTER_DATA_VALID_HEADERS,
                sheet_name=ExcelSheetName.AWARD_PROJECT_MASTER_DATA.value,
            )

            # 3. Summary Balances
            results["summary"] = self.validate_excel_headers(
                excel_file,
                configs.SUMMARY_BALANCES_VALID_HEADERS,
                sheet_name=ExcelSheetName.SUMMARY_BALANCES.value,
            )

            # 4. Transactional Detail Data
            results["transactions"] = self.validate_excel_headers(
                excel_file,
                configs.TRANSACTIONAL_DETAIL_DATA_VALID_HEADERS,
                sheet_name=ExcelSheetName.TRANSACTIONAL_DETAIL_DATA.value,
            )

            # Calculate totals
            total_errors = sum(len(result) for result in results.values())
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(
                f"Validation completed in {duration:.2f}s. Total errors: {total_errors}"
            )
            errors = [item for sublist in results.values() for item in sublist]
            logger.info(f"Validation errors: {errors}")
            return total_errors == 0, errors

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False, [str(e)]

    def validate_excel_sheets(self, excel_file: Path) -> Tuple[bool, List[str]]:
        try:
            excel = pd.ExcelFile(excel_file)
            available_sheets = set(excel.sheet_names)
            missing_sheets = configs.EXCEL_FILE_SHEET_NAMES - available_sheets
            if missing_sheets:
                logger.warning(
                    f"Missing required sheets: {', '.join(missing_sheets)}. Please ensure the file contains all required sheets."
                )
            return len(missing_sheets) == 0, list(missing_sheets)
        except Exception as e:
            logger.error(f"Failed to validate Excel sheets: {e}")
            return False, [str(e)]

    def validate_sheets_data(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_files = []
        for file in files:
            sheets_wise_invalid_row_indexes = {}
            logger.info(f"Validating file present at path: {file["content"]}")
            file_path = file["content"]

            copy_file_path = self.copy_excel_file(Path(file_path))
            
            # Validate the data in the sheets
            invalid_data_mapping_coa = self.validate_coa_master_data(file_path)
            sheets_wise_invalid_row_indexes[ExcelSheetName.COA_MASTER_DATA.value] = list(set(invalid_data_mapping_coa['invalid_rows']).union(set(invalid_data_mapping_coa['non_identified_rows'])))
            logger.info(f"Number of invalid rows in coa master data sheet: {len(list(set(invalid_data_mapping_coa['invalid_rows']).union(set(invalid_data_mapping_coa['non_identified_rows']))))}")

            invalid_data_mapping_award_project, sub_tasks = self.validate_award_project_data(file_path, invalid_data_mapping_coa)
            sheets_wise_invalid_row_indexes[ExcelSheetName.AWARD_PROJECT_MASTER_DATA.value] = list(set(invalid_data_mapping_award_project['invalid_rows']).union(set(invalid_data_mapping_award_project['non_identified_rows'])))
            logger.info(f"Number of invalid rows in award project master data sheet: {len(list(set(invalid_data_mapping_award_project['invalid_rows']).union(set(invalid_data_mapping_award_project['non_identified_rows']))))}")

            invalid_data_mapping_summary_balances, sub_task_by_project_award_map = self.validate_summary_balances(file_path, sub_tasks)
            sheets_wise_invalid_row_indexes[ExcelSheetName.SUMMARY_BALANCES.value] = list(set(invalid_data_mapping_summary_balances['invalid_rows']).union(set(invalid_data_mapping_summary_balances['non_identified_rows'])))
            logger.info(f"Number of invalid rows in summary balances sheet: {len(list(set(invalid_data_mapping_summary_balances['invalid_rows']).union(set(invalid_data_mapping_summary_balances['non_identified_rows']))))}")
            
            invalid_data_mapping_transactional_detail_data = self.validate_transactional_detail_data(file_path, sub_task_by_project_award_map)
            sheets_wise_invalid_row_indexes[ExcelSheetName.TRANSACTIONAL_DETAIL_DATA.value] = list(set(invalid_data_mapping_transactional_detail_data['invalid_rows']).union(set(invalid_data_mapping_transactional_detail_data['non_identified_rows'])))
            logger.info(f"Number of invalid rows in transactional detail data sheet: {len(list(set(invalid_data_mapping_transactional_detail_data['invalid_rows']).union(set(invalid_data_mapping_transactional_detail_data['non_identified_rows']))))}")

            valid_files.append(sheets_wise_invalid_row_indexes)
            file["file_path_of_invalid_data"] = copy_file_path

            self.keep_only_invalid_rows(copy_file_path, valid_files)
            self.keep_only_valid_rows(file_path, valid_files)
        return files

    def validate_coa_master_data(
        self, file_path: Path
    ) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        try:

            segment_mappings = {
                "Fund": WorkflowFundSchema,
                "Program-Service Number": WorkflowProgramSchema,
                "Cost Center-Office Number": WorkflowCostCenterSchema,
                "Account": WorkflowAccountSchema,
            }
            logger.info("Starting COA Master Data validation")
            valid_coa_data = []
            invalid_coa_data = []
            invalid_data_mapping = {
                "invalid_rows":[],
                "non_identified_rows":[],
                "fund_number":[],
                "program":[],
                "cost_center":[]
            }

            # Validate file exists
            excel_file = Path(file_path)
            if not excel_file.exists():
                return invalid_data_mapping

            df = pd.read_excel(
                file_path,
                sheet_name=ExcelSheetName.COA_MASTER_DATA.value,
                dtype=str,
                header=0
            )

            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                if not row_dict["Segment Name"] or isinstance(row_dict["Segment Name"], float):

                    invalid_entry = {"row_number": idx, **row_dict}
                    invalid_coa_data.append(invalid_entry)

                    invalid_data_mapping["non_identified_rows"].append(idx)
                    invalid_data_mapping["invalid_rows"].append(idx)
                    continue

                if row_dict["Segment Name"] and not row_dict["Segment Value "]:
                    invalid_entry = {"row_number": idx, **row_dict}
                    invalid_coa_data.append(invalid_entry)

                    invalid_data_mapping["non_identified_rows"].append(idx)
                    invalid_data_mapping["invalid_rows"].append(idx)
                    continue
                else:
                    schema_class = segment_mappings[row_dict["Segment Name"]]
                    try:
                        coa_master_data = schema_class(**row_dict)
                        valid_coa_data.append(coa_master_data)
                    except Exception as e:
                        invalid_entry = {"row_number": idx, **row_dict}
                        invalid_coa_data.append(invalid_entry)

                        if row_dict["Segment Name"] == "Fund":
                            if row_dict["Segment Value "] not in invalid_data_mapping["fund_number"]:
                                invalid_data_mapping["fund_number"].append(row_dict["Segment Value "])
                            invalid_data_mapping["invalid_rows"].append(idx)
                        elif row_dict["Segment Name"] == "Program-Service Number":
                            if row_dict["Segment Value "] not in invalid_data_mapping["program"]:
                                invalid_data_mapping["program"].append(row_dict["Segment Value "])
                            invalid_data_mapping["invalid_rows"].append(idx)
                        elif row_dict["Segment Name"] == "Cost Center-Office Number":
                            if row_dict["Segment Value "] not in invalid_data_mapping["cost_center"]:
                                invalid_data_mapping["cost_center"].append(row_dict["Segment Value "])
                            invalid_data_mapping["invalid_rows"].append(idx)
                        elif row_dict["Segment Name"] == "Account":
                            if row_dict["Segment Value "] not in invalid_data_mapping["account"]:
                                invalid_data_mapping["account"].append(row_dict["Segment Value "])
                            invalid_data_mapping["invalid_rows"].append(idx)
                        else:
                            invalid_data_mapping["non_identified_rows"].append(idx)
                            invalid_data_mapping["invalid_rows"].append(idx)

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"COA Master Data validation completed in {duration:.2f}s")

            return invalid_data_mapping

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return invalid_data_mapping

    def validate_award_project_data(self, file_path: Path, invalid_data_mapping: Dict) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        start_time = datetime.now(timezone.utc)
        try:
            logger.info("Starting Award & Project Master Data validation")
            invalid_data_mapping_award_project = {
                "invalid_rows":[],
                "non_identified_rows":[],
                "award_number":[],
                "sponsor_number":[],
                "project_number":[],
                "parent_task_number":[],
                "sub_task_number":[],
            }

            sub_tasks = {}
            awards = {}
            sponsors = {}
            parent_tasks = {}
            projects = {}

            # Validate file exists
            excel_file = Path(file_path)
            if not excel_file.exists():
                return invalid_data_mapping_award_project, sub_tasks

            df = pd.read_excel(file_path, sheet_name=ExcelSheetName.AWARD_PROJECT_MASTER_DATA.value, dtype=str, header=0)

            # Replace empty strings or "nan" strings with actual NaN
            df = df.replace(r'^\s*$', None, regex=True)
            # Filter rows where any of three columns are None
            mask = df["FUND_NUMBER"].isna() | df["PROGRAM"].isna() | df["COST_CENTER"].isna() | df["AWARD_NUMBER"].isna() | df["SPONSOR_NUMBER"].isna() | df["PROJECT_NUMBER"].isna() | df["PARENT_TASK_NUMBER"].isna() | df["SUB_TASK_NUMBER"].isna()
            # Get row indices (Excel rows are usually +2 if header=0)
            invalid_row_ids = df.index[mask].tolist()
            invalid_data_mapping_award_project["non_identified_rows"] = invalid_row_ids

            invalid_fund_numbers = invalid_data_mapping["fund_number"]
            invalid_program_numbers = invalid_data_mapping["program"]
            invalid_cost_center_numbers = invalid_data_mapping["cost_center"]

            mask = (
                df["FUND_NUMBER"].isin(invalid_fund_numbers) |
                df["PROGRAM"].isin(invalid_program_numbers) |
                df["COST_CENTER"].isin(invalid_cost_center_numbers)
            )
            invalid_row_indices = df.index[mask].tolist()
            invalid_data_mapping_award_project["non_identified_rows"].extend(invalid_row_indices)
            
            df = df.fillna("")

            for idx, row in df.iterrows():
                if idx in invalid_data_mapping_award_project["non_identified_rows"]:
                    continue
                if idx in invalid_data_mapping_award_project["invalid_rows"]:
                    continue
                
                # Award data
                award_key = row["AWARD_NUMBER"]
                if award_key:
                    if award_key not in awards:
                        awards[award_key] = {
                            "number": row["AWARD_NUMBER"],
                            "name": row["AWARD_NAME"],
                            "organization": row["AWARD_ORGANIZATION"],
                            "start_date": self._parse_date(row["AWARD_START_DATE"]),
                            "end_date": self._parse_date(row["AWARD_END_DATE"]),
                            "closed_date": self._parse_date(row["AWARD_CLOSE_DATE"]),
                            "status": row["AWARD_STATUS"],
                            "award_type": row["AWARD_TYPE"],
                        }

                # Sponsor data
                sponsor_key = row["SPONSOR_NUMBER"]
                if sponsor_key:
                    if sponsor_key not in sponsors:
                        sponsors[sponsor_key] = {
                            "name": row["SPONSOR_NAME"],
                            "number": row["SPONSOR_NUMBER"],
                            "award_number": row["SPONSOR_AWARD_NUMBER"],
                        }

                # Parent task data
                parent_key = (row["PROJECT_NUMBER"], row["PARENT_TASK_NUMBER"])
                if parent_key:
                    if parent_key not in parent_tasks:
                        parent_tasks[parent_key] = {
                            "number": row["PARENT_TASK_NUMBER"],
                            "name": row["PARENT_TASK_NAME"],
                            "project_id": row["PROJECT_NUMBER"],
                        }

                # Sub task data
                sub_task_key = (
                    row["PROJECT_NUMBER"],
                    row["SUB_TASK_NUMBER"],
                    row["FUND_NUMBER"],
                    row["AWARD_NUMBER"],
                )

                sub_tasks[sub_task_key] = {
                    "number": str(float(row["SUB_TASK_NUMBER"])),
                    "name": row["SUB_TASK_NAME"],
                    "parent_task_id": parent_key,
                    "start_date": self._parse_date(row["SUBTASK_START_DATE"]),
                    "completion_date": self._parse_date(row["SUBTASK_COMPLETION_DATE"]),
                    "award_id": award_key,
                    "fund_id": row["FUND_NUMBER"],
                    "project_id": row["PROJECT_NUMBER"],
                }

                # Project data
                if row["PROJECT_NUMBER"]:
                    if row["PROJECT_NUMBER"] not in projects:
                        projects[row["PROJECT_NUMBER"]] = {
                            "owning_agency": row["Owning_Agency"],
                            "principal_investigator": row["PRINCIPAL_INVESTIGATOR"],
                            "number": row["PROJECT_NUMBER"],
                            "name": row["PROJECT_NAME"],
                            "description": row["PROJECT_DESCRIPTION"],
                            "project_type": row["PROJECT_TYPE"],
                            "organization": row["PROJECT_ORGANIZATION"],
                            "master_project_number": row["Master_Project_Number"],
                            "primary_category": row["Primary_Category"],
                            "project_category": row["Project_Category"],
                            "project_classification": row["Project_Classification"],
                            "ward": row["Ward"],
                            "fhwa_improvement_types": row["FHWA_IMPROVEMENT_TYPES"],
                            "fhwa_functional_codes": row["FHWA_FUNCTIONAL_CODE"],
                            "fhwa_capital_outlay_category": row[
                                "FHWA_CAPITAL_OUTLAY_CATEGORY"
                            ],
                            "fhwa_system_code": row["FHWA_SYSTEM_CODE"],
                            "nhs": row["NHS"],
                            "start_date": self._parse_date(row["PROJECT_START_DATE"]),
                            "end_date": self._parse_date(row["PROJECT_END_DATE"]),
                            "status_code": row["PROJECT_STATUS_CODE"],
                            "owner_agency": row["PROJECT_OWNER_AGENCY"],
                            "award_project_burden_schedule_name": row[
                                "Award_Project_Burden_Schedule_Name"
                            ],
                            "iba_project_number": row["IBA_PROJECT_NUMBER"],
                            "burden_rate_multiplier": float(
                                row["Burden_Rate_Multiplier"] or 0
                            ),
                            "burden_schedule_version_start_date": self._parse_date(
                                row["Burden_Schedule_Version_Start_Date"]
                            ),
                            "burden_schedule_version_end_date": self._parse_date(
                                row["Burden_Schedule_Version_End_Date"]
                            ),
                            "burden_schedule_version_name": row[
                                "Burden_Schedule_Version_Name"
                            ],
                            "ind_rate_sch_id": row["IND_RATE_SCH_ID"],
                            "chargeable_flag": row["CHARGEABLE_FLAG"] == "Y",
                            "billable_flag": row["BILLABLE_FLAG"] == "Y",
                            "capitalizable_flag": row["CAPITALIZABLE_FLAG"] == "Y",
                            "cost_center_id": row["COST_CENTER"],
                            "program_id": row["PROGRAM"],
                            "sponsor_id": row["SPONSOR_NUMBER"],
                        }

            for award_object_key, award_object_data in awards.items():
                try:
                    award_data = WorkflowAwardSchema(**award_object_data)
                except Exception as e:
                    invalid_data_mapping_award_project["award_number"].append(award_object_key)

            for sponsor_object_key, sponsor_object_data in sponsors.items():
                try:
                    sponsor_data = WorkflowSponsorSchema(**sponsor_object_data)
                except Exception as e:
                    invalid_data_mapping_award_project["sponsor_number"].append(sponsor_object_key)

            for project_object_key, project_object_data in projects.items():
                try:
                    project_data = WorkflowProjectSchemaForValidation(**project_object_data)
                except Exception as e:
                    invalid_data_mapping_award_project["project_number"].append(project_object_key)

            for parent_object_key, parent_object_data in parent_tasks.items():
                try:
                    parent_data = WorkflowParentTaskSchema(**parent_object_data)
                except Exception as e:
                    invalid_data_mapping_award_project["parent_task_number"].append(parent_object_key)

            mask = (
                df["AWARD_NUMBER"].isin(list(set(invalid_data_mapping_award_project["award_number"]))) |
                df["SPONSOR_NUMBER"].isin(list(set(invalid_data_mapping_award_project["sponsor_number"]))) |
                df["PROJECT_NUMBER"].isin(list(set(invalid_data_mapping_award_project["project_number"]))) |
                df["PARENT_TASK_NUMBER"].isin(list(set(invalid_data_mapping_award_project["parent_task_number"])))
            )
            invalid_row_indices = df.index[mask].tolist()

            invalid_data_mapping_award_project["invalid_rows"].extend(invalid_row_indices)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Award & Project Master Data validation completed in {duration:.2f}s")
            return invalid_data_mapping_award_project,sub_tasks
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return invalid_data_mapping_award_project,sub_tasks

    def validate_summary_balances(self, file_path: Path, sub_tasks: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Any]]:
        start_time = datetime.now(timezone.utc)
        try:
            logger.info("Starting Summary Balances validation")

            invalid_data_mapping_summary_balances = {
                "invalid_rows":[],
                "non_identified_rows":[]
            }
            sub_task_by_project_award_map = []

            # Validate file exists
            excel_file = Path(file_path)
            if not excel_file.exists():
                return invalid_data_mapping_summary_balances, sub_task_by_project_award_map

            df = pd.read_excel(file_path, sheet_name=ExcelSheetName.SUMMARY_BALANCES.value, dtype=str, header=0)

            # Replace empty strings or "nan" strings with actual NaN
            df = df.replace(r'^\s*$', None, regex=True)
            # Filter rows where any of three columns are None
            mask = df["PROJECT"].isna() | df["TASK NUMBER"].isna() | df["FUND"].isna() | df["AWARD"].isna()
            invalid_row_ids = df.index[mask].tolist()
            invalid_data_mapping_summary_balances["non_identified_rows"] = invalid_row_ids

            for idx, row in df.iterrows():
                if idx in invalid_data_mapping_summary_balances["non_identified_rows"]:
                    continue
                if idx in invalid_data_mapping_summary_balances["invalid_rows"]:
                    continue
                
                # Sub task data
                task_key = (
                    str(row.get("PROJECT", "")).strip(),
                    str(row.get("TASK NUMBER", "")).strip(),
                    str(row.get("FUND", "")).strip(),
                    str(row.get("AWARD", "")).strip(),
                )

                task = sub_tasks.get(task_key)
                if not task:
                    invalid_data_mapping_summary_balances["invalid_rows"].append(idx)
                    continue
                sub_tasks.get(task_key).update(
                    {
                        "award_funding_amount": float(
                            row.get("AWARD_FUNDING_AMOUNT") or 0
                        ),
                        "png_lifetime_budget": float(
                            row.get("PNG_LIFETIME_BUDGET") or 0
                        ),
                        "png_lifetime_allotment": float(
                            row.get("PNG_LIFETIME_ALLOTMENT") or 0
                        ),
                        "commitment": float(row.get("COMMITMENT") or 0),
                        "obligation": float(row.get("OBLIGATION") or 0),
                        "expenditure": float(row.get("EXPENDITURE") or 0),
                        "receivables": float(row.get("RECEIVABLES") or 0),
                        "revenue": float(row.get("REVENUE") or 0),
                    }
                )
                
                try:
                    parent_data = WorkflowParentTaskSchema(**sub_tasks.get(task_key))
                    sub_task_by_project_award_map.append(
                        (
                            sub_tasks.get(task_key)["project_id"],
                            sub_tasks.get(task_key)["award_id"],
                            sub_tasks.get(task_key)["number"],
                        )
                    )
                except Exception as e:
                    invalid_data_mapping_summary_balances["invalid_rows"].append(idx)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Summary Balances validation completed in {duration:.2f}s")
            return invalid_data_mapping_summary_balances, sub_task_by_project_award_map
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return invalid_data_mapping_summary_balances, sub_task_by_project_award_map

    def validate_transactional_detail_data(self, file_path: Path, sub_task_by_project_award_map: List[Any]) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        try:
            logger.info("Starting Transactional Detail Data validation")

            invalid_data_mapping_transactional_detail_data = {
                "invalid_rows":[],
                "non_identified_rows":[]
            }

            # Validate file exists
            excel_file = Path(file_path)
            if not excel_file.exists():
                return invalid_data_mapping_transactional_detail_data

            df = pd.read_excel(file_path, sheet_name=ExcelSheetName.TRANSACTIONAL_DETAIL_DATA.value, dtype=str, header=0)

            # Replace empty strings or "nan" strings with actual NaN
            df = df.replace(r'^\s*$', None, regex=True)
            # Filter rows where any of three columns are None
            mask = df["Project Number"].isna() | df["Subtask Number"].isna() | df["Award Number"].isna() | df["Transaction Number"].isna()
            # Get row indices (Excel rows are usually +2 if header=0)
            invalid_row_ids = df.index[mask].tolist()
            invalid_data_mapping_transactional_detail_data["non_identified_rows"] = invalid_row_ids

            for idx, row in df.iterrows():
                if idx in invalid_data_mapping_transactional_detail_data["non_identified_rows"]:
                    continue
                if idx in invalid_data_mapping_transactional_detail_data["invalid_rows"]:
                    continue

                # Sub task data
                sub_task_key = (
                    str(row.get("Project Number", "")).strip(),
                    str(row.get("Award Number", "")).strip(),
                    str(row.get("Subtask Number", "")).strip(),
                )
                if sub_task_key not in sub_task_by_project_award_map:
                    invalid_data_mapping_transactional_detail_data["invalid_rows"].append(idx)
                    continue
                
                # Transaction data
                data = {
                    "sub_task_id": row.get("Subtask Number", ""),
                    "award_id": row.get("Award Number", ""),
                    "transaction_number": self._safe_strip(row["Transaction Number"]),
                    "transaction_source": self._safe_strip(row["Transaction Source"]),
                    "expenditure_type": self._safe_strip(row["Expenditure Type"]),
                    "expenditure_category": self._safe_strip(
                        row["Expenditure Category"]
                    ),
                    "expenditure_organization": self._safe_strip(
                        row["Expenditure Organization"]
                    ),
                    "expenditure_item_date": self._parse_date(
                        row["Expenditure Item Date"]
                    ),
                    "accounting_period": self._safe_strip(row["Accounting Period"]),
                    "unit_of_measure": self._safe_strip(row["Unit of Measure"]),
                    "incurred_by_person": self._safe_strip(row["Incurred By Person"]),
                    "person_number": self._safe_strip(row["Person Number"]),
                    "position_number": self._safe_strip(row["Position Number"]),
                    "vendor_name": self._safe_strip(row["Vendor Name"]),
                    "po_number": self._safe_strip(row["PO Number"]),
                    "po_line_number": self._safe_strip(row["PO Line Number"]),
                    "ap_invoice_number": self._safe_strip(row["AP Invoice Number"]),
                    "ap_invoice_line_number": self._safe_strip(
                        row["AP Invoice Line Number"]
                    ),
                    "dist_line_num": self._safe_strip(row["Dist Line Num"]),
                    "invoice_date": self._parse_date(row["Invoice Date"]),
                    "check_number": self._safe_strip(row["Check Number"]),
                    "check_date": self._parse_date(row["Check Date"]),
                    "expenditure_batch": self._safe_strip(row["Expenditure Batch"]),
                    "expenditure_comment": self._safe_strip(row["Expenditure Comment"]),
                    "orig_transaction_reference": self._safe_strip(
                        row["Orig Transaction Reference"]
                    ),
                    "capitalizable_flag": self._safe_strip(row["Capitalizable Flag"])
                    == "Y",
                    "billable_flag": self._safe_strip(row["Billable Flag"]) == "Y",
                    "bill_hold_flag": self._safe_strip(row["Bill Hold Flag"]) == "Y",
                    "revenue_status": self._safe_strip(row["Revenue status"]),
                    "transaction_ar_invoice_status": self._safe_strip(
                        row["Transaction AR Invoice Status"]
                    ),
                    "servicedate_from": self._parse_date(row["ServiceDate From"]),
                    "servicedate_to": self._parse_date(row["ServiceDate To"]),
                    "gl_batch_name": self._safe_strip(row["GL Batch Name"]),
                    "quantity": float(row["Quantity"] or 0),
                    "transaction_amount": float(row["Transaction Amount"] or 0),
                    "burdened_amount": float(row["Burdened Amount"] or 0),
                    "rate": float(row["Rate"] or 0),
                }

                try:
                    transaction_data = WorkflowTransactionSchemaForValidation(**data)
                except Exception as e:
                    invalid_data_mapping_transactional_detail_data["invalid_rows"].append(idx)

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Transactional Detail Data validation completed in {duration:.2f}s")
            return invalid_data_mapping_transactional_detail_data
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return invalid_data_mapping_transactional_detail_data

    def _safe_strip(self, value):
        """Safely strip string values"""
        if value is None or pd.isna(value):
            return None
        return str(value).strip()

    def _parse_date(self, value):
        """Parse date value safely"""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        try:
            return pd.to_datetime(value).date()
        except Exception:
            logger.warning(f"Error parsing date: {value}")
            return None

    # Managing Excel files with same structure for invalid data

    def create_empty_excel_with_same_structure(self, excel_file: Path) -> str:
        try:
            # Read the original Excel file to get sheet names and headers
            excel = pd.ExcelFile(excel_file)
            sheet_names = excel.sheet_names
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".xlsx", 
                prefix="empty_structure_", 
                delete=False
            )
            temp_file.close()
            
            # Create a new workbook
            workbook = Workbook()
            
            # Remove the default sheet
            if workbook.active:
                workbook.remove(workbook.active)
            
            # Create sheets with the same names and headers as the original file
            for sheet_name in sheet_names:
                # Excel sheet names are limited to 31 characters
                safe_sheet_name = sheet_name[:31]
                worksheet = workbook.create_sheet(title=safe_sheet_name)
                
                # Read the original sheet to get headers
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=0)
                    headers = df.columns.tolist()
                    
                    # Add headers to the new sheet
                    worksheet.append(headers)
                    
                    # Style the header row (make it bold)
                    for cell in worksheet[1]:
                        cell.font = cell.font.copy(bold=True)
                        
                except Exception as e:
                    logger.warning(f"Could not read headers from sheet '{sheet_name}': {e}")
                    # Add a default header if we can't read the original
                    worksheet.append(["Column 1"])
            
            # Save the workbook
            workbook.save(temp_file.name)
            workbook.close()
            
            # Store the file path
            self.empty_structure_file_path = temp_file.name
            
            logger.info(f"Created empty Excel file with same structure")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to create empty Excel file with same structure: {e}")
            return None

    def copy_excel_file(self, file_path: Path) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_copy:
            shutil.copy2(file_path, tmp_copy.name)
            copy_path = tmp_copy.name
            logger.info(f"Copied Excel file")
            return copy_path

    def keep_only_invalid_rows(self, copy_file_path, sheets_wise_invalid_row_indexes):
        # Load all sheets from the file
        all_sheets = pd.read_excel(copy_file_path, sheet_name=None, dtype=str, header=0)
        for invalid_row_indexes_dict in sheets_wise_invalid_row_indexes:
            for sheet_name, invalid_row_indexes in invalid_row_indexes_dict.items():
                # Filter each relevant sheet
                if sheet_name in all_sheets:
                    df = all_sheets[sheet_name]
                    all_sheets[sheet_name] = df.loc[invalid_row_indexes].reset_index(drop=True)

        # Write all sheets back at once (preserves the ones we didn't touch)
        with pd.ExcelWriter(copy_file_path, engine="openpyxl") as writer:
            for sheet_name, df in all_sheets.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)

        logger.info(f"Updated file saved with only invalid rows")

    def keep_only_valid_rows(self, file_path, sheets_wise_invalid_row_indexes):

        # Load all sheets from the file
        all_sheets = pd.read_excel(file_path, sheet_name=None, dtype=str, header=0)
        for invalid_row_indexes_dict in sheets_wise_invalid_row_indexes:
            for sheet_name, invalid_row_indexes in invalid_row_indexes_dict.items():
                if sheet_name in all_sheets:
                    df = all_sheets[sheet_name]

                    # Drop the invalid rows, keep valid ones
                    valid_df = df.drop(index=invalid_row_indexes).reset_index(drop=True)

                    all_sheets[sheet_name] = valid_df

        # Write all sheets back (preserves untouched sheets)
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for s_name, df in all_sheets.items():
                df.to_excel(writer, index=False, sheet_name=s_name)

        logger.info(f"Updated file saved with only valid rows")