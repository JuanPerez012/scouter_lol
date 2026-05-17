import { useRef, useState } from "react";

const LANE_ICONS = {
  Top: "⚔️",
  Jungle: "🌿",
  Mid: "⚡",
  ADC: "🏹",
  Support: "🛡️",
};

export default function ChampionSlot({ lane, index, value, onChange }) {
  const fileRef = useRef(null);
  const [preview, setPreview] = useState(value.icon || null);

  const laneKey = lane.toLowerCase().replace(" ", "");

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    onChange({ ...value, icon: url, iconFile: file });
  };

  const handleNameChange = (e) => {
    onChange({ ...value, name: e.target.value });
  };

  return (
    <div className={`champion-slot ${laneKey} ${value.name ? "filled" : ""}`}>
      <div className="champ-icon-wrapper">
        <div
          className="champ-icon-upload"
          onClick={() => fileRef.current.click()}
          title="Subir ícono del campeón"
        >
          {preview ? (
            <img src={preview} alt={value.name || "champion"} />
          ) : (
            <span style={{ fontSize: "1.4rem", opacity: 0.5 }}>
              {LANE_ICONS[lane] || "?"}
            </span>
          )}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            onChange={handleImageChange}
          />
        </div>
      </div>

      <div className="champ-info">
        <div className={`lane-badge ${laneKey}`}>{lane}</div>
        <input
          className="champ-name-input"
          type="text"
          placeholder={`Campeón ${index + 1}`}
          value={value.name}
          onChange={handleNameChange}
        />
      </div>
    </div>
  );
}