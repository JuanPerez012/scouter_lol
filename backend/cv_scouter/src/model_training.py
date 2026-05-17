# ============================================================
# src/model_training.py
# Generación del dataset espacial y entrenamiento del modelo
# táctico — PyTorch (sin TensorFlow)
# ============================================================

import sys as _sys
import os as _os
_CV_BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _CV_BASE not in _sys.path:
    _sys.path.insert(0, _CV_BASE)

import os
import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import STRATEGY_PATTERNS, TRAINING, MODEL_FILES, LOGS_DIR
from src.spatial_analysis import extract_spatial_features

DEVICE = torch.device("cpu")
FEATURE_COLS = [
    "avg_distance", "dispersion", "min_distance", "max_distance",
    "isolated", "central_control", "side_pressure",
    "y_mean", "y_std", "x_std", "vertical_spread", "horizontal_spread",
    "top_zone", "bottom_zone",
]


# ─── RUIDO ESPACIAL ───────────────────────────────────────────

def add_noise(values: list, noise_level: float = 0.03) -> list:
    """Agrega variación aleatoria controlada a posiciones tácticas."""
    return [v + np.random.uniform(-noise_level, noise_level) for v in values]


# ─── GENERACIÓN DEL DATASET ESPACIAL ─────────────────────────

def generate_spatial_dataset(
    samples_per_strategy: int = 200,
    noise_level: float = 0.05,
) -> pd.DataFrame:
    """
    Genera el dataset de entrenamiento espacial táctico.
    Cada estrategia produce N escenarios con ruido aleatorio.
    Equivalente a las Fases 10-11 del notebook.
    """
    records = []

    for strategy, pattern in STRATEGY_PATTERNS.items():
        print(f"  Generando escenarios: {strategy}")
        for _ in range(samples_per_strategy):
            x_pos = add_noise(pattern["x"], noise_level)
            y_pos = add_noise(pattern["y"], noise_level)
            features = extract_spatial_features(x_pos, y_pos)
            features["strategy_label"] = strategy
            records.append(features)

    df = pd.DataFrame(records)
    print(f"\n✓ Dataset generado: {len(df)} registros, {len(STRATEGY_PATTERNS)} estrategias")
    return df


# ─── PREPROCESAMIENTO ─────────────────────────────────────────

def preprocess(df: pd.DataFrame):
    """
    Codifica labels, normaliza features y divide en train/test.
    Equivalente a las celdas 71-74 del notebook.
    """
    X = df[FEATURE_COLS].values
    y = df["strategy_label"].values

    label_encoder = LabelEncoder()
    y_encoded     = label_encoder.fit_transform(y)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded,
        test_size=TRAINING["test_size"],
        random_state=TRAINING["random_state"],
        stratify=y_encoded,
    )

    print(f"✓ Train: {X_train.shape}  |  Test: {X_test.shape}")
    print(f"✓ Clases: {list(label_encoder.classes_)}")

    return X_train, X_test, y_train, y_test, label_encoder, scaler


# ─── MODELO NEURONAL ──────────────────────────────────────────

class TacticalModel(nn.Module):
    """
    Red neuronal densa para clasificación táctica espacial.
    Versión mejorada: 3 capas ocultas + dropout para regularización.
    """
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, TRAINING["dense_units_1"]),
            nn.ReLU(),
            nn.Dropout(TRAINING.get("dropout_rate", 0.2)),
            nn.Linear(TRAINING["dense_units_1"], TRAINING["dense_units_2"]),
            nn.ReLU(),
            nn.Dropout(TRAINING.get("dropout_rate", 0.2)),
            nn.Linear(TRAINING["dense_units_2"], TRAINING.get("dense_units_3", 32)),
            nn.ReLU(),
            nn.Linear(TRAINING.get("dense_units_3", 32), num_classes),
        )

    def forward(self, x):
        return self.net(x)


def build_model(input_dim: int, num_classes: int) -> TacticalModel:
    model = TacticalModel(input_dim, num_classes).to(DEVICE)
    print(model)
    return model


def train_model(model, X_train, y_train, X_test, y_test):
    """
    Entrena el modelo táctico.
    Equivalente a las celdas 77-78 del notebook.
    """
    Xt = torch.tensor(X_train, dtype=torch.float32)
    Xv = torch.tensor(X_test,  dtype=torch.float32)
    yt = torch.tensor(y_train, dtype=torch.long)
    yv = torch.tensor(y_test,  dtype=torch.long)

    loader_train = DataLoader(
        TensorDataset(Xt, yt),
        batch_size=TRAINING["batch_size"], shuffle=True,
    )
    loader_val = DataLoader(TensorDataset(Xv, yv), batch_size=TRAINING["batch_size"])

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=TRAINING.get("learning_rate", 1e-3))

    history = {"accuracy": [], "val_accuracy": [], "loss": [], "val_loss": []}

    for epoch in range(TRAINING["epochs"]):
        model.train()
        total_loss, correct, total = 0.0, 0, 0
        for Xb, yb in loader_train:
            optimizer.zero_grad()
            logits = model(Xb)
            loss   = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(yb)
            correct    += (logits.argmax(1) == yb).sum().item()
            total      += len(yb)

        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for Xb, yb in loader_val:
                logits = model(Xb)
                loss   = criterion(logits, yb)
                val_loss    += loss.item() * len(yb)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_total   += len(yb)

        train_loss = total_loss / total
        train_acc  = correct / total
        val_loss  /= val_total
        val_acc    = val_correct / val_total

        history["loss"].append(train_loss)
        history["accuracy"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_acc)

        print(
            f"[TacticalModel] Epoch {epoch+1:>2}/{TRAINING['epochs']} — "
            f"loss: {train_loss:.4f}  acc: {train_acc:.4f} | "
            f"val_loss: {val_loss:.4f}  val_acc: {val_acc:.4f}"
        )

    return history


# ─── EVALUACIÓN ───────────────────────────────────────────────

def evaluate_model(model, X_test, y_test, label_encoder):
    """Evaluación completa con classification report y matriz de confusión."""
    import seaborn as sns

    Xv = torch.tensor(X_test, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        logits = model(Xv)

    y_pred = logits.argmax(1).numpy()
    acc    = (y_pred == y_test).mean()

    print(f"\n[TacticalModel] Accuracy: {acc:.4f}\n")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
    ))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_,
    )
    plt.xticks(rotation=45)
    plt.title("Matriz de confusión táctica")
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(os.path.join(LOGS_DIR, "confusion_tactical.png"), dpi=120)
    plt.close()
    return acc


def plot_training_curves(history: dict):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(history["accuracy"],     label="Train")
    axes[0].plot(history["val_accuracy"], label="Val")
    axes[0].set_title("Accuracy — TacticalModel"); axes[0].legend()
    axes[1].plot(history["loss"],     label="Train")
    axes[1].plot(history["val_loss"], label="Val")
    axes[1].set_title("Loss — TacticalModel"); axes[1].legend()
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(os.path.join(LOGS_DIR, "curves_tactical.png"), dpi=120)
    plt.close()
    print("✓ Curvas guardadas en logs/")


# ─── SERIALIZACIÓN ────────────────────────────────────────────

def save_model(model, label_encoder, scaler, input_dim: int, num_classes: int):
    os.makedirs(os.path.dirname(MODEL_FILES["tactical_model"]), exist_ok=True)
    torch.save({
        "state_dict":  model.state_dict(),
        "input_dim":   input_dim,
        "num_classes": num_classes,
    }, MODEL_FILES["tactical_model"])
    with open(MODEL_FILES["label_encoder"], "wb") as f:
        pickle.dump(label_encoder, f)
    with open(MODEL_FILES["scaler"], "wb") as f:
        pickle.dump(scaler, f)
    print("✓ Modelo táctico guardado correctamente.")


def load_model():
    """Carga modelo, label encoder y scaler desde disco."""
    checkpoint    = torch.load(MODEL_FILES["tactical_model"], map_location=DEVICE)
    model         = TacticalModel(
        checkpoint["input_dim"],
        checkpoint["num_classes"],
    ).to(DEVICE)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    with open(MODEL_FILES["label_encoder"], "rb") as f:
        label_encoder = pickle.load(f)
    with open(MODEL_FILES["scaler"], "rb") as f:
        scaler = pickle.load(f)

    return model, label_encoder, scaler
