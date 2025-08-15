from typing import Callable, List

from sqlalchemy.orm import Session

from src.model.par_award_association_model import ParAwardAssociation
from src.repository.base_repository import BaseRepository


class ParAwardAssociationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ParAwardAssociation)
        self._session_factory = session_factory

    def update_by_project_details_id(
        self, project_details_id: int, award_type_ids: List[int]
    ):
        with self._session_factory() as session:
            # Fetch existing associations
            existing_associations = (
                session.query(ParAwardAssociation)
                .filter(ParAwardAssociation.project_details_id == project_details_id)
                .all()
            )

            # Extract existing award_type_ids
            existing_award_type_ids = {
                assoc.award_type_id for assoc in existing_associations
            }

            # Determine which award_type_ids to remove
            award_type_ids_to_remove = existing_award_type_ids - set(award_type_ids)

            # Remove associations that are not in the new list
            for award_type_id in award_type_ids_to_remove:
                association_to_remove = (
                    session.query(ParAwardAssociation)
                    .filter(
                        ParAwardAssociation.project_details_id == project_details_id,
                        ParAwardAssociation.award_type_id == award_type_id,
                    )
                    .first()
                )
                if association_to_remove:
                    session.delete(association_to_remove)

            # Add new associations
            for award_type_id in award_type_ids:
                if award_type_id not in existing_award_type_ids:
                    new_association = ParAwardAssociation(
                        project_details_id=project_details_id,
                        award_type_id=award_type_id,
                    )
                    session.add(new_association)

            session.commit()
