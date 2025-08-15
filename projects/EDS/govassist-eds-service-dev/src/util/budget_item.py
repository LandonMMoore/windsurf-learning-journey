def prepare_budget_item_data(budget_item) -> dict:
    """Prepare budget item data for Elasticsearch"""
    return {
        "id": budget_item.id,
        "uuid": str(budget_item.uuid),
        "created_at": (
            budget_item.created_at.isoformat() if budget_item.created_at else None
        ),
        "updated_at": (
            budget_item.updated_at.isoformat() if budget_item.updated_at else None
        ),
        "account": budget_item.account,
        "parent_task_number": budget_item.parent_task_number,
        "parent_task_name": budget_item.parent_task_name,
        "subtask_number": budget_item.subtask_number,
        "lifetime_budget": (
            float(budget_item.lifetime_budget)
            if budget_item.lifetime_budget is not None
            else None
        ),
        "initial_allotment": (
            float(budget_item.initial_allotment)
            if budget_item.initial_allotment is not None
            else None
        ),
        "expenditures": (
            float(budget_item.expenditures)
            if budget_item.expenditures is not None
            else None
        ),
        "obligations": (
            float(budget_item.obligations)
            if budget_item.obligations is not None
            else None
        ),
        "commitments": (
            float(budget_item.commitments)
            if budget_item.commitments is not None
            else None
        ),
        "current_balance": (
            float(budget_item.current_balance)
            if budget_item.current_balance is not None
            else None
        ),
        "lifetime_balance": (
            float(budget_item.lifetime_balance)
            if budget_item.lifetime_balance is not None
            else None
        ),
        "proposed_budget": (
            float(budget_item.proposed_budget)
            if budget_item.proposed_budget is not None
            else None
        ),
        "change_amount": (
            float(budget_item.change_amount)
            if budget_item.change_amount is not None
            else None
        ),
        "budget_info_id": budget_item.budget_info_id,
        "comment": budget_item.comment,
    }
