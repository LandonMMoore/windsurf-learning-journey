from src.core.exceptions import ValidationError


def group_and_sum_change_amount(data):
    """
    Groups data based on "parent_task_name" and sums up "change_amount".
    Handles exceptions to prevent crashes.
    """
    result = {}
    try:
        for task in data:
            parent_task_name = getattr(task, "task_name", "Unknown")
            budget_items = getattr(task, "budget_items", [])
            total_change_amount = sum(
                getattr(item, "change_amount", 0.0) or 0.0 for item in budget_items
            )
            result[parent_task_name] = total_change_amount
    except Exception:
        raise ValidationError(detail="Error processing data")
    return result
