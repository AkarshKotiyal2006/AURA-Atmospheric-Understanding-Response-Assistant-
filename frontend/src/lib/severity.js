export const SEVERITY_COLORS = {
  LOW: "#3EDB84",
  MODERATE: "#F2C14E",
  HIGH: "#F2884B",
  CRITICAL: "#F0505A",
};

export const SEVERITY_BG = {
  LOW: "bg-risk-low/15 text-risk-low border-risk-low/30",
  MODERATE: "bg-risk-moderate/15 text-risk-moderate border-risk-moderate/30",
  HIGH: "bg-risk-high/15 text-risk-high border-risk-high/30",
  CRITICAL: "bg-risk-critical/15 text-risk-critical border-risk-critical/30",
};

export function severityColor(sev) {
  return SEVERITY_COLORS[sev] || "#7C8B9C";
}

export function hazardLabel(h) {
  return { flood: "Flood", heat: "Heat", aqi: "Air Quality" }[h] || h;
}
