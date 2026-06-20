from pathlib import Path
from typing import Iterator

from devlens.config import settings
from devlens.providers.base import BaseProvider, RawSession


class ClaudeProvider(BaseProvider):
    provider_name = "claude"

    def is_available(self) -> bool:
        projects_dir = settings.claude_data_path / "projects"
        return projects_dir.exists()

    def discover_sessions(self) -> Iterator[RawSession]:
        projects_dir = settings.claude_data_path / "projects"
        if not projects_dir.exists():
            return

        for project_dir in sorted(projects_dir.iterdir()):
            if not project_dir.is_dir():
                continue

            slug, path = self._parse_project_dir(project_dir.name)

            for jsonl_file in sorted(project_dir.glob("*.jsonl")):
                yield RawSession(
                    session_id=jsonl_file.stem,
                    project_slug=slug,
                    project_path=path,
                    file_path=jsonl_file,
                )

    def _parse_project_dir(self, dirname: str) -> tuple[str, str]:
        """Convert '-home-user-MyProject' → ('MyProject', '/home/user/MyProject')."""
        stripped = dirname.lstrip("-")
        parts = stripped.split("-")

        try:
            user_idx = parts.index("user")
            project_parts = parts[user_idx + 1 :]
            slug = "-".join(project_parts) if project_parts else stripped
            path = "/" + "/".join(parts[: user_idx + 1]) + "/" + "/".join(project_parts)
        except ValueError:
            slug = stripped
            path = ""

        return slug or dirname, path
