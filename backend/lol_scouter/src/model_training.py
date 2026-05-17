# ============================================================
# src/model_training.py
# Entrenamiento Dense baseline y BiLSTM manual — PyTorch
# ============================================================

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TRAINING, NLP, MODEL_FILES, LOGS_DIR
from src.manual_lstm import ManualBiLSTM

DEVICE = torch.device("cpu")


# ─── MODELO DENSE (BASELINE) ──────────────────────────────────

class DenseModel(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, TRAINING["dense_units_1"]),
            nn.ReLU(),
            nn.Dropout(TRAINING["dropout_rate"]),
            nn.Linear(TRAINING["dense_units_1"], TRAINING["dense_units_2"]),
            nn.ReLU(),
            nn.Dropout(TRAINING["dropout_rate"]),
            nn.Linear(TRAINING["dense_units_2"], num_classes),
        )

    def forward(self, x):
        return self.net(x)


# ─── MODELO BiLSTM MANUAL ─────────────────────────────────────

class BiLSTMModel(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        vocab_size  = NLP["tokenizer_vocab"]
        embed_dim   = TRAINING["embedding_dim"]
        hidden_size = TRAINING["lstm_units"]

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embed_dim,
            padding_idx=0,
        )
        self.bilstm  = ManualBiLSTM(embed_dim, hidden_size)
        self.dropout = nn.Dropout(TRAINING["dropout_rate"])
        self.fc1     = nn.Linear(hidden_size * 2, hidden_size)
        self.relu    = nn.ReLU()
        self.fc2     = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x   = self.embedding(x)          # (batch, seq_len, embed_dim)
        out = self.bilstm(x)             # (batch, seq_len, hidden*2)
        out = out[:, -1, :]              # último paso temporal
        out = self.dropout(out)
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        return self.fc2(out)


# ─── ENTRENAMIENTO GENÉRICO ───────────────────────────────────

def _train_model(model, loader_train, loader_val, epochs, model_name):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=TRAINING["learning_rate"])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", patience=TRAINING["lr_patience"], factor=TRAINING["lr_factor"]
    )
    history = {"accuracy": [], "val_accuracy": [], "loss": [], "val_loss": []}

    for epoch in range(epochs):
        model.train()
        total_loss, correct, total = 0.0, 0, 0
        for Xb, yb in loader_train:
            optimizer.zero_grad()
            logits = model(Xb)
            loss   = criterion(logits, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=TRAINING["grad_clip"])
            optimizer.step()
            total_loss += loss.item() * len(yb)
            correct    += (logits.argmax(1) == yb).sum().item()
            total      += len(yb)

        train_loss = total_loss / total
        train_acc  = correct / total

        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for Xb, yb in loader_val:
                logits = model(Xb)
                loss   = criterion(logits, yb)
                val_loss    += loss.item() * len(yb)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_total   += len(yb)

        val_loss /= val_total
        val_acc   = val_correct / val_total
        scheduler.step(val_loss)

        history["loss"].append(train_loss)
        history["accuracy"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_accuracy"].append(val_acc)

        print(
            f"[{model_name}] Epoch {epoch+1:>2}/{epochs} — "
            f"loss: {train_loss:.4f}  acc: {train_acc:.4f} | "
            f"val_loss: {val_loss:.4f}  val_acc: {val_acc:.4f}"
        )

    return history


# ─── DENSE ────────────────────────────────────────────────────

def build_dense_model(input_dim: int, num_classes: int) -> DenseModel:
    model = DenseModel(input_dim, num_classes).to(DEVICE)
    print(model)
    return model


def train_dense(model, X_train_tfidf, y_train, X_test_tfidf, y_test):
    Xt = torch.tensor(X_train_tfidf.toarray(), dtype=torch.float32)
    Xv = torch.tensor(X_test_tfidf.toarray(),  dtype=torch.float32)
    yt = torch.tensor(y_train, dtype=torch.long)
    yv = torch.tensor(y_test,  dtype=torch.long)

    loader_train = DataLoader(TensorDataset(Xt, yt), batch_size=TRAINING["batch_size"], shuffle=True)
    loader_val   = DataLoader(TensorDataset(Xv, yv), batch_size=TRAINING["batch_size"])

    history = _train_model(model, loader_train, loader_val, TRAINING["dense_epochs"], "Dense")

    os.makedirs(os.path.dirname(MODEL_FILES["dense"]), exist_ok=True)
    torch.save({
        "state_dict":  model.state_dict(),
        "input_dim":   Xt.shape[1],
        "num_classes": model.net[-1].out_features,
    }, MODEL_FILES["dense"])
    print(f"✓ Modelo Dense guardado en {MODEL_FILES['dense']}")
    return history


# ─── BILSTM ───────────────────────────────────────────────────

def build_bilstm_model(num_classes: int) -> BiLSTMModel:
    model = BiLSTMModel(num_classes).to(DEVICE)
    print(model)
    return model


def train_bilstm(model, X_train_pad, y_train, X_test_pad, y_test):
    Xt = torch.tensor(X_train_pad, dtype=torch.long)
    Xv = torch.tensor(X_test_pad,  dtype=torch.long)
    yt = torch.tensor(y_train, dtype=torch.long)
    yv = torch.tensor(y_test,  dtype=torch.long)

    loader_train = DataLoader(TensorDataset(Xt, yt), batch_size=TRAINING["batch_size"], shuffle=True)
    loader_val   = DataLoader(TensorDataset(Xv, yv), batch_size=TRAINING["batch_size"])

    history = _train_model(model, loader_train, loader_val, TRAINING["bilstm_epochs"], "BiLSTM")

    os.makedirs(os.path.dirname(MODEL_FILES["bilstm"]), exist_ok=True)
    torch.save({
        "state_dict":  model.state_dict(),
        "num_classes": model.fc2.out_features,
    }, MODEL_FILES["bilstm"])
    print(f"✓ Modelo BiLSTM guardado en {MODEL_FILES['bilstm']}")
    return history


# ─── EVALUACIÓN ───────────────────────────────────────────────

def evaluate_model(model, X_test, y_test, label_encoder, model_name: str, is_sequence=False):
    from sklearn.metrics import classification_report, confusion_matrix
    import seaborn as sns

    if is_sequence:
        Xv = torch.tensor(X_test, dtype=torch.long)
    else:
        arr = X_test if isinstance(X_test, np.ndarray) else X_test.toarray()
        Xv  = torch.tensor(arr, dtype=torch.float32)

    model.eval()
    with torch.no_grad():
        logits = model(Xv)

    criterion = nn.CrossEntropyLoss()
    yv     = torch.tensor(y_test, dtype=torch.long)
    loss   = criterion(logits, yv).item()
    y_pred = logits.argmax(1).numpy()
    acc    = (y_pred == y_test).mean()

    print(f"\n[{model_name}] Accuracy: {acc:.4f}  |  Loss: {loss:.4f}\n")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
    ))

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(12, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_)
    plt.xticks(rotation=45)
    plt.title(f"Matriz de confusión — {model_name}")
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(os.path.join(LOGS_DIR,
        f"confusion_{model_name.lower().replace(' ','_')}.png"), dpi=120)
    plt.close()
    return acc, loss


def plot_training_curves(history: dict, model_name: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(history["accuracy"],     label="Train")
    axes[0].plot(history["val_accuracy"], label="Val")
    axes[0].set_title(f"Accuracy — {model_name}"); axes[0].legend()
    axes[1].plot(history["loss"],     label="Train")
    axes[1].plot(history["val_loss"], label="Val")
    axes[1].set_title(f"Loss — {model_name}"); axes[1].legend()
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(os.path.join(LOGS_DIR,
        f"curves_{model_name.lower().replace(' ','_')}.png"), dpi=120)
    plt.close()
    print(f"✓ Curvas guardadas en logs/")


def compare_models(acc_dense: float, acc_bilstm: float):
    import pandas as pd
    import seaborn as sns

    df = pd.DataFrame({
        "Modelo":   ["Dense TF-IDF", "BiLSTM"],
        "Accuracy": [acc_dense,       acc_bilstm],
    })
    print(df.to_string(index=False))
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="Modelo", y="Accuracy")
    plt.ylim(0.50, 1.01)
    plt.title("Comparación final de accuracy")
    plt.tight_layout()
    os.makedirs(LOGS_DIR, exist_ok=True)
    plt.savefig(os.path.join(LOGS_DIR, "comparacion_modelos.png"), dpi=120)
    plt.close()
    return df


# ─── CARGA ────────────────────────────────────────────────────

def load_bilstm(num_classes: int) -> BiLSTMModel:
    checkpoint = torch.load(MODEL_FILES["bilstm"], map_location=DEVICE)
    model = BiLSTMModel(checkpoint.get("num_classes", num_classes)).to(DEVICE)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model


def load_dense(input_dim: int, num_classes: int) -> DenseModel:
    checkpoint = torch.load(MODEL_FILES["dense"], map_location=DEVICE)
    model = DenseModel(
        checkpoint.get("input_dim", input_dim),
        checkpoint.get("num_classes", num_classes),
    ).to(DEVICE)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model
