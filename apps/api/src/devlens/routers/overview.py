from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import DailyAggregate, Message, Session as SessionModel
from devlens.db.models.project import Project
from devlens.db.session import get_db
from devlens.schemas.overview import DailyCostPoint, DailyTokenPoint, OverviewResponse

router = APIRouter(tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(db: Session = Depends(get_db)) -> OverviewResponse:
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_projects = db.query(func.count(Project.id)).scalar() or 0

    token_totals = db.query(
        func.sum(DailyAggregate.input_tokens),
        func.sum(DailyAggregate.output_tokens),
        func.sum(DailyAggregate.cache_creation_tokens),
        func.sum(DailyAggregate.cache_read_tokens),
        func.sum(DailyAggregate.estimated_cost),
    ).first()

    total_input = int(token_totals[0] or 0)
    total_output = int(token_totals[1] or 0)
    total_cache_create = int(token_totals[2] or 0)
    total_cache_read = int(token_totals[3] or 0)
    cost_all_time = float(token_totals[4] or 0.0)

    cost_30d_row = (
        db.query(func.sum(DailyAggregate.estimated_cost))
        .filter(DailyAggregate.date >= thirty_days_ago)
        .scalar()
    )
    cost_30d = float(cost_30d_row or 0.0)

    cost_7d_row = (
        db.query(func.sum(DailyAggregate.estimated_cost))
        .filter(DailyAggregate.date >= seven_days_ago)
        .scalar()
    )
    cost_7d = float(cost_7d_row or 0.0)

    active_projects_30d = (
        db.query(func.count(func.distinct(SessionModel.project_id)))
        .filter(SessionModel.started_at >= thirty_days_ago)
        .scalar()
        or 0
    )

    # Daily token trend — last 30 days
    daily_rows = (
        db.query(
            DailyAggregate.date,
            func.sum(DailyAggregate.input_tokens),
            func.sum(DailyAggregate.output_tokens),
            func.sum(DailyAggregate.cache_creation_tokens),
            func.sum(DailyAggregate.cache_read_tokens),
            func.sum(DailyAggregate.estimated_cost),
        )
        .filter(DailyAggregate.date >= thirty_days_ago)
        .group_by(DailyAggregate.date)
        .order_by(DailyAggregate.date)
        .all()
    )

    token_trend = []
    cost_trend = []
    for row in daily_rows:
        inp = int(row[1] or 0)
        out = int(row[2] or 0)
        cache_c = int(row[3] or 0)
        cache_r = int(row[4] or 0)
        cost = float(row[5] or 0.0)

        token_trend.append(
            DailyTokenPoint(
                date=row[0],
                input_tokens=inp,
                output_tokens=out,
                cache_creation_tokens=cache_c,
                cache_read_tokens=cache_r,
                total_tokens=inp + out + cache_c + cache_r,
            )
        )
        cost_trend.append(
            DailyCostPoint(
                date=row[0],
                estimated_cost=cost,
                input_cost=cost * 0.6,
                output_cost=cost * 0.35,
                cache_cost=cost * 0.05,
            )
        )

    # Most active project (by session count)
    most_active = (
        db.query(Project.name, func.count(SessionModel.id).label("cnt"))
        .join(SessionModel, SessionModel.project_id == Project.id)
        .group_by(Project.id)
        .order_by(func.count(SessionModel.id).desc())
        .first()
    )

    # Most used model
    most_model = (
        db.query(SessionModel.model, func.count(SessionModel.id).label("cnt"))
        .filter(SessionModel.model.isnot(None))
        .group_by(SessionModel.model)
        .order_by(func.count(SessionModel.id).desc())
        .first()
    )

    return OverviewResponse(
        total_sessions=total_sessions,
        total_projects=total_projects,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_cache_tokens=total_cache_create + total_cache_read,
        total_tokens=total_input + total_output + total_cache_create + total_cache_read,
        cost_all_time=cost_all_time,
        cost_30d=cost_30d,
        cost_7d=cost_7d,
        active_projects_30d=int(active_projects_30d),
        token_trend=token_trend,
        cost_trend=cost_trend,
        most_active_project=most_active[0] if most_active else None,
        most_used_model=most_model[0] if most_model else None,
    )
