from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from devlens.db.session import get_db
from devlens.ingestion.engine import SyncEngine
from devlens.schemas.sync import SyncResponse

router = APIRouter(tags=["sync"])


@router.post("/sync", response_model=SyncResponse)
def trigger_sync(db: Session = Depends(get_db)) -> SyncResponse:
    engine = SyncEngine(db)
    stats = engine.run()
    return SyncResponse(
        **stats,
        synced_at=datetime.now(timezone.utc),
    )
