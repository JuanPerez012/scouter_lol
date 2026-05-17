#!/usr/bin/env python3
# ============================================================
# scripts/debug_tokenizer.py
# Diagnóstico completo del tokenizador y el BiLSTM
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import torch

from config.settings import DATA_FILES, NLP
from src.nlp_preprocessing import SimpleTokenizer, pad_sequences, clean_text

# ─── 1. CARGAR DATASET ───────────────────────────────────────
print("="*60)
print("PASO 1 — CARGAR DATASET")
print("="*60)
df = pd.read_csv(DATA_FILES["scouting_nlp"])
print(f"Shape: {df.shape}")

sample_text = df["texto_entrada_nlp"].iloc[0]
print(f"\nTexto original (primeros 300 chars):\n{sample_text[:300]}")

# ─── 2. LIMPIEZA ─────────────────────────────────────────────
print("\n" + "="*60)
print("PASO 2 — LIMPIEZA")
print("="*60)
clean = clean_text(sample_text)
print(f"Texto limpio (primeros 300 chars):\n{clean[:300]}")

# ─── 3. TOKENIZADOR ──────────────────────────────────────────
print("\n" + "="*60)
print("PASO 3 — TOKENIZADOR")
print("="*60)

X = df["texto_entrada_nlp"].apply(clean_text)

tok = SimpleTokenizer(num_words=NLP["tokenizer_vocab"], oov_token="<OOV>")
tok.fit_on_texts(X)

print(f"\nVocabulario total construido: {len(tok.word_index)}")
print(f"Max índice en word_index:    {max(tok.word_index.values())}")
print(f"Primeras 30 palabras del vocab:")
sorted_vocab = sorted(tok.word_index.items(), key=lambda x: x[1])
for word, idx in sorted_vocab[:30]:
    print(f"  [{idx:5d}] {word}")

# ─── 4. SECUENCIAS ───────────────────────────────────────────
print("\n" + "="*60)
print("PASO 4 — SECUENCIAS DEL TEXTO DE MUESTRA")
print("="*60)

seq = tok.texts_to_sequences([clean])[0]
print(f"Longitud de la secuencia: {len(seq)}")
print(f"Primeros 20 índices: {seq[:20]}")

# Cuántos son OOV (índice 1)
oov_count = seq.count(1)
oov_pct   = oov_count / len(seq) * 100 if seq else 0
print(f"\nTokens OOV en esta muestra: {oov_count}/{len(seq)} ({oov_pct:.1f}%)")

# ─── 5. OOV GLOBAL ───────────────────────────────────────────
print("\n" + "="*60)
print("PASO 5 — OOV GLOBAL EN TODO EL DATASET")
print("="*60)

all_seqs   = tok.texts_to_sequences(X)
total_tok  = sum(len(s) for s in all_seqs)
total_oov  = sum(s.count(1) for s in all_seqs)
oov_global = total_oov / total_tok * 100 if total_tok else 0

print(f"Total tokens procesados: {total_tok}")
print(f"Tokens OOV:              {total_oov} ({oov_global:.1f}%)")
print()
if oov_global > 20:
    print("⚠ OOV > 20%: el tokenizador NO está capturando bien el vocabulario.")
    print("  Esto explica la baja precisión del BiLSTM.")
else:
    print("✓ OOV < 20%: el tokenizador está funcionando correctamente.")

# ─── 6. PALABRAS QUE SE PIERDEN ──────────────────────────────
print("\n" + "="*60)
print("PASO 6 — PALABRAS FUERA DE VOCABULARIO")
print("="*60)

import re
def _tokenize_raw(text):
    text = str(text).lower()
    text = re.sub(r"[^a-záéíóúüñà-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return [t for t in text.split() if t]

all_words  = []
for text in X:
    all_words.extend(_tokenize_raw(text))

from collections import Counter
word_freq  = Counter(all_words)
oov_words  = {w: c for w, c in word_freq.items() if w not in tok.word_index}
print(f"Palabras únicas totales:       {len(word_freq)}")
print(f"Palabras en vocabulario:       {len(tok.word_index)}")
print(f"Palabras fuera de vocabulario: {len(oov_words)}")

if oov_words:
    print(f"\nTop-20 palabras OOV más frecuentes:")
    for w, c in sorted(oov_words.items(), key=lambda x: -x[1])[:20]:
        print(f"  {w:30s}: {c} veces")

# ─── 7. PADDING ──────────────────────────────────────────────
print("\n" + "="*60)
print("PASO 7 — PADDING Y SECUENCIAS VACÍAS")
print("="*60)

padded = pad_sequences(all_seqs[:10], maxlen=NLP["max_sequence_length"])
print(f"Shape padded (primeras 10): {padded.shape}")
print(f"Max índice en padded: {padded.max()}")
print(f"Secuencias completamente cero (solo padding): "
      f"{sum(1 for row in padded if row.max() == 0)}")

# ─── 8. COMPATIBILIDAD CON EMBEDDING ─────────────────────────
print("\n" + "="*60)
print("PASO 8 — COMPATIBILIDAD CON EMBEDDING DE PYTORCH")
print("="*60)

vocab_size = NLP["tokenizer_vocab"]
max_idx_found = padded.max()
print(f"Vocab configurado (num_words): {vocab_size}")
print(f"Max índice encontrado en secuencias: {max_idx_found}")

if max_idx_found >= vocab_size:
    print(f"⚠ PROBLEMA: índice {max_idx_found} >= vocab_size {vocab_size}")
    print("  Esto causa errores silenciosos en el Embedding de PyTorch.")
else:
    print(f"✓ Todos los índices dentro del rango [0, {vocab_size-1}]")

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETO")
print("="*60)
print(f"Vocabulario real del dataset:  {len(word_freq)}")
print(f"Vocabulario capturado:         {len(tok.word_index)}")
print(f"OOV global:                    {oov_global:.1f}%")
print(f"Max índice vs vocab_size:      {max_idx_found} vs {vocab_size}")
