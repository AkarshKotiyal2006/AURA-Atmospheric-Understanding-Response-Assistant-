import { useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Circle, Popup, Marker } from "react-leaflet";
import L from "leaflet";
import { severityColor } from "../lib/severity";

const HAZARD_LAYERS = [
  { id: "overall_severity", label: "Risk Zones" },
  { id: "flood", label: "Flood" },
  { id: "heat", label: "Heat" },
  { id: "aqi", label: "AQI" },
];

const ASSET_COLORS = {
  hospital: "#F0505A",
  school: "#F2C14E",
  road: "#7C8B9C",
  transit: "#3ED6C4",
  residential: "#B7C3D0",
};

function assetIcon(color) {
  return L.divIcon({
    className: "",
    html: `<div style="width:10px;height:10px;border-radius:2px;background:${color};border:1px solid #0A0E14"></div>`,
    iconSize: [10, 10],
  });
}

export default function MapView({ mapData, selectedZoneId, onSelectZone }) {
  const [hazardLayer, setHazardLayer] = useState("overall_severity");
  const [showVulnerability, setShowVulnerability] = useState(true);
  const [showIncidents, setShowIncidents] = useState(true);

  if (!mapData) return null;

  const center = [28.4744, 77.504];

  const severityFor = (zone) => {
    if (hazardLayer === "overall_severity") return zone.overall_severity;
    const score = zone[`${hazardLayer}_score`];
    if (score >= 80) return "CRITICAL";
    if (score >= 60) return "HIGH";
    if (score >= 40) return "MODERATE";
    return "LOW";
  };

  return (
    <div className="rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="text-[11px] uppercase tracking-wide text-mist-400">Interactive Risk Map</div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1 rounded-md border border-ink-600 bg-ink-900 p-1">
            {HAZARD_LAYERS.map((l) => (
              <button
                key={l.id}
                onClick={() => setHazardLayer(l.id)}
                className={`rounded px-2.5 py-1 text-[11px] font-medium transition ${
                  hazardLayer === l.id ? "bg-signal-teal text-ink-950" : "text-mist-400 hover:text-mist-50"
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
          <label className="flex items-center gap-1 text-[11px] text-mist-400">
            <input type="checkbox" checked={showVulnerability} onChange={(e) => setShowVulnerability(e.target.checked)} />
            Vulnerability
          </label>
          <label className="flex items-center gap-1 text-[11px] text-mist-400">
            <input type="checkbox" checked={showIncidents} onChange={(e) => setShowIncidents(e.target.checked)} />
            Community Incidents
          </label>
        </div>
      </div>

      <div className="h-[420px] overflow-hidden rounded-md border border-ink-600">
        <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {mapData.zones.map((z) => {
            const sev = severityFor(z);
            const color = severityColor(sev);
            const isSelected = selectedZoneId === z.zone_id;
            return (
              <Circle
                key={z.zone_id}
                center={[z.lat, z.lon]}
                radius={z.radius_m}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: isSelected ? 0.35 : 0.18,
                  weight: isSelected ? 3 : 1.5,
                }}
                eventHandlers={{ click: () => onSelectZone(z.zone_id) }}
              >
                <Popup>
                  <div style={{ fontFamily: "IBM Plex Sans, sans-serif" }}>
                    <strong>{z.name}</strong>
                    <div>Overall: {z.overall_severity} ({z.overall_score}/100)</div>
                    <div>Flood {z.flood_score} · Heat {z.heat_score} · AQI {z.aqi_score}</div>
                  </div>
                </Popup>
              </Circle>
            );
          })}

          {showVulnerability &&
            mapData.vulnerability_assets.map((a) => (
              <Marker key={a.id} position={[a.lat, a.lon]} icon={assetIcon(ASSET_COLORS[a.type] || "#7C8B9C")}>
                <Popup>
                  <div style={{ fontFamily: "IBM Plex Sans, sans-serif" }}>
                    <strong>{a.name}</strong>
                    <div>Type: {a.type}</div>
                    <div>{a.exposure_note}</div>
                  </div>
                </Popup>
              </Marker>
            ))}

          {showIncidents &&
            mapData.community_incidents.map((inc) => (
              <CircleMarker
                key={inc.incident_id}
                center={[inc.center_lat, inc.center_lon]}
                radius={6 + Math.min(inc.report_count, 6)}
                pathOptions={{ color: "#3ED6C4", fillColor: "#3ED6C4", fillOpacity: 0.6 }}
              >
                <Popup>
                  <div style={{ fontFamily: "IBM Plex Sans, sans-serif" }}>
                    <strong>{inc.incident_type}</strong>
                    <div>Reports: {inc.report_count}</div>
                    <div>Zone: {inc.zone_name}</div>
                    <div>Status: {inc.status}</div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
        </MapContainer>
      </div>
    </div>
  );
}
