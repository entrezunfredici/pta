from django.db import models


class _SyncStatus(models.TextChoices):
    BRANCH_CREATED = "branch_created", "Branch Created"
    MR_OPENED = "mr_opened", "MR Opened"
    CHANGES_REQUESTED = "changes_requested", "Changes Requested"
    APPROVED = "approved", "Approved"
    MERGED_DEV = "merged_dev", "Merged Dev"
    MERGED_MAIN = "merged_main", "Merged Main"
    CLOSED = "closed", "Closed"


class Meta:
    db_table = "bridge_tasksync"
    indexes = [
        models.Index(fields=["odoo_project_id"]),
        models.Index(fields=["status"]),
        models.Index(fields=["last_event_at"]),
    ]


class BridgeTaskSync(models.Model):
    odoo_task_id = models.BigIntegerField(unique=True)
    odoo_project_id = models.BigIntegerField()
    git_branch = models.CharField(max_length=255)
    git_base_branch = models.CharField(max_length=120)
    mr_id = models.CharField(max_length=120, blank=True, null=True)
    mr_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=_SyncStatus.choices,
        default=_SyncStatus.BRANCH_CREATED,
    )
    last_event_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"task={self.odoo_task_id} status={self.status}"
