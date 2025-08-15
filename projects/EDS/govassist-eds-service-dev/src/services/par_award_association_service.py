from typing import Callable, List

from loguru import logger
from sqlalchemy.orm import Session, joinedload

from src.core.exceptions import InternalServerError
from src.model.elasticsearch_models import ParModel
from src.model.par_award_association_model import ParAwardAssociation
from src.repository.par_award_association_repository import (
    ParAwardAssociationRepository,
)
from src.schema.par_award_association_schema import ParAwardAssociationListResponse
from src.services.base_service import BaseService
from src.util.par_award_association import (
    _format_association_info,
    _format_award_association,
)


class ParAwardAssociationService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ParAwardAssociationRepository(session_factory))
        self._session_factory = session_factory
        self._par_model = ParModel()

    def _get_updated_associations(
        self, project_details_id: int
    ) -> List[ParAwardAssociation]:
        """Get updated associations from database"""
        with self._session_factory() as session:
            return (
                session.query(ParAwardAssociation)
                .options(joinedload(ParAwardAssociation.award_type))
                .filter(ParAwardAssociation.project_details_id == project_details_id)
                .all()
            )

    async def _update_elasticsearch(
        self, project_details_id: int, award_associations: List[dict]
    ):
        """Update Elasticsearch document with new award associations"""
        try:
            query = {"query": {"term": {"project_details_id": project_details_id}}}
            client = await self._par_model._get_client()
            response = await client.search(index=self._par_model.index_name, body=query)
            hits = response["hits"]["hits"]

            if hits:
                par_doc = hits[0]
                update_data = {"doc": {"award_associations": award_associations}}
                client = await self._par_model._get_client()
                await client.update(
                    index=self._par_model.index_name,
                    id=par_doc["_id"],
                    body=update_data,
                )
            else:
                logger.error(
                    f"No PAR document found with project_details_id: {project_details_id}"
                )
        except Exception:
            logger.error("Error updating Elasticsearch document")
            raise InternalServerError(detail="Internal Server Error")

    async def update_by_project_details_id(
        self, project_details_id: int, award_type_ids: List[int]
    ) -> ParAwardAssociationListResponse:
        # Update associations in database
        self._repository.update_by_project_details_id(
            project_details_id, award_type_ids
        )

        # Get updated associations
        updated_associations = self._get_updated_associations(project_details_id)

        # Format associations for Elasticsearch and response
        award_associations = [
            _format_award_association(assoc) for assoc in updated_associations
        ]
        formatted_associations = [
            _format_association_info(assoc) for assoc in updated_associations
        ]

        # Update Elasticsearch
        await self._update_elasticsearch(project_details_id, award_associations)

        return ParAwardAssociationListResponse(
            founds=formatted_associations, search_options=None
        )
