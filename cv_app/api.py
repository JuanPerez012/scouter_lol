# ============================================================
# cv_app/api.py
# Endpoints REST para integración con el frontend React
# ============================================================

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .services import analyze_positions, get_strategy_visualization, STRATEGY_PATTERNS


@csrf_exempt
@require_http_methods(["POST"])
def api_strategy_positions(request):
    """
    POST /api/cv/strategy-positions/
    Body JSON:
        { "strategy": "wombo combo" }

    Retorna las posiciones normalizadas [0,1] del patrón táctico
    para blue team, listas para mover los íconos en el minimapa.
    Las coordenadas se convierten al espacio SVG [0, 600].
    """
    try:
        data     = json.loads(request.body)
        strategy = data.get("strategy", "")

        if strategy not in STRATEGY_PATTERNS:
            return JsonResponse(
                {"error": f"Estrategia no encontrada: {strategy}"},
                status=404,
            )

        pattern = STRATEGY_PATTERNS[strategy]
        VB = 600  # viewBox del minimapa SVG

        # Convertir coordenadas normalizadas [0,1] → SVG [0, VB]
        blue_positions = [
            {"x": round(x * VB), "y": round(y * VB)}
            for x, y in zip(pattern["x"], pattern["y"])
        ]

        # Posiciones enemigas (espejo horizontal)
        red_positions = [
            {"x": round((1.0 - x) * VB), "y": round((1.0 - y) * VB)}
            for x, y in zip(pattern["x"], pattern["y"])
        ]

        return JsonResponse({
            "strategy":        strategy,
            "blue_positions":  blue_positions,
            "red_positions":   red_positions,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_identify_strategy(request):
    """
    POST /api/cv/identify/
    Body JSON:
        {
          "x_positions": [0.45, 0.50, 0.48, 0.52, 0.55],
          "y_positions": [0.45, 0.50, 0.48, 0.52, 0.50]
        }

    Identifica la estrategia a partir de las posiciones actuales
    de los íconos en el minimapa (coordenadas normalizadas).
    """
    try:
        data = json.loads(request.body)
        x_positions = [float(v) for v in data.get("x_positions", [])]
        y_positions = [float(v) for v in data.get("y_positions", [])]

        if len(x_positions) < 2 or len(x_positions) != len(y_positions):
            return JsonResponse(
                {"error": "Se necesitan al menos 2 posiciones X e Y válidas."},
                status=400,
            )

        result = analyze_positions(x_positions, y_positions)

        if result.get("error"):
            return JsonResponse({"error": result["error"]}, status=500)

        return JsonResponse({
            "top_predictions": result["top_predictions"],
            "main_strategy":   result["top_predictions"][0][0],
            "confidence":      result["top_predictions"][0][1],
            "report":          result["report"],
            "inference":       result["inference"],
            "minimap_b64":     result["minimap_b64"],
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
