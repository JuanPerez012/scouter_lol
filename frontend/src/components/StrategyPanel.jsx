export default function StrategyPanel({ strategy, loading, cvResult, cvLoading }) {
  if (loading) return (
    <div className="strategy-panel">
      <div className="strategy-title">⚔ Analizando NLP</div>
      <div className="strategy-content">
        <div style={{ textAlign:"center", paddingTop:"1.5rem" }}>
          <div className="loading-dots"><span>●</span><span>●</span><span>●</span></div>
          <p style={{ marginTop:".75rem", color:"var(--text-muted)", fontSize:".8rem" }}>
            Analizando composición con NLP...
          </p>
        </div>
      </div>
    </div>
  );

  if (!strategy) return (
    <div className="strategy-panel">
      <div className="strategy-title">⚔ Estrategia IA</div>
      <div className="strategy-content">
        <div className="strategy-empty">
          <div style={{ fontSize:"2rem", marginBottom:".5rem", opacity:.3 }}>🏆</div>
          <p>Ingresa los campeones y presiona</p>
          <p><strong style={{ color:"var(--gold)", fontFamily:"Cinzel,serif" }}>SCOUTING COMPLETO</strong></p>
          <p style={{ fontSize:".75rem", marginTop:".5rem", color:"var(--text-muted)" }}>
            O arrastra los íconos y usa <strong>IDENTIFICAR ESTRATEGIA</strong>
          </p>
        </div>
      </div>
    </div>
  );

  // Parsear top_strategies del NLP
  const topStrategies = strategy.top_strategies || [];
  const mainStrategy  = strategy.main_strategy  || "";
  const confidence    = strategy.confidence     || 0;

  return (
    <div className="strategy-panel">
      <div className="strategy-title">⚔ Análisis Estratégico</div>
      <div className="strategy-content">

        {/* Estrategia principal */}
        {mainStrategy && (
          <div style={{ marginBottom:".75rem" }}>
            <div style={{ color:"var(--text-muted)", fontSize:".7rem", letterSpacing:"1px" }}>
              IDENTIDAD ESTRATÉGICA PRINCIPAL (NLP)
            </div>
            <div style={{ color:"var(--gold-light)", fontWeight:600, fontSize:".95rem", marginTop:".2rem" }}>
              {mainStrategy}
              <span style={{ color:"var(--text-muted)", fontSize:".75rem", marginLeft:".5rem" }}>
                {(confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {/* Top-3 estrategias */}
        {topStrategies.length > 0 && (
          <div style={{ marginBottom:".75rem" }}>
            <div style={{ color:"var(--text-muted)", fontSize:".7rem", letterSpacing:"1px", marginBottom:".3rem" }}>
              TOP ESTRATEGIAS DETECTADAS
            </div>
            {topStrategies.map(([name, conf], i) => (
              <div key={i} className={`strategy-phase ${i === 0 ? "early" : i === 1 ? "mid" : "late"}`}>
                <span className="phase-label">#{i+1}</span>
                <span style={{ fontSize:".8rem", flex:1 }}>{name}</span>
                <span style={{ fontSize:".75rem", color:"var(--text-muted)" }}>
                  {(conf * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Estado CV */}
        {(cvLoading || cvResult) && (
          <div className="win-condition">
            {cvLoading ? (
              <span style={{ color:"var(--text-muted)" }}>
                🗺 Generando posiciones tácticas en el minimapa...
              </span>
            ) : cvResult?.source === "nlp" ? (
              <>
                <strong>MINIMAPA · </strong>
                Posiciones actualizadas para <em>{cvResult.strategy}</em>
              </>
            ) : cvResult?.source === "identify" ? (
              <>
                <strong>CV DETECTÓ · </strong>
                {cvResult.main_strategy} ({(cvResult.confidence * 100).toFixed(1)}%)
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
