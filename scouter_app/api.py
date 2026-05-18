# ============================================================
# scouter_app/api.py
# Endpoints REST para integración con el frontend React
# ============================================================

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .services import run_scouting, get_champion_list

LANES = ["Top", "Jungle", "Mid", "ADC", "Support"]


@csrf_exempt
@require_http_methods(["POST"])
def api_full_scouting(request):
    """
    POST /api/nlp/scouting/
    Body JSON:
        {
          "ally_team":  ["Gnar", "Sejuani", "Orianna", "Jinx", "Thresh"],
          "enemy_team": ["Camille", "LeeSin", "Zed", "KaiSa", "Nautilus"]
        }
    Retorna reporte NLP + estrategia principal detectada.
    """
    try:
        data       = json.loads(request.body)
        ally_team  = data.get("ally_team",  [])
        enemy_team = data.get("enemy_team", [])

        if len(ally_team) != 5 or len(enemy_team) != 5:
            return JsonResponse(
                {"error": "Se necesitan exactamente 5 campeones por equipo."},
                status=400,
            )

        result = run_scouting(ally_team, enemy_team)

        if result["error"]:
            return JsonResponse({"error": result["error"]}, status=500)

        return JsonResponse({
            "report":          result["report"],
            "top_strategies":  result["top_strategies"],
            "main_strategy":   result["top_strategies"][0][0] if result["top_strategies"] else "",
            "confidence":      result["top_strategies"][0][1] if result["top_strategies"] else 0.0,
            "ally_team":       dict(zip(LANES, ally_team)),
            "enemy_team":      dict(zip(LANES, enemy_team)),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_champions(request):
    """GET /api/champions/ — lista de campeones disponibles."""
    try:
        return JsonResponse({"champions": get_champion_list()})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
