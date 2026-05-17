# ============================================================
# src/spatial_analysis.py — versión mejorada
# Features adicionales para mejor discriminación entre estrategias
# ============================================================

import sys as _sys
import os as _os
_CV_BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _CV_BASE not in _sys.path:
    _sys.path.insert(0, _CV_BASE)

import os
import numpy as np
from math import sqrt
from typing import List, Dict


def extract_positions(label_path: str) -> List[Dict]:
    positions = []
    if not os.path.exists(label_path):
        return positions
    with open(label_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        data = line.strip().split()
        if len(data) < 3:
            continue
        positions.append({
            "champion_id": int(data[0]),
            "x":           float(data[1]),
            "y":           float(data[2]),
        })
    return positions


def get_image_paths(base_path: str, splits: List[str]) -> List[str]:
    imagenes = []
    for split in splits:
        image_folder = os.path.join(base_path, split, "images")
        if not os.path.exists(image_folder):
            continue
        for file in os.listdir(image_folder):
            if file.endswith((".jpg", ".png", ".jpeg")) and "preview" not in file:
                imagenes.append(os.path.join(image_folder, file))
    return imagenes


def label_path_from_image(image_path: str) -> str:
    return image_path.replace("images", "labels") \
                     .replace(".jpg", ".txt") \
                     .replace(".png", ".txt") \
                     .replace(".jpeg", ".txt")


def euclidean_distance(x1, y1, x2, y2) -> float:
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def extract_spatial_features(
    x_positions: List[float],
    y_positions: List[float],
    isolated_threshold: float = 0.40,
) -> Dict:
    """
    Features espaciales extendidas para mejor discriminación.

    Originales (notebook):
        avg_distance, dispersion, isolated, central_control, side_pressure

    Nuevas (mejoran precisión):
        min_distance    — distancia mínima entre cualquier par (agrupación extrema)
        max_distance    — distancia máxima (dispersión máxima)
        y_mean          — posición vertical promedio (zona alta/baja del mapa)
        y_std           — variación vertical
        x_std           — variación horizontal
        vertical_spread — diferencia entre y_max e y_min
        horizontal_spread — diferencia entre x_max e x_min
        top_zone        — campeones en zona alta del mapa (y < 0.40)
        bottom_zone     — campeones en zona baja (y > 0.60)
    """
    distances = []
    for i in range(len(x_positions)):
        for j in range(i + 1, len(x_positions)):
            d = euclidean_distance(
                x_positions[i], y_positions[i],
                x_positions[j], y_positions[j],
            )
            distances.append(d)

    avg_distance     = float(np.mean(distances))  if distances else 0.0
    dispersion       = float(np.std(distances))   if distances else 0.0
    min_distance     = float(np.min(distances))   if distances else 0.0
    max_distance     = float(np.max(distances))   if distances else 0.0
    isolated         = sum(d > isolated_threshold for d in distances)
    central_control  = sum(
        0.35 <= x <= 0.65 and 0.35 <= y <= 0.65
        for x, y in zip(x_positions, y_positions)
    )
    side_pressure    = sum(x < 0.25 or x > 0.75 for x in x_positions)
    y_mean           = float(np.mean(y_positions))
    y_std            = float(np.std(y_positions))
    x_std            = float(np.std(x_positions))
    vertical_spread  = float(max(y_positions) - min(y_positions))
    horizontal_spread= float(max(x_positions) - min(x_positions))
    top_zone         = sum(y < 0.40 for y in y_positions)
    bottom_zone      = sum(y > 0.60 for y in y_positions)

    return {
        "avg_distance":      avg_distance,
        "dispersion":        dispersion,
        "min_distance":      min_distance,
        "max_distance":      max_distance,
        "isolated":          isolated,
        "central_control":   central_control,
        "side_pressure":     side_pressure,
        "y_mean":            y_mean,
        "y_std":             y_std,
        "x_std":             x_std,
        "vertical_spread":   vertical_spread,
        "horizontal_spread": horizontal_spread,
        "top_zone":          top_zone,
        "bottom_zone":       bottom_zone,
    }


def tactical_inference(
    positions: List[Dict],
    grouped_threshold:  float = 0.15,
    semi_threshold:     float = 0.30,
    isolated_threshold: float = 0.25,
) -> str:
    if not positions:
        return "No se detectaron posiciones en el minimapa."

    x_coords = [p["x"] for p in positions]
    y_coords  = [p["y"] for p in positions]
    features  = extract_spatial_features(x_coords, y_coords)
    avg_dist  = features["avg_distance"]
    aislados  = sum(
        1 for i, p in enumerate(positions)
        if all(
            euclidean_distance(p["x"], p["y"], q["x"], q["y"]) >= isolated_threshold
            for j, q in enumerate(positions) if i != j
        )
    )

    lines = ["\n" + "=" * 50, "ANÁLISIS TÁCTICO DEL MINIMAPA", "=" * 50 + "\n"]

    if avg_dist < grouped_threshold:
        lines.append(
            "La distribución espacial muestra agrupación fuerte — "
            "posible preparación de teamfight u objetivo neutral."
        )
    elif avg_dist < semi_threshold:
        lines.append(
            "Estructura semi-agrupada con presión coordinada "
            "sobre zonas importantes del mapa."
        )
    else:
        lines.append(
            "Campeones relativamente separados — posible presión "
            "lateral o macro distribuido."
        )

    if aislados >= 2:
        lines.append(
            "\nCampeones aislados detectados — posible splitpush, "
            "presión lateral o control periférico."
        )
    else:
        lines.append("\nNo se observan estructuras fuertes de aislamiento táctico.")

    return "\n".join(lines)
