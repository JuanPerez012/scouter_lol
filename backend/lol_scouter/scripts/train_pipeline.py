#!/usr/bin/env python3
# ============================================================
# scripts/train_pipeline.py  — versión PyTorch (sin TensorFlow)
# Ejecutar desde la raíz del proyecto:
#   python backend/lol_scouter/scripts/train_pipeline.py
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from config.settings import DATA_FILES, MODEL_FILES, LOGS_DIR
from src.data_loader import load_all_tables, summary_table
from src.nlp_preprocessing import (
    encode_and_split, build_tfidf, build_sequences, save_preprocessors,
)
from src.model_training import (
    build_dense_model, train_dense,
    build_bilstm_model, train_bilstm,
    evaluate_model, plot_training_curves, compare_models,
)


def main():
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(MODEL_FILES["bilstm"])).mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("FASE 1 — CARGA DEL ECOSISTEMA DE DATOS")
    print("="*60)
    tables = load_all_tables()
    print(summary_table(tables).to_string(index=False))

    df_v3 = tables["scouting_nlp"]
    if df_v3.empty:
        print("[ERROR] Scouting_5000_V3.csv no encontrado en data/")
        sys.exit(1)

    print(f"\nShape dataset NLP: {df_v3.shape}")
    print(f"Nulos: {df_v3.isnull().sum().sum()}")

    print("\n" + "="*60)
    print("FASE 3 — PREPROCESAMIENTO NLP")
    print("="*60)
    X_train_clean, X_test_clean, y_train, y_test, label_encoder = encode_and_split(df_v3)
    num_classes = len(label_encoder.classes_)

    print("\n" + "="*60)
    print("FASE 4 — TF-IDF + N-GRAMS")
    print("="*60)
    X_train_tfidf, X_test_tfidf, tfidf_vectorizer = build_tfidf(X_train_clean, X_test_clean)

    print("\n" + "="*60)
    print("FASE 5 — TOKENIZACIÓN SECUENCIAL")
    print("="*60)
    X_train_pad, X_test_pad, tokenizer = build_sequences(X_train_clean, X_test_clean)

    print("\n" + "="*60)
    print("FASE 6 — MODELO DENSE BASELINE (PyTorch)")
    print("="*60)
    dense_model = build_dense_model(X_train_tfidf.shape[1], num_classes)
    history_dense = train_dense(dense_model, X_train_tfidf, y_train, X_test_tfidf, y_test)
    acc_dense, _ = evaluate_model(
        dense_model, X_test_tfidf, y_test, label_encoder, "Dense TF-IDF", is_sequence=False
    )
    plot_training_curves(history_dense, "Dense TF-IDF")

    print("\n" + "="*60)
    print("FASE 7 — MODELO BiLSTM (PyTorch)")
    print("="*60)
    bilstm_model = build_bilstm_model(num_classes)
    history_bilstm = train_bilstm(bilstm_model, X_train_pad, y_train, X_test_pad, y_test)
    acc_bilstm, _ = evaluate_model(
        bilstm_model, X_test_pad, y_test, label_encoder, "BiLSTM", is_sequence=True
    )
    plot_training_curves(history_bilstm, "BiLSTM")

    print("\n" + "="*60)
    print("FASE 9 — COMPARACIÓN FINAL")
    print("="*60)
    compare_models(acc_dense, acc_bilstm)

    save_preprocessors(label_encoder, tokenizer, tfidf_vectorizer)

    print("\n✅ Pipeline completado correctamente.")
    print(f"   Modelos en: {os.path.dirname(MODEL_FILES['bilstm'])}")


if __name__ == "__main__":
    main()
