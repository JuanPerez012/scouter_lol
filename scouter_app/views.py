# ============================================================
# scouter_app/views.py
# Vistas Django del Scouter LoL
# ============================================================

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .services import get_champion_list, run_scouting

LANES = ["Top", "Jungle", "Mid", "ADC", "Support"]


def index(request):
    """Vista principal: formulario de selección de equipos."""
    champions = get_champion_list()
    context = {
        "champions": champions,
        "lanes":     LANES,
    }
    return render(request, "scouter_app/index.html", context)


@require_http_methods(["POST"])
def scouting_report(request):
    """
    Recibe los dos equipos vía POST y retorna el reporte.
    Acepta tanto form-data como JSON.
    """
    try:
        # Soporte para JSON (fetch API) y form clásico
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST

        ally_team  = [data.get(f"ally_{lane.lower()}", "")  for lane in LANES]
        enemy_team = [data.get(f"enemy_{lane.lower()}", "") for lane in LANES]

        # Validar que todos los campos estén llenos
        if any(c == "" for c in ally_team + enemy_team):
            return JsonResponse(
                {"error": "Debes seleccionar los 10 campeones."},
                status=400,
            )

        result = run_scouting(ally_team, enemy_team)

        if result["error"]:
            return JsonResponse({"error": result["error"]}, status=500)

        return JsonResponse({
            "report":         result["report"],
            "top_strategies": result["top_strategies"],
            "ally_team":      dict(zip(LANES, ally_team)),
            "enemy_team":     dict(zip(LANES, enemy_team)),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def report_view(request):
    """Vista para mostrar el reporte tras envío de formulario HTML clásico."""
    if request.method != "POST":
        return index(request)

    ally_team  = [request.POST.get(f"ally_{lane.lower()}", "")  for lane in LANES]
    enemy_team = [request.POST.get(f"enemy_{lane.lower()}", "") for lane in LANES]

    result = run_scouting(ally_team, enemy_team)
    champions = get_champion_list()

    context = {
        "champions":      champions,
        "lanes":          LANES,
        "result":         result,
        "ally_labeled":   dict(zip(LANES, ally_team)),
        "enemy_labeled":  dict(zip(LANES, enemy_team)),
    }
    return render(request, "scouter_app/report.html", context)
