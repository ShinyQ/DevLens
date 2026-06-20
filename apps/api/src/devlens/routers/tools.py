from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import Session as SessionModel
from devlens.db.models.analytics import ToolUsage
from devlens.db.session import get_db
from devlens.schemas.tool import ToolStat

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolStat])
def get_tools(
    project_id: Optional[int] = None,
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[ToolStat]:
    query = (
        db.query(
            ToolUsage.tool_name,
            func.sum(ToolUsage.execution_count).label("execution_count"),
            func.sum(ToolUsage.is_error_count).label("is_error_count"),
            func.count(func.distinct(ToolUsage.session_id)).label("session_count"),
        )
        .join(SessionModel, ToolUsage.session_id == SessionModel.id)
    )

    if project_id is not None:
        query = query.filter(SessionModel.project_id == project_id)
    if provider:
        query = query.filter(SessionModel.provider == provider)

    rows = (
        query.group_by(ToolUsage.tool_name)
        .order_by(func.sum(ToolUsage.execution_count).desc())
        .all()
    )

    results = []
    for row in rows:
        exec_count = int(row.execution_count or 0)
        err_count = int(row.is_error_count or 0)
        error_rate = (err_count / exec_count) if exec_count > 0 else 0.0
        results.append(
            ToolStat(
                tool_name=row.tool_name,
                execution_count=exec_count,
                is_error_count=err_count,
                error_rate=round(error_rate * 100, 1),
                session_count=int(row.session_count or 0),
            )
        )

    return results
