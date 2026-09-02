const SCENARIOS = ["NORMAL", "FLOOD", "HEAT", "AQI", "STORM"];
const CONTEXTS = ["citizen", "commuter", "resident", "authority"];

export default function ControlBar({ scenario, onScenario, context, onContext, dataSource, loading }) {
  return (
    <div className="flex flex-col gap-3 border-b border-ink-600 bg-ink-800/60 px-6 py-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md border border-signal-teal/40 bg-signal-tealDim/30">
          <span className="data-mono text-sm font-semibold text-signal-teal">A</span>
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight text-mist-50">AURA</div>
          <div className="text-[11px] text-mist-400">Atmospheric Understanding &amp; Response Assistant</div>
        </div>
        <span
          className={`ml-3 rounded border px-2 py-1 text-[11px] data-mono ${
            dataSource === "LIVE"
              ? "border-risk-low/40 text-risk-low"
              : "border-signal-teal/40 text-signal-teal"
          }`}
        >
          {loading ? "SYNCING…" : dataSource === "LIVE" ? "● LIVE DATA" : "◆ DEMO DATA"}
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-1 rounded-md border border-ink-600 bg-ink-900 p-1">
          {SCENARIOS.map((s) => (
            <button
              key={s}
              onClick={() => onScenario(s)}
              className={`rounded px-3 py-1.5 text-xs font-medium transition ${
                scenario === s
                  ? "bg-signal-teal text-ink-950"
                  : "text-mist-400 hover:text-mist-50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] text-mist-400">View as</span>
          <select
            value={context}
            onChange={(e) => onContext(e.target.value)}
            className="rounded border border-ink-600 bg-ink-900 px-2 py-1.5 text-xs text-mist-50 outline-none focus:border-signal-teal"
          >
            {CONTEXTS.map((c) => (
              <option key={c} value={c}>
                {c[0].toUpperCase() + c.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
