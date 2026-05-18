import { useRef, useCallback } from "react";

const LANES = ["Top", "Jungle", "Mid", "ADC", "Support"];
const LANE_COLORS = {
  Top: "#e74c3c", Jungle: "#27ae60", Mid: "#9b59b6",
  ADC: "#3498db", Support: "#f39c12",
};

const R  = 18;
const VB = 600;

const MAP_URLS = [
  "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-navigation/global/default/minimap-icon-map-1.png",
  "https://ddragon.leagueoflegends.com/cdn/img/map/map11.png",
];

// ─── Fondo SVG del mapa ───────────────────────────────────────
const MapBackground = () => (
  <g>
    <defs>
      <radialGradient id="grassGrad" cx="50%" cy="50%" r="70%">
        <stop offset="0%"   stopColor="#1a4a1a" />
        <stop offset="60%"  stopColor="#0f3010" />
        <stop offset="100%" stopColor="#081a08" />
      </radialGradient>
      <linearGradient id="pathGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%"   stopColor="#7a6535" />
        <stop offset="100%" stopColor="#5a4820" />
      </linearGradient>
      <linearGradient id="riverGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%"  stopColor="#0d5a8a" />
        <stop offset="50%" stopColor="#1a7ab5" />
        <stop offset="100%" stopColor="#0d4a7a" />
      </linearGradient>
    </defs>
    <rect width={VB} height={VB} fill="url(#grassGrad)" />
    {/* Río */}
    <path d="M -10,340 C 80,310 150,280 220,255 C 290,230 340,220 390,225 C 440,230 490,250 610,240"
      fill="none" stroke="url(#riverGrad)" strokeWidth="42" strokeLinecap="round"/>
    <path d="M -10,340 C 80,310 150,280 220,255 C 290,230 340,220 390,225 C 440,230 490,250 610,240"
      fill="none" stroke="#5ab5e0" strokeWidth="8" opacity="0.3" strokeLinecap="round"/>
    {/* Carriles */}
    <line x1="65" y1="65" x2="65" y2="310" stroke="url(#pathGrad)" strokeWidth="26" strokeLinecap="round"/>
    <line x1="65" y1="65" x2="310" y2="65" stroke="url(#pathGrad)" strokeWidth="26" strokeLinecap="round"/>
    <line x1="90" y1="510" x2="510" y2="90" stroke="url(#pathGrad)" strokeWidth="28" strokeLinecap="round"/>
    <line x1="290" y1="535" x2="535" y2="535" stroke="url(#pathGrad)" strokeWidth="26" strokeLinecap="round"/>
    <line x1="535" y1="290" x2="535" y2="535" stroke="url(#pathGrad)" strokeWidth="26" strokeLinecap="round"/>
    {/* Nexus azul */}
    <circle cx="60" cy="540" r="30" fill="#0d2244" stroke="#2980b9" strokeWidth="3"/>
    <circle cx="60" cy="540" r="12" fill="#60b0ff" opacity="0.6"/>
    <text x="60" y="545" textAnchor="middle" fill="#a0d8ff" fontSize="8" fontWeight="bold">NEXUS</text>
    {/* Nexus rojo */}
    <circle cx="540" cy="60"  r="30" fill="#440d0d" stroke="#c0392b" strokeWidth="3"/>
    <circle cx="540" cy="60"  r="12" fill="#ff6060" opacity="0.6"/>
    <text x="540" y="65" textAnchor="middle" fill="#ffaaaa" fontSize="8" fontWeight="bold">NEXUS</text>
    {/* Dragón y Barón */}
    <circle cx="405" cy="415" r="18" fill="#5a2008" stroke="#e67e22" strokeWidth="2"/>
    <text x="405" y="421" textAnchor="middle" fontSize="16">🐉</text>
    <circle cx="180" cy="180" r="18" fill="#2a0845" stroke="#8e44ad" strokeWidth="2"/>
    <text x="180" y="186" textAnchor="middle" fontSize="16">💀</text>
  </g>
);

export default function Minimap({ blueTeam, redTeam, positions, onMove, cvResult, cvLoading }) {
  const svgRef  = useRef(null);
  const dragging = useRef(null);

  const toSVGCoords = useCallback((clientX, clientY) => {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const pt = svg.createSVGPoint();
    pt.x = clientX; pt.y = clientY;
    const sp = pt.matrixTransform(svg.getScreenCTM().inverse());
    return {
      x: Math.min(VB - R, Math.max(R, sp.x)),
      y: Math.min(VB - R, Math.max(R, sp.y)),
    };
  }, []);

  const startDrag = (team, index) => (e) => {
    e.preventDefault();
    dragging.current = { team, index };
  };
  const moveDrag = useCallback((e) => {
    if (!dragging.current) return;
    const { team, index } = dragging.current;
    onMove(team, index, toSVGCoords(e.clientX, e.clientY));
  }, [toSVGCoords, onMove]);
  const endDrag = useCallback(() => { dragging.current = null; }, []);
  const moveTouchDrag = useCallback((e) => {
    if (!dragging.current) return;
    const t = e.touches[0];
    const { team, index } = dragging.current;
    onMove(team, index, toSVGCoords(t.clientX, t.clientY));
  }, [toSVGCoords, onMove]);

  const renderDot = (team, index, champion) => {
    const pos    = positions[team][index];
    const isBlue = team === "blue";
    const fill   = isBlue ? "#0d2b5e" : "#3a0d0d";
    const ring   = isBlue ? "#2980b9" : "#c0392b";
    const txt    = isBlue ? "#7ec8e3" : "#e87c7c";
    const lane   = LANE_COLORS[LANES[index]];
    const clipId = `clip-${team}-${index}`;
    const abbr   = champion?.name
      ? champion.name.substring(0, 2).toUpperCase()
      : LANES[index][0];

    return (
      <g key={`${team}-${index}`}
        transform={`translate(${pos.x},${pos.y})`}
        style={{ cursor: "grab" }}
        onMouseDown={startDrag(team, index)}
        onTouchStart={startDrag(team, index)}
      >
        <circle cx="0" cy="3"  r={R + 4} fill="rgba(0,0,0,0.6)" />
        <circle cx="0" cy="0"  r={R + 6} fill={isBlue ? "rgba(41,128,185,0.25)" : "rgba(192,57,43,0.25)"} />
        <circle cx="0" cy="0"  r={R + 4} fill="none" stroke={lane} strokeWidth="2.5" opacity="0.85" />
        <circle cx="0" cy="0"  r={R + 1} fill="none" stroke={ring} strokeWidth="3" />
        <circle cx="0" cy="0"  r={R}     fill={fill} />
        {champion?.icon ? (
          <>
            <defs><clipPath id={clipId}><circle cx="0" cy="0" r={R - 1} /></clipPath></defs>
            <image href={champion.icon}
              x={-(R-1)} y={-(R-1)} width={(R-1)*2} height={(R-1)*2}
              clipPath={`url(#${clipId})`} preserveAspectRatio="xMidYMid slice" />
          </>
        ) : (
          <text x="0" y="5" textAnchor="middle"
            fill={txt} fontSize="11" fontWeight="bold"
            style={{ fontFamily:"'Exo 2',sans-serif", userSelect:"none" }}>
            {abbr}
          </text>
        )}
        {champion?.name && (
          <>
            <rect x={-26} y={R+3} width={52} height={14} rx="3"
              fill="rgba(0,0,0,0.85)" stroke={ring} strokeWidth="0.8" />
            <text x="0" y={R+13} textAnchor="middle"
              fill={txt} fontSize="8.5" fontWeight="600"
              style={{ fontFamily:"'Exo 2',sans-serif", userSelect:"none" }}>
              {champion.name.length > 7 ? champion.name.substring(0,7) : champion.name}
            </text>
          </>
        )}
      </g>
    );
  };

  // Badge de estrategia identificada por CV
  const cvBadge = cvResult && (
    <div className="cv-badge">
      {cvLoading ? (
        <span>🔍 Calculando...</span>
      ) : cvResult.source === "identify" ? (
        <>
          <span className="cv-badge-label">Estrategia detectada:</span>
          <span className="cv-badge-strategy">{cvResult.main_strategy}</span>
          <span className="cv-badge-conf">{(cvResult.confidence * 100).toFixed(1)}%</span>
        </>
      ) : (
        <>
          <span className="cv-badge-label">Posiciones para:</span>
          <span className="cv-badge-strategy">{cvResult.strategy}</span>
        </>
      )}
    </div>
  );

  return (
    <div className="minimap-container">
      <div className="minimap-title">
        🗺 Minimapa — Arrastra los íconos para posicionar
      </div>

      {cvBadge}

      <div className="minimap-wrapper">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${VB} ${VB}`}
          xmlns="http://www.w3.org/2000/svg"
          style={{ width:"100%", height:"100%", display:"block" }}
          onMouseMove={moveDrag}
          onMouseUp={endDrag}
          onMouseLeave={endDrag}
          onTouchMove={moveTouchDrag}
          onTouchEnd={endDrag}
        >
          <MapBackground />
          {LANES.map((_, i) => renderDot("red",  i, redTeam[i]))}
          {LANES.map((_, i) => renderDot("blue", i, blueTeam[i]))}
        </svg>
      </div>

      <div className="minimap-legend">
        <span><span className="legend-dot blue"/> Aliados</span>
        <span><span className="legend-dot red"/>  Enemigos</span>
        <span style={{color:"var(--text-muted)",fontSize:".7rem"}}>
          · Arrastra para mover · Scouting mueve automáticamente
        </span>
      </div>
    </div>
  );
}
