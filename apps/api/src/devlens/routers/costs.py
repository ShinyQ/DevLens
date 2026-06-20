from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import DailyAggregate, Message
from devlens.db.models.analytics import Session as SessionModel
from devlens.db.session import get_db
from devlens.ingestion.cost import compute_cost
from devlens.schemas.cost import CostDataPoint, CostResponse, ModelCostBreakdown

router = APIRouter(tags=["costs"])


@router.get("/costs", response_model=CostResponse)
def get_costs(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    days: int = Query(90, ge=7, le=730),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> CostResponse:
    cutoff = date.today() - timedelta(days=days)

    query = db.query(
        DailyAggregate.date,
        func.sum(DailyAggregate.input_tokens).label("input_tokens"),
        func.sum(DailyAggregate.output_tokens).label("output_tokens"),
        func.sum(DailyAggregate.cache_creation_tokens).label("cache_creation_tokens"),
        func.sum(DailyAggregate.cache_read_tokens).label("cache_read_tokens"),
        func.sum(DailyAggregate.estimated_cost).label("total_cost"),
    ).filter(DailyAggregate.date >= cutoff)

    if project_id is not None:
        query = query.filter(DailyAggregate.project_id == project_id)

    daily_rows = query.group_by(DailyAggregate.date).order_by(DailyAggregate.date).all()

    # Group by requested granularity
    def _period_key(d: date) -> str:
        if granularity == "day":
            return d.isoformat()
        elif granularity == "week":
            monday = d - timedelta(days=d.weekday())
            return f"W{monday.isocalendar()[1]} {monday.year}"
        else:
            return f"{d.year}-{d.month:02d}"

    period_map: dict[str, dict] = {}
    for row in daily_rows:
        key = _period_key(row.date)
        if key not in period_map:
            period_map[key] = {
                "period": key,
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_tokens": 0,
                "total_cost": 0.0,
            }
        inp = int(row.input_tokens or 0)
        out = int(row.output_tokens or 0)
        cache_c = int(row.cache_creation_tokens or 0)
        cache_r = int(row.cache_read_tokens or 0)
        cost = float(row.total_cost or 0.0)
        period_map[key]["input_tokens"] += inp
        period_map[key]["output_tokens"] += out
        period_map[key]["cache_tokens"] += cache_c + cache_r
        period_map[key]["total_cost"] += cost

    data_points = []
    for p in period_map.values():
        total = p["total_cost"]
        data_points.append(
            CostDataPoint(
                period=p["period"],
                input_cost=total * 0.60,
                output_cost=total * 0.35,
                cache_cost=total * 0.05,
                total_cost=total,
                input_tokens=p["input_tokens"],
                output_tokens=p["output_tokens"],
            )
        )

    total_cost = sum(p["total_cost"] for p in period_map.values())

    # Model breakdown
    model_query = (
        db.query(
            Message.model,
            func.sum(Message.input_tokens).label("input_tokens"),
            func.sum(Message.output_tokens).label("output_tokens"),
            func.sum(Message.cache_creation_tokens).label("cache_creation_tokens"),
            func.sum(Message.cache_read_tokens).label("cache_read_tokens"),
        )
        .join(SessionModel, Message.session_id == SessionModel.id)
        .filter(Message.model.isnot(None), Message.timestamp >= cutoff)
    )
    if project_id is not None:
        model_query = model_query.filter(SessionModel.project_id == project_id)

    model_rows = model_query.group_by(Message.model).all()

    model_breakdown = []
    for mr in model_rows:
        cost = compute_cost(
            mr.model or "",
            int(mr.input_tokens or 0),
            int(mr.output_tokens or 0),
            int(mr.cache_creation_tokens or 0),
            int(mr.cache_read_tokens or 0),
        )
        pct = (cost / total_cost * 100) if total_cost > 0 else 0.0
        model_breakdown.append(
            ModelCostBreakdown(
                model=mr.model,
                input_tokens=int(mr.input_tokens or 0),
                output_tokens=int(mr.output_tokens or 0),
                estimated_cost=cost,
                percentage=round(pct, 1),
            )
        )

    model_breakdown.sort(key=lambda x: x.estimated_cost, reverse=True)

    return CostResponse(
        granularity=granularity,
        total_cost=total_cost,
        total_input_cost=total_cost * 0.60,
        total_output_cost=total_cost * 0.35,
        total_cache_cost=total_cost * 0.05,
        data_points=data_points,
        model_breakdown=model_breakdown,
    )
