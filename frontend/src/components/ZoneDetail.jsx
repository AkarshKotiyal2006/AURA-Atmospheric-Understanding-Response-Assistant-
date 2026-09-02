import { SEVERITY_BG, hazardLabel } from "../lib/severity";

function HazardRow({ h }) {
  return (
    <div className="border-t border-ink-600 pt-3 first:border-t-0 first:pt-0">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-mist-50">{hazardLabel(h.hazard)}</span>
        <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold ${SEVERITY_BG[h.severity]}`}>
          {h.severity} · {h.score}
        </span>
      </div>
      <ul className="mt-1.5 space-y-1">
        {h.factors.map((f, i) => (
          <li key={i} className="text-[11px] text-mist-400">
            • {f}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ZoneDetail({ zone }) {
  if (!zone) {
    return (
      <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
        <div className="mb-2 text-[11px] uppercase tracking-wide text-mist-400">Why is this risk high?</div>
        <p className="text-xs text-mist-400">Select a zone on the map or from the grid to see the explanation.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-1 text-[11px] uppercase tracking-wide text-mist-400">Why is this risk high?</div>
      <div className="mb-3 text-sm font-semibold text-mist-50">{zone.zone_name}</div>
      <div className="space-y-3">
        <HazardRow h={zone.flood} />
        <HazardRow h={zone.heat} />
        <HazardRow h={zone.aqi} />
      </div>
      {zone.potential_impact?.length > 0 && (
        <div className="mt-4 border-t border-ink-600 pt-3">
          <div className="mb-1.5 text-[11px] uppercase tracking-wide text-mist-400">Potential Impact Chain</div>
          <div className="flex flex-wrap items-center gap-1 text-[11px] text-mist-200">
            {zone.potential_impact.map((step, i) => (
              <span key={i} className="flex items-center gap-1">
                <span className="rounded bg-ink-900 px-2 py-1">{step}</span>
                {i < zone.potential_impact.length - 1 && <span className="text-signal-teal">→</span>}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
