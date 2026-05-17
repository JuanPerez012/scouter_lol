# ============================================================
# cv_app/services.py
# ============================================================

import sys
import os
import importlib.util
from django.conf import settings

CV_BASE = str(settings.CV_SCOUTER_BASE_DIR)


def _load_absolute(sys_module_name: str, rel_path: str):
    """
    Carga un archivo Python por ruta absoluta y lo registra
    en sys.modules con el nombre dado.
    Si ya está registrado, lo devuelve directamente.
    """
    if sys_module_name in sys.modules:
        return sys.modules[sys_module_name]
    abs_path = os.path.join(CV_BASE, rel_path)
    spec     = importlib.util.spec_from_file_location(sys_module_name, abs_path)
    mod      = importlib.util.module_from_spec(spec)
    sys.modules[sys_module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_all():
    """
    Carga todos los módulos de cv_scouter registrándolos con
    nombres únicos Y también bajo sus nombres canónicos
    (config.settings, src.spatial_analysis, etc.) para que
    las importaciones internas entre módulos funcionen.
    """
    # ── 1. config.settings ───────────────────────────────────
    # Guardar el config.settings de lol_scouter si existe
    _saved_config = sys.modules.pop("config", None)
    _saved_config_settings = sys.modules.pop("config.settings", None)

    try:
        # Registrar config de cv_scouter
        cfg = _load_absolute("config.settings", "config/settings.py")
        # También registrar el paquete config
        import types
        config_pkg = types.ModuleType("config")
        config_pkg.settings = cfg
        sys.modules["config"] = config_pkg

        # ── 2. src.spatial_analysis ──────────────────────────
        _saved_src = sys.modules.pop("src", None)
        _saved_spatial = sys.modules.pop("src.spatial_analysis", None)

        spatial = _load_absolute("src.spatial_analysis",
                                 "src/spatial_analysis.py")
        src_pkg = types.ModuleType("src")
        src_pkg.spatial_analysis = spatial
        sys.modules["src"] = src_pkg

        # ── 3. src.model_training ────────────────────────────
        _saved_mt = sys.modules.pop("src.model_training", None)
        training = _load_absolute("src.model_training",
                                  "src/model_training.py")
        sys.modules["src"].model_training = training

        # ── 4. src.visualization ─────────────────────────────
        _saved_viz = sys.modules.pop("src.visualization", None)
        viz = _load_absolute("src.visualization",
                             "src/visualization.py")
        sys.modules["src"].visualization = viz

        # ── 5. src.inference ─────────────────────────────────
        _saved_inf = sys.modules.pop("src.inference", None)
        infer = _load_absolute("src.inference",
                               "src/inference.py")
        sys.modules["src"].inference = infer

    finally:
        # Restaurar config de lol_scouter para no romper el módulo NLP
        if _saved_config is not None:
            sys.modules["config"] = _saved_config
        if _saved_config_settings is not None:
            sys.modules["config.settings"] = _saved_config_settings

    return cfg, spatial, training, viz, infer


# ── Ejecutar carga al importar el servicio ────────────────────
(
    _cv_config,
    _cv_spatial,
    _cv_training,
    _cv_viz,
    _cv_infer,
) = _load_all()

STRATEGY_PATTERNS = _cv_config.STRATEGY_PATTERNS
COUNTER_STRATEGY  = _cv_viz.COUNTER_STRATEGY

# ─── SINGLETON ────────────────────────────────────────────────
_model         = None
_label_encoder = None
_scaler        = None


def _load_resources():
    global _model, _label_encoder, _scaler
    if _model is not None:
        return
    _model, _label_encoder, _scaler = _cv_training.load_model()
    print("✓ Modelo CV cargado correctamente.")


# ─── API PÚBLICA ──────────────────────────────────────────────

def analyze_positions(x_positions: list, y_positions: list) -> dict:
    _load_resources()
    if len(x_positions) < 2:
        return {"error": "Se necesitan al menos 2 posiciones."}
    try:
        top_predictions = _cv_infer.predict_from_positions(
            x_positions, y_positions,
            _model, _label_encoder, _scaler,
        )
        positions = [
            {"champion_id": i, "x": x, "y": y}
            for i, (x, y) in enumerate(zip(x_positions, y_positions))
        ]
        return {
            "positions":       positions,
            "top_predictions": top_predictions,
            "report":          _cv_infer.build_tactical_report(
                                   x_positions, y_positions, top_predictions),
            "inference":       _cv_spatial.tactical_inference(positions),
            "scatter_b64":     _cv_viz.plot_positions(positions),
            "minimap_b64":     _cv_viz.plot_tactical_pattern(
                                   top_predictions[0][0],
                                   enemy_strategy=COUNTER_STRATEGY.get(
                                       top_predictions[0][0])),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


def get_strategy_visualization(strategy: str) -> dict:
    if strategy not in STRATEGY_PATTERNS:
        return {"error": f"Estrategia no encontrada: {strategy}"}
    enemy = COUNTER_STRATEGY.get(strategy)
    return {
        "strategy":       strategy,
        "enemy_strategy": enemy,
        "minimap_b64":    _cv_viz.plot_tactical_pattern(
                              strategy, enemy_strategy=enemy),
        "error": None,
    }


def get_available_strategies() -> list:
    return sorted(STRATEGY_PATTERNS.keys())
