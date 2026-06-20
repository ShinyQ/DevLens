"""GitHub Copilot provider via GitHub REST API.

Requires GITHUB_TOKEN env var with 'copilot' scope.
Silently skipped if token is absent.
"""
from typing import Iterator

from devlens.config import settings
from devlens.providers.base import BaseProvider, RawSession


class CopilotProvider(BaseProvider):
    provider_name = "copilot"

    def is_available(self) -> bool:
        return bool(settings.github_token)

    def discover_sessions(self) -> Iterator[RawSession]:
        if not self.is_available():
            return

        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            if settings.github_org:
                url = f"https://api.github.com/orgs/{settings.github_org}/copilot/usage"
            else:
                url = "https://api.github.com/user/copilot/usage"

            response = httpx.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            usage_data = response.json()

            import json
            import tempfile
            from pathlib import Path

            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".jsonl", delete=False, prefix="copilot_"
            )
            for day in usage_data:
                tmp.write(json.dumps({"type": "copilot_daily", "data": day}) + "\n")
            tmp.close()

            yield RawSession(
                session_id="copilot-usage",
                project_slug="github-copilot",
                project_path="",
                file_path=Path(tmp.name),
            )

        except Exception:
            return
