import { useState } from "react";
import "./App.css";
import ChampionSlot from "./components/ChampionSlot";
import StrategyPanel from "./components/StrategyPanel";
import Minimap from "./components/Minimap";

const LANES = ["Top", "Jungle", "Mid", "ADC", "Support"];

const emptyChamp = () => ({ name: "", icon: null, iconFile: null });
const emptyTeam = () => LANES.map(() => emptyChamp());

async function analyzeWithAI(blueTeam, redTeam) {
  const apiUrl = import.meta.env.VITE_API_URL || "";
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY || "";

  const blueNames = blueTeam
    .map((c, i) => `${LANES[i]}: ${c.name || "Desconocido"}`)
    .join(", ");
  const redNames = redTeam
    .map((c, i) => `${LANES[i]}: ${c.name || "Desconocido"}`)
    .join(", ");

  const prompt = `
Eres un analista experto en League of Legends.

Equipo Aliado: ${blueNames}
Equipo Enemigo: ${redNames}

Analiza la composición enemiga y genera una estrategia detallada para vencer a este equipo.
Responde en el siguiente formato exacto:

Composición: [tipo de composición enemiga]
Early: [qué hacer en early game]
Mid: [qué hacer en mid game]
Late: [qué hacer en late game]
Win Condition: [condición principal de victoria]
`.trim();

  // OPCIÓN A: Anthropic directo
  if (apiKey) {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 600,
        messages: [{ role: "user", content: prompt }],
      }),
    });
    const data = await response.json();
    return data.content[0].text;
  }

  // OPCIÓN B: Tu backend propio
  if (apiUrl) {
    const response = await fetch(`${apiUrl}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ blueTeam, redTeam, prompt }),
    });
    const data = await response.json();
    return data.strategy || data.result || JSON.stringify(data);
  }

  // FALLBACK: estrategia de ejemplo sin API
  return `Composición: Teamfight / Control de Área
Early: Priorizar farm y control de visión en los carriles clave.
Mid: Buscar peleas en objetivos como Heraldo y Dragones.
Late: Agruparse y controlar objetivos mayores antes de los Baron fights.
Win Condition: Teamfights 5v5 con control de visión y posicionamiento superior.`;
}

export default function App() {
  const [blueTeam, setBlueTeam] = useState(emptyTeam());
  const [redTeam, setRedTeam]   = useState(emptyTeam());
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  const updateBlue = (index, value) =>
    setBlueTeam((prev) => prev.map((c, i) => (i === index ? value : c)));

  const updateRed = (index, value) =>
    setRedTeam((prev) => prev.map((c, i) => (i === index ? value : c)));

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setStrategy(null);
    try {
      const result = await analyzeWithAI(blueTeam, redTeam);
      setStrategy(result);
    } catch (err) {
      console.error(err);
      setError("Error al conectar con el modelo. Verifica tu API y configuración.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>⚔ LOL SCOUTING AI ⚔</h1>
        <p>Análisis Táctico Mediante Inteligencia Artificial</p>
        <div className="header-divider" />
      </header>

      <main className="main-layout">
        {/* Equipo Aliado */}
        <div className="team-panel">
          <div className="team-label blue">🔵 Tu Equipo</div>
          {LANES.map((lane, i) => (
            <ChampionSlot
              key={`blue-${lane}`}
              lane={lane}
              index={i}
              value={blueTeam[i]}
              onChange={(val) => updateBlue(i, val)}
            />
          ))}
        </div>

        {/* Panel Central */}
        <div className="center-panel">
          <StrategyPanel strategy={strategy} loading={loading} />

          {error && (
            <div style={{
              background: "rgba(192,57,43,0.1)",
              border: "1px solid #c0392b",
              borderRadius: "6px",
              padding: "0.6rem 0.9rem",
              fontSize: "0.8rem",
              color: "#e87c7c",
            }}>
              ⚠ {error}
            </div>
          )}

          <button
            className={`analyze-btn ${loading ? "loading" : ""}`}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "⚙ Analizando..." : "⚔ Analizar Composición"}
          </button>

          <Minimap blueTeam={blueTeam} redTeam={redTeam} strategy={strategy} />
        </div>

        {/* Equipo Rival */}
        <div className="team-panel">
          <div className="team-label red">🔴 Rivales</div>
          {LANES.map((lane, i) => (
            <ChampionSlot
              key={`red-${lane}`}
              lane={lane}
              index={i}
              value={redTeam[i]}
              onChange={(val) => updateRed(i, val)}
            />
          ))}
        </div>
      </main>

      <footer style={{
        textAlign: "center",
        padding: "0.75rem",
        borderTop: "1px solid var(--panel-border)",
        fontSize: "0.65rem",
        color: "var(--text-muted)",
        letterSpacing: "1px",
      }}>
        LOL SCOUTING AI · Proyecto IA · Visión por Computador + PLN
      </footer>
    </div>
  );
}