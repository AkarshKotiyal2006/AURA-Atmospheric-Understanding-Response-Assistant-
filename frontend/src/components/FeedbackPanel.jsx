import { useState } from "react";

export default function FeedbackPanel({ feedback, zones, onSubmit }) {
  const [zoneId, setZoneId] = useState(zones?.[0]?.zone_id || "");
  const [hazard, setHazard] = useState("flood");
  const [occurred, setOccurred] = useState(true);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!zoneId) return;
    setBusy(true);
    try {
      await onSubmit({ zone_id: zoneId, hazard, occurred, notes: "" });
    } finally {
      setBusy(false);
    }
  };

  if (!feedback) return null;

  const stat = (label, value, suffix = "") => (
    <div>
      <div className="data-mono text-lg font-semibold text-mist-50">{value === null || value === undefined ? "—" : `${value}${suffix}`}</div>
      <div className="text-[11px] text-mist-400">{label}</div>
    </div>
  );

  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-1 text-[11px] uppercase tracking-wide text-mist-400">Prediction vs Reality</div>
      <p className="mb-3 text-[10px] text-mist-400">{feedback.note}</p>

      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-7">
        {stat("Predictions", feedback.total_predictions)}
        {stat("Detections", feedback.true_positive_detections)}
        {stat("False Alarms", feedback.false_alarms)}
        {stat("Unverified", feedback.unverified_predictions)}
        {stat("Missed", feedback.missed_events)}
        {stat("Precision", feedback.precision)}
        {stat("Recall", feedback.recall)}
      </div>

      <div className="border-t border-ink-600 pt-3">
        <div className="mb-2 text-[11px] text-mist-400">Log an actual observed event (demo ground-truth)</div>
        <div className="flex flex-wrap items-center gap-2">
          <select value={zoneId} onChange={(e) => setZoneId(e.target.value)} className="rounded border border-ink-600 bg-ink-900 px-2 py-1.5 text-[11px] text-mist-50">
            {zones.map((z) => (
              <option key={z.zone_id} value={z.zone_id}>{z.zone_name}</option>
            ))}
          </select>
          <select value={hazard} onChange={(e) => setHazard(e.target.value)} className="rounded border border-ink-600 bg-ink-900 px-2 py-1.5 text-[11px] text-mist-50">
            <option value="flood">Flood</option>
            <option value="heat">Heat</option>
            <option value="aqi">AQI</option>
          </select>
          <label className="flex items-center gap-1 text-[11px] text-mist-400">
            <input type="checkbox" checked={occurred} onChange={(e) => setOccurred(e.target.checked)} /> Event occurred
          </label>
          <button onClick={submit} disabled={busy} className="rounded-md bg-signal-teal px-3 py-1.5 text-[11px] font-semibold text-ink-950 disabled:opacity-50">
            {busy ? "Saving…" : "Log Event"}
          </button>
        </div>
      </div>
    </div>
  );
}
