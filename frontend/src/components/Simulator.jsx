import { useState } from "react";
import { SEVERITY_BG } from "../lib/severity";

export default function Simulator({ onSimulate, result, loading }) {
  const [rainfall, setRainfall] = useState(40);

  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 text-[11px] uppercase tracking-wide text-mist-400">What-If Rainfall Simulation</div>
      <div className="flex items-center gap-4">
        <input
          type="range"
          min="0"
          max="150"
          step="5"
          value={rainfall}
          onChange={(e) => setRainfall(Number(e.target.value))}
          className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-ink-600 accent-signal-teal"
        />
        <span className="data-mono w-20 text-right text-lg font-semibold text-signal-teal">{rainfall} mm</span>
      </div>
      <div className="mt-2 flex justify-between text-[10px] text-mist-400">
        <span>0 mm</span>
        <span>40 mm</span>
        <span>70 mm</span>
        <span>100 mm</span>
        <span>150 mm</span>
      </div>
      <button
        onClick={() => onSimulate(rainfall)}
        disabled={loading}
        className="mt-4 w-full rounded-md bg-signal-teal py-2 text-xs font-semibold text-ink-950 transition hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Recalculating…" : "Run Simulation"}
      </button>

      {result && (
        <div className="mt-4 border-t border-ink-600 pt-3">
          <div className="text-[11px] text-mist-400">Resulting top risk at {result.rainfall_mm} mm</div>
          <div className={`mt-1 inline-flex items-center gap-2 rounded border px-2 py-1 text-xs font-semibold ${SEVERITY_BG[result.top_risk.severity]}`}>
            {result.top_risk.severity}
            <span className="data-mono">{result.top_risk.score}/100</span>
          </div>
          <ul className="mt-3 space-y-1">
            {result.zones
              .slice()
              .sort((a, b) => b.overall_score - a.overall_score)
              .slice(0, 4)
              .map((z) => (
                <li key={z.zone_id} className="flex items-center justify-between text-[11px] text-mist-300">
                  <span>{z.zone_name}</span>
                  <span className="data-mono">{z.flood.score}</span>
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}
