# ============================================================
# config/settings.py
# Configuración central del sistema Scouter LoL
# ============================================================

import os

# ─── RUTAS BASE ───────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR   = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR   = os.path.join(BASE_DIR, "logs")

# ─── ARCHIVOS DE DATOS ────────────────────────────────────────
DATA_FILES = {
    "champion_kb":       os.path.join(DATA_DIR, "Champion_KB.csv"),
    "champion_kb_fixed": os.path.join(DATA_DIR, "Champion_KB_corrected.csv"),
    "counters":          os.path.join(DATA_DIR, "Counters.csv"),
    "flex_picks":        os.path.join(DATA_DIR, "Flex_Picks.csv"),
    "competitive_comps": os.path.join(DATA_DIR, "Competitive_Comps.csv"),
    "temporal_context":  os.path.join(DATA_DIR, "Temporal_Context.csv"),
    "taxonomy":          os.path.join(DATA_DIR, "Taxonomy.csv"),
    "champion_synergies":os.path.join(DATA_DIR, "Champion_Synergies.csv"),
    "objective_priority":os.path.join(DATA_DIR, "Objective_Priority.csv"),
    "draft_tags":        os.path.join(DATA_DIR, "Draft_Tags.csv"),
    "scouting_nlp":      os.path.join(DATA_DIR, "Scouting_5000_V3.csv"),
}

# ─── PARÁMETROS NLP ───────────────────────────────────────────
NLP = {
    "tfidf_max_features":  7000,
    "tfidf_ngram_range":   (1, 2),
    "tokenizer_vocab":     600,
    "oov_token":           "<OOV>",
    "max_sequence_length": 80,
    "test_size":           0.20,
    "random_state":        42,
}

# ─── PARÁMETROS DE ENTRENAMIENTO ──────────────────────────────
TRAINING = {
    "dense_epochs":   10,
    "bilstm_epochs":  20,       # más épocas para convergencia completa
    "batch_size":     64,       # batch más grande = gradientes más estables
    "dense_units_1":  256,
    "dense_units_2":  128,
    "lstm_units":     128,
    "embedding_dim":  64,
    "dropout_rate":   0.1,      # menos dropout al inicio para aprender más rápido
    "learning_rate":  5e-3,     # lr más alto para arrancar más rápido
    "lr_patience":    8,        # esperar más antes de reducir lr
    "lr_factor":      0.5,
    "grad_clip":      1.0,
}

# ─── ARCHIVOS DE MODELO GUARDADOS ─────────────────────────────
MODEL_FILES = {
    "bilstm":        os.path.join(MODELS_DIR, "bilstm_model.keras"),
    "dense":         os.path.join(MODELS_DIR, "dense_model.keras"),
    "tokenizer":     os.path.join(MODELS_DIR, "tokenizer.pkl"),
    "label_encoder": os.path.join(MODELS_DIR, "label_encoder.pkl"),
    "tfidf":         os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"),
}
