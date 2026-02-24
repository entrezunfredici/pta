from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import (
    AutomationRule,
    AutomationRunLog,
    GitProfile,
    OdooProfile,
)
from .services.git import GitClient, GitClientError
from .services.odoo import OdooClient, OdooClientError


def _parse_json(request: HttpRequest) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload") from exc


def _odoo_client(profile: OdooProfile) -> OdooClient:
    return OdooClient(
        base_url=profile.base_url,
        database=profile.database,
        email=profile.email,
        password=profile.password,
    )


def _git_client(profile: GitProfile) -> GitClient:
    return GitClient(
        repository_url=profile.repository_url,
        username=profile.username,
        token=profile.token,
    )


@require_GET
def ping(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def odoo_profiles(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        data = [
            {
                "id": profile.id,
                "name": profile.name,
                "base_url": profile.base_url,
                "database": profile.database,
                "email": profile.email,
                "is_active": profile.is_active,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }
            for profile in OdooProfile.objects.all().order_by("name")
        ]
        return JsonResponse({"results": data})

    try:
        payload = _parse_json(request)
        profile = OdooProfile.objects.create(
            name=payload["name"],
            base_url=payload["base_url"],
            database=payload["database"],
            email=payload["email"],
            password=payload["password"],
            is_active=payload.get("is_active", True),
        )
    except (KeyError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "id": profile.id,
            "name": profile.name,
            "base_url": profile.base_url,
            "database": profile.database,
            "email": profile.email,
            "is_active": profile.is_active,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def odoo_profile_test(request: HttpRequest, profile_id: int) -> JsonResponse:
    try:
        profile = OdooProfile.objects.get(pk=profile_id)
    except OdooProfile.DoesNotExist:
        return JsonResponse({"error": "Odoo profile not found"}, status=404)

    try:
        uid = _odoo_client(profile).authenticate()
    except OdooClientError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "uid": uid})


@require_GET
def odoo_profile_projects(request: HttpRequest, profile_id: int) -> JsonResponse:
    try:
        profile = OdooProfile.objects.get(pk=profile_id)
    except OdooProfile.DoesNotExist:
        return JsonResponse({"error": "Odoo profile not found"}, status=404)

    try:
        projects = _odoo_client(profile).list_projects()
    except OdooClientError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"results": projects})


@require_GET
def odoo_profile_project_stages(
    request: HttpRequest,
    profile_id: int,
    project_id: int,
) -> JsonResponse:
    try:
        profile = OdooProfile.objects.get(pk=profile_id)
    except OdooProfile.DoesNotExist:
        return JsonResponse({"error": "Odoo profile not found"}, status=404)

    try:
        stages = _odoo_client(profile).list_task_stages(project_id)
    except OdooClientError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"results": stages})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def git_profiles(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        data = [
            {
                "id": profile.id,
                "name": profile.name,
                "provider": profile.provider,
                "repository_url": profile.repository_url,
                "username": profile.username,
                "default_source_branch": profile.default_source_branch,
                "is_active": profile.is_active,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }
            for profile in GitProfile.objects.all().order_by("name")
        ]
        return JsonResponse({"results": data})

    try:
        payload = _parse_json(request)
        profile = GitProfile.objects.create(
            name=payload["name"],
            provider=payload.get("provider", GitProfile._meta.get_field("provider").default),
            repository_url=payload["repository_url"],
            username=payload.get("username"),
            token=payload.get("token"),
            default_source_branch=payload.get("default_source_branch", "dev"),
            is_active=payload.get("is_active", True),
        )
    except (KeyError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse(
        {
            "id": profile.id,
            "name": profile.name,
            "provider": profile.provider,
            "repository_url": profile.repository_url,
            "username": profile.username,
            "default_source_branch": profile.default_source_branch,
            "is_active": profile.is_active,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def git_profile_test(request: HttpRequest, profile_id: int) -> JsonResponse:
    try:
        profile = GitProfile.objects.get(pk=profile_id)
    except GitProfile.DoesNotExist:
        return JsonResponse({"error": "Git profile not found"}, status=404)

    try:
        source_branch = profile.default_source_branch
        sha = _git_client(profile).get_branch_sha(source_branch)
    except GitClientError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "default_source_branch": source_branch, "sha": sha})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def automations(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        rows = []
        for rule in AutomationRule.objects.select_related("odoo_profile", "git_profile").order_by("name"):
            rows.append(
                {
                    "id": rule.id,
                    "name": rule.name,
                    "odoo_profile_id": rule.odoo_profile_id,
                    "git_profile_id": rule.git_profile_id,
                    "odoo_project_id": rule.odoo_project_id,
                    "odoo_project_name": rule.odoo_project_name,
                    "trigger_stage_id": rule.trigger_stage_id,
                    "trigger_stage_name": rule.trigger_stage_name,
                    "source_branch_field": rule.source_branch_field,
                    "work_branch_field": rule.work_branch_field,
                    "is_active": rule.is_active,
                    "last_run_at": rule.last_run_at,
                }
            )
        return JsonResponse({"results": rows})

    try:
        payload = _parse_json(request)
        rule = AutomationRule.objects.create(
            name=payload["name"],
            odoo_profile_id=payload["odoo_profile_id"],
            git_profile_id=payload["git_profile_id"],
            odoo_project_id=payload["odoo_project_id"],
            odoo_project_name=payload.get("odoo_project_name"),
            trigger_stage_id=payload["trigger_stage_id"],
            trigger_stage_name=payload.get("trigger_stage_name"),
            source_branch_field=payload.get("source_branch_field", "x_branch_source"),
            work_branch_field=payload.get("work_branch_field", "x_work_branch"),
            is_active=payload.get("is_active", True),
        )
    except (KeyError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"id": rule.id, "name": rule.name}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def automation_run_task(request: HttpRequest, automation_id: int) -> JsonResponse:
    try:
        payload = _parse_json(request)
        task_id = int(payload["task_id"])
    except (KeyError, TypeError, ValueError) as exc:
        return JsonResponse({"error": f"Invalid task_id: {exc}"}, status=400)

    try:
        rule = AutomationRule.objects.select_related("odoo_profile", "git_profile").get(
            pk=automation_id,
            is_active=True,
        )
    except AutomationRule.DoesNotExist:
        return JsonResponse({"error": "Automation not found or inactive"}, status=404)

    odoo_client = _odoo_client(rule.odoo_profile)
    fields = ["stage_id", rule.source_branch_field, rule.work_branch_field]
    try:
        task = odoo_client.read_task(task_id, fields=fields)
    except OdooClientError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    stage_value = task.get("stage_id") or []
    current_stage_id = stage_value[0] if stage_value else None
    if current_stage_id != rule.trigger_stage_id:
        AutomationRunLog.objects.create(
            automation_rule=rule,
            odoo_task_id=task_id,
            status="skipped",
            message=(
                f"Task stage {current_stage_id} does not match trigger stage "
                f"{rule.trigger_stage_id}"
            ),
        )
        return JsonResponse(
            {
                "status": "skipped",
                "reason": "stage_not_matching",
                "current_stage_id": current_stage_id,
                "trigger_stage_id": rule.trigger_stage_id,
            }
        )

    source_branch = task.get(rule.source_branch_field) or rule.git_profile.default_source_branch
    work_branch = task.get(rule.work_branch_field) or ""
    if not work_branch.strip():
        AutomationRunLog.objects.create(
            automation_rule=rule,
            odoo_task_id=task_id,
            status="skipped",
            message="No work branch on task; branch creation skipped",
            source_branch=source_branch,
        )
        return JsonResponse({"status": "skipped", "reason": "empty_work_branch"})

    git_client = _git_client(rule.git_profile)
    try:
        result = git_client.create_branch(source_branch=source_branch, work_branch=work_branch.strip())
    except GitClientError as exc:
        AutomationRunLog.objects.create(
            automation_rule=rule,
            odoo_task_id=task_id,
            status="failed",
            message=str(exc),
            created_branch=work_branch.strip(),
            source_branch=source_branch,
        )
        return JsonResponse({"status": "failed", "error": str(exc)}, status=400)

    rule.last_run_at = timezone.now()
    rule.save(update_fields=["last_run_at", "updated_at"])

    AutomationRunLog.objects.create(
        automation_rule=rule,
        odoo_task_id=task_id,
        status=result,
        message=f"Branch automation result: {result}",
        created_branch=work_branch.strip(),
        source_branch=source_branch,
    )
    return JsonResponse(
        {
            "status": result,
            "source_branch": source_branch,
            "work_branch": work_branch.strip(),
        }
    )
