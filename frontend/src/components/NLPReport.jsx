export default function NLPReport({ result }) {
  if (!result?.report) return null;

  const lines = result.report
    .split("\n")
    .filter(l => l.trim() !== "");

  return (
    <div className="nlp-report">
      <div className="nlp-report-title">
        📋 Reporte Completo de Scouting NLP
      </div>
      <div className="nlp-report-body">
        {lines.map((line, i) => {
          const isSep = line.startsWith("=") || line.startsWith("-");
          const isTitle = !isSep && line === line.toUpperCase() && line.length > 4;
          return (
            <div key={i} className={
              isSep    ? "nlp-line-sep" :
              isTitle  ? "nlp-line-title" :
                         "nlp-line"
            }>
              {line}
            </div>
          );
        })}
      </div>
    </div>
  );
}
