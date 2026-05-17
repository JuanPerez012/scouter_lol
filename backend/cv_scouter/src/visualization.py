# ============================================================
# src/visualization.py
# Visualización táctica sobre el minimapa competitivo
# Equivalente a las Fases 9 y 16 del notebook
# ============================================================

import sys as _sys
import os as _os
_CV_BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _CV_BASE not in _sys.path:
    _sys.path.insert(0, _CV_BASE)

import os
import io
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import STRATEGY_PATTERNS, THRESHOLDS, DATASET


# ─── RUIDO ESPACIAL ───────────────────────────────────────────

def add_noise(values: list, noise_level: float = None) -> list:
    if noise_level is None:
        noise_level = THRESHOLDS["noise"]
    return [v + np.random.uniform(-noise_level, noise_level) for v in values]


# ─── CARGA DEL MINIMAPA ───────────────────────────────────────

def load_minimap():
    """Carga el minimapa base como array RGB."""
    import cv2
    path = DATASET["minimap_img"]
    if not os.path.exists(path):
        return None
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# ─── FIGURA A BASE64 ──────────────────────────────────────────

def fig_to_base64(fig) -> str:
    """Convierte una figura matplotlib a string base64 para HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


# ─── SCATTER ESPACIAL SIN MAPA ────────────────────────────────

def plot_positions(positions: list) -> str:
    """
    Visualiza posiciones detectadas desde labels YOLO.
    Equivalente a la Fase 6 del notebook.
    Retorna imagen base64.
    """
    x_coords = [p["x"] for p in positions]
    y_coords  = [p["y"] for p in positions]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x_coords, y_coords, s=150, c="#3b82f6", edgecolors="black", linewidths=1.5)
    ax.invert_yaxis()
    ax.set_title("Distribución espacial de campeones")
    ax.set_xlabel("Posición X")
    ax.set_ylabel("Posición Y")
    ax.grid(True)
    fig.tight_layout()
    return fig_to_base64(fig)


# ─── PATRÓN TÁCTICO SOBRE MINIMAPA ───────────────────────────

def plot_tactical_pattern(
    strategy: str,
    ally_team_x: list = None,
    ally_team_y: list = None,
    enemy_strategy: str = None,
    save_path: str = None,
) -> str:
    """
    Visualiza el patrón táctico de una estrategia sobre el minimapa.
    Aliados en azul, enemigos en rojo.
    Equivalente a las Fases 9 y 16 del notebook.
    Retorna imagen base64.
    """
    map_image = load_minimap()

    pattern = STRATEGY_PATTERNS.get(strategy)
    if pattern is None:
        return ""

    blue_x = add_noise(pattern["x"])
    blue_y = add_noise(pattern["y"])

    # Si se provee enemy_strategy, usar su patrón; si no, usar posiciones simétricas
    if enemy_strategy and enemy_strategy in STRATEGY_PATTERNS:
        ep = STRATEGY_PATTERNS[enemy_strategy]
        red_x = add_noise(ep["x"])
        red_y = add_noise(ep["y"])
    else:
        red_x = [1.0 - x for x in blue_x]
        red_y = [1.0 - y for y in blue_y]

    fig, ax = plt.subplots(figsize=(7, 7))

    if map_image is not None:
        ax.imshow(map_image)
        h, w, _ = map_image.shape
        bx = [x * w for x in blue_x]
        by = [y * h for y in blue_y]
        rx = [x * w for x in red_x]
        ry = [y * h for y in red_y]
    else:
        # Sin minimapa: scatter normalizado
        bx, by = blue_x, blue_y
        rx, ry = red_x, red_y
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.invert_yaxis()
        ax.grid(True)

    ax.scatter(bx, by, s=450, c="dodgerblue", edgecolors="black",
               linewidths=2, alpha=0.90, label="Aliados", zorder=5)
    ax.scatter(rx, ry, s=450, c="red",        edgecolors="black",
               linewidths=2, alpha=0.90, label="Enemigos", zorder=5)

    ax.set_title(f"Estructura táctica: {strategy}", fontsize=14)
    ax.legend()
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=120, bbox_inches="tight")

    return fig_to_base64(fig)


# ─── VISUALIZACIÓN DE MÚLTIPLES ESTRATEGIAS ──────────────────

COUNTER_STRATEGY = {
    "wombo combo":       "poke composition",
    "splitpush táctico": "front-to-back",
    "front-to-back":     "dive composition",
    "macro composition": "pick composition",
    "agresivo early":    "escalar late",
    "jugar a objetivos": "wombo combo",
    "escalar late":      "agresivo early",
    "poke composition":  "wombo combo",
    "protect hypercarry":"dive composition",
    "tempo composition": "pick composition",
    "pick composition":  "front-to-back",
    "dive composition":  "protect hypercarry",
}


def plot_multi_strategies(strategies: list, save_path: str = None) -> str:
    """
    Muestra varias estrategias en grid (hasta 4).
    Equivalente a la celda 59 del notebook.
    Retorna imagen base64.
    """
    map_image = load_minimap()
    n = min(len(strategies), 4)
    cols = 2
    rows = (n + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 7 * rows))
    axes = axes.flatten() if n > 1 else [axes]

    for idx in range(n):
        strategy = strategies[idx]
        pattern  = STRATEGY_PATTERNS.get(strategy, {})
        enemy_st = COUNTER_STRATEGY.get(strategy)
        enemy_pt = STRATEGY_PATTERNS.get(enemy_st, {})

        blue_x = add_noise(pattern.get("x", [0.5] * 5))
        blue_y = add_noise(pattern.get("y", [0.5] * 5))
        red_x  = add_noise(enemy_pt.get("x", [0.5] * 5))
        red_y  = add_noise(enemy_pt.get("y", [0.5] * 5))

        ax = axes[idx]
        if map_image is not None:
            ax.imshow(map_image)
            h, w, _ = map_image.shape
            bx = [x * w for x in blue_x]; by = [y * h for y in blue_y]
            rx = [x * w for x in red_x];  ry = [y * h for y in red_y]
        else:
            bx, by, rx, ry = blue_x, blue_y, red_x, red_y
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.invert_yaxis()

        ax.scatter(bx, by, s=300, c="dodgerblue", edgecolors="black",
                   linewidths=1.5, alpha=0.80, label="Aliados")
        ax.scatter(rx, ry, s=300, c="red",        edgecolors="black",
                   linewidths=1.5, alpha=0.80, label="Enemigos")
        ax.set_title(f"{strategy}\nvs {enemy_st}", fontsize=10)
        ax.legend(fontsize=8)
        ax.axis("off")

    # Ocultar ejes sobrantes
    for idx in range(n, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=120, bbox_inches="tight")
    return fig_to_base64(fig)
