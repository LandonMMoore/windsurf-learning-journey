def prepare_budget_info_data(budget_info) -> dict:
    """Prepare budget info data for Elasticsearch"""
    return {
        "id": budget_info.id,
        "uuid": str(budget_info.uuid),
        "created_at": (
            budget_info.created_at.isoformat() if budget_info.created_at else None
        ),
        "updated_at": (
            budget_info.updated_at.isoformat() if budget_info.updated_at else None
        ),
        "par_id": budget_info.par_id,
        "task_name": budget_info.task_name,
    }
