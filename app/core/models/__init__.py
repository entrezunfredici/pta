from django.db import models


class _GitProvider(models.TextChoices):
    GITLAB = "gitlab", "GitLab"
    GITHUB = "github", "GitHub"


class _SyncStatus(models.TextChoices):
    BRANCH_CREATED = "branch_created", "Branch Created"
    MR_OPENED = "mr_opened", "MR Opened"
    CHANGES_REQUESTED = "changes_requested", "Changes Requested"
    APPROVED = "approved", "Approved"
    MERGED_DEV = "merged_dev", "Merged Dev"
    MERGED_MAIN = "merged_main", "Merged Main"
    CLOSED = "closed", "Closed"


class _WebhookProvider(models.TextChoices):
    GITLAB = "gitlab", "GitLab"
    GITHUB = "github", "GitHub"


class _GitProfileProvider(models.TextChoices):
    GITHUB = "github", "GitHub"
    GITLAB = "gitlab", "GitLab"
    OTHER = "other", "Other"


class _AutomationRunStatus(models.TextChoices):
    CREATED = "created", "Created"
    SKIPPED = "skipped", "Skipped"
    FAILED = "failed", "Failed"
    ALREADY_EXISTS = "already_exists", "Already Exists"


class BridgeLink(models.Model):
    odoo_project_id = models.BigIntegerField(unique=True)
    git_provider = models.CharField(max_length=20, choices=_GitProvider.choices)
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
    provider = models.CharField(max_length=20, choices=_WebhookProvider.choices)
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


class OdooProfile(models.Model):
    name = models.CharField(max_length=120, unique=True)
    base_url = models.URLField()
    database = models.CharField(max_length=120)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "odoo_profile"
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class GitProfile(models.Model):
    name = models.CharField(max_length=120, unique=True)
    provider = models.CharField(
        max_length=20,
        choices=_GitProfileProvider.choices,
        default=_GitProfileProvider.GITHUB,
    )
    repository_url = models.URLField()
    username = models.CharField(max_length=120, blank=True, null=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    default_source_branch = models.CharField(max_length=120, default="dev")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "git_profile"
        indexes = [
            models.Index(fields=["provider"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class AutomationRule(models.Model):
    name = models.CharField(max_length=140, unique=True)
    odoo_profile = models.ForeignKey(
        OdooProfile,
        on_delete=models.CASCADE,
        related_name="automation_rules",
    )
    git_profile = models.ForeignKey(
        GitProfile,
        on_delete=models.CASCADE,
        related_name="automation_rules",
    )
    odoo_project_id = models.BigIntegerField()
    odoo_project_name = models.CharField(max_length=255, blank=True, null=True)
    trigger_stage_id = models.BigIntegerField()
    trigger_stage_name = models.CharField(max_length=255, blank=True, null=True)
    source_branch_field = models.CharField(max_length=120, default="x_branch_source")
    work_branch_field = models.CharField(max_length=120, default="x_work_branch")
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "automation_rule"
        indexes = [
            models.Index(fields=["odoo_project_id", "trigger_stage_id"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class AutomationRunLog(models.Model):
    automation_rule = models.ForeignKey(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    odoo_task_id = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=_AutomationRunStatus.choices)
    message = models.TextField(blank=True, null=True)
    created_branch = models.CharField(max_length=255, blank=True, null=True)
    source_branch = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "automation_run_log"
        indexes = [
            models.Index(fields=["odoo_task_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.automation_rule_id}:{self.odoo_task_id}:{self.status}"
