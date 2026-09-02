import re

FALLBACK = "I don't have enough data to answer that."


def _find_zone(question: str, zones: list):
    q = question.lower()
    for z in zones:
        if z["zone_name"].lower() in q or z["zone_id"].lower() in q:
            return z
    # allow "zone 1".."zone 6" style references
    m = re.search(r"zone\s*(\d+)", q)
    if m:
        idx = int(m.group(1))
        for z in zones:
            if z["zone_id"] == f"z{idx}":
                return z
    return None


def answer(question: str, zones: list, weather: dict, alerts: list, simulation_zones: list | None = None):
    if not question or not question.strip():
        return FALLBACK
    q = question.lower().strip()

    if not zones:
        return FALLBACK

    # "what is the biggest risk right now?"
    if any(p in q for p in ["biggest risk", "top risk", "highest risk", "worst risk"]):
        top = max(zones, key=lambda z: z["overall_score"])
        return (f"The highest current risk is {top['top_hazard'].upper()} in {top['zone_name']} "
                f"({top['overall_severity']}, score {top['overall_score']}/100, confidence {top['confidence']}%).")

    # "why is Zone X high risk?"
    if "why" in q:
        zone = _find_zone(q, zones)
        if zone:
            factors = zone[zone["top_hazard"]]["factors"]
            return (f"{zone['zone_name']} is {zone['overall_severity']} for {zone['top_hazard']}. "
                     f"Contributing factors: " + "; ".join(factors) + ".")
        return FALLBACK

    # "which areas are vulnerable?"
    if "vulnerable" in q:
        high = [z for z in zones if z["overall_severity"] in ("HIGH", "CRITICAL")]
        if not high:
            return "No zones are currently at HIGH or CRITICAL risk based on the latest data."
        names = ", ".join(f"{z['zone_name']} ({z['overall_severity']})" for z in high)
        return f"Currently vulnerable zones: {names}."

    # What-if rainfall questions use a temporary calculation from the same
    # application data as the simulator.
    if "rainfall reaches" in q or ("what happens if" in q and "mm" in q) or ("rainfall" in q and "mm" in q):
        m = re.search(r"(\d+(?:\.\d+)?)\s*mm", q)
        if m and simulation_zones:
            mm = float(m.group(1))
            current_top = max(zones, key=lambda z: z["flood"]["score"])
            sim_top = max(simulation_zones, key=lambda z: z["flood"]["score"])
            ranked = sorted(simulation_zones, key=lambda z: z["flood"]["score"], reverse=True)[:3]
            details = "; ".join(
                f"{z['zone_name']} {z['flood']['score']}/100 ({z['flood']['severity']})"
                for z in ranked
            )
            return (
                f"At {mm:g} mm rainfall, modeled flood risk peaks in {sim_top['zone_name']} "
                f"at {sim_top['flood']['score']}/100 ({sim_top['flood']['severity']}). "
                f"The current highest flood-risk zone is {current_top['zone_name']} at "
                f"{current_top['flood']['score']}/100. Top simulated zones: {details}."
            )
        return FALLBACK

    # "why is AQI risk high" / general hazard question
    for hazard in ("flood", "heat", "aqi"):
        if hazard in q:
            zone = _find_zone(q, zones)
            candidates = [zone] if zone else zones
            worst = max(candidates, key=lambda z: z[hazard]["score"])
            factors = worst[hazard]["factors"]
            return (f"{hazard.upper()} risk in {worst['zone_name']} is {worst[hazard]['severity']} "
                     f"(score {worst[hazard]['score']}/100). Reasons: " + "; ".join(factors) + ".")

    # "what should commuters know?"
    for context in ("commuter", "citizen", "resident", "authority"):
        if context in q:
            if not alerts:
                return "There are no active alerts for that audience right now."
            msgs = [a["messages"][context] for a in alerts if context in a.get("messages", {})]
            return " ".join(msgs[:3]) if msgs else "No active alerts for that audience right now."

    # "explain this alert"
    if "explain" in q and "alert" in q:
        if not alerts:
            return "There are no active alerts to explain right now."
        a = alerts[0]
        return f"{a['zone_name']} - {a['hazard'].upper()} {a['severity']}: " + "; ".join(a["factors"]) + "."

    return FALLBACK
