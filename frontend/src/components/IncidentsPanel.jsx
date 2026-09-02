export default function IncidentsPanel({ incidents }) {
  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-wide text-mist-400">Clustered Incidents</div>
        <span className="text-[11px] text-mist-400">{incidents.length}</span>
      </div>
      {incidents.length === 0 ? (
        <p className="text-xs text-mist-400">No community reports yet. Submitted reports will cluster here automatically.</p>
      ) : (
        <div className="space-y-2">
          {incidents.map((inc) => (
            <div key={inc.incident_id} className="flex items-center justify-between rounded-md border border-ink-600 bg-ink-900 px-3 py-2">
              <div>
                <div className="text-xs font-medium text-mist-50">{inc.incident_type}</div>
                <div className="text-[10px] text-mist-400">{inc.zone_name}</div>
              </div>
              <div className="text-right">
                <div className="data-mono text-xs text-signal-teal">{inc.report_count} reports</div>
                <div className="text-[10px] text-mist-400">{inc.status}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
