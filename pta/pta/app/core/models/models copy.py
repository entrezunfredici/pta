from django.db import models


class BridgeLink(models.Model):
    class GitProvider(models.TextChoices):
        GITLAB = "gitlab", "GitLab"
        GITHUB = "github", "GitHub"

    odoo_project_id = models.BigIntegerField(unique=True)
    git_provider = models.CharField(max_length=20, choices=GitProvider.choices)
    git_repo = models.CharField(max_length=255)
    default_base_branch = models.CharField(max_length=120, default="dev")
    main_branch = models.CharField(max_length=120, default="main")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bridge_link"
        indexes = [
            models.Index(fields=["git_provider", "git_repo"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.odoo_project_id} -> {self.git_provider}:{self.git_repo}"


class BridgeTaskSync(models.Model):
    class SyncStatus(models.TextChoices):
        BRANCH_CREATED = "branch_created", "Branch Created"
        MR_OPENED = "mr_opened", "MR Opened"
        CHANGES_REQUESTED = "changes_requested", "Changes Requested"
        APPROVED = "approved", "Approved"
        MERGED_DEV = "merged_dev", "Merged Dev"
        MERGED_MAIN = "merged_main", "Merged Main"
        CLOSED = "closed", "Closed"

    odoo_task_id = models.BigIntegerField(unique=True)
    odoo_project_id = models.BigIntegerField()
    git_branch = models.CharField(max_length=255)
    git_base_branch = models.CharField(max_length=120)
    mr_id = models.CharField(max_length=120, blank=True, null=True)
    mr_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=SyncStatus.choices, default=SyncStatus.BRANCH_CREATED)
    last_event_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bridge_tasksync"
        indexes = [
            models.Index(fields=["odoo_project_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["last_event_at"]),
        ]

    def __str__(self) -> str:
        return f"task={self.odoo_task_id} status={self.status}"


class BridgeWebhookEvent(models.Model):
    class Provider(models.TextChoices):
        GITLAB = "gitlab", "GitLab"
        GITHUB = "github", "GitHub"

    provider = models.CharField(max_length=20, choices=Provider.choices)
    event_type = models.CharField(max_length=80)
    event_id = models.CharField(max_length=255, blank=True, null=True)
    signature_ok = models.BooleanField(default=False)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bridge_webhookevent"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "event_id"],
                name="uq_bridge_webhookevent_provider_event_id",
                condition=models.Q(event_id__isnull=False),
            )
        ]
        indexes = [
            models.Index(fields=["provider", "event_type"]),
            models.Index(fields=["received_at"]),
        ]

    def __str__(self) -> str:
        event = self.event_id or "no-id"
        return f"{self.provider}:{self.event_type}:{event}"
