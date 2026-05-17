const LANES      = ["Top", "Jungle", "Mid", "ADC", "Support"];
const LANE_POS   = {
  Top:     { blue: { x: 15, y: 20 }, red: { x: 82, y: 20 } },
  Jungle:  { blue: { x: 28, y: 42 }, red: { x: 70, y: 58 } },
  Mid:     { blue: { x: 35, y: 55 }, red: { x: 62, y: 42 } },
  ADC:     { blue: { x: 22, y: 75 }, red: { x: 75, y: 75 } },
  Support: { blue: { x: 15, y: 82 }, red: { x: 82, y: 82 } },
};

export default function Minimap({ blueTeam, redTeam }) {
  return (
    <div className="minimap-container">
      <div className="minimap-title">🗺 Minimapa — Summoner's Rift</div>
      <div className="minimap-wrapper">
        <svg className="minimap-svg" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="mapGrad" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%"   stopColor="#0d1f12" />
              <stop offset="40%"  stopColor="#091428" />
              <stop offset="100%" stopColor="#0d1f12" />
            </linearGradient>
          </defs>

          {/* Fondo */}
          <rect width="300" height="300" fill="url(#mapGrad)" />
          <rect x="2" y="2" width="296" height="296" fill="none" stroke="#1e3a5f" strokeWidth="2" rx="4" />

          {/* Río */}
          <path d="M 0,150 Q 75,120 150,150 Q 225,180 300,150"
            fill="none" stroke="#1a4a6e" strokeWidth="18" opacity="0.5" />
          <path d="M 0,150 Q 75,120 150,150 Q 225,180 300,150"
            fill="none" stroke="#1e5f8a" strokeWidth="6"  opacity="0.4" />

          {/* Carriles */}
          <line x1="20" y1="20" x2="20" y2="140" stroke="#1e3a5f" strokeWidth="8" opacity="0.6"/>
          <line x1="20" y1="20" x2="140" y2="20" stroke="#1e3a5f" strokeWidth="8" opacity="0.6"/>
          <line x1="25" y1="275" x2="275" y2="25" stroke="#1e3a5f" strokeWidth="8" opacity="0.6"/>
          <line x1="160" y1="280" x2="280" y2="280" stroke="#1e3a5f" strokeWidth="8" opacity="0.6"/>
          <line x1="280" y1="160" x2="280" y2="280" stroke="#1e3a5f" strokeWidth="8" opacity="0.6"/>

          {/* Nexus Azul */}
          <rect x="5" y="245" width="40" height="40" rx="4" fill="#0d2b5e" stroke="#2980b9" strokeWidth="1.5"/>
          <text x="25" y="269" textAnchor="middle" fill="#7ec8e3" fontSize="8" fontWeight="bold">NEXUS</text>
          <text x="25" y="279" textAnchor="middle" fill="#7ec8e3" fontSize="6">BLUE</text>

          {/* Nexus Rojo */}
          <rect x="255" y="15" width="40" height="40" rx="4" fill="#5e0d0d" stroke="#c0392b" strokeWidth="1.5"/>
          <text x="275" y="39" textAnchor="middle" fill="#e87c7c" fontSize="8" fontWeight="bold">NEXUS</text>
          <text x="275" y="49" textAnchor="middle" fill="#e87c7c" fontSize="6">RED</text>

          {/* Torres Azules */}
          {[[15,130],[15,80],[100,15],[55,15]].map(([x,y],i) => (
            <circle key={`bt-${i}`} cx={x} cy={y} r="5"
              fill="#2980b9" stroke="#7ec8e3" strokeWidth="1" opacity="0.8"/>
          ))}
          {/* Torres Rojas */}
          {[[285,170],[285,220],[200,285],[245,285]].map(([x,y],i) => (
            <circle key={`rt-${i}`} cx={x} cy={y} r="5"
              fill="#c0392b" stroke="#e87c7c" strokeWidth="1" opacity="0.8"/>
          ))}

          {/* Dragón y Barón */}
          <text x="220" y="214" textAnchor="middle" fontSize="14">🐉</text>
          <text x="80"  y="94"  textAnchor="middle" fontSize="14">💜</text>

          {/* Campeones por carril */}
          {LANES.map((lane, i) => {
            const pos  = LANE_POS[lane];
            const blue = blueTeam[i];
            const red  = redTeam[i];

            return (
              <g key={lane}>
                {/* Blue */}
                <circle cx={pos.blue.x*3} cy={pos.blue.y*3} r="11"
                  fill={blue?.name ? "#0d2b5e" : "rgba(0,0,0,0.3)"}
                  stroke={blue?.name ? "#2980b9" : "#1e3a5f"} strokeWidth="1.5"/>
                {blue?.icon
                  ? <image href={blue.icon}
                      x={pos.blue.x*3-10} y={pos.blue.y*3-10} width="20" height="20"/>
                  : <text x={pos.blue.x*3} y={pos.blue.y*3+4} textAnchor="middle"
                      fill={blue?.name ? "#7ec8e3" : "#1e3a5f"} fontSize="8" fontWeight="bold">
                      {blue?.name ? blue.name.substring(0,2).toUpperCase() : lane[0]}
                    </text>
                }

                {/* Red */}
                <circle cx={pos.red.x*3} cy={pos.red.y*3} r="11"
                  fill={red?.name ? "#3a0d0d" : "rgba(0,0,0,0.3)"}
                  stroke={red?.name ? "#c0392b" : "#1e3a5f"} strokeWidth="1.5"/>
                {red?.icon
                  ? <image href={red.icon}
                      x={pos.red.x*3-10} y={pos.red.y*3-10} width="20" height="20"/>
                  : <text x={pos.red.x*3} y={pos.red.y*3+4} textAnchor="middle"
                      fill={red?.name ? "#e87c7c" : "#1e3a5f"} fontSize="8" fontWeight="bold">
                      {red?.name ? red.name.substring(0,2).toUpperCase() : lane[0]}
                    </text>
                }
              </g>
            );
          })}

          {/* Leyenda */}
          <rect x="100" y="275" width="100" height="22" rx="3" fill="rgba(0,0,0,0.5)"/>
          <circle cx="118" cy="286" r="5" fill="#0d2b5e" stroke="#2980b9" strokeWidth="1"/>
          <text x="127" y="290" fill="#7ec8e3" fontSize="7">Tu equipo</text>
          <circle cx="165" cy="286" r="5" fill="#3a0d0d" stroke="#c0392b" strokeWidth="1"/>
          <text x="174" y="290" fill="#e87c7c" fontSize="7">Rivales</text>
        </svg>
      </div>
    </div>
  );
}