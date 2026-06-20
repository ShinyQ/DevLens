from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import DailyAggregate, Message
from devlens.db.models.analytics import Session as SessionModel
from devlens.db.models.analytics import ToolUsage
from devlens.db.models.project import Project
from devlens.db.session import get_db
from devlens.schemas.project import ProjectDetail, ProjectSummary

router = APIRouter(tags=["projects"])


def _build_project_summary(project: Project, db: Session) -> ProjectSummary:
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_sessions = (
        db.query(func.count(SessionModel.id)).filter_by(project_id=project.id).scalar() or 0
    )
    sessions_30d = (
        db.query(func.count(SessionModel.id))
        .filter(
            SessionModel.project_id == project.id,
            SessionModel.started_at >= thirty_days_ago,
        )
        .scalar()
        or 0
    )

    token_row = (
        db.query(
            func.sum(DailyAggregate.input_tokens),
            func.sum(DailyAggregate.output_tokens),
            func.sum(DailyAggregate.estimated_cost),
        )
        .filter_by(project_id=project.id)
        .first()
    )

    total_input = int(token_row[0] or 0)
    total_output = int(token_row[1] or 0)
    est_cost = float(token_row[2] or 0.0)

    last_active = (
        db.query(func.max(SessionModel.ended_at))
        .filter_by(project_id=project.id)
        .scalar()
    )

    most_model_row = (
        db.query(SessionModel.model, func.count(SessionModel.id).label("cnt"))
        .filter(SessionModel.project_id == project.id, SessionModel.model.isnot(None))
        .group_by(SessionModel.model)
        .order_by(func.count(SessionModel.id).desc())
        .first()
    )

    return ProjectSummary(
        id=project.id,
        name=project.name,
        slug=project.slug,
        path=project.path,
        total_sessions=int(total_sessions),
        sessions_30d=int(sessions_30d),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_tokens=total_input + total_output,
        estimated_cost=est_cost,
        last_active=last_active,
        most_used_model=most_model_row[0] if most_model_row else None,
    )


@router.get("/projects", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectSummary]:
    projects = db.query(Project).order_by(Project.name).all()
    return [_build_project_summary(p, db) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectDetail:
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    summary = _build_project_summary(project, db)

    total_messages = (
        db.query(func.count(Message.id))
        .join(SessionModel, Message.session_id == SessionModel.id)
        .filter(SessionModel.project_id == project_id)
        .scalar()
        or 0
    )

    total_tool_calls = (
        db.query(func.sum(ToolUsage.execution_count))
        .join(SessionModel, ToolUsage.session_id == SessionModel.id)
        .filter(SessionModel.project_id == project_id)
        .scalar()
        or 0
    )

    sessions = db.query(SessionModel).filter_by(project_id=project_id).all()
    durations = []
    for s in sessions:
        if s.started_at and s.ended_at:
            delta = (s.ended_at - s.started_at).total_seconds() / 60
            if delta > 0:
                durations.append(delta)

    avg_duration = sum(durations) / len(durations) if durations else None

    return ProjectDetail(
        **summary.model_dump(),
        total_messages=int(total_messages),
        total_tool_calls=int(total_tool_calls),
        avg_session_duration_minutes=avg_duration,
    )
