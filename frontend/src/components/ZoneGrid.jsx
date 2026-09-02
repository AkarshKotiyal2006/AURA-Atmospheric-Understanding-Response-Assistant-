import { SEVERITY_BG, hazardLabel } from "../lib/severity";

export default function ZoneGrid({ zones, selectedZoneId, onSelect }) {
  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-wide text-mist-400">Zone Risk Summary</div>
        <div className="text-[11px] text-mist-400">{zones.length} zones</div>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {zones.map((z) => (
          <button
            key={z.zone_id}
            onClick={() => onSelect(z.zone_id)}
            className={`rounded-md border p-3 text-left transition ${
              selectedZoneId === z.zone_id
                ? "border-signal-teal bg-ink-700"
                : "border-ink-600 bg-ink-900 hover:border-ink-500"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-mist-50">{z.zone_name}</span>
              <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold ${SEVERITY_BG[z.overall_severity]}`}>
                {z.overall_severity}
              </span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-[11px] text-mist-400">
              <div>
                Flood <span className="data-mono block text-mist-50">{z.flood.score}</span>
              </div>
              <div>
                Heat <span className="data-mono block text-mist-50">{z.heat.score}</span>
              </div>
              <div>
                AQI <span className="data-mono block text-mist-50">{z.aqi.score}</span>
              </div>
            </div>
            <div className="mt-2 text-[10px] text-mist-400">
              Top: {hazardLabel(z.top_hazard)} · Confidence {z.confidence}%
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
