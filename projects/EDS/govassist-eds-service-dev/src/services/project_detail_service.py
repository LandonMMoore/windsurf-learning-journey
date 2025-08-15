from typing import Any, Callable, Dict

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.core.exceptions import InternalServerError, NotFoundError
from src.model.elasticsearch_models import ParModel
from src.model.par_award_association_model import ParAwardAssociation
from src.model.par_model import Par
from src.model.project_detail_model import ProjectDetails
from src.repository.project_detail_repository import ProjectDetailRepository
from src.schema.elastic_search_schema import ProjectDetailsES
from src.schema.par_schema import ParUpdate
from src.schema.project_detail_schema import (
    ProjectDetailCreate,
    ProjectDetailCreateRequest,
)
from src.services.base_service import BaseService
from src.services.par_award_association_service import ParAwardAssociationService
from src.services.par_service import ParService


class ProjectDetailService(BaseService):

    PROJECT_RELATIONSHIP_FIELDS = {
        "award",
        "cost_center",
        "fhwa_program_code",
        "fhwa_project_number",
        "fhwa_soar_grant",
        "fhwa_soar_project_no",
        "fhwa_stip_reference",
        "fhwa_categories",
        "master_project",
        "organization",
        "project_location",
        "par_budget_analysis",
        "award_types",
    }

    PROJECT_RELATIONSHIP_BY_ID_FIELDS = {
        "award_id": "award",
        "cost_center_id": "cost_center",
        "fhwa_program_code_id": "fhwa_program_code",
        "fhwa_project_number_id": "fhwa_project_number",
        "fhwa_soar_grant_id": "fhwa_soar_grant",
        "fhwa_soar_project_no_id": "fhwa_soar_project_no",
        "fhwa_stip_reference_id": "fhwa_stip_reference",
        "fhwa_categories_id": "fhwa_categories",
        "master_project_id": "master_project",
        "eds_organization_id": "organization",
        "project_location_id": "project_location",
    }

    def __init__(
        self,
        session_factory: Callable[..., Session],
        par_service: ParService,
        par_award_service: ParAwardAssociationService,
    ):
        super().__init__(ProjectDetailRepository(session_factory))
        self._par_award_service = par_award_service
        self._par_service = par_service
        self._par_model = ParModel()

    def _get_updated_relationship_fields(self, updated_fields: Dict[str, Any]) -> set:
        """Identify which relationship fields were updated based on foreign key changes"""
        # Map foreign key fields to their relationship names
        fk_to_relationship = self.PROJECT_RELATIONSHIP_BY_ID_FIELDS

        updated_relationships = set()
        for field_name in updated_fields:
            if field_name in fk_to_relationship:
                updated_relationships.add(fk_to_relationship[field_name])

        return updated_relationships

    def _fetch_project_details_with_selective_relationships(
        self, project_details_id: int, updated_relationships: set
    ):
        """Fetch project details with only the updated relationships loaded"""
        with self._repository.session_factory() as session:
            query = session.query(ProjectDetails).filter(
                ProjectDetails.id == project_details_id
            )

            # Load only the relationships that were updated
            if updated_relationships:
                for rel_name in updated_relationships:
                    if hasattr(ProjectDetails, rel_name):
                        query = query.options(
                            joinedload(getattr(ProjectDetails, rel_name))
                        )

            project_details = query.first()

            if not project_details:
                logger.error(f"ProjectDetails not found with id: {project_details_id}")
                return None

            return project_details

    def _get_relationship_fields_to_exclude(self, updated_relationships: set) -> set:
        """Get the set of relationship fields to exclude from ES update"""
        # All possible relationship fields in ProjectDetailsES
        all_relationship_fields = self.PROJECT_RELATIONSHIP_FIELDS

        # Exclude relationship fields that weren't updated
        exclude_fields = all_relationship_fields - updated_relationships

        # Always exclude these heavy fields regardless because they are not updated via the project_detail_service.
        exclude_fields.add("par_budget_analysis")
        exclude_fields.add("award_types")

        return exclude_fields

    async def _update_all_elasticsearch_documents(
        self, project_details_id: int, es_data: Dict[str, Any]
    ):
        """Update all PAR documents that reference the given project_details_id"""
        try:
            client = await self._par_model._get_client()

            # Define the update script to replace the nested 'project_details' object
            script = {
                "source": """
                    if (ctx._source.containsKey("project_details")) {
                        ctx._source.project_details = params.project_details;
                    }
                """,
                "lang": "painless",
                "params": {"project_details": es_data},
            }

            # Use the update_by_query API
            query = {
                "query": {"term": {"project_details.id": project_details_id}},
                "script": script,
            }

            response = await client.update_by_query(
                index=self._par_model.index_name,
                body=query,
                conflicts="proceed",  # Optional: handle version conflicts
                refresh=True,  # Optional: make changes immediately visible
            )

            logger.info(
                f"Updated {response.get('updated', 0)} documents in Elasticsearch for project_details_id: {project_details_id}"
            )

        except Exception:
            logger.error(
                "Error in update_by_query for project_details_id={project_details_id}"
            )
            raise InternalServerError(detail="Internal Server Error")

    async def add(self, schema: ProjectDetailCreateRequest) -> Any:
        # Create project detail
        project_detail = ProjectDetailCreate(
            **schema.dict(exclude={"award_type_ids", "par_id"})
        )
        created_project = super().add(project_detail)

        # Add award associations if provided
        if schema.award_type_ids:
            par_award_objs = [
                ParAwardAssociation(
                    project_details_id=created_project.id, award_type_id=award_type_id
                )
                for award_type_id in schema.award_type_ids
            ]
            with self._repository.session_factory() as session:
                session.bulk_save_objects(par_award_objs)
                session.commit()

        # Refetch the project details with to fetch the award_types as well.

        par_update = ParUpdate(project_details_id=created_project.id)
        await self._par_service.patch(schema.par_id, par_update)
        # Update PAR if provided
        if schema.par_id:
            with self._repository.session_factory() as session:
                project_details = (
                    session.query(ProjectDetails)
                    .filter(ProjectDetails.id == created_project.id)
                    .first()
                )

                project_details_es = ProjectDetailsES.model_validate(project_details)
                data = project_details_es.model_dump(exclude={"par_budget_analysis"})
                await self._par_model.update(
                    doc_id=schema.par_id, data={"project_details": data}
                )

        return created_project

    async def patch(self, id: int, schema: Any) -> Any:
        # Update project details
        data = super().patch(id, schema)

        # Get only the updated fields from the schema
        updated_fields = schema.dict(exclude_unset=True)
        # Only proceed with Elasticsearch update if there are actual field updates
        if not updated_fields:
            return data

        # Identify which relationship fields were updated
        updated_relationship_fields = self._get_updated_relationship_fields(
            updated_fields
        )

        # Fetch project details with only the updated relationships loaded
        project_details = self._fetch_project_details_with_selective_relationships(
            id, updated_relationship_fields
        )

        if project_details:
            # Use schema to dump the model object
            project_details_es = ProjectDetailsES.construct(**project_details.__dict__)

            # Exclude relationship fields that weren't updated
            exclude_fields = self._get_relationship_fields_to_exclude(
                updated_relationship_fields
            )
            es_data = project_details_es.model_dump(exclude=exclude_fields)

            # Update the first matching document in Elasticsearch
            await self._update_all_elasticsearch_documents(id, es_data)

        return data

    async def update_par_meta(self, par_id: int, par_meta):
        par_data = self._par_service.get_by_id(par_id)
        if par_data.project_details:
            project_details_data = self.get_by_id(par_data.project_details.id)
            await self.patch(project_details_data.id, par_meta)
            return par_meta
        else:
            raise NotFoundError(detail=f"not found project details: {par_id}")

    def sync_project_name_with_project_number(
        self,
        page: int = 1,
        page_size: int = 15,
        search: str = None,
        request_type: str = None,
    ):
        with self._repository.session_factory() as session:
            # Query for unique project numbers and their names
            query = (
                session.query(
                    func.distinct(func.trim(self._repository.model.project_number)),
                    func.trim(self._repository.model.project_name),
                    func.min(self._repository.model.id).label("project_details_id"),
                    func.min(Par.id).label("par_id"),
                )
                .outerjoin(Par, self._repository.model.id == Par.project_details_id)
                .filter(
                    Par.request_type == request_type,
                    self._repository.model.project_number.isnot(None),
                    func.trim(self._repository.model.project_number) != "",
                    self._repository.model.project_name.isnot(None),
                    func.trim(self._repository.model.project_name) != "",
                )
            )

            # Apply search filter if provided
            if search:
                search_filter = func.trim(self._repository.model.project_number).ilike(
                    f"%{search}%"
                ) | func.trim(self._repository.model.project_name).ilike(f"%{search}%")
                query = query.filter(search_filter)

            # Only unique project numbers
            query = query.group_by(
                func.trim(self._repository.model.project_number),
                func.trim(self._repository.model.project_name),
            )
            query = query.order_by(
                func.trim(self._repository.model.project_number).asc()
            )

            total_count = query.count()
            results = query.offset((page - 1) * page_size).limit(page_size).all()

            formatted = [
                {
                    "project_details_id": project_details_id,
                    "par_id": par_id,
                    "difs_project_number": project_number,
                    "difs_project_name": project_name,
                }
                for project_number, project_name, project_details_id, par_id in results
                if project_number and project_name
            ]
            return {
                "results": formatted,
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "search": search,
            }
