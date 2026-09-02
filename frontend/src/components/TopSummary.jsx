import { SEVERITY_BG, hazardLabel } from "../lib/severity";

function actionFor(topZone) {
  if (!topZone) return "Monitoring conditions. No specific action required.";
  const hazard = topZone.top_hazard;
  const sev = topZone.overall_severity;
  if (sev === "LOW") return "Conditions are within normal range. No specific action required.";
  if (hazard === "flood") return `Avoid low-lying roads near ${topZone.zone_name} during the expected rainfall window.`;
  if (hazard === "heat") return `Limit outdoor activity in ${topZone.zone_name}, especially during midday hours. Stay hydrated.`;
  return `Consider limiting prolonged outdoor exposure near ${topZone.zone_name}; sensitive groups should take extra precaution.`;
}

export default function TopSummary({ weather, topZone }) {
  if (!weather) return null;

  const metrics = [
    { label: "Temperature", value: `${weather.temperature_c}°C` },
    { label: "Humidity", value: `${weather.humidity_pct}%` },
    { label: "Wind", value: `${weather.wind_kmh} km/h` },
    { label: "Rainfall", value: `${weather.rainfall_mm} mm` },
    { label: "AQI", value: `${Math.round(weather.aqi)}` },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel lg:col-span-2">
        <div className="mb-3 text-[11px] uppercase tracking-wide text-mist-400">Current Conditions</div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {metrics.map((m) => (
            <div key={m.label}>
              <div className="data-mono text-lg font-semibold text-mist-50">{m.value}</div>
              <div className="text-[11px] text-mist-400">{m.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
        <div className="mb-2 text-[11px] uppercase tracking-wide text-mist-400">Top Risk</div>
        {topZone ? (
          <>
            <div className="text-sm font-medium text-mist-50">{hazardLabel(topZone.top_hazard)}</div>
            <div className={`mt-2 inline-flex items-center gap-2 rounded border px-2 py-1 text-xs font-semibold ${SEVERITY_BG[topZone.overall_severity]}`}>
              {topZone.overall_severity}
              <span className="data-mono">{topZone.overall_score}/100</span>
            </div>
            <div className="mt-2 text-[11px] text-mist-400">{topZone.zone_name}</div>
          </>
        ) : (
          <div className="text-sm text-mist-400">No data</div>
        )}
      </div>

      <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
        <div className="mb-2 text-[11px] uppercase tracking-wide text-mist-400">Potential Impact</div>
        {topZone?.potential_impact?.length ? (
          <ul className="space-y-1 text-xs text-mist-200">
            {topZone.potential_impact.slice(0, 3).map((step, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-signal-teal">›</span>
                <span>{step}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-xs text-mist-400">No significant impact expected.</div>
        )}
      </div>

      <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
        <div className="mb-2 text-[11px] uppercase tracking-wide text-mist-400">Recommended Action</div>
        <p className="text-xs leading-relaxed text-mist-200">{actionFor(topZone)}</p>
        {topZone && (
          <div className="mt-3 border-t border-ink-600 pt-2">
            <div className="text-[11px] text-mist-400">Confidence</div>
            <div className="data-mono text-lg font-semibold text-signal-teal">{topZone.confidence}%</div>
          </div>
        )}
      </div>
    </div>
  );
}
