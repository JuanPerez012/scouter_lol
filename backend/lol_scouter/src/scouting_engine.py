# ============================================================
# src/scouting_engine.py
# Motor principal de scouting competitivo
# ============================================================
#
# Integra:
#   - Análisis individual de matchups (1v1 narrativo)
#   - Análisis macro de composición 5v5
#   - Predicción de estrategia con BiLSTM
#   - Top-N estrategias con confianza
#   - Narrativa híbrida y explicación taxonómica
#   - Reporte final completo
#
# ============================================================

import numpy as np
import pandas as pd
from src.nlp_preprocessing import pad_sequences

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import NLP
from src.nlp_preprocessing import clean_text


# ─── DESCRIPCIONES TÁCTICAS ───────────────────────────────────

PLAYSTYLE_DESCRIPTIONS = {
    "poke":              "desgaste constante y control de espacio",
    "engage":            "iniciación y peleas grupales",
    "splitpush":         "presión lateral y presión sobre side lane",
    "hypercarry":        "escalado y daño sostenido en peleas largas",
    "control mage":      "control de zonas y teamfights organizadas",
    "pick composition":  "pickoffs y castigo sobre enemigos aislados",
    "early gank":        "presión temprana y movilidad sobre líneas",
    "scaling":           "escalado tardío y control progresivo del mapa",
    "front-to-back":     "peleas organizadas alrededor de frontline",
    "teamfight":         "peleas grupales coordinadas",
    "dive":              "acceso agresivo hacia carries vulnerables",
    "utility":           "protección y utilidad para el equipo",
}

WEAKNESS_DESCRIPTIONS = {
    "low":    "dependencia de generar ventajas durante early game",
    "medium": "necesidad de mantener buena ejecución táctica",
    "high":   "early game vulnerable antes del escalado",
}

LANES = ["Top", "Jungle", "Mid", "ADC", "Support"]


# ─── CONSULTA DE CAMPEÓN ──────────────────────────────────────

def get_champion_info(champion_kb: pd.DataFrame, champion_name: str):
    """Retorna la fila de un campeón en Champion_KB o None si no existe."""
    result = champion_kb[champion_kb["champion"] == champion_name]
    if result.empty:
        return None
    return result.iloc[0]


# ─── MATCHUP NARRATIVO 1V1 ────────────────────────────────────

def analyze_matchup(
    champion_kb: pd.DataFrame,
    lane: str,
    ally_champion: str,
    enemy_champion: str,
) -> str:
    """Genera un análisis narrativo del enfrentamiento en una línea."""

    ally  = get_champion_info(champion_kb, ally_champion)
    enemy = get_champion_info(champion_kb, enemy_champion)

    if ally is None or enemy is None:
        missing = ally_champion if ally is None else enemy_champion
        return f"[WARN] No se encontró información para: {missing}"

    ally_strength  = PLAYSTYLE_DESCRIPTIONS.get(ally["main_playstyle"],  ally["main_playstyle"])
    enemy_strength = PLAYSTYLE_DESCRIPTIONS.get(enemy["main_playstyle"], enemy["main_playstyle"])
    ally_weakness  = WEAKNESS_DESCRIPTIONS.get(ally["scaling_level"],    ally["scaling_level"])

    text = (
        f"\nEn la línea de {lane},\n"
        f"{ally_champion} destaca por\n"
        f"{ally_strength}.\n\n"
        f"Sin embargo,\n"
        f"{ally_weakness}\n"
        f"puede generar dificultades\n"
        f"si el rival logra controlar correctamente\n"
        f"el ritmo de la partida.\n\n"
        f"Por otro lado,\n"
        f"{enemy_champion} sobresale por\n"
        f"{enemy_strength},\n"
        f"lo que puede influir directamente\n"
        f"en el desarrollo del enfrentamiento.\n"
    )

    if ally["scaling_level"] == "high":
        text += (
            f"\nDebido a esta diferencia de escalado,\n"
            f"{ally_champion} necesita administrar correctamente\n"
            f"los primeros minutos de la partida\n"
            f"y priorizar recursos antes de buscar\n"
            f"peleas completamente extendidas.\n"
        )
    elif enemy["engage_score"] > ally["peel_score"]:
        text += (
            f"\nEl matchup exigirá especial cuidado\n"
            f"con visión lateral y posicionamiento,\n"
            f"ya que {enemy_champion}\n"
            f"posee herramientas suficientes\n"
            f"para castigar errores de ubicación.\n"
        )
    else:
        text += (
            "\nEl enfrentamiento dependerá principalmente\n"
            "de control de visión,\n"
            "administración de recursos\n"
            "y coordinación con el equipo.\n"
        )

    return text


# ─── SCOUTING 5V5 ─────────────────────────────────────────────

def generate_team_scouting(
    champion_kb: pd.DataFrame,
    ally_team: list,
    enemy_team: list,
) -> str:
    """Genera el reporte de matchups para las 5 líneas."""
    report  = "\n" + "=" * 60
    report += "\nSCOUTING CONTEXTUAL EXPLICATIVO\n"
    report += "=" * 60 + "\n\n"

    for lane, ally, enemy in zip(LANES, ally_team, enemy_team):
        report += analyze_matchup(champion_kb, lane, ally, enemy)
        report += "\n\n"

    return report


# ─── ANÁLISIS MACRO DE COMPOSICIÓN ───────────────────────────

def analyze_team_macro(
    champion_kb: pd.DataFrame,
    ally_team: list,
    enemy_team: list,
) -> str:
    """Genera análisis macro narrativo de la composición completa."""

    ally_data  = champion_kb[champion_kb["champion"].isin(ally_team)]
    enemy_data = champion_kb[champion_kb["champion"].isin(enemy_team)]

    ally_engage    = ally_data["engage_score"].mean()
    ally_peel      = ally_data["peel_score"].mean()
    ally_cc        = ally_data["cc_score"].mean()
    enemy_engage   = enemy_data["engage_score"].mean()

    scaling_count  = ally_data[ally_data["scaling_level"] == "high"].shape[0]
    frontline_count = ally_data[
        ally_data["champion_class"].isin(["tank", "fighter"])
    ].shape[0]

    report  = "\n" + "=" * 60
    report += "\nANÁLISIS GLOBAL DE COMPOSICIÓN\n"
    report += "=" * 60 + "\n\n"

    if frontline_count >= 2:
        report += (
            "La composición aliada tiene herramientas "
            "suficientes para jugar peleas organizadas "
            "alrededor de objetivos, principalmente "
            "gracias a la frontline disponible.\n\n"
        )
    else:
        report += (
            "La composición aliada posee una frontline "
            "limitada, por lo que el posicionamiento "
            "y la visión previa serán fundamentales.\n\n"
        )

    if scaling_count >= 2:
        report += (
            "Además, el draft escala correctamente "
            "hacia mid-late game, permitiendo "
            "mantener daño constante en peleas largas.\n\n"
        )
    else:
        report += (
            "Sin embargo, el equipo necesita generar "
            "ventajas antes del late game, ya que "
            "el escalado no es su punto más fuerte.\n\n"
        )

    if ally_peel >= 5:
        report += (
            "La composición también posee herramientas "
            "de peel suficientes para proteger carries "
            "durante teamfights importantes.\n\n"
        )
    else:
        report += (
            "Los carries podrían quedar expuestos "
            "frente a composiciones de acceso rápido "
            "o dive agresivo.\n\n"
        )

    if enemy_engage > ally_engage:
        report += (
            "El rival presenta amenazas fuertes "
            "de engage y presión directa, por lo que "
            "será importante controlar flancos "
            "y evitar peleas desordenadas.\n\n"
        )
    else:
        report += (
            "El equipo aliado posee mejores herramientas "
            "para iniciar peleas y controlar el ritmo "
            "de los enfrentamientos.\n\n"
        )

    if ally_cc >= 5:
        report += (
            "El control de masas disponible permite "
            "pelear mejor alrededor de dragones, Nashor "
            "y zonas cerradas del mapa.\n\n"
        )

    report += (
        "La prioridad macro debería centrarse en "
        "visión profunda, preparación de objetivos "
        "y administración correcta del tempo "
        "antes de las peleas importantes."
    )

    return report


# ─── GENERACIÓN DE TEXTO PARA IA ─────────────────────────────

def build_prediction_text(
    champion_kb: pd.DataFrame,
    ally_team: list,
    enemy_team: list,
) -> str:
    """
    Construye el texto descriptivo contextualizado que el modelo BiLSTM
    usará para predecir la estrategia competitiva.
    """
    ally_data  = champion_kb[champion_kb["champion"].isin(ally_team)]
    enemy_data = champion_kb[champion_kb["champion"].isin(enemy_team)]

    ally_engage    = ally_data["engage_score"].mean()
    ally_peel      = ally_data["peel_score"].mean()
    ally_cc        = ally_data["cc_score"].mean()
    ally_obj       = ally_data["objective_control_score"].mean()
    enemy_engage   = enemy_data["engage_score"].mean()
    enemy_mobility = enemy_data["mobility_score"].mean()

    high_scaling = ally_data[
        ally_data["scaling_level"] == "high"
    ]["champion"].tolist()

    marksmen = ally_data[
        ally_data["champion_class"] == "marksman"
    ]["champion"].tolist()

    frontline = ally_data[
        ally_data["champion_class"].isin(["tank", "fighter"])
    ]["champion"].tolist()

    frontline_str = ", ".join(frontline) if frontline else "poca frontline"
    marksmen_str  = ", ".join(marksmen)  if marksmen  else "los carries principales"

    text = (
        f"La composición aliada está formada por\n"
        f"{', '.join(ally_team)}.\n\n"
        f"El equipo rival presenta\n"
        f"{', '.join(enemy_team)}.\n\n"
        f"La composición aliada cuenta con\n"
        f"{frontline_str}\n"
        f"como estructura frontal para absorber presión.\n\n"
        f"Además,\n"
        f"{marksmen_str}\n"
        f"representan la fuente principal de daño sostenido.\n\n"
        f"El equipo aliado posee un promedio de engage de\n"
        f"{ally_engage:.1f},\n"
        f"un peel promedio de\n"
        f"{ally_peel:.1f},\n"
        f"control de masas de\n"
        f"{ally_cc:.1f}\n"
        f"y control de objetivos de\n"
        f"{ally_obj:.1f}.\n\n"
        f"El rival posee engage promedio de\n"
        f"{enemy_engage:.1f}\n"
        f"y movilidad promedio de\n"
        f"{enemy_mobility:.1f}.\n\n"
        f"La lectura táctica indica que el equipo aliado\n"
        f"debe jugar alrededor de peleas organizadas,\n"
        f"protección de carries,\n"
        f"visión previa y control de objetivos neutrales.\n\n"
        f"Si el rival encuentra flancos o entradas directas,\n"
        f"la backline aliada puede quedar expuesta,\n"
        f"por lo que será importante mantener formación,\n"
        f"controlar zonas cerradas y evitar peleas desordenadas.\n"
    )

    if high_scaling:
        text += (
            f"\nLa presencia de {', '.join(high_scaling)}\n"
            f"indica que la composición gana valor\n"
            f"cuando la partida avanza hacia mid-late game.\n"
        )

    return text


# ─── PREDICCIÓN CON BILSTM ────────────────────────────────────

def predict_top_strategies(
    model,
    tokenizer,
    label_encoder,
    champion_kb: pd.DataFrame,
    ally_team: list,
    enemy_team: list,
    top_n: int = 3,
) -> list:
    """
    Retorna las top-N estrategias predichas con sus probabilidades.

    Retorna:
        lista de tuplas (strategy_name, confidence_float)
    """
    text_input = build_prediction_text(champion_kb, ally_team, enemy_team)
    text_clean = clean_text(text_input)

    sequence = tokenizer.texts_to_sequences([text_clean])
    padded   = pad_sequences(
        sequence,
        maxlen=NLP["max_sequence_length"],
        padding="post",
    )

    import torch
    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor(padded, dtype=torch.long))
    import torch.nn.functional as F
    prediction = F.softmax(logits, dim=1).squeeze(0).numpy()

    top_indices = np.argsort(prediction)[::-1][:top_n]

    return [
        (label_encoder.inverse_transform([idx])[0], float(prediction[idx]))
        for idx in top_indices
    ]


# ─── NARRATIVA HÍBRIDA ────────────────────────────────────────

def build_hybrid_strategy_report(top_predictions: list) -> str:
    """
    Genera narrativa estratégica a partir del top-3 de predicciones.
    """
    primary   = top_predictions[0]
    secondary = top_predictions[1]
    tertiary  = top_predictions[2]

    return (
        f"La composición presenta principalmente\n"
        f"una identidad estratégica de tipo\n"
        f"{primary[0]},\n\n"
        f"con una probabilidad aproximada de\n"
        f"{primary[1]:.2f}.\n\n"
        f"Sin embargo,\n"
        f"también incorpora elementos tácticos\n"
        f"relacionados con:\n\n"
        f"- {secondary[0]} ({secondary[1]:.2f})\n"
        f"- {tertiary[0]} ({tertiary[1]:.2f})\n\n"
        f"Esto indica que el draft no depende\n"
        f"de una única condición de victoria,\n"
        f"sino de múltiples capas estratégicas\n"
        f"que pueden variar según el contexto\n"
        f"de la partida.\n\n"
        f"En términos competitivos,\n"
        f"la composición puede alternar entre\n"
        f"peleas grupales coordinadas,\n"
        f"control estructurado de objetivos\n"
        f"y escalado progresivo hacia mid-late game.\n"
    )


# ─── EXPLICACIÓN TAXONÓMICA ───────────────────────────────────

def build_strategy_explanation(taxonomy_df: pd.DataFrame, strategy_name: str) -> str:
    """
    Genera explicación detallada de una estrategia usando la tabla Taxonomy.
    """
    result = taxonomy_df[taxonomy_df["strategy_label"] == strategy_name]

    if result.empty:
        return f"No existe información estratégica para: {strategy_name}"

    info = result.iloc[0]

    return (
        f"La composición detectada corresponde a\n"
        f"una estrategia de tipo\n"
        f"{info['strategy_label']}.\n\n"
        f"Este tipo de draft se caracteriza por:\n\n"
        f"{info['definition']}\n\n"
        f"Normalmente,\n"
        f"su punto fuerte aparece durante la fase:\n\n"
        f"{info['main_phase']}.\n\n"
        f"Algunos campeones representativos\n"
        f"de este estilo son:\n\n"
        f"{info['example_champions']}.\n\n"
        f"Sin embargo,\n"
        f"el principal riesgo táctico consiste en:\n\n"
        f"{info['main_risk']}\n"
    )


# ─── REPORTE FINAL ────────────────────────────────────────────

def generate_final_scouting_report(
    champion_kb: pd.DataFrame,
    taxonomy_df: pd.DataFrame,
    model,
    tokenizer,
    label_encoder,
    ally_team: list,
    enemy_team: list,
) -> str:
    """
    Genera el reporte completo de scouting competitivo:
      1. Matchups línea a línea
      2. Análisis macro de composición
      3. Identidad estratégica híbrida (top-3 IA)
      4. Explicación taxonómica de la estrategia principal
    """
    matchup_report = generate_team_scouting(champion_kb, ally_team, enemy_team)
    macro_report   = analyze_team_macro(champion_kb, ally_team, enemy_team)

    top_predictions = predict_top_strategies(
        model, tokenizer, label_encoder,
        champion_kb, ally_team, enemy_team,
    )

    hybrid_report   = build_hybrid_strategy_report(top_predictions)
    primary_strategy = top_predictions[0][0]
    strategy_report  = build_strategy_explanation(taxonomy_df, primary_strategy)

    sep = "=" * 70
    sep2 = "=" * 60

    report  = f"\n{sep}\nSCOUTING ESTRATÉGICO COMPLETO\n{sep}\n\n"
    report += matchup_report + "\n\n"
    report += macro_report   + "\n\n"

    report += f"{sep2}\nIDENTIDAD ESTRATÉGICA HÍBRIDA\n{sep2}\n\n"
    report += hybrid_report  + "\n\n"

    report += f"{sep2}\nEXPLICACIÓN TÁCTICA PRINCIPAL\n{sep2}\n\n"
    report += strategy_report + "\n\n"

    report += f"Confianza principal del modelo: {top_predictions[0][1]:.2f}\n"

    return report
