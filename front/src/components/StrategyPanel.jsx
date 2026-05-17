export default function StrategyPanel({ strategy, loading }) {
  if (loading) {
    return (
      <div className="strategy-panel">
        <div className="strategy-title">⚔ Analizando Estrategia</div>
        <div className="strategy-content">
          <div style={{ textAlign: "center", paddingTop: "1rem" }}>
            <div className="loading-dots">
              <span>●</span><span>●</span><span>●</span>
            </div>
            <p style={{ marginTop: "0.75rem", color: "var(--text-muted)", fontSize: "0.8rem" }}>
              El modelo está analizando la composición enemiga...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!strategy) {
    return (
      <div className="strategy-panel">
        <div className="strategy-title">⚔ Estrategia IA</div>
        <div className="strategy-content">
          <div className="strategy-empty">
            <div style={{ fontSize: "2rem", marginBottom: "0.5rem", opacity: 0.3 }}>🏆</div>
            <p>Ingresa los campeones rivales y haz clic en</p>
            <p>
              <strong style={{ color: "var(--gold)", fontFamily: "Cinzel, serif" }}>
                ANALIZAR COMPOSICIÓN
              </strong>
            </p>
            <p>para obtener la estrategia óptima.</p>
          </div>
        </div>
      </div>
    );
  }

  const parseStrategy = (text) => {
    if (typeof text === "object") return text;
    const result = { composition: "", early: "", mid: "", late: "", winCondition: "", raw: text };

    const compMatch  = text.match(/composici[oó]n[:\s]+([^\n.]+)/i);
    const earlyMatch = text.match(/early[:\s]+([^\n]+)/i);
    const midMatch   = text.match(/mid[:\s]+([^\n]+)/i);
    const lateMatch  = text.match(/late[:\s]+([^\n]+)/i);
    const winMatch   = text.match(/win condition[:\s]+([^\n]+)/i);

    if (compMatch)  result.composition  = compMatch[1].trim();
    if (earlyMatch) result.early        = earlyMatch[1].trim();
    if (midMatch)   result.mid          = midMatch[1].trim();
    if (lateMatch)  result.late         = lateMatch[1].trim();
    if (winMatch)   result.winCondition = winMatch[1].trim();

    return result;
  };

  const p = parseStrategy(strategy);

  return (
    <div className="strategy-panel">
      <div className="strategy-title">⚔ Estrategia Recomendada</div>
      <div className="strategy-content">

        {p.composition && (
          <div style={{ marginBottom: "0.75rem" }}>
            <span style={{ color: "var(--text-muted)", fontSize: "0.72rem", letterSpacing: "1px" }}>
              COMPOSICIÓN
            </span>
            <div style={{ color: "var(--gold-light)", fontWeight: 600, fontSize: "0.9rem" }}>
              {p.composition}
            </div>
          </div>
        )}

        {(p.early || p.mid || p.late) ? (
          <>
            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", letterSpacing: "1px", marginBottom: "0.4rem" }}>
              PLAN DE JUEGO
            </div>
            {p.early && (
              <div className="strategy-phase early">
                <span className="phase-label">Early</span>
                <span style={{ fontSize: "0.8rem" }}>{p.early}</span>
              </div>
            )}
            {p.mid && (
              <div className="strategy-phase mid">
                <span className="phase-label">Mid</span>
                <span style={{ fontSize: "0.8rem" }}>{p.mid}</span>
              </div>
            )}
            {p.late && (
              <div className="strategy-phase late">
                <span className="phase-label">Late</span>
                <span style={{ fontSize: "0.8rem" }}>{p.late}</span>
              </div>
            )}
          </>
        ) : (
          <div style={{ fontSize: "0.82rem", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
            {p.raw}
          </div>
        )}

        {p.winCondition && (
          <div className="win-condition">
            <strong>WIN CONDITION · </strong>
            {p.winCondition}
          </div>
        )}
      </div>
    </div>
  );
}