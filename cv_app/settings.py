# ============================================================
# config/settings.py — versión mejorada
# ============================================================

import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR   = os.path.join(BASE_DIR, "logs")

DATASET = {
    "base_path":   os.path.join(DATA_DIR, "minimap_dataset"),
    "splits":      ["train", "val", "test"],
    "minimap_img": os.path.join(DATA_DIR, "minimapa.png"),
}

# ─── PATRONES TÁCTICOS DIFERENCIADOS ─────────────────────────
# Criterios de diferenciación aplicados:
#
# wombo combo       → máxima agrupación central (avg_dist ~0.05)
# jugar a objetivos → agrupación media-alta en zona de río (avg_dist ~0.12)
# tempo composition → distribución lineal diagonal media (avg_dist ~0.28)
# macro composition → distribución amplia uniforme (avg_dist ~0.35)
# front-to-back     → formación compacta con frontline adelantada
# agresivo early    → presión hacia zona enemiga (coords altas)
# escalar late      → dispersión máxima en zonas propias (coords bajas)
# splitpush táctico → un campeón muy separado (flanco extremo)
# poke composition  → línea horizontal separada
# pick composition  → presión en flancos con centro vacío
# protect hypercarry→ 4 agrupados protegiendo 1 aislado
# dive composition  → agresivo con salto hacia atrás enemigo

STRATEGY_PATTERNS = {
    # ── MÁXIMA AGRUPACIÓN CENTRAL ────────────────────────────
    "wombo combo": {
        "x": [0.48, 0.50, 0.49, 0.51, 0.50],
        "y": [0.48, 0.50, 0.51, 0.49, 0.50],
    },
    # ── AGRUPACIÓN MEDIA EN ZONA DE RÍO ──────────────────────
    "jugar a objetivos": {
        "x": [0.42, 0.46, 0.50, 0.54, 0.58],
        "y": [0.38, 0.44, 0.50, 0.56, 0.42],
    },
    # ── DIAGONAL MEDIA — PRESIÓN COORDINADA ──────────────────
    "tempo composition": {
        "x": [0.28, 0.38, 0.50, 0.62, 0.72],
        "y": [0.32, 0.42, 0.50, 0.58, 0.68],
    },
    # ── DISPERSIÓN AMPLIA — MACRO DISTRIBUIDO ────────────────
    "macro composition": {
        "x": [0.15, 0.35, 0.50, 0.68, 0.85],
        "y": [0.20, 0.38, 0.50, 0.65, 0.82],
    },
    # ── FORMACIÓN COMPACTA FRONTAL ────────────────────────────
    "front-to-back": {
        "x": [0.38, 0.42, 0.50, 0.58, 0.62],
        "y": [0.40, 0.44, 0.50, 0.56, 0.60],
    },
    # ── PRESIÓN ZONA ALTA (early aggression) ─────────────────
    "agresivo early": {
        "x": [0.35, 0.42, 0.50, 0.58, 0.68],
        "y": [0.22, 0.30, 0.38, 0.32, 0.25],
    },
    # ── DISPERSIÓN MÁXIMA — ZONA PROPIA ──────────────────────
    "escalar late": {
        "x": [0.18, 0.32, 0.50, 0.70, 0.82],
        "y": [0.65, 0.72, 0.75, 0.70, 0.68],
    },
    # ── UN FLANCO EXTREMO + 4 AGRUPADOS ──────────────────────
    "splitpush táctico": {
        "x": [0.10, 0.48, 0.50, 0.52, 0.92],
        "y": [0.10, 0.48, 0.50, 0.52, 0.90],
    },
    # ── LÍNEA HORIZONTAL SEPARADA ─────────────────────────────
    "poke composition": {
        "x": [0.15, 0.32, 0.50, 0.68, 0.85],
        "y": [0.35, 0.37, 0.38, 0.37, 0.35],
    },
    # ── FLANCOS ACTIVOS — CENTRO VACÍO ────────────────────────
    "pick composition": {
        "x": [0.12, 0.20, 0.50, 0.80, 0.88],
        "y": [0.30, 0.65, 0.50, 0.35, 0.70],
    },
    # ── 4 PROTEGIENDO 1 CARRY CENTRAL ────────────────────────
    "protect hypercarry": {
        "x": [0.42, 0.46, 0.50, 0.54, 0.58],
        "y": [0.44, 0.56, 0.50, 0.44, 0.56],
    },
    # ── AGRESIVO HACIA BACKLINE ENEMIGA ──────────────────────
    "dive composition": {
        "x": [0.38, 0.45, 0.50, 0.55, 0.62],
        "y": [0.28, 0.32, 0.30, 0.32, 0.28],
    },
}

# ─── PARÁMETROS DE ENTRENAMIENTO MEJORADOS ────────────────────
TRAINING = {
    "samples_per_strategy": 500,    # 200→500: más datos
    "noise_level":          0.04,   # ruido moderado
    "test_size":            0.20,
    "random_state":         42,
    "epochs":               80,     # 40→80: más entrenamiento
    "batch_size":           64,     # batch más grande
    "dense_units_1":        128,    # 64→128: red más profunda
    "dense_units_2":        64,     # 32→64
    "dense_units_3":        32,     # capa extra
    "learning_rate":        1e-3,
    "lr_patience":          8,
    "dropout_rate":         0.2,
}

THRESHOLDS = {
    "grouped":  0.15,
    "semi":     0.30,
    "isolated": 0.40,
    "noise":    0.03,
}

MODEL_FILES = {
    "tactical_model": os.path.join(MODELS_DIR, "tactical_model.pkl"),
    "label_encoder":  os.path.join(MODELS_DIR, "label_encoder_cv.pkl"),
    "scaler":         os.path.join(MODELS_DIR, "scaler_cv.pkl"),
}
