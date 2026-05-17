#!/usr/bin/env python3
# ============================================================
# scripts/debug_bilstm.py
# Prueba mínima del BiLSTM para aislar el problema
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# ─── 1. DATOS SINTÉTICOS SIMPLES ─────────────────────────────
# Si el BiLSTM no aprende NI CON DATOS SINTÉTICOS TRIVIALES,
# el problema es estructural del modelo, no del dataset.

print("="*60)
print("TEST 1 — BiLSTM con datos sintéticos triviales")
print("="*60)

# 4 clases, secuencias donde clase = primer token
# Clase 0: secuencias que empiezan con token 2
# Clase 1: secuencias que empiezan con token 3
# Clase 2: secuencias que empiezan con token 4
# Clase 3: secuencias que empiezan con token 5

np.random.seed(42)
torch.manual_seed(42)

N = 400
SEQ_LEN = 20
VOCAB = 50
NUM_CLASSES = 4

X_synt = np.random.randint(10, VOCAB, size=(N, SEQ_LEN))
y_synt = np.random.randint(0, NUM_CLASSES, size=N)

# Hacer la señal obvia: primer token = clase + 2
for i in range(N):
    X_synt[i, 0] = y_synt[i] + 2

Xt = torch.tensor(X_synt[:320], dtype=torch.long)
Xv = torch.tensor(X_synt[320:], dtype=torch.long)
yt = torch.tensor(y_synt[:320], dtype=torch.long)
yv = torch.tensor(y_synt[320:], dtype=torch.long)

loader_train = DataLoader(TensorDataset(Xt, yt), batch_size=32, shuffle=True)
loader_val   = DataLoader(TensorDataset(Xv, yv), batch_size=32)

# Modelo mínimo
class MiniBiLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb    = nn.Embedding(VOCAB, 16, padding_idx=0)
        self.bilstm = nn.LSTM(16, 32, batch_first=True, bidirectional=True)
        self.fc     = nn.Linear(64, NUM_CLASSES)

    def forward(self, x):
        x = self.emb(x)
        out, _ = self.bilstm(x)
        return self.fc(out[:, -1, :])

model     = MiniBiLSTM()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(10):
    model.train()
    for Xb, yb in loader_train:
        optimizer.zero_grad()
        loss = criterion(model(Xb), yb)
        loss.backward()
        optimizer.step()

model.eval()
with torch.no_grad():
    logits = model(Xv)
acc = (logits.argmax(1) == yv).float().mean().item()
print(f"Accuracy datos sintéticos: {acc:.4f}")
if acc > 0.80:
    print("✓ BiLSTM FUNCIONA correctamente con PyTorch")
    print("  → El problema está en los DATOS o HIPERPARÁMETROS")
else:
    print("✗ BiLSTM NO aprende ni datos triviales")
    print("  → Problema estructural de PyTorch/entorno")

# ─── 2. VERIFICAR GRADIENTES ─────────────────────────────────
print("\n" + "="*60)
print("TEST 2 — Verificar que los gradientes fluyen")
print("="*60)

model2    = MiniBiLSTM()
optimizer2 = torch.optim.Adam(model2.parameters(), lr=1e-3)

Xb, yb = next(iter(loader_train))
logits2 = model2(Xb)
loss2   = criterion(logits2, yb)
loss2.backward()

for name, param in model2.named_parameters():
    if param.grad is not None:
        print(f"  ✓ {name:30s} grad_norm={param.grad.norm():.6f}")
    else:
        print(f"  ✗ {name:30s} SIN GRADIENTE")

# ─── 3. PROBAR CON DATASET REAL ──────────────────────────────
print("\n" + "="*60)
print("TEST 3 — BiLSTM con dataset real (vocabulario 600)")
print("="*60)

import pandas as pd
from config.settings import DATA_FILES, NLP, TRAINING
from src.nlp_preprocessing import (
    encode_and_split, build_sequences, clean_text
)

df = pd.read_csv(DATA_FILES["scouting_nlp"])
X_train_c, X_test_c, y_train, y_test, le = encode_and_split(df)
X_train_pad, X_test_pad, tok = build_sequences(X_train_c, X_test_c)

print(f"\nVocab real: {len(tok.word_index)}")
print(f"Max índice en train: {X_train_pad.max()}")
print(f"Max índice en test:  {X_test_pad.max()}")

# Longitud real de las secuencias (sin padding)
lengths = [(row != 0).sum() for row in X_train_pad]
print(f"Longitud promedio de secuencia (sin padding): {np.mean(lengths):.1f}")
print(f"Longitud máxima: {max(lengths)}")
print(f"Longitud mínima: {min(lengths)}")

# Verificar que las secuencias son distintas entre clases
print(f"\nPrimera secuencia (clase {y_train[0]}):")
print(X_train_pad[0][:15])
print(f"Segunda secuencia (clase {y_train[1]}):")
print(X_train_pad[1][:15])

# Probar 3 épocas rápidas con lr=1e-3
VOCAB_REAL = len(tok.word_index) + 1
NUM_CLS    = len(le.classes_)

class RealBiLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb    = nn.Embedding(VOCAB_REAL, 32, padding_idx=0)
        self.bilstm = nn.LSTM(32, 64, batch_first=True, bidirectional=True)
        self.drop   = nn.Dropout(0.3)
        self.fc     = nn.Linear(128, NUM_CLS)

    def forward(self, x):
        x = self.emb(x)
        out, _ = self.bilstm(x)
        return self.fc(self.drop(out[:, -1, :]))

Xt_r = torch.tensor(X_train_pad, dtype=torch.long)
Xv_r = torch.tensor(X_test_pad,  dtype=torch.long)
yt_r = torch.tensor(y_train, dtype=torch.long)
yv_r = torch.tensor(y_test,  dtype=torch.long)

loader_r = DataLoader(TensorDataset(Xt_r, yt_r), batch_size=32, shuffle=True)

model3    = RealBiLSTM()
crit3     = nn.CrossEntropyLoss()
opt3      = torch.optim.Adam(model3.parameters(), lr=1e-3)

print("\nEntrenando 5 épocas rápidas con vocab real...")
for epoch in range(5):
    model3.train()
    total_loss, correct, total = 0, 0, 0
    for Xb, yb in loader_r:
        opt3.zero_grad()
        logits = model3(Xb)
        loss   = crit3(logits, yb)
        loss.backward()
        opt3.step()
        total_loss += loss.item() * len(yb)
        correct    += (logits.argmax(1) == yb).sum().item()
        total      += len(yb)
    print(f"  Epoch {epoch+1}: loss={total_loss/total:.4f}  acc={correct/total:.4f}")

model3.eval()
with torch.no_grad():
    acc_r = (model3(Xv_r).argmax(1) == yv_r).float().mean().item()
print(f"\nAccuracy val tras 5 épocas: {acc_r:.4f}")
if acc_r > 0.30:
    print("✓ El modelo SÍ aprende con el dataset real")
    print("  → Solo necesita más épocas o ajuste de hiperparámetros")
else:
    print("✗ El modelo NO aprende con el dataset real")
    print("  → Problema en los datos: todas las secuencias son idénticas")
    print("    o el dataset no tiene señal suficiente para BiLSTM")

