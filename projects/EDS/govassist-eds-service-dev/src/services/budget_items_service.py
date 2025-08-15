import asyncio
from typing import Callable

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.exceptions import InternalServerError
from src.model.budget_info_model import BudgetInfo
from src.model.budget_items_model import BudgetItems
from src.model.elasticsearch_models import ParModel
from src.model.par_model import Par
from src.repository.budget_items_repository import BudgetItemsRepository
from src.schema.elastic_search_schema import BudgetInfoBaseES, BudgetItemES
from src.services.base_service import BaseService


class BudgetItemsService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(BudgetItemsRepository(session_factory))
        self._par_model = ParModel()

    async def _update_elasticsearch(self, budget_info_id: int, budget_item_data: dict):
        """Update Elasticsearch document with budget item"""
        max_retries = 2
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # First get the budget info to get the PAR ID
                with self._repository.session_factory() as session:
                    # Query the budget info table directly
                    stmt = select(BudgetInfo).where(BudgetInfo.id == budget_info_id)
                    budget_info = session.execute(stmt).scalar_one_or_none()

                    if not budget_info:
                        logger.error(
                            f"Budget info with ID {budget_info_id} not found in database"
                        )
                        raise ValueError(
                            f"Budget info with ID {budget_info_id} not found"
                        )

                    par_id = budget_info.par_id

                # First refresh the index to ensure latest data
                client = await self._par_model._get_client()
                await client.indices.refresh(index=self._par_model.index_name)

                # Get the PAR document directly by ID
                par_doc = await self._par_model.get_par(par_id)
                if not par_doc:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"PAR with ID {par_id} not found in Elasticsearch, retrying..."
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    raise ValueError(f"PAR with ID {par_id} not found in Elasticsearch")

                budget_info_list = par_doc.get("budget_info", [])
                budget_info_index = next(
                    (
                        i
                        for i, info in enumerate(budget_info_list)
                        if info.get("id") == budget_info_id
                    ),
                    None,
                )

                if budget_info_index is None:
                    logger.warning(
                        f"Budget info with ID {budget_info_id} not found in PAR document, adding it"
                    )
                    # If budget info not found in PAR document, add it
                    budget_info_list.append(
                        {"id": budget_info_id, "budget_items": [budget_item_data]}
                    )
                else:
                    budget_items = budget_info_list[budget_info_index].get(
                        "budget_items", []
                    )

                    existing_index = next(
                        (
                            i
                            for i, item in enumerate(budget_items)
                            if item.get("id") == budget_item_data["id"]
                        ),
                        None,
                    )

                    if existing_index is not None:
                        budget_items[existing_index] = budget_item_data
                    else:
                        budget_items.append(budget_item_data)

                    budget_info_list[budget_info_index]["budget_items"] = budget_items

                update_data = {"doc": {"budget_info": budget_info_list}}
                await client.update(
                    index=self._par_model.index_name,
                    id=par_doc["_id"],
                    body=update_data,
                )
                return
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise

    async def _update_budget_item_in_elasticsearch(
        self,
        par_id: int,
        budget_info_id: int,
        updated_data: dict,
        total_project_budget: float = None,
        budget_info_es_data: dict = None,
    ):
        client = await self._par_model._get_client()

        # Build the script based on whether we need to update total_project_budget
        script_source = """
            if (ctx._source.id == params.par_id) {
                if (ctx._source.budget_info == null) {
                    ctx._source.budget_info = [];
                }

                boolean budget_info_found = false;
                boolean budget_item_found = false;
                
                // Look for existing budget_info
                for (int i = 0; i < ctx._source.budget_info.length; i++) {
                    def b = ctx._source.budget_info[i];
                    if (b.id == params.budget_info_id) {
                        budget_info_found = true;
                        if (b.budget_items == null) {
                            b.budget_items = [];
                        }

                        // Look for existing budget_item within this budget_info
                        for (int j = 0; j < b.budget_items.length; j++) {
                            def bi = b.budget_items[j];
                            if (bi.id == params.updated_data.id) {
                                b.budget_items[j] = params.updated_data;
                                budget_item_found = true;
                                break;
                            }
                        }

                        // If budget_item not found, add it to existing budget_info
                        if (!budget_item_found) {
                            b.budget_items.add(params.updated_data);
                        }
                        break;
                    }
                }
                
                // If budget_info not found, create new budget_info with the budget_item
                if (!budget_info_found) {
                    ctx._source.budget_info.add(params.budget_info_es_data);
                    ctx._source.budget_info[0].budget_items = [params.updated_data];
                }
                
                // Update total project budget if provided
                ctx._source.total_project_budget = params.total_project_budget;
            }
        """
        script_params = {
            "par_id": par_id,
            "budget_info_id": budget_info_id,
            "updated_data": updated_data,
            "total_project_budget": total_project_budget,
            "budget_info_es_data": budget_info_es_data,
        }

        script = {
            "source": script_source,
            "lang": "painless",
            "params": script_params,
        }
        query = {"query": {"term": {"id": par_id}}, "script": script}

        try:
            response = await client.update_by_query(
                index=self._par_model.index_name,
                body=query,
                conflicts="proceed",
                refresh=True,
            )
            logger.info(
                f"Updated {response.get('updated', 0)} docs for budget_info in par_id={par_id}"
            )
        except Exception as e:
            logger.error(f"Failed to update budget_info in ES: {str(e)}")
            raise

    async def _update_par_total_budget_and_elasticsearch(
        self, par_id: int, budget_info_id: int, budget_item, budget_info_es_data: dict
    ):
        """
        Generic method to update PAR's total project budget in database and sync with Elasticsearch
        """
        with self._repository.session_factory() as session:
            # Calculate new total project budget
            total_proposed_budget = (
                session.query(func.coalesce(func.sum(BudgetItems.proposed_budget), 0.0))
                .join(BudgetInfo)
                .filter(
                    BudgetInfo.par_id == par_id,
                    BudgetItems.proposed_budget.isnot(None),  # Only sum non-NULL values
                )
                .scalar()
            )

            # Update PAR's total project budget in database
            par = session.query(Par).filter(Par.id == par_id).first()
            if par:
                par.total_project_budget = total_proposed_budget
                session.commit()

            # Update Elasticsearch - both budget item and total project budget in one call
            try:
                budget_item_es = BudgetItemES.model_validate(budget_item)
                budget_item_es_data = budget_item_es.model_dump()
                await self._update_budget_item_in_elasticsearch(
                    par_id,
                    budget_info_id,
                    budget_item_es_data,
                    float(total_proposed_budget),
                    budget_info_es_data,
                )
            except Exception as e:
                logger.error(f"Error updating Elasticsearch: {str(e)}")
                # Don't raise the error since the database update was successful

    async def add(self, data):
        created_budget_item = super().add(data)

        with self._repository.session_factory() as session:
            budget_info = (
                session.query(BudgetInfo)
                .filter(BudgetInfo.id == created_budget_item.budget_info_id)
                .first()
            )
            budget_info_id = budget_info.id
            par_id = budget_info.par_id

            budget_info_es = BudgetInfoBaseES.model_validate(budget_info)
            budget_info_es_data = budget_info_es.model_dump()

        # Update PAR total budget and sync with Elasticsearch
        await self._update_par_total_budget_and_elasticsearch(
            par_id, budget_info_id, created_budget_item, budget_info_es_data
        )

        return created_budget_item

    async def patch(self, id: int, schema):
        try:
            # First get the budget item to get its budget_info_id
            with self._repository.session_factory() as session:
                budget_item = (
                    session.query(self._repository.model)
                    .filter(self._repository.model.id == id)
                    .first()
                )
                if not budget_item:
                    raise ValueError(f"Budget item with ID {id} not found")

                budget_info_id = budget_item.budget_info_id

                # Get the budget info to get the par_id
                budget_info = (
                    session.query(BudgetInfo)
                    .filter(BudgetInfo.id == budget_info_id)
                    .first()
                )
                if not budget_info:
                    raise ValueError(f"Budget info with ID {budget_info_id} not found")

                par_id = budget_info.par_id

                budget_info_es = BudgetInfoBaseES.model_validate(budget_info)
                budget_info_es_data = budget_info_es.model_dump()

            # Update the budget item
            updated_budget_item = super().patch(id, schema)

            # Update PAR total budget and sync with Elasticsearch
            await self._update_par_total_budget_and_elasticsearch(
                par_id, budget_info_id, updated_budget_item, budget_info_es_data
            )

            return updated_budget_item
        except Exception:
            raise InternalServerError(detail="Internal Server Error")
