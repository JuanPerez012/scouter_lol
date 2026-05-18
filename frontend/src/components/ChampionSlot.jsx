import { useEffect, useMemo, useRef, useState } from "react";

const ICONS = {
  Top: "⚔️",
  Jungle: "🌿",
  Mid: "⚡",
  ADC: "🏹",
  Support: "🛡️"
};

export default function ChampionSlot({
  lane,
  index,
  team,
  value,
  onChange,
  champions = [],
  selectedChampions = [],
  activeDropdown,
  setActiveDropdown
}) {

  const fileRef = useRef(null);

  const wrapperRef = useRef(null);

  const [preview, setPreview] = useState(value.icon || null);

  const key = lane.toLowerCase();

  const dropdownId = `${team}-${lane}-${index}`;
  const isOpen = activeDropdown === dropdownId;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target)
      ) {
        if (activeDropdown === dropdownId) {
          setActiveDropdown(null);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [activeDropdown, dropdownId, setActiveDropdown]);

  const filteredChampions = useMemo(() => {

    const currentName = value.name?.toLowerCase();

    let filtered = champions.filter(champ => {

      const champName = champ.champion.toLowerCase();

      const matchesSearch =
        champName.includes((value.name || "").toLowerCase());

      const alreadySelected =
        selectedChampions.includes(champName) &&
        champName !== currentName;

      return matchesSearch && !alreadySelected;
    });

    return filtered.slice(0, 15);

  }, [champions, selectedChampions, value.name]);

  const handleSelect = (champ) => {
    onChange({
      ...value,
      name: champ.champion,
      data: champ
    });

    setActiveDropdown(null);
  };

  const handleFile = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    const url = URL.createObjectURL(file);

    setPreview(url);

    onChange({
      ...value,
      icon: url
    });
  };

  return (
    <div
      ref={wrapperRef}
      className={`champion-slot ${key} ${value.name ? "filled" : ""}`}
    >

      <div
        className="champ-icon-upload"
        onClick={() => fileRef.current.click()}
        title="Subir ícono"
      >
        {preview ? (
          <img src={preview} alt={value.name || lane} />
        ) : (
          <span style={{ opacity: .5 }}>
            {ICONS[lane] || "?"}
          </span>
        )}

        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          onChange={handleFile}
        />
      </div>

      <div className="champ-info">

        <div className={`lane-badge ${key}`}>
          {lane}
        </div>

        <div className="champ-search-wrapper">

          <input
            className="champ-name-input"
            placeholder={`Buscar campeón`}
            value={value.name || ""}
            onFocus={() => setActiveDropdown(dropdownId)}
            onChange={(e) => {
              onChange({
                ...value,
                name: e.target.value
              });

              setActiveDropdown(dropdownId);
            }} />

          {isOpen && filteredChampions.length > 0 && (
            <div className="champ-dropdown">

              {filteredChampions.map((champ) => (
                <div
                  key={champ.champion_id}
                  className="champ-option"
                  onMouseDown={() => handleSelect(champ)}
                >

                  <div className="champ-option-name">
                    {champ.champion}
                  </div>

                  <div className="champ-option-meta">
                    {champ.primary_role} · {champ.main_playstyle}
                  </div>

                </div>
              ))}

            </div>
          )}

        </div>

      </div>

    </div>
  );
}