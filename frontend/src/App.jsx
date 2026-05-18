import { useState, useCallback } from "react";
import "./App.css";
import ChampionSlot    from "./components/ChampionSlot";
import StrategyPanel   from "./components/StrategyPanel";
import Minimap         from "./components/Minimap";
import NLPReport       from "./components/NLPReport";

// ─── Constantes ───────────────────────────────────────────────
const LANES    = ["Top", "Jungle", "Mid", "ADC", "Support"];
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const emptyChamp = () => ({ name: "", icon: null });
const emptyTeam  = () => LANES.map(() => emptyChamp());

const DEFAULT_POSITIONS = {
  blue: [
    { x: 80,  y: 460 },
    { x: 155, y: 345 },
    { x: 245, y: 280 },
    { x: 185, y: 185 },
    { x: 110, y: 155 },
  ],
  red: [
    { x: 500, y: 140 },
    { x: 415, y: 250 },
    { x: 335, y: 310 },
    { x: 390, y: 400 },
    { x: 470, y: 430 },
  ],
};

// ─── Helpers de API ───────────────────────────────────────────

async function callNLP(allyTeam, enemyTeam) {
  const res = await fetch(`${API_BASE}/api/nlp/scouting/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({
      ally_team:  allyTeam.map(c => c.name || "Desconocido"),
      enemy_team: enemyTeam.map(c => c.name || "Desconocido"),
    }),
  });
  if (!res.ok) throw new Error(`NLP error ${res.status}`);
  return res.json();
}

async function callCVPositions(strategy) {
  const res = await fetch(`${API_BASE}/api/cv/strategy-positions/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ strategy }),
  });
  if (!res.ok) throw new Error(`CV error ${res.status}`);
  return res.json();
}

async function callCVIdentify(positions) {
  // Convertir posiciones SVG [0,600] → normalizadas [0,1]
  const VB = 600;
  const x_positions = positions.blue.map(p => +(p.x / VB).toFixed(4));
  const y_positions = positions.blue.map(p => +(p.y / VB).toFixed(4));

  const res = await fetch(`${API_BASE}/api/cv/identify/`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ x_positions, y_positions }),
  });
  if (!res.ok) throw new Error(`CV identify error ${res.status}`);
  return res.json();
}

// ─── Componente principal ─────────────────────────────────────

export default function App() {
  const [blueTeam,   setBlueTeam]   = useState(emptyTeam());
  const [redTeam,    setRedTeam]    = useState(emptyTeam());
  const [positions,  setPositions]  = useState(DEFAULT_POSITIONS);

  // Estado NLP
  const [nlpResult,  setNlpResult]  = useState(null);
  const [nlpLoading, setNlpLoading] = useState(false);
  const [nlpError,   setNlpError]   = useState(null);

  // Estado CV
  const [cvResult,   setCvResult]   = useState(null);
  const [cvLoading,  setCvLoading]  = useState(false);
  const [cvError,    setCvError]    = useState(null);

  const updateBlue = (i, val) =>
    setBlueTeam(prev => prev.map((c, j) => j === i ? val : c));
  const updateRed = (i, val) =>
    setRedTeam(prev => prev.map((c, j) => j === i ? val : c));

  const updatePosition = useCallback((team, index, pos) => {
    setPositions(prev => ({
      ...prev,
      [team]: prev[team].map((p, i) => i === index ? pos : p),
    }));
  }, []);

  // ── SCOUTING COMPLETO: NLP → CV ───────────────────────────
  const handleFullScouting = async () => {
    setNlpLoading(true);
    setNlpError(null);
    setNlpResult(null);
    setCvResult(null);
    setCvError(null);

    try {
      // 1. Llamar al NLP
      const nlp = await callNLP(blueTeam, redTeam);
      setNlpResult(nlp);

      // 2. Usar la estrategia principal como entrada del CV
      const mainStrategy = nlp.main_strategy;
      if (mainStrategy) {
        setCvLoading(true);
        try {
          const cv = await callCVPositions(mainStrategy);
          // 3. Mover íconos del minimapa según las posiciones del CV
          setPositions({
            blue: cv.blue_positions,
            red:  cv.red_positions,
          });
          setCvResult({ strategy: mainStrategy, source: "nlp" });
        } catch (e) {
          setCvError(`Error CV: ${e.message}`);
        } finally {
          setCvLoading(false);
        }
      }
    } catch (e) {
      setNlpError(`Error NLP: ${e.message}`);
    } finally {
      setNlpLoading(false);
    }
  };

  // ── IDENTIFICAR ESTRATEGIA desde posiciones actuales ──────
  const handleIdentifyStrategy = async () => {
    setCvLoading(true);
    setCvError(null);
    setCvResult(null);
    try {
      const cv = await callCVIdentify(positions);
      setCvResult({ ...cv, source: "identify" });
    } catch (e) {
      setCvError(`Error CV: ${e.message}`);
    } finally {
      setCvLoading(false);
    }
  };

  const isLoading = nlpLoading || cvLoading;

  return (
    <div className="app">
      <header className="header">
        <h1>⚔ LOL SCOUTING AI ⚔</h1>
        <p>Análisis Táctico · NLP + Visión por Computadora</p>
        <div className="header-divider" />
      </header>

      <main className="main-layout">
        {/* Equipo Azul */}
        <div className="team-panel">
          <div className="team-label blue">🔵 Tu Equipo</div>
          {LANES.map((lane, i) => (
            <ChampionSlot key={`b-${lane}`} lane={lane} index={i}
              value={blueTeam[i]} onChange={v => updateBlue(i, v)} team="blue" />
          ))}
        </div>

        {/* Centro */}
        <div className="center-panel">
          <StrategyPanel
            strategy={nlpResult}
            loading={nlpLoading}
            cvResult={cvResult}
            cvLoading={cvLoading}
          />

          {(nlpError || cvError) && (
            <div className="error-box">
              {nlpError && <div>⚠ {nlpError}</div>}
              {cvError  && <div>⚠ {cvError}</div>}
            </div>
          )}

          {/* Botones de acción */}
          <div className="action-buttons">
            <button
              className={`analyze-btn primary${isLoading ? " loading" : ""}`}
              onClick={handleFullScouting}
              disabled={isLoading}
              title="NLP analiza los campeones → CV mueve el minimapa"
            >
              {nlpLoading ? "⚙ Analizando NLP..." :
               cvLoading  ? "🗺 Calculando posiciones..." :
               "⚔ Scouting Completo"}
            </button>

            <button
              className={`analyze-btn secondary${cvLoading ? " loading" : ""}`}
              onClick={handleIdentifyStrategy}
              disabled={isLoading}
              title="CV identifica la estrategia según la posición actual de los íconos"
            >
              {cvLoading ? "🔍 Identificando..." : "🔍 Identificar Estrategia"}
            </button>
          </div>

          {/* Minimapa */}
          <Minimap
            blueTeam={blueTeam}
            redTeam={redTeam}
            positions={positions}
            onMove={updatePosition}
            cvResult={cvResult}
            cvLoading={cvLoading}
          />

          {/* Reporte NLP */}
          {nlpResult && <NLPReport result={nlpResult} />}
        </div>

        {/* Equipo Rojo */}
        <div className="team-panel">
          <div className="team-label red">🔴 Rivales</div>
          {LANES.map((lane, i) => (
            <ChampionSlot key={`r-${lane}`} lane={lane} index={i}
              value={redTeam[i]} onChange={v => updateRed(i, v)} team="red" />
          ))}
        </div>
      </main>

      <footer className="footer">
        LOL SCOUTING AI · NLP (BiLSTM + TF-IDF) + CV (Red Táctica Espacial)
      </footer>
    </div>
  );
}
