from __future__ import annotations

import xmlrpc.client


class OdooClientError(Exception):
    pass


class OdooClient:
    def __init__(self, base_url: str, database: str, email: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.database = database
        self.email = email
        self.password = password
        self._uid: int | None = None

    @property
    def common(self) -> xmlrpc.client.ServerProxy:
        return xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")

    @property
    def models(self) -> xmlrpc.client.ServerProxy:
        return xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")

    def authenticate(self) -> int:
        uid = self.common.authenticate(
            self.database,
            self.email,
            self.password,
            {},
        )
        if not isinstance(uid, int) or isinstance(uid, bool) or uid <= 0:
            raise OdooClientError("Authentication failed")
        self._uid = uid
        return uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            return self.authenticate()
        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ):
        args = args or []
        kwargs = kwargs or {}
        try:
            return self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs,
            )
        except xmlrpc.client.Fault as exc:
            raise OdooClientError(f"Odoo XML-RPC fault: {exc.faultString}") from exc
        except OSError as exc:
            raise OdooClientError(f"Odoo connection error: {exc}") from exc

    def list_projects(self) -> list[dict]:
        return self.execute_kw(
            "project.project",
            "search_read",
            args=[[("active", "=", True)]],
            kwargs={"fields": ["id", "name"], "order": "name asc"},
        )

    def list_task_stages(self, project_id: int) -> list[dict]:
        domain = ["|", ("project_ids", "=", False), ("project_ids", "in", [project_id])]
        return self.execute_kw(
            "project.task.type",
            "search_read",
            args=[domain],
            kwargs={"fields": ["id", "name"], "order": "sequence asc, name asc"},
        )

    def read_task(self, task_id: int, fields: list[str]) -> dict:
        rows = self.execute_kw(
            "project.task",
            "read",
            args=[[task_id]],
            kwargs={"fields": fields},
        )
        if not rows:
            raise OdooClientError(f"Task {task_id} not found")
        return rows[0]
