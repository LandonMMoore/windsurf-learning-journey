from src.schema.par_award_association_schema import ParAwardAssociationInfo


def _format_award_association(assoc):
    """Format a single award association for Elasticsearch"""
    return {
        "id": assoc.id,
        "uuid": str(assoc.uuid),
        "created_at": assoc.created_at.isoformat() if assoc.created_at else None,
        "updated_at": assoc.updated_at.isoformat() if assoc.updated_at else None,
        "project_details_id": assoc.project_details_id,
        "award_type_id": assoc.award_type_id,
        "award_type": (
            {
                "id": assoc.award_type.id,
                "uuid": str(assoc.award_type.uuid),
                "created_at": (
                    assoc.award_type.created_at.isoformat()
                    if assoc.award_type.created_at
                    else None
                ),
                "updated_at": (
                    assoc.award_type.updated_at.isoformat()
                    if assoc.award_type.updated_at
                    else None
                ),
                "code": assoc.award_type.code,
                "description": assoc.award_type.description,
            }
            if assoc.award_type
            else None
        ),
    }


def _format_association_info(assoc):
    """Format a single award association for response"""
    return ParAwardAssociationInfo(
        id=assoc.id,
        project_details_id=assoc.project_details_id,
        award_type_id=assoc.award_type_id,
        award_type=(
            {
                "id": assoc.award_type.id,
                "code": assoc.award_type.code,
                "description": assoc.award_type.description,
            }
            if assoc.award_type
            else None
        ),
    )
