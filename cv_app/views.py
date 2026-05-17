# ============================================================
# cv_app/views.py
# ============================================================

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .services import (
    analyze_positions,
    get_strategy_visualization,
    get_available_strategies,
)


def index(request):
    """Vista principal del módulo CV."""
    strategies = get_available_strategies()
    return render(request, "cv_app/index.html", {"strategies": strategies})


@require_http_methods(["POST"])
def analyze(request):
    """
    Recibe posiciones X/Y y retorna análisis táctico completo.
    Acepta JSON o form-data.
    """
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST

        raw_x = data.get("x_positions", "")
        raw_y = data.get("y_positions", "")

        if isinstance(raw_x, str):
            x_positions = [float(v.strip()) for v in raw_x.split(",") if v.strip()]
            y_positions = [float(v.strip()) for v in raw_y.split(",") if v.strip()]
        else:
            x_positions = [float(v) for v in raw_x]
            y_positions = [float(v) for v in raw_y]

        if len(x_positions) != len(y_positions) or len(x_positions) < 2:
            return JsonResponse(
                {"error": "Se necesitan al menos 2 posiciones X e Y válidas."},
                status=400,
            )

        result = analyze_positions(x_positions, y_positions)

        if result.get("error"):
            return JsonResponse({"error": result["error"]}, status=500)

        return JsonResponse({
            "top_predictions": result["top_predictions"],
            "report":          result["report"],
            "inference":       result["inference"],
            "scatter_b64":     result["scatter_b64"],
            "minimap_b64":     result["minimap_b64"],
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def strategy_viz(request, strategy_name: str):
    """Retorna la visualización de una estrategia específica."""
    result = get_strategy_visualization(strategy_name)
    if result.get("error"):
        return JsonResponse({"error": result["error"]}, status=404)
    return JsonResponse(result)
