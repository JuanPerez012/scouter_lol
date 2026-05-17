# ============================================================
# src/nlp_preprocessing.py
# Preprocesamiento NLP, TF-IDF y tokenización — sin TensorFlow
# ============================================================

import re
import pickle
import numpy as np
import pandas as pd
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import NLP, MODEL_FILES


# ─── LIMPIEZA DE TEXTO ────────────────────────────────────────

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ─── SPLIT Y ENCODING ─────────────────────────────────────────

def encode_and_split(df: pd.DataFrame):
    X = df["texto_entrada_nlp"]
    y = df["strategy_label"]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=NLP["test_size"],
        random_state=NLP["random_state"],
        stratify=y_encoded,
    )

    X_train_clean = X_train.apply(clean_text)
    X_test_clean  = X_test.apply(clean_text)

    print(f"✓ Entrenamiento: {len(X_train)} muestras")
    print(f"✓ Prueba:        {len(X_test)} muestras")
    print(f"✓ Clases: {list(label_encoder.classes_)}")

    return X_train_clean, X_test_clean, y_train, y_test, label_encoder


# ─── TF-IDF ───────────────────────────────────────────────────

def build_tfidf(X_train_clean, X_test_clean):
    vectorizer = TfidfVectorizer(
        max_features=NLP["tfidf_max_features"],
        ngram_range=NLP["tfidf_ngram_range"],
    )
    X_train_tfidf = vectorizer.fit_transform(X_train_clean)
    X_test_tfidf  = vectorizer.transform(X_test_clean)

    print(f"✓ TF-IDF train: {X_train_tfidf.shape}")
    print(f"✓ TF-IDF test:  {X_test_tfidf.shape}")
    return X_train_tfidf, X_test_tfidf, vectorizer


# ─── TOKENIZADOR (replica exacta del Tokenizer de Keras) ─────
#
# El Tokenizer de Keras tokeniza así:
#   - convierte a minúsculas
#   - separa puntuación con espacios
#   - luego split por espacios
#   - índice 0 = padding (reservado)
#   - índice 1 = <OOV>
#   - índices 2..N = vocabulario por frecuencia
#
# El SimpleTokenizer anterior solo hacía .split() y perdía
# toda la puntuación como parte de tokens, reduciendo el
# vocabulario de ~4500 a solo 953 palabras.

class SimpleTokenizer:
    def __init__(self, num_words: int = 12000, oov_token: str = "<OOV>"):
        self.num_words  = num_words
        self.oov_token  = oov_token
        self.word_index = {}
        self._oov_idx   = 1

    def _tokenize(self, text: str) -> list:
        """
        Replica el tokenizador interno de Keras:
        - minúsculas
        - separar puntuación con espacios
        - split por espacios
        - filtrar tokens vacíos
        """
        text = str(text).lower()
        # Separar puntuación igual que Keras
        text = re.sub(r"[^a-záéíóúüñà-ÿ0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return [t for t in text.split() if t]

    def fit_on_texts(self, texts):
        counter = Counter()
        for text in texts:
            counter.update(self._tokenize(text))

        # 0=padding, 1=OOV, 2..N=vocabulario
        self.word_index = {self.oov_token: self._oov_idx}
        for idx, (word, _) in enumerate(
            counter.most_common(self.num_words - 2), start=2
        ):
            self.word_index[word] = idx

        actual_vocab = len(self.word_index)
        max_idx = max(self.word_index.values())
        print(f"✓ Vocabulario construido: {actual_vocab} tokens "
              f"(max índice: {max_idx})")

    def texts_to_sequences(self, texts):
        oov = self._oov_idx
        return [
            [self.word_index.get(w, oov) for w in self._tokenize(t)]
            for t in texts
        ]


def pad_sequences(sequences, maxlen: int, padding: str = "post") -> np.ndarray:
    """Equivalente a keras.preprocessing.sequence.pad_sequences."""
    result = np.zeros((len(sequences), maxlen), dtype=np.int64)
    for i, seq in enumerate(sequences):
        seq = seq[:maxlen]
        if padding == "post":
            result[i, :len(seq)] = seq
        else:
            result[i, maxlen - len(seq):] = seq
    return result


def build_sequences(X_train_clean, X_test_clean):
    tokenizer = SimpleTokenizer(
        num_words=NLP["tokenizer_vocab"],
        oov_token=NLP["oov_token"],
    )
    tokenizer.fit_on_texts(X_train_clean)

    X_train_seq = tokenizer.texts_to_sequences(X_train_clean)
    X_test_seq  = tokenizer.texts_to_sequences(X_test_clean)

    max_len = NLP["max_sequence_length"]
    X_train_pad = pad_sequences(X_train_seq, maxlen=max_len)
    X_test_pad  = pad_sequences(X_test_seq,  maxlen=max_len)

    print(f"✓ Padding train: {X_train_pad.shape}")
    print(f"✓ Padding test:  {X_test_pad.shape}")
    return X_train_pad, X_test_pad, tokenizer


# ─── SERIALIZACIÓN ────────────────────────────────────────────

def save_preprocessors(label_encoder, tokenizer, tfidf_vectorizer):
    os.makedirs(os.path.dirname(MODEL_FILES["tokenizer"]), exist_ok=True)
    with open(MODEL_FILES["tokenizer"],     "wb") as f: pickle.dump(tokenizer,        f)
    with open(MODEL_FILES["label_encoder"], "wb") as f: pickle.dump(label_encoder,    f)
    with open(MODEL_FILES["tfidf"],         "wb") as f: pickle.dump(tfidf_vectorizer, f)
    print("✓ Preprocesadores guardados.")


def load_preprocessors():
    with open(MODEL_FILES["tokenizer"],     "rb") as f: tokenizer        = pickle.load(f)
    with open(MODEL_FILES["label_encoder"], "rb") as f: label_encoder    = pickle.load(f)
    with open(MODEL_FILES["tfidf"],         "rb") as f: tfidf_vectorizer = pickle.load(f)
    return label_encoder, tokenizer, tfidf_vectorizer
