import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from devlens.db.models.analytics import Message
from devlens.db.models.analytics import Session as SessionModel
from devlens.db.models.analytics import ToolUsage
from devlens.db.models.project import Project
from devlens.db.session import get_db
from devlens.ingestion.cost import compute_cost
from devlens.schemas.session import (
    MessageDetail,
    PaginatedSessionList,
    SessionDetail,
    SessionSummary,
    ToolUsageDetail,
)

router = APIRouter(tags=["sessions"])

VALID_SORT_FIELDS = {"started_at", "ended_at", "message_count", "tool_call_count", "total_input_tokens"}


def _session_to_summary(session: SessionModel, project_name: str) -> SessionSummary:
    duration = None
    if session.started_at and session.ended_at:
        delta = (session.ended_at - session.started_at).total_seconds() / 60
        if delta >= 0:
            duration = round(delta, 1)

    cost = compute_cost(
        session.model or "",
        session.total_input_tokens,
        session.total_output_tokens,
    )

    return SessionSummary(
        id=session.id,
        session_id=session.session_id,
        provider=session.provider,
        project_id=session.project_id,
        project_name=project_name,
        model=session.model,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_minutes=duration,
        message_count=session.message_count,
        tool_call_count=session.tool_call_count,
        total_input_tokens=session.total_input_tokens,
        total_output_tokens=session.total_output_tokens,
        total_tokens=session.total_input_tokens + session.total_output_tokens,
        estimated_cost=cost,
        has_compaction=session.has_compaction,
    )


@router.get("/sessions", response_model=PaginatedSessionList)
def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("started_at", pattern="^(started_at|ended_at|message_count|tool_call_count|total_input_tokens)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
) -> PaginatedSessionList:
    query = db.query(SessionModel).join(Project, SessionModel.project_id == Project.id)

    if project_id is not None:
        query = query.filter(SessionModel.project_id == project_id)
    if provider:
        query = query.filter(SessionModel.provider == provider)
    if model:
        query = query.filter(SessionModel.model.ilike(f"%{model}%"))
    if search:
        query = query.filter(
            or_(
                SessionModel.session_id.ilike(f"%{search}%"),
                Project.name.ilike(f"%{search}%"),
            )
        )

    sort_col = getattr(SessionModel, sort_by, SessionModel.started_at)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc().nullslast())
    else:
        query = query.order_by(sort_col.asc().nullsfirst())

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 0
    sessions = query.offset((page - 1) * page_size).limit(page_size).all()

    project_names: dict[int, str] = {}
    for s in sessions:
        if s.project_id not in project_names:
            p = db.query(Project).filter_by(id=s.project_id).first()
            project_names[s.project_id] = p.name if p else "unknown"

    items = [_session_to_summary(s, project_names[s.project_id]) for s in sessions]

    return PaginatedSessionList(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: int, db: Session = Depends(get_db)) -> SessionDetail:
    session = db.query(SessionModel).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    project = db.query(Project).filter_by(id=session.project_id).first()
    project_name = project.name if project else "unknown"

    summary = _session_to_summary(session, project_name)

    messages = (
        db.query(Message)
        .filter_by(session_id=session.id)
        .order_by(Message.timestamp.asc().nullslast())
        .all()
    )
    tool_usages = db.query(ToolUsage).filter_by(session_id=session.id).all()

    return SessionDetail(
        **summary.model_dump(),
        messages=[
            MessageDetail(
                id=m.id,
                role=m.role,
                content_summary=m.content_summary,
                input_tokens=m.input_tokens,
                output_tokens=m.output_tokens,
                cache_creation_tokens=m.cache_creation_tokens,
                cache_read_tokens=m.cache_read_tokens,
                model=m.model,
                timestamp=m.timestamp,
            )
            for m in messages
        ],
        tool_usages=[
            ToolUsageDetail(
                tool_name=t.tool_name,
                execution_count=t.execution_count,
                is_error_count=t.is_error_count,
            )
            for t in tool_usages
        ],
    )
