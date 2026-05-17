# ============================================================
# cv_app/services.py
# Capa de servicio Django para el módulo CV Scouter
# ============================================================

import sys
import os
from django.conf import settings

CV_PATH = str(settings.CV_SCOUTER_BASE_DIR)
if CV_PATH not in sys.path:
    sys.path.insert(0, CV_PATH)

from src.model_training import load_model
from src.spatial_analysis import extract_positions, label_path_from_image, tactical_inference
from src.inference import predict_from_positions, build_tactical_report
from src.visualization import (
    plot_positions,
    plot_tactical_pattern,
    plot_multi_strategies,
    COUNTER_STRATEGY,
)
from config.settings import STRATEGY_PATTERNS

# ─── SINGLETON ────────────────────────────────────────────────
_model         = None
_label_encoder = None
_scaler        = None


def _load_resources():
    global _model, _label_encoder, _scaler
    if _model is not None:
        return
    _model, _label_encoder, _scaler = load_model()
    print("✓ Modelo CV cargado correctamente.")


# ─── API PÚBLICA ──────────────────────────────────────────────

def analyze_label_file(label_path: str) -> dict:
    """
    Analiza un archivo de anotaciones YOLO y retorna posiciones,
    métricas, inferencia táctica y visualización.
    """
    _load_resources()

    positions = extract_positions(label_path)
    if not positions:
        return {"error": f"No se encontraron anotaciones en: {label_path}"}

    x_pos = [p["x"] for p in positions]
    y_pos = [p["y"] for p in positions]

    top_predictions = predict_from_positions(
        x_pos, y_pos, _model, _label_encoder, _scaler
    )
    tactical_report = build_tactical_report(x_pos, y_pos, top_predictions)
    inference_text  = tactical_inference(positions)
    scatter_b64     = plot_positions(positions)
    main_strategy   = top_predictions[0][0]
    enemy_strategy  = COUNTER_STRATEGY.get(main_strategy)
    minimap_b64     = plot_tactical_pattern(main_strategy, enemy_strategy=enemy_strategy)

    return {
        "positions":       positions,
        "top_predictions": top_predictions,
        "report":          tactical_report,
        "inference":       inference_text,
        "scatter_b64":     scatter_b64,
        "minimap_b64":     minimap_b64,
        "error":           None,
    }


def analyze_positions(x_positions: list, y_positions: list) -> dict:
    """
    Analiza posiciones ingresadas manualmente (sin archivo YOLO).
    Útil para la interfaz web donde el usuario ingresa coordenadas.
    """
    _load_resources()

    if len(x_positions) < 2:
        return {"error": "Se necesitan al menos 2 posiciones."}

    top_predictions = predict_from_positions(
        x_positions, y_positions, _model, _label_encoder, _scaler
    )
    positions = [{"champion_id": i, "x": x, "y": y}
                 for i, (x, y) in enumerate(zip(x_positions, y_positions))]

    tactical_report = build_tactical_report(x_positions, y_positions, top_predictions)
    inference_text  = tactical_inference(positions)
    scatter_b64     = plot_positions(positions)
    main_strategy   = top_predictions[0][0]
    enemy_strategy  = COUNTER_STRATEGY.get(main_strategy)
    minimap_b64     = plot_tactical_pattern(main_strategy, enemy_strategy=enemy_strategy)

    return {
        "positions":       positions,
        "top_predictions": top_predictions,
        "report":          tactical_report,
        "inference":       inference_text,
        "scatter_b64":     scatter_b64,
        "minimap_b64":     minimap_b64,
        "error":           None,
    }


def get_strategy_visualization(strategy: str) -> dict:
    """Genera visualización para una estrategia específica."""
    if strategy not in STRATEGY_PATTERNS:
        return {"error": f"Estrategia no encontrada: {strategy}"}

    enemy_strategy = COUNTER_STRATEGY.get(strategy)
    minimap_b64    = plot_tactical_pattern(strategy, enemy_strategy=enemy_strategy)

    return {
        "strategy":        strategy,
        "enemy_strategy":  enemy_strategy,
        "minimap_b64":     minimap_b64,
        "error":           None,
    }


def get_available_strategies() -> list:
    return sorted(STRATEGY_PATTERNS.keys())
