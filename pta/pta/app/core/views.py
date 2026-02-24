from django.shortcuts import render

from .models import AutomationRule, GitProfile, OdooProfile


def home(request):
    return render(request, "home.html")


def config_dashboard(request):
    context = {
        "odoo_profiles_count": OdooProfile.objects.count(),
        "git_profiles_count": GitProfile.objects.count(),
        "automation_rules_count": AutomationRule.objects.count(),
    }
    return render(request, "config_dashboard.html", context)
