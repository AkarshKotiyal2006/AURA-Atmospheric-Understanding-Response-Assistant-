import { useRef, useState } from "react";

const INCIDENT_TYPES = ["Waterlogging", "Flooding", "Fallen Tree", "Road Blockage", "Heavy Rain", "Storm", "Other"];
const DEFAULT_LAT = 28.4744;
const DEFAULT_LON = 77.504;

export default function ReportForm({ onSubmit, lastResult }) {
  const [form, setForm] = useState({
    incident_type: INCIDENT_TYPES[0],
    text: "",
    lat: DEFAULT_LAT,
    lon: DEFAULT_LON,
    photo: null,
  });
  const [submitting, setSubmitting] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef(null);

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser.");
      return;
    }
    setLocating(true);
    setError("");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        update("lat", Number(pos.coords.latitude.toFixed(5)));
        update("lon", Number(pos.coords.longitude.toFixed(5)));
        setLocating(false);
      },
      () => {
        setError("Could not read your location. Enter coordinates manually.");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.text.trim() && !form.photo) {
      setError("Add a short description or a photo before submitting.");
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit(form);
      setForm((f) => ({ ...f, text: "", photo: null }));
      if (fileRef.current) fileRef.current.value = "";
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not submit the report.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 text-[11px] uppercase tracking-wide text-mist-400">Report an Incident</div>

      <label className="mb-2 block text-[11px] text-mist-400">Incident type</label>
      <select
        value={form.incident_type}
        onChange={(e) => update("incident_type", e.target.value)}
        className="mb-3 w-full rounded border border-ink-600 bg-ink-900 px-2 py-2 text-xs text-mist-50 outline-none focus:border-signal-teal"
      >
        {INCIDENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
      </select>

      <label className="mb-2 block text-[11px] text-mist-400">Description</label>
      <textarea
        value={form.text}
        onChange={(e) => update("text", e.target.value)}
        placeholder="What are you seeing? e.g. Water rising near the market road."
        rows={2}
        className="mb-3 w-full rounded border border-ink-600 bg-ink-900 px-2 py-2 text-xs text-mist-50 outline-none focus:border-signal-teal"
      />

      <label className="mb-2 block text-[11px] text-mist-400">Photo (optional, max 5 MB)</label>
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={(e) => update("photo", e.target.files?.[0] || null)}
        className="mb-3 block w-full text-[11px] text-mist-400 file:mr-2 file:rounded file:border-0 file:bg-ink-600 file:px-2 file:py-1 file:text-[11px] file:text-mist-50"
      />

      <div className="mb-3 grid grid-cols-2 gap-2">
        <div>
          <label className="mb-1 block text-[11px] text-mist-400">Latitude</label>
          <input type="number" step="0.00001" value={form.lat} onChange={(e) => update("lat", Number(e.target.value))}
            className="w-full rounded border border-ink-600 bg-ink-900 px-2 py-2 text-xs text-mist-50 outline-none focus:border-signal-teal" />
        </div>
        <div>
          <label className="mb-1 block text-[11px] text-mist-400">Longitude</label>
          <input type="number" step="0.00001" value={form.lon} onChange={(e) => update("lon", Number(e.target.value))}
            className="w-full rounded border border-ink-600 bg-ink-900 px-2 py-2 text-xs text-mist-50 outline-none focus:border-signal-teal" />
        </div>
      </div>

      <button type="button" onClick={useMyLocation} disabled={locating}
        className="mb-3 w-full rounded-md border border-ink-600 py-2 text-[11px] font-medium text-mist-200 hover:border-signal-teal hover:text-signal-teal disabled:opacity-50">
        {locating ? "Reading location…" : "Use my current location"}
      </button>

      <button type="submit" disabled={submitting}
        className="w-full rounded-md bg-signal-teal py-2 text-xs font-semibold text-ink-950 transition hover:opacity-90 disabled:opacity-50">
        {submitting ? "Submitting…" : "Submit Report"}
      </button>

      {error && <p className="mt-2 text-[11px] text-risk-critical">{error}</p>}
      {lastResult && (
        <p className="mt-2 text-[11px] text-risk-low">
          Saved to {lastResult.zone_name}. It will appear on the map and feed incident clustering.
          {lastResult.photo_url ? " Photo saved." : ""}
        </p>
      )}
    </form>
  );
}
