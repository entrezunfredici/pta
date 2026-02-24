from django.db import models


class _GitProvider(models.TextChoices):
    GITLAB = "gitlab", "GitLab"
    GITHUB = "github", "GitHub"


class Meta:
    db_table = "bridge_link"
    indexes = [
        models.Index(fields=["git_provider", "git_repo"]),
        models.Index(fields=["is_active"]),
    ]


class BridgeLink(models.Model):
    odoo_project_id = models.BigIntegerField(unique=True)
    git_provider = models.CharField(max_length=20, choices=_GitProvider.choices)
    git_repo = models.CharField(max_length=255)
    default_base_branch = models.CharField(max_length=120, default="dev")
    main_branch = models.CharField(max_length=120, default="main")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.odoo_project_id} -> {self.git_provider}:{self.git_repo}"
