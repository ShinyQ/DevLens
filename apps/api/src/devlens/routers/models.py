from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from devlens.db.models.analytics import Message
from devlens.db.models.analytics import Session as SessionModel
from devlens.db.session import get_db
from devlens.ingestion.cost import compute_cost
from devlens.schemas.model import ModelStat

router = APIRouter(tags=["models"])


@router.get("/models", response_model=list[ModelStat])
def get_models(db: Session = Depends(get_db)) -> list[ModelStat]:
    rows = (
        db.query(
            Message.model,
            func.count(func.distinct(SessionModel.id)).label("session_count"),
            func.count(Message.id).label("message_count"),
            func.sum(Message.input_tokens).label("input_tokens"),
            func.sum(Message.output_tokens).label("output_tokens"),
            func.sum(Message.cache_creation_tokens).label("cache_creation_tokens"),
            func.sum(Message.cache_read_tokens).label("cache_read_tokens"),
        )
        .join(SessionModel, Message.session_id == SessionModel.id)
        .filter(Message.model.isnot(None))
        .group_by(Message.model)
        .order_by(func.count(Message.id).desc())
        .all()
    )

    results = []
    for row in rows:
        inp = int(row.input_tokens or 0)
        out = int(row.output_tokens or 0)
        cache_c = int(row.cache_creation_tokens or 0)
        cache_r = int(row.cache_read_tokens or 0)
        cost = compute_cost(row.model, inp, out, cache_c, cache_r)
        results.append(
            ModelStat(
                model=row.model,
                session_count=int(row.session_count or 0),
                message_count=int(row.message_count or 0),
                input_tokens=inp,
                output_tokens=out,
                cache_creation_tokens=cache_c,
                cache_read_tokens=cache_r,
                estimated_cost=cost,
            )
        )

    return results
