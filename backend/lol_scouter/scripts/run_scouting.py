#!/usr/bin/env python3
# ============================================================
# scripts/run_scouting.py  — versión PyTorch
# Ejecutar: python backend/lol_scouter/scripts/run_scouting.py
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MODEL_FILES
from src.data_loader import load_all_tables
from src.nlp_preprocessing import load_preprocessors
from src.model_training import load_bilstm
from src.scouting_engine import generate_final_scouting_report


def main():
    print("Cargando ecosistema de datos...")
    tables = load_all_tables()
    champion_kb = tables["champion_kb"]
    taxonomy_df = tables["taxonomy"]

    print("Cargando modelo BiLSTM (PyTorch)...")
    label_encoder, tokenizer, _ = load_preprocessors()
    num_classes  = len(label_encoder.classes_)
    bilstm_model = load_bilstm(num_classes)

    # Orden: [Top, Jungle, Mid, ADC, Support]
    ally_team  = ["Gnar",   "Sejuani", "Orianna", "Jinx",  "Thresh"]
    enemy_team = ["Camille","LeeSin",  "Zed",     "KaiSa", "Nautilus"]

    print(f"\nAliados: {ally_team}")
    print(f"Rivales: {enemy_team}\n")

    report = generate_final_scouting_report(
        champion_kb=champion_kb,
        taxonomy_df=taxonomy_df,
        model=bilstm_model,
        tokenizer=tokenizer,
        label_encoder=label_encoder,
        ally_team=ally_team,
        enemy_team=enemy_team,
    )
    print(report)

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs", "last_scouting_report.txt",
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReporte guardado en: {output_path}")


if __name__ == "__main__":
    main()
