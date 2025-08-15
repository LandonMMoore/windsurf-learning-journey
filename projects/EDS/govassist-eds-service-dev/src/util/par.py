from sqlalchemy import func

from src.model.par_activity_model import ParActivity


def copy_model(instance, exclude=(), **overrides):
    data = {
        k: v
        for k, v in vars(instance).items()
        if not k.startswith("_") and k not in exclude
    }
    data.update(overrides)
    return type(instance)(**data)


def get_latest_par_status_map(par_ids, session_factory):
    if not par_ids:
        return {}

    with session_factory() as session:
        latest_activities = (
            session.query(
                ParActivity.par_id,
                ParActivity.status,
                func.row_number()
                .over(
                    partition_by=ParActivity.par_id,
                    order_by=ParActivity.date.desc(),
                )
                .label("rn"),
            )
            .filter(ParActivity.par_id.in_(par_ids))
            .subquery()
        )

        # Get only the latest status for each par_id
        status_map = dict(
            session.query(latest_activities.c.par_id, latest_activities.c.status)
            .filter(latest_activities.c.rn == 1)
            .all()
        )

    return status_map
