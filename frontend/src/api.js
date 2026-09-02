import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: BASE_URL, timeout: 8000 });

export const api = {
  weather: () => client.get("/api/weather").then((r) => r.data),
  forecast: () => client.get("/api/forecast").then((r) => r.data),
  risks: () => client.get("/api/risks").then((r) => r.data),
  zones: () => client.get("/api/zones").then((r) => r.data),
  map: () => client.get("/api/map").then((r) => r.data),
  vulnerability: () => client.get("/api/vulnerability").then((r) => r.data),
  alerts: () => client.get("/api/alerts").then((r) => r.data),
  incidents: () => client.get("/api/incidents").then((r) => r.data),
  feedback: () => client.get("/api/feedback").then((r) => r.data),
  predictions: () => client.get("/api/predictions").then((r) => r.data),
  demo: () => client.get("/api/demo").then((r) => r.data),
  setDemo: (scenario) => client.post("/api/demo", { scenario }).then((r) => r.data),
  simulate: (rainfall_mm) => client.post("/api/simulation", { rainfall_mm }).then((r) => r.data),
  submitReport: (payload) => {
    if (payload?.photo instanceof File) {
      const form = new FormData();
      form.append("incident_type", payload.incident_type);
      form.append("text", payload.text || "");
      form.append("lat", String(payload.lat));
      form.append("lon", String(payload.lon));
      form.append("photo", payload.photo);
      return client.post("/api/reports/upload", form).then((r) => r.data);
    }
    return client.post("/api/reports", payload).then((r) => r.data);
  },
  submitFeedback: (payload) => client.post("/api/feedback", payload).then((r) => r.data),
  ask: (question) => client.post("/api/assistant", { question }).then((r) => r.data),
};

export default api;
