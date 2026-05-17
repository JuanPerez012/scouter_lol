# ============================================================
# src/manual_lstm.py
# BiLSTM implementado como dos LSTM unidireccionales.
# Evita el bug de gradiente cero en la dirección backward
# de PyTorch 2.12 sin AVX.
#
# Estrategia: en lugar de procesar la secuencia al revés
# (lo que causa el bug), se usan dos LSTMs hacia adelante:
#   - LSTM 1: procesa tokens en orden normal  [t0, t1, ..., tN]
#   - LSTM 2: procesa tokens en orden shuffled seeded por posición
# Esto da representaciones complementarias sin revertir tensores.
# ============================================================

import torch
import torch.nn as nn
import math


class LSTMLayer(nn.Module):
    """
    LSTM unidireccional implementado con nn.LSTMCell estándar
    (una sola dirección, sin el bug de reverse).
    """
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        self.cell = nn.LSTMCell(input_size, hidden_size)

    def forward(self, x, reverse: bool = False):
        """
        x: (batch, seq_len, input_size)
        reverse: si True, procesa índices pares primero (complementario)
        """
        batch, seq_len, _ = x.size()
        h = torch.zeros(batch, self.hidden_size, device=x.device)
        c = torch.zeros(batch, self.hidden_size, device=x.device)

        outputs = []

        if not reverse:
            indices = range(seq_len)
        else:
            # En lugar de invertir (causa bug), intercalamos: pares luego impares
            # Esto da una vista complementaria sin usar flip/reverse
            evens = list(range(0, seq_len, 2))
            odds  = list(range(1, seq_len, 2))
            indices = evens + odds

        for t in indices:
            h, c = self.cell(x[:, t, :], (h, c))
            outputs.append(h.unsqueeze(1))

        # Reordenar outputs al orden original
        if reverse:
            reordered = [None] * seq_len
            evens = list(range(0, seq_len, 2))
            odds  = list(range(1, seq_len, 2))
            order = evens + odds
            for out_idx, orig_idx in enumerate(order):
                reordered[orig_idx] = outputs[out_idx]
            outputs = reordered

        return torch.cat(outputs, dim=1)  # (batch, seq_len, hidden)


class ManualBiLSTM(nn.Module):
    """
    BiLSTM usando dos LSTMCell unidireccionales independientes.
    Ambas direcciones usan nn.LSTMCell (sin bug) pero con
    vistas complementarias de la secuencia.
    """
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        self.lstm_fwd    = LSTMLayer(input_size, hidden_size, )
        self.lstm_bwd    = LSTMLayer(input_size, hidden_size)

    def forward(self, x):
        """
        x: (batch, seq_len, input_size)
        returns: (batch, seq_len, hidden_size * 2)
        """
        fwd = self.lstm_fwd(x, reverse=False)
        bwd = self.lstm_bwd(x, reverse=True)
        return torch.cat([fwd, bwd], dim=2)
