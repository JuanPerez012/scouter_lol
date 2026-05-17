# ============================================================
# src/inference.py
# Predicción táctica desde posiciones espaciales
# Equivalente a las Fases 15-16 del notebook
# ============================================================

import sys as _sys
import os as _os
_CV_BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _CV_BASE not in _sys.path:
    _sys.path.insert(0, _CV_BASE)

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from src.spatial_analysis import extract_spatial_features

FEATURE_COLS = [
    "avg_distance", "dispersion", "min_distance", "max_distance",
    "isolated", "central_control", "side_pressure",
    "y_mean", "y_std", "x_std", "vertical_spread", "horizontal_spread",
    "top_zone", "bottom_zone",
]


def predict_from_positions(
    x_positions: list,
    y_positions: list,
    model,
    label_encoder,
    scaler,
    top_n: int = 3,
) -> list:
    """
    Predice las top-N estrategias tácticas a partir de posiciones
    espaciales sobre el minimapa.

    Retorna:
        lista de tuplas (strategy_name, confidence_float)
    """
    features = extract_spatial_features(x_positions, y_positions)
    df       = pd.DataFrame([features])[FEATURE_COLS]
    scaled   = scaler.transform(df)

    X = torch.tensor(scaled, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        logits    = model(X)
        probs     = F.softmax(logits, dim=1).squeeze(0).numpy()

    top_indices = np.argsort(probs)[::-1][:top_n]
    return [
        (label_encoder.inverse_transform([idx])[0], float(probs[idx]))
        for idx in top_indices
    ]


def build_tactical_report(
    x_positions: list,
    y_positions: list,
    top_predictions: list,
) -> str:
    """
    Genera el reporte de interpretación táctica automática.
    Equivalente a la celda 101 del notebook.
    """
    main_strategy = top_predictions[0][0]
    main_prob     = top_predictions[0][1]

    sep = "=" * 50
    report = f"\n{sep}\nINTERPRETACIÓN TÁCTICA\n{sep}\n\n"
    report += (
        f"La estructura espacial analizada presenta características "
        f"asociadas a la estrategia: {main_strategy}.\n\n"
        f"El modelo detectó una probabilidad aproximada de {main_prob:.2%}.\n\n"
    )

    features = extract_spatial_features(x_positions, y_positions)
    avg_dist  = features["avg_distance"]

    if avg_dist < 0.25:
        report += (
            "La distribución observada muestra agrupación espacial "
            "y control sobre zonas centrales del minimapa."
        )
    elif avg_dist < 0.40:
        report += (
            "La distribución muestra presión semi-agrupada con "
            "control moderado sobre zonas clave del mapa."
        )
    else:
        report += (
            "La distribución indica separación táctica, posible "
            "presión lateral o estructura de macro distribuido."
        )

    report += f"\n\nTop-{len(top_predictions)} estrategias detectadas:\n"
    for name, conf in top_predictions:
        report += f"  - {name}: {conf:.2%}\n"

    return report
