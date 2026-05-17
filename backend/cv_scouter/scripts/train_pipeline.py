#!/usr/bin/env python3
# ============================================================
# scripts/train_pipeline.py
# Pipeline completo de entrenamiento del modelo táctico CV
# Ejecutar desde la raíz del proyecto:
#   python backend/cv_scouter/scripts/train_pipeline.py
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from config.settings import MODEL_FILES, LOGS_DIR, TRAINING
from src.model_training import (
    generate_spatial_dataset,
    preprocess,
    build_model,
    train_model,
    evaluate_model,
    plot_training_curves,
    save_model,
)


def main():
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(MODEL_FILES["tactical_model"])).mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("FASE 1 — GENERACIÓN DEL DATASET ESPACIAL")
    print("="*60)
    df = generate_spatial_dataset(
        samples_per_strategy=TRAINING["samples_per_strategy"],
        noise_level=TRAINING["noise_level"],
    )
    print(df.head())

    print("\n" + "="*60)
    print("FASE 2 — PREPROCESAMIENTO")
    print("="*60)
    X_train, X_test, y_train, y_test, label_encoder, scaler = preprocess(df)
    num_classes = len(label_encoder.classes_)

    print("\n" + "="*60)
    print("FASE 3 — CONSTRUCCIÓN Y ENTRENAMIENTO DEL MODELO")
    print("="*60)
    model = build_model(input_dim=X_train.shape[1], num_classes=num_classes)
    history = train_model(model, X_train, y_train, X_test, y_test)

    print("\n" + "="*60)
    print("FASE 4 — EVALUACIÓN")
    print("="*60)
    evaluate_model(model, X_test, y_test, label_encoder)
    plot_training_curves(history)

    print("\n" + "="*60)
    print("FASE 5 — GUARDAR MODELO")
    print("="*60)
    save_model(model, label_encoder, scaler, X_train.shape[1], num_classes)

    print("\n✅ Pipeline CV completado correctamente.")


if __name__ == "__main__":
    main()
