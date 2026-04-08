from flask import Flask, jsonify, render_template

from config import IPINFO_TOKEN, REFRESH_SECONDS
from monitor import (
    build_category_summary,
    classify_all_processes,
    get_active_processes,
    get_connection_summary,
    get_primary_activity,
    get_public_ip_info,
    load_state,
    save_state,
    update_usage_tracking,
)
from rules import evaluate_alerts

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', refresh_seconds=REFRESH_SECONDS)


@app.route('/api/dashboard')
def dashboard_data():
    try:
        processes = get_active_processes()
        classified_processes = classify_all_processes(processes)
        category_summary = build_category_summary(classified_processes)
        category = get_primary_activity(category_summary)

        connection_summary = get_connection_summary()
        ip_info = get_public_ip_info(IPINFO_TOKEN)

        update_usage_tracking(category, seconds=REFRESH_SECONDS)
        new_alerts = evaluate_alerts(ip_info, category, connection_summary)
        state = load_state()

        return jsonify({
            'ip_info': ip_info,
            'current_category': category,
            'category_summary': category_summary,
            'processes': classified_processes,
            'connection_summary': connection_summary,
            'new_alerts': new_alerts,
            'alerts_history': state.get('alerts_history', []),
            'usage_seconds': state.get('usage_seconds', {}),
            'history': state.get('history', []),
            'refresh_seconds': REFRESH_SECONDS,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate_alert')
def simulate_alert():
    try:
        state = load_state()
        fake_alert = {
            'timestamp': 'SIMULATED',
            'severity': 'High',
            'description': 'Simulated suspicious activity: unusual outbound connection burst',
        }
        alerts = state.get('alerts_history', [])
        alerts.append(fake_alert)
        state['alerts_history'] = alerts[-100:]
        save_state(state)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
