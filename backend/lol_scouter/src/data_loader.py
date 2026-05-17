# ============================================================
# src/data_loader.py
# Carga y corrección del ecosistema de datos
# ============================================================

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DATA_FILES


# ─── DICCIONARIO DE CLASES MANUALES ──────────────────────────
CLASS_FIX = {
    # Mids / magos / asesinos
    "Ahri": "mage",       "Orianna": "mage",     "Syndra": "mage",
    "Viktor": "mage",     "Azir": "mage",         "Lux": "mage",
    "Annie": "mage",      "Taliyah": "mage",      "LeBlanc": "assassin",
    "Zed": "assassin",    "Akali": "assassin",    "Fizz": "assassin",
    "Katarina": "assassin","Qiyana": "assassin",  "Yasuo": "fighter",
    "Yone": "fighter",    "Sylas": "mage",        "Karma": "mage",
    "Hwei": "mage",       "Vex": "mage",          "Zoe": "mage",
    "Xerath": "mage",     "VelKoz": "mage",       "Veigar": "mage",
    "Malzahar": "mage",   "Cassiopeia": "mage",   "Ryze": "mage",
    "Vladimir": "mage",   "Aurora": "mage",       "Mel": "mage",
    # ADC / tiradores
    "Jinx": "marksman",   "KaiSa": "marksman",    "Caitlyn": "marksman",
    "Ashe": "marksman",   "Ezreal": "marksman",   "Lucian": "marksman",
    "Draven": "marksman", "Aphelios": "marksman", "Xayah": "marksman",
    "Zeri": "marksman",   "Varus": "marksman",    "Vayne": "marksman",
    "Tristana": "marksman","Sivir": "marksman",   "Kalista": "marksman",
    "Jhin": "marksman",   "MissFortune": "marksman","Twitch": "marksman",
    "KogMaw": "marksman", "Smolder": "marksman",  "Samira": "marksman",
    "Nilah": "marksman",
    # Supports
    "Thresh": "support",  "Nautilus": "tank",     "Leona": "tank",
    "Rakan": "support",   "Lulu": "support",      "Milio": "support",
    "Nami": "support",    "Janna": "support",     "Soraka": "support",
    "Yuumi": "support",   "Sona": "support",      "RenataGlasc": "support",
    "Braum": "tank",      "Alistar": "tank",      "Rell": "tank",
    "Blitzcrank": "tank", "Pyke": "assassin",     "Morgana": "mage",
    "Bard": "support",    "Zilean": "support",    "Taric": "support",
    # Junglas
    "LeeSin": "fighter",  "Vi": "fighter",        "JarvanIV": "fighter",
    "Sejuani": "tank",    "Maokai": "tank",       "Poppy": "tank",
    "Nidalee": "mage",    "Elise": "mage",        "Graves": "marksman",
    "Kindred": "marksman","KhaZix": "assassin",   "Rengar": "assassin",
    "Evelynn": "assassin","Ekko": "assassin",     "Nocturne": "assassin",
    "Viego": "fighter",   "Kayn": "fighter",      "Hecarim": "fighter",
    "Lillia": "mage",     "Karthus": "mage",      "Fiddlesticks": "mage",
    "Warwick": "fighter", "XinZhao": "fighter",   "Wukong": "fighter",
    # Top
    "Aatrox": "fighter",  "Camille": "fighter",   "Fiora": "fighter",
    "Jax": "fighter",     "Renekton": "fighter",  "Riven": "fighter",
    "Darius": "fighter",  "Garen": "fighter",     "Sett": "fighter",
    "Irelia": "fighter",  "Gwen": "fighter",      "Kled": "fighter",
    "Olaf": "fighter",    "Tryndamere": "fighter","Yorick": "fighter",
    "Nasus": "fighter",   "Mordekaiser": "fighter","Jayce": "fighter",
    "Gnar": "fighter",    "Kennen": "mage",       "Rumble": "mage",
    "Malphite": "tank",   "Ornn": "tank",         "Sion": "tank",
    "DrMundo": "tank",    "KSante": "tank",       "Shen": "tank",
    "TahmKench": "tank",  "Singed": "tank",       "Urgot": "fighter",
    "Quinn": "marksman",  "Teemo": "marksman",    "Kayle": "fighter",
    "Ambessa": "fighter",
}


def _validate_class_by_role(row: pd.Series) -> str:
    """Regla de seguridad por rol cuando el campeón no está en CLASS_FIX."""
    champion    = row["champion"]
    role        = row["primary_role"]
    curr_class  = row["champion_class"]

    if champion in CLASS_FIX:
        return CLASS_FIX[champion]
    if role == "ADC":
        return "marksman"
    if role == "Support" and curr_class not in ["support", "tank", "mage", "assassin"]:
        return "support"
    if role == "Mid" and curr_class == "support":
        return "mage"
    if role in ("Top", "Jungle") and curr_class == "support":
        return "fighter"
    return curr_class


def fix_champion_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el diccionario manual + reglas por rol a Champion_KB."""
    df = df.copy()
    df["champion_class"] = df.apply(
        lambda row: CLASS_FIX.get(row["champion"], row["champion_class"]),
        axis=1,
    )
    df["champion_class"] = df.apply(_validate_class_by_role, axis=1)
    return df


def load_all_tables() -> dict:
    """
    Carga todas las tablas del ecosistema de datos.
    Retorna un diccionario con DataFrames listos para usar.
    """
    tables = {}

    for key, path in DATA_FILES.items():
        if not os.path.exists(path):
            print(f"[WARN] Archivo no encontrado: {path}")
            tables[key] = pd.DataFrame()
            continue
        tables[key] = pd.read_csv(path)

    # Aplicar corrección de clases sobre Champion_KB base
    if not tables["champion_kb"].empty:
        tables["champion_kb"] = fix_champion_classes(tables["champion_kb"])

    print("✓ Todas las tablas fueron cargadas correctamente.")
    return tables


def summary_table(tables: dict) -> pd.DataFrame:
    """Devuelve un resumen de dimensiones del ecosistema de datos."""
    rows = []
    for key, df in tables.items():
        rows.append({
            "Tabla":    key,
            "Filas":    df.shape[0],
            "Columnas": df.shape[1],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    tables = load_all_tables()
    print(summary_table(tables).to_string(index=False))
