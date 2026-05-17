# ============================================================
# scouter_app/services.py
# Capa de servicio: carga modelos y ejecuta inferencia
# Se integra con el backend lol_scouter existente
# ============================================================

import sys
import os
from pathlib import Path
from django.conf import settings

# Agregar backend/lol_scouter al path de Python
SCOUTER_PATH = str(settings.SCOUTER_BASE_DIR)
if SCOUTER_PATH not in sys.path:
    sys.path.insert(0, SCOUTER_PATH)

import torch
from config.settings import MODEL_FILES
from src.data_loader import load_all_tables
from src.nlp_preprocessing import load_preprocessors
from src.model_training import load_bilstm
from src.scouting_engine import generate_final_scouting_report

# ─── SINGLETON: carga una sola vez al iniciar Django ──────────

_tables        = None
_label_encoder = None
_tokenizer     = None
_bilstm_model  = None


def _load_resources():
    """Carga tablas y modelos en memoria una sola vez."""
    global _tables, _label_encoder, _tokenizer, _bilstm_model

    if _bilstm_model is not None:
        return  # ya cargado

    _tables        = load_all_tables()
    _label_encoder, _tokenizer, _ = load_preprocessors()
    num_classes    = len(_label_encoder.classes_)
    _bilstm_model  = load_bilstm(num_classes)

    print("✓ Modelos del Scouter cargados correctamente.")


def get_champion_list() -> list:
    """Retorna la lista de campeones disponibles ordenada."""
    _load_resources()
    champions = sorted(_tables["champion_kb"]["champion"].tolist())
    return champions


def run_scouting(ally_team: list, enemy_team: list) -> dict:
    """
    Ejecuta el scouting completo y retorna un diccionario
    con el reporte y los datos estructurados para la vista.

    Parámetros:
        ally_team:  lista de 5 campeones aliados [Top, Jg, Mid, ADC, Sup]
        enemy_team: lista de 5 campeones rivales [Top, Jg, Mid, ADC, Sup]

    Retorna:
        {
            "report":        str  — reporte narrativo completo,
            "top_strategies": list — [(nombre, confianza), ...],
            "ally_team":     list,
            "enemy_team":    list,
            "error":         str | None,
        }
    """
    _load_resources()

    try:
        from src.scouting_engine import predict_top_strategies

        report = generate_final_scouting_report(
            champion_kb   = _tables["champion_kb"],
            taxonomy_df   = _tables["taxonomy"],
            model         = _bilstm_model,
            tokenizer     = _tokenizer,
            label_encoder = _label_encoder,
            ally_team     = ally_team,
            enemy_team    = enemy_team,
        )

        top_strategies = predict_top_strategies(
            model         = _bilstm_model,
            tokenizer     = _tokenizer,
            label_encoder = _label_encoder,
            champion_kb   = _tables["champion_kb"],
            ally_team     = ally_team,
            enemy_team    = enemy_team,
            top_n         = 3,
        )

        return {
            "report":         report,
            "top_strategies": top_strategies,
            "ally_team":      ally_team,
            "enemy_team":     enemy_team,
            "error":          None,
        }

    except Exception as e:
        return {
            "report":         "",
            "top_strategies": [],
            "ally_team":      ally_team,
            "enemy_team":     enemy_team,
            "error":          str(e),
        }
