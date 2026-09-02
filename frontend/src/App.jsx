import { useEffect, useState, useCallback } from "react";
import api from "./api";
import ControlBar from "./components/ControlBar";
import TopSummary from "./components/TopSummary";
import ZoneGrid from "./components/ZoneGrid";
import ZoneDetail from "./components/ZoneDetail";
import MapView from "./components/MapView";
import Simulator from "./components/Simulator";
import AlertsPanel from "./components/AlertsPanel";
import ReportForm from "./components/ReportForm";
import Assistant from "./components/Assistant";
import FeedbackPanel from "./components/FeedbackPanel";
import IncidentsPanel from "./components/IncidentsPanel";

export default function App() {
  const [scenario, setScenario] = useState("NORMAL");
  const [context, setContext] = useState("citizen");
  const [risks, setRisks] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [selectedZoneId, setSelectedZoneId] = useState(null);
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simLoading, setSimLoading] = useState(false);
  const [lastReport, setLastReport] = useState(null);
  const [error, setError] = useState(null);

  const refreshAll = useCallback(async () => {
    try {
      const [risksRes, mapRes, alertsRes, feedbackRes, demoRes] = await Promise.all([
        api.risks(), api.map(), api.alerts(), api.feedback(), api.demo(),
      ]);
      setRisks(risksRes);
      setMapData(mapRes);
      setAlerts(alertsRes.alerts);
      setFeedback(feedbackRes);
      setScenario(demoRes.current);
      setError(null);
      if (!selectedZoneId && risksRes.zones.length) {
        const topMatch = risksRes.zones.find((z) => z.zone_name === risksRes.top_risk.zone);
        setSelectedZoneId((topMatch || risksRes.zones[0]).zone_id);
      }
    } catch (e) {
      setError("Could not reach the AURA backend. Is docker compose running?");
    } finally {
      setLoading(false);
    }
  }, [selectedZoneId]);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleScenario = async (s) => {
    setLoading(true);
    setSimResult(null);
    try {
      await api.setDemo(s);
      await refreshAll();
    } catch (e) {
      setError(e?.response?.data?.detail || "Could not change the AURA scenario.");
      setLoading(false);
    }
  };

  const handleSimulate = async (mm) => {
    setSimLoading(true);
    try {
      const result = await api.simulate(mm);
      setSimResult(result);
      await refreshAll();
    } catch (e) {
      setError(e?.response?.data?.detail || "Could not run the rainfall simulation.");
    } finally {
      setSimLoading(false);
    }
  };

  const handleReport = async (payload) => {
    const res = await api.submitReport(payload);
    setLastReport(res);
    await refreshAll();
  };

  const handleFeedback = async (payload) => {
    await api.submitFeedback(payload);
    const fb = await api.feedback();
    setFeedback(fb);
  };

  const selectedZone = risks?.zones.find((z) => z.zone_id === selectedZoneId) || null;
  const topZone = risks?.zones.find((z) => z.zone_name === risks?.top_risk?.zone) || risks?.zones?.[0] || null;

  return (
    <div className="min-h-screen bg-ink-900">
      <ControlBar
        scenario={scenario}
        onScenario={handleScenario}
        context={context}
        onContext={setContext}
        dataSource={risks?.data_source}
        loading={loading}
      />

      <main className="mx-auto max-w-[1400px] space-y-4 px-6 py-6">
        {error && (
          <div className="rounded-md border border-risk-critical/40 bg-risk-critical/10 px-4 py-2 text-xs text-risk-critical">
            {error}
          </div>
        )}

        {risks && <ZoneWeather risks={risks} topZone={topZone} />}

        {mapData && risks && (
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <div className="xl:col-span-2">
              <MapView mapData={mapData} selectedZoneId={selectedZoneId} onSelectZone={setSelectedZoneId} />
            </div>
            <ZoneDetail zone={selectedZone} />
          </div>
        )}

        {risks && <ZoneGrid zones={risks.zones} selectedZoneId={selectedZoneId} onSelect={setSelectedZoneId} />}

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Simulator onSimulate={handleSimulate} result={simResult} loading={simLoading} />
          <AlertsPanel alerts={alerts} context={context} />
          <Assistant onAsk={api.ask} />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <ReportForm onSubmit={handleReport} lastResult={lastReport} />
          <IncidentsPanel incidents={mapData?.community_incidents || []} />
          {feedback && risks && (
            <FeedbackPanel feedback={feedback} zones={risks.zones} onSubmit={handleFeedback} />
          )}
        </div>

        <footer className="py-6 text-center text-[10px] text-mist-400">
          AURA is a decision-support prototype, not an authoritative weather forecasting system.
        </footer>
      </main>
    </div>
  );
}

// Fetches the current weather snapshot and feeds it into TopSummary; re-fetches
// whenever the risk data changes (scenario switch, simulation, or poll interval).
function ZoneWeather({ risks, topZone }) {
  const [weather, setWeather] = useState(null);
  useEffect(() => {
    api.weather().then(setWeather).catch(() => {});
  }, [risks]);
  return <TopSummary weather={weather} topZone={topZone} />;
}
