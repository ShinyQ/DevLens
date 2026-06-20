from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from devlens.ingestion.parser import ParsedSession


@dataclass
class RawSession:
    session_id: str
    project_slug: str
    project_path: str
    file_path: Path


class BaseProvider(ABC):
    provider_name: str

    @abstractmethod
    def discover_sessions(self) -> Iterator[RawSession]:
        """Yield all session files this provider knows about."""
        ...

    def file_checksum(self, path: Path) -> str:
        import hashlib

        return hashlib.md5(path.read_bytes()).hexdigest()

    def is_available(self) -> bool:
        return True
