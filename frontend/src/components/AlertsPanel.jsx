import { SEVERITY_BG, hazardLabel } from "../lib/severity";

export default function AlertsPanel({ alerts, context }) {
  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-wide text-mist-400">Active Alerts</div>
        <span className="text-[11px] text-mist-400">{alerts.length} active</span>
      </div>
      {alerts.length === 0 ? (
        <p className="text-xs text-mist-400">No active alerts. All zones within normal risk range.</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((a) => (
            <div key={`${a.zone_id}-${a.hazard}`} className="rounded-md border border-ink-600 bg-ink-900 p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-mist-50">
                  {hazardLabel(a.hazard).toUpperCase()} — {a.zone_name}
                </span>
                <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold ${SEVERITY_BG[a.severity]}`}>
                  {a.severity}
                </span>
              </div>
              <p className="mt-1.5 text-[11px] text-mist-300">{a.messages[context]}</p>
              <details className="mt-1.5">
                <summary className="cursor-pointer text-[10px] text-signal-teal">Why is this risk {a.severity.toLowerCase()}?</summary>
                <ul className="mt-1 space-y-0.5">
                  {a.factors.map((f, i) => (
                    <li key={i} className="text-[10px] text-mist-400">• {f}</li>
                  ))}
                </ul>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
