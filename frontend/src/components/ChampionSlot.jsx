import { useRef, useState } from "react";

const ICONS = { Top:"⚔️", Jungle:"🌿", Mid:"⚡", ADC:"🏹", Support:"🛡️" };

export default function ChampionSlot({ lane, index, value, onChange }) {
  const fileRef = useRef(null);
  const [preview, setPreview] = useState(value.icon || null);
  const key = lane.toLowerCase();

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setPreview(url);
    onChange({ ...value, icon: url });
  };

  return (
    <div className={`champion-slot ${key} ${value.name ? "filled" : ""}`}>
      <div className="champ-icon-upload" onClick={() => fileRef.current.click()} title="Subir ícono">
        {preview
          ? <img src={preview} alt={value.name || lane} />
          : <span style={{ opacity:.5 }}>{ICONS[lane] || "?"}</span>
        }
        <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} />
      </div>
      <div className="champ-info">
        <div className={`lane-badge ${key}`}>{lane}</div>
        <input
          className="champ-name-input"
          placeholder={`Campeón ${index + 1}`}
          value={value.name}
          onChange={e => onChange({ ...value, name: e.target.value })}
        />
      </div>
    </div>
  );
}