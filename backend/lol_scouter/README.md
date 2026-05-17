# 🎮 LoL Scouter — Sistema de Scouting Inteligente para League of Legends

Sistema de análisis estratégico competitivo basado en NLP, entrenado sobre un dataset de scouting de 5.000 partidas contextualizadas. Combina procesamiento de lenguaje natural clásico (TF-IDF + n-grams) con arquitecturas secuenciales avanzadas (BiLSTM) para clasificar estrategias competitivas y generar reportes tácticos completos.

---

## 📁 Estructura del Proyecto

```
lol_scouter/
│
├── config/
│   ├── __init__.py
│   └── settings.py              ← Rutas, hiperparámetros y configuración central
│
├── data/                        ← Archivos CSV del ecosistema de datos (colocar aquí)
│   ├── Champion_KB.csv
│   ├── Champion_KB_corrected.csv  (generado automáticamente)
│   ├── Counters.csv
│   ├── Flex_Picks.csv
│   ├── Competitive_Comps.csv
│   ├── Temporal_Context.csv
│   ├── Taxonomy.csv
│   ├── Champion_Synergies.csv
│   ├── Objective_Priority.csv
│   ├── Draft_Tags.csv
│   └── Scouting_5000_V3.csv
│
├── logs/                        ← Reportes, gráficas y matrices de confusión
│
├── models/                      ← Modelos entrenados y preprocesadores serializados
│   ├── bilstm_model.keras
│   ├── dense_model.keras
│   ├── tokenizer.pkl
│   ├── label_encoder.pkl
│   └── tfidf_vectorizer.pkl
│
├── notebooks/                   ← Notebooks de exploración (opcional)
│
├── scripts/
│   ├── train_pipeline.py        ← Entrenamiento completo (Fases 1–9)
│   └── run_scouting.py          ← Inferencia y generación de reporte
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py           ← Carga y corrección del ecosistema de datos
│   ├── nlp_preprocessing.py     ← Limpieza, TF-IDF, tokenización, serialización
│   ├── model_training.py        ← Arquitecturas Dense y BiLSTM, evaluación
│   └── scouting_engine.py       ← Motor de scouting: matchups, macro, IA, reporte
│
├── requirements.txt
└── README.md
```

---

## ⚡ Puesta en marcha

```bash
# 1. Entrenar (solo la primera vez)
python backend/lol_scouter/scripts/train_pipeline.py

# 2. Generar scouting (editar equipos en el script)
python backend/lol_scouter/backend/scripts/run_scouting.py```

---

## 📂 Datos requeridos

Colocar los siguientes CSV en la carpeta `data/`:

| Archivo                  | Descripción                                       |
|--------------------------|---------------------------------------------------|
| `Champion_KB.csv`        | Base de conocimiento de campeones                 |
| `Counters.csv`           | Relaciones de counter entre campeones             |
| `Flex_Picks.csv`         | Campeones flex y sus variantes de rol             |
| `Competitive_Comps.csv`  | Composiciones competitivas de referencia          |
| `Temporal_Context.csv`   | Contexto meta temporal (parches, buffs, nerfs)    |
| `Taxonomy.csv`           | Taxonomía de estrategias competitivas             |
| `Champion_Synergies.csv` | Sinergias entre campeones                         |
| `Objective_Priority.csv` | Prioridades de objetivos por composición          |
| `Draft_Tags.csv`         | Etiquetas estratégicas del draft                  |
| `Scouting_5000_V3.csv`   | Dataset NLP contextual (5.000 muestras)           |

---

## 🏋️ Entrenamiento

```bash
python scripts/train_pipeline.py
```

El pipeline ejecuta:

1. **Carga del ecosistema** — todas las tablas CSV
2. **Exploración del dataset NLP** — validación de dimensiones y balance de clases
3. **Preprocesamiento** — limpieza textual moderada, LabelEncoder, split 80/20
4. **TF-IDF + n-grams** — vectorización con 7.000 features, bigramas
5. **Modelo Dense baseline** — red densa 256→128→softmax, 10 épocas
6. **Tokenización secuencial** — vocab 12.000, padding 80 tokens
7. **Modelo BiLSTM** — Embedding(128) + BiLSTM(64) + Dense, 12 épocas
8. **Evaluación** — classification report + matrices de confusión
9. **Comparación** — tabla y gráfica accuracy Dense vs BiLSTM

Los modelos y preprocesadores se guardan en `models/`.  
Las gráficas se guardan en `logs/`.

---

## 🔍 Inferencia / Scouting

```bash
python scripts/run_scouting.py
```

Editar los equipos al final de `run_scouting.py` (orden: Top, Jungle, Mid, ADC, Support):

```python
ally_team  = ["Gnar", "Sejuani", "Orianna", "Jinx", "Thresh"]
enemy_team = ["Camille", "LeeSin", "Zed", "KaiSa", "Nautilus"]
```

El reporte final incluye:

- Análisis narrativo de cada matchup (5 líneas)
- Análisis macro de composición (frontline, escalado, peel, engage)
- Identidad estratégica híbrida (top-3 probabilidades del BiLSTM)
- Explicación taxonómica de la estrategia principal
- Confianza del modelo

El reporte también se guarda en `logs/last_scouting_report.txt`.

---

## 🧩 Uso programático

```python
import tensorflow as tf
from src.data_loader import load_all_tables
from src.nlp_preprocessing import load_preprocessors
from src.scouting_engine import generate_final_scouting_report

tables        = load_all_tables()
bilstm_model  = tf.keras.models.load_model("models/bilstm_model.keras")
label_encoder, tokenizer, _ = load_preprocessors()

report = generate_final_scouting_report(
    champion_kb   = tables["champion_kb"],
    taxonomy_df   = tables["taxonomy"],
    model         = bilstm_model,
    tokenizer     = tokenizer,
    label_encoder = label_encoder,
    ally_team     = ["Gnar", "Sejuani", "Orianna", "Jinx", "Thresh"],
    enemy_team    = ["Camille", "LeeSin", "Zed", "KaiSa", "Nautilus"],
)
print(report)
```

---

## 🧠 Arquitectura NLP

```
Texto de scouting
        │
        ▼
  clean_text()        ← minúsculas + colapso de espacios
        │
   ┌────┴────┐
   │         │
TF-IDF    Tokenizer
n-grams   pad_sequences
   │         │
   ▼         ▼
Dense      BiLSTM
baseline   contextual
   │         │
   └────┬────┘
        │
  LabelEncoder
  (strategy_label)
        │
        ▼
  Reporte final
```

---

## 📊 Métricas esperadas

| Modelo       | Accuracy esperado |
|--------------|:-----------------:|
| Dense TF-IDF | ~99–100 %         |
| BiLSTM       | ~95–99 %          |

El modelo Dense converge más rápido gracias a la alta separabilidad del dataset.  
El BiLSTM muestra aprendizaje más progresivo y representa mejor la narrativa contextual competitiva.

---

## 📝 Notas

- `Champion_KB_corrected.csv` se genera automáticamente con la corrección de `champion_class` al cargar datos.
- El preprocesamiento **no elimina vocabulario táctico** (sin stemming ni stop-word removal agresivo) para preservar la complejidad contextual del scouting.
- Ajustar épocas, unidades y vocab en `config/settings.py`.
