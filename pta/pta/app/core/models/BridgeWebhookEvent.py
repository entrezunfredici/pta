from django.db import models

class _Provider(models.TextChoices):
    GITLAB = "gitlab", "GitLab"
    GITHUB = "github", "GitHub"

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

class BridgeWebhookEvent(models.Model):
    provider = models.CharField(max_length=20, choices=_Provider.choices)
    event_type = models.CharField(max_length=80)
    event_id = models.CharField(max_length=255, blank=True, null=True)
    signature_ok = models.BooleanField(default=False)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        event = self.event_id or "no-id"
        return f"{self.provider}:{self.event_type}:{event}"
