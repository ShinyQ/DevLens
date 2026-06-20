from datetime import datetime

from pydantic import BaseModel


class ProviderStats(BaseModel):
    name: str
    processed: int


class SyncResponse(BaseModel):
    files_checked: int
    files_processed: int
    sessions_upserted: int
    providers: list[ProviderStats]
    synced_at: datetime
