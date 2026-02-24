from django import forms
from django.contrib import admin

from .models import (
    AutomationRule,
    AutomationRunLog,
    BridgeLink,
    BridgeTaskSync,
    BridgeWebhookEvent,
    GitProfile,
    OdooProfile,
)


class OdooProfileAdminForm(forms.ModelForm):
    class Meta:
        model = OdooProfile
        fields = "__all__"
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }


@admin.register(OdooProfile)
class OdooProfileAdmin(admin.ModelAdmin):
    form = OdooProfileAdminForm
    list_display = ("name", "base_url", "database", "email", "is_active", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "base_url", "database", "email")
    ordering = ("name",)


@admin.register(GitProfile)
class GitProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "provider",
        "repository_url",
        "username",
        "default_source_branch",
        "is_active",
        "updated_at",
    )
    list_filter = ("provider", "is_active", "created_at", "updated_at")
    search_fields = ("name", "repository_url", "username")
    ordering = ("name",)


@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "odoo_profile",
        "git_profile",
        "odoo_project_id",
        "trigger_stage_id",
        "source_branch_field",
        "work_branch_field",
        "is_active",
        "last_run_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "odoo_project_name", "trigger_stage_name")
    autocomplete_fields = ("odoo_profile", "git_profile")
    ordering = ("name",)


@admin.register(AutomationRunLog)
class AutomationRunLogAdmin(admin.ModelAdmin):
    list_display = (
        "automation_rule",
        "odoo_task_id",
        "status",
        "source_branch",
        "created_branch",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("odoo_task_id", "source_branch", "created_branch", "message")
    autocomplete_fields = ("automation_rule",)
    ordering = ("-created_at",)
    readonly_fields = (
        "automation_rule",
        "odoo_task_id",
        "status",
        "message",
        "created_branch",
        "source_branch",
        "created_at",
    )


@admin.register(BridgeLink)
class BridgeLinkAdmin(admin.ModelAdmin):
    list_display = (
        "odoo_project_id",
        "git_provider",
        "git_repo",
        "default_base_branch",
        "main_branch",
        "is_active",
    )
    list_filter = ("git_provider", "is_active")
    search_fields = ("odoo_project_id", "git_repo")


@admin.register(BridgeTaskSync)
class BridgeTaskSyncAdmin(admin.ModelAdmin):
    list_display = (
        "odoo_task_id",
        "odoo_project_id",
        "git_branch",
        "git_base_branch",
        "status",
        "last_event_at",
    )
    list_filter = ("status",)
    search_fields = ("odoo_task_id", "odoo_project_id", "git_branch")


@admin.register(BridgeWebhookEvent)
class BridgeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_type", "event_id", "signature_ok", "received_at")
    list_filter = ("provider", "event_type", "signature_ok")
    search_fields = ("event_id", "event_type")
    readonly_fields = (
        "provider",
        "event_type",
        "event_id",
        "signature_ok",
        "payload",
        "received_at",
    )
