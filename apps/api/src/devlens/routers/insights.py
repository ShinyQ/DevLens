from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import DailyAggregate, Message
from devlens.db.models.analytics import Session as SessionModel
from devlens.db.models.analytics import ToolUsage
from devlens.db.models.project import Project
from devlens.db.session import get_db
from devlens.schemas.insight import InsightsResponse

router = APIRouter(tags=["insights"])

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@router.get("/insights", response_model=InsightsResponse)
def get_insights(db: Session = Depends(get_db)) -> InsightsResponse:
    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_messages = db.query(func.count(Message.id)).scalar() or 0

    avg_messages = (total_messages / total_sessions) if total_sessions > 0 else 0.0

    total_tool_calls = db.query(func.sum(ToolUsage.execution_count)).scalar() or 0

    # Peak day of week (SQLite strftime %w: 0=Sunday, 1=Monday, ..., 6=Saturday)
    day_row = (
        db.query(
            func.strftime("%w", Message.timestamp).label("dow"),
            func.count(Message.id).label("cnt"),
        )
        .filter(Message.timestamp.isnot(None))
        .group_by(func.strftime("%w", Message.timestamp))
        .order_by(func.count(Message.id).desc())
        .first()
    )
    peak_day = None
    if day_row and day_row.dow is not None:
        # strftime %w: 0=Sun, 1=Mon, ..., 6=Sat → map to our DAYS list (0=Mon)
        dow_map = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
        peak_day = dow_map.get(int(day_row.dow))

    # Most active hour
    hour_row = (
        db.query(
            func.strftime("%H", Message.timestamp).label("hour"),
            func.count(Message.id).label("cnt"),
        )
        .filter(Message.timestamp.isnot(None))
        .group_by(func.strftime("%H", Message.timestamp))
        .order_by(func.count(Message.id).desc())
        .first()
    )
    most_active_hour = int(hour_row.hour) if hour_row and hour_row.hour else None

    # Session durations
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.started_at.isnot(None), SessionModel.ended_at.isnot(None))
        .all()
    )
    durations = []
    for s in sessions:
        delta = (s.ended_at - s.started_at).total_seconds() / 60
        if delta >= 0:
            durations.append((s.session_id, delta))

    avg_duration = sum(d for _, d in durations) / len(durations) if durations else 0.0
    longest_session_id = None
    longest_duration = 0.0
    if durations:
        longest_session_id, longest_duration = max(durations, key=lambda x: x[1])

    # Most used tool
    tool_row = (
        db.query(ToolUsage.tool_name, func.sum(ToolUsage.execution_count).label("cnt"))
        .group_by(ToolUsage.tool_name)
        .order_by(func.sum(ToolUsage.execution_count).desc())
        .first()
    )

    # Busiest project
    project_row = (
        db.query(Project.name, func.count(SessionModel.id).label("cnt"))
        .join(SessionModel, SessionModel.project_id == Project.id)
        .group_by(Project.id)
        .order_by(func.count(SessionModel.id).desc())
        .first()
    )

    # Cache hit rate
    cache_totals = db.query(
        func.sum(Message.cache_creation_tokens),
        func.sum(Message.cache_read_tokens),
    ).first()
    cache_create = int(cache_totals[0] or 0)
    cache_read = int(cache_totals[1] or 0)
    cache_hit_rate = cache_read / (cache_create + cache_read) if (cache_create + cache_read) > 0 else 0.0

    return InsightsResponse(
        peak_day_of_week=peak_day,
        most_active_hour=most_active_hour,
        avg_session_duration_minutes=round(avg_duration, 1),
        longest_session_id=longest_session_id,
        longest_session_duration_minutes=round(longest_duration, 1),
        most_used_tool=tool_row.tool_name if tool_row else None,
        most_used_tool_count=int(tool_row.cnt) if tool_row else 0,
        busiest_project=project_row.name if project_row else None,
        cache_hit_rate=round(cache_hit_rate, 3),
        avg_messages_per_session=round(avg_messages, 1),
        total_tool_calls=int(total_tool_calls),
        total_sessions=int(total_sessions),
        total_messages=int(total_messages),
    )
