import os
from datetime import datetime

from config import ALERT_LOG_FILE, CONNECTION_THRESHOLD, KNOWN_SAFE_PROCESSES
from monitor import load_state, save_state


def log_alert(alert):
    os.makedirs("logs", exist_ok=True)
    with open(ALERT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{alert['timestamp']} | {alert['severity']} | {alert['description']}\n"
        )


def add_alert(alerts, severity, description):
    alerts.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "severity": severity,
        "description": description
    })


def evaluate_alerts(ip_info, category, connection_summary):
    alerts = []
    state = load_state()

    last_ip = state.get("last_ip")
    last_location = state.get("last_location")
    last_category = state.get("last_category", "Unknown")

    current_ip = ip_info["ip"]
    current_location = f"{ip_info['city']}, {ip_info['region']}, {ip_info['country']}"

    if last_ip and current_ip != last_ip:
        add_alert(alerts, "Medium", f"Public IP changed from {last_ip} to {current_ip}")

    if last_location and current_location != last_location:
        add_alert(alerts, "Low", f"Location changed from {last_location} to {current_location}")

    if ip_info.get("vpn_detected"):
        add_alert(alerts, "Low", "Possible VPN or cloud-hosted public IP detected")

    if connection_summary["total_connections"] > CONNECTION_THRESHOLD:
        add_alert(
            alerts,
            "High",
            f"High connection count detected: {connection_summary['total_connections']}"
        )

    if last_category != "Unknown" and category != last_category:
        add_alert(alerts, "Low", f"Activity changed from {last_category} to {category}")

    for proc in connection_summary.get("top_connection_processes", []):
        if proc["name"] not in KNOWN_SAFE_PROCESSES and proc["count"] >= 3:
            add_alert(
                alerts,
                "Medium",
                f"Process {proc['name']} (PID {proc['pid']}) has {proc['count']} network connections"
            )

    state["last_ip"] = current_ip
    state["last_location"] = current_location
    state["last_category"] = category

    alert_history = state.get("alerts_history", [])
    if alerts:
        alert_history.extend(alerts)
    state["alerts_history"] = alert_history[-100:]

    save_state(state)

    for alert in alerts:
        log_alert(alert)

    return alerts