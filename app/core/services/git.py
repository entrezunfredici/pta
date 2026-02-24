from __future__ import annotations

import subprocess
from urllib.parse import quote, urlsplit, urlunsplit


class GitClientError(Exception):
    pass


class GitClient:
    def __init__(
        self,
        repository_url: str,
        username: str | None = None,
        token: str | None = None,
    ) -> None:
        self.repository_url = repository_url
        self.username = username
        self.token = token

    @property
    def auth_repository_url(self) -> str:
        if not self.token:
            return self.repository_url
        split = urlsplit(self.repository_url)
        safe_user = quote(self.username or "oauth2", safe="")
        safe_token = quote(self.token, safe="")
        netloc = f"{safe_user}:{safe_token}@{split.hostname or ''}"
        if split.port:
            netloc = f"{netloc}:{split.port}"
        return urlunsplit((split.scheme, netloc, split.path, split.query, split.fragment))

    def _run(self, args: list[str]) -> str:
        proc = subprocess.run(args, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise GitClientError(proc.stderr.strip() or "Git command failed")
        return proc.stdout.strip()

    def get_branch_sha(self, branch_name: str) -> str | None:
        output = self._run(
            ["git", "ls-remote", self.auth_repository_url, f"refs/heads/{branch_name}"]
        )
        if not output:
            return None
        return output.split()[0]

    def create_branch(self, source_branch: str, work_branch: str) -> str:
        if not work_branch:
            return "skipped"
        if self.get_branch_sha(work_branch):
            return "already_exists"
        source_sha = self.get_branch_sha(source_branch)
        if not source_sha:
            raise GitClientError(f"Source branch '{source_branch}' not found")
        self._run(
            ["git", "push", self.auth_repository_url, f"{source_sha}:refs/heads/{work_branch}"]
        )
        return "created"
