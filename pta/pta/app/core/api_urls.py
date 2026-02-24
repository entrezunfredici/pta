from django.urls import path

from . import api_views


urlpatterns = [
    path("ping/", api_views.ping, name="ping"),
    path("odoo-profiles/", api_views.odoo_profiles, name="odoo_profiles"),
    path("odoo-profiles/<int:profile_id>/test/", api_views.odoo_profile_test, name="odoo_profile_test"),
    path("odoo-profiles/<int:profile_id>/projects/", api_views.odoo_profile_projects, name="odoo_profile_projects"),
    path(
        "odoo-profiles/<int:profile_id>/projects/<int:project_id>/stages/",
        api_views.odoo_profile_project_stages,
        name="odoo_profile_project_stages",
    ),
    path("git-profiles/", api_views.git_profiles, name="git_profiles"),
    path("git-profiles/<int:profile_id>/test/", api_views.git_profile_test, name="git_profile_test"),
    path("automations/", api_views.automations, name="automations"),
    path("automations/<int:automation_id>/run-task/", api_views.automation_run_task, name="automation_run_task"),
]
