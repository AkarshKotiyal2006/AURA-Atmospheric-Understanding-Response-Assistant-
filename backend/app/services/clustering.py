import math
import datetime as dt

TIME_WINDOW_HOURS = 6
DISTANCE_THRESHOLD_M = 700


def _haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def haversine_m(lat1, lon1, lat2, lon2):
    return _haversine_m(lat1, lon1, lat2, lon2)


def cluster_reports(reports):
    """Groups reports sharing incident type + geographic proximity + time proximity.
    reports: list of dicts with id, incident_type, lat, lon, created_at (datetime), zone_id, zone_name.
    Returns list of incident clusters."""
    unclustered = sorted(reports, key=lambda r: r["created_at"])
    clusters = []

    for report in unclustered:
        placed = False
        for cluster in clusters:
            same_type = cluster["incident_type"] == report["incident_type"]
            near = _haversine_m(cluster["center_lat"], cluster["center_lon"], report["lat"], report["lon"]) <= DISTANCE_THRESHOLD_M
            recent = abs((report["created_at"] - cluster["latest_time"]).total_seconds()) <= TIME_WINDOW_HOURS * 3600
            if same_type and near and recent:
                cluster["reports"].append(report)
                n = len(cluster["reports"])
                cluster["center_lat"] = (cluster["center_lat"] * (n - 1) + report["lat"]) / n
                cluster["center_lon"] = (cluster["center_lon"] * (n - 1) + report["lon"]) / n
                cluster["latest_time"] = max(cluster["latest_time"], report["created_at"])
                cluster["zone_id"] = report["zone_id"]
                cluster["zone_name"] = report["zone_name"]
                placed = True
                break
        if not placed:
            clusters.append(dict(
                incident_type=report["incident_type"],
                center_lat=report["lat"], center_lon=report["lon"],
                latest_time=report["created_at"],
                zone_id=report["zone_id"], zone_name=report["zone_name"],
                reports=[report],
            ))

    incidents = []
    for i, c in enumerate(clusters, start=1):
        incidents.append(dict(
            incident_id=f"inc-{i}",
            incident_type=c["incident_type"],
            report_count=len(c["reports"]),
            zone_id=c["zone_id"],
            zone_name=c["zone_name"],
            center_lat=round(c["center_lat"], 5),
            center_lon=round(c["center_lon"], 5),
            latest_report_at=c["latest_time"].isoformat(),
            status="EMERGING" if len(c["reports"]) >= 3 else "REPORTED",
            report_ids=[r["id"] for r in c["reports"]],
        ))
    return incidents
