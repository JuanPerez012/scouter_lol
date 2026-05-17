#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
from src.manual_lstm import ManualBiLSTM

torch.manual_seed(0)

# ─── Datos sintéticos triviales ───────────────────────────────
crit = nn.CrossEntropyLoss()
X = torch.zeros(200, 10, dtype=torch.long)
y = torch.randint(0, 4, (200,))
for i in range(200):
    X[i, 0] = y[i] + 2

# ─── TEST: ManualBiLSTM con dos LSTMCell independientes ───────
print("="*55)
print("TEST — ManualBiLSTM dual (dos LSTMCell independientes)")
print("="*55)

class TinyBiLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb    = nn.Embedding(20, 8, padding_idx=0)
        self.bilstm = ManualBiLSTM(8, 16)
        self.fc     = nn.Linear(32, 4)
    def forward(self, x):
        x = self.emb(x)
        o = self.bilstm(x)
        return self.fc(o[:, -1, :])

model = TinyBiLSTM()
opt   = torch.optim.Adam(model.parameters(), lr=1e-2)

for epoch in range(20):
    model.train()
    opt.zero_grad()
    logits = model(X)
    loss   = crit(logits, y)
    loss.backward()
    opt.step()
    acc = (logits.argmax(1) == y).float().mean().item()
    if epoch % 5 == 0 or epoch == 19:
        print(f"  Epoch {epoch+1:>2}: loss={loss.item():.4f}  acc={acc:.4f}")

print("\nGradientes finales:")
for name, p in model.named_parameters():
    if p.grad is not None:
        status = '✓' if p.grad.norm() > 0 else '✗ MUERTO'
        print(f"  {name:45s}: {p.grad.norm():.6f}  {status}")

print()
if acc > 0.70:
    print("✓ SOLUCIÓN FUNCIONA — correr train_pipeline.py")
else:
    print(f"✗ Sigue sin aprender (acc={acc:.4f})")
    print("  → El entorno no soporta BiLSTM. Usar Dense como modelo principal.")
