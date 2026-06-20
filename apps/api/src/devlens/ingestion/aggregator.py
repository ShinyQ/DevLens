from sqlalchemy import cast, func
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.types import Date

from devlens.db.models.analytics import DailyAggregate, Message, Session
from devlens.ingestion.cost import compute_cost


def rebuild_daily_aggregates(db: DBSession) -> None:
    """Full delete + rebuild of daily_aggregates from message data."""
    db.query(DailyAggregate).delete()

    rows = (
        db.query(
            cast(Message.timestamp, Date).label("agg_date"),
            Session.provider,
            Session.project_id,
            func.sum(Message.input_tokens).label("input_tokens"),
            func.sum(Message.output_tokens).label("output_tokens"),
            func.sum(Message.cache_creation_tokens).label("cache_creation_tokens"),
            func.sum(Message.cache_read_tokens).label("cache_read_tokens"),
            func.count(func.distinct(Session.id)).label("session_count"),
            func.count(Message.id).label("message_count"),
        )
        .join(Session, Message.session_id == Session.id)
        .filter(Message.timestamp.isnot(None))
        .group_by(
            cast(Message.timestamp, Date),
            Session.provider,
            Session.project_id,
        )
        .all()
    )

    # Gather per-model token totals for cost estimation
    model_rows = (
        db.query(
            cast(Message.timestamp, Date).label("agg_date"),
            Session.provider,
            Session.project_id,
            Message.model,
            func.sum(Message.input_tokens).label("input_tokens"),
            func.sum(Message.output_tokens).label("output_tokens"),
            func.sum(Message.cache_creation_tokens).label("cache_creation_tokens"),
            func.sum(Message.cache_read_tokens).label("cache_read_tokens"),
        )
        .join(Session, Message.session_id == Session.id)
        .filter(Message.timestamp.isnot(None), Message.model.isnot(None))
        .group_by(
            cast(Message.timestamp, Date),
            Session.provider,
            Session.project_id,
            Message.model,
        )
        .all()
    )

    # Build cost lookup: (date, provider, project_id) → total_cost
    cost_map: dict[tuple, float] = {}
    for mr in model_rows:
        key = (str(mr.agg_date), mr.provider, mr.project_id)
        cost = compute_cost(
            mr.model or "",
            mr.input_tokens or 0,
            mr.output_tokens or 0,
            mr.cache_creation_tokens or 0,
            mr.cache_read_tokens or 0,
        )
        cost_map[key] = cost_map.get(key, 0.0) + cost

    for row in rows:
        key = (str(row.agg_date), row.provider, row.project_id)
        estimated_cost = cost_map.get(key, 0.0)
        db.add(
            DailyAggregate(
                date=row.agg_date,
                provider=row.provider,
                project_id=row.project_id,
                input_tokens=row.input_tokens or 0,
                output_tokens=row.output_tokens or 0,
                cache_creation_tokens=row.cache_creation_tokens or 0,
                cache_read_tokens=row.cache_read_tokens or 0,
                session_count=row.session_count or 0,
                message_count=row.message_count or 0,
                estimated_cost=estimated_cost,
            )
        )
