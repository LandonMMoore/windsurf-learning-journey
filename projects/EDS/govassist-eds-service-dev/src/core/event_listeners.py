from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history

from src.model.log import Log


def log_insert(mapper, connection, target):
    # session = Session.object_session(target)
    log_entry = Log(
        table_name=target.__tablename__, action="INSERT", details=str(target.__dict__)
    )
    connection.execute(
        Log.__table__.insert().values(
            table_name=log_entry.table_name,
            action=log_entry.action,
            details=log_entry.details,
        )
    )


def log_update(mapper, connection, target):
    # session = Session.object_session(target)
    changes = {}
    for key, attr in target.__mapper__.c.items():
        history = get_history(target, key)
        if history.has_changes():
            changes[key] = history.added[0] if history.added else None
    log_entry = Log(
        table_name=target.__tablename__, action="UPDATE", details=str(changes)
    )
    connection.execute(
        Log.__table__.insert().values(
            table_name=log_entry.table_name,
            action=log_entry.action,
            details=log_entry.details,
        )
    )


def log_delete(mapper, connection, target):
    # session = Session.object_session(target)
    log_entry = Log(
        table_name=target.__tablename__, action="DELETE", details=str(target.__dict__)
    )
    connection.execute(
        Log.__table__.insert().values(
            table_name=log_entry.table_name,
            action=log_entry.action,
            details=log_entry.details,
        )
    )


def register_listeners():

    for model in [Log]:
        event.listen(model, "after_insert", log_insert)
        event.listen(model, "after_update", log_update)
        event.listen(model, "after_delete", log_delete)
