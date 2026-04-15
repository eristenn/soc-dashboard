import os
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template

from config import (
    GOOGLE_CALENDAR_EMBED_URL,
    IP_CACHE_TTL,
    IPINFO_TOKEN,
    NEWS_CACHE_TTL,
    NEWS_FEED_URL,
    REFRESH_SECONDS,
)
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
app.secret_key = os.getenv('FLASK_SECRET_KEY') or os.urandom(24)

# ── Caches ────────────────────────────────────────────────────────────────────
_ip_cache   = {'data': None, 'fetched_at': None}
_news_cache = {'items': [],  'fetched_at': None}


def get_cached_ip_info():
    now = datetime.utcnow()
    if _ip_cache['data'] and _ip_cache['fetched_at']:
        age = (now - _ip_cache['fetched_at']).total_seconds()
        if age < IP_CACHE_TTL:
            return _ip_cache['data']
    data = get_public_ip_info(IPINFO_TOKEN)
    _ip_cache['data'] = data
    _ip_cache['fetched_at'] = now
    return data


def get_cached_news():
    now = datetime.utcnow()
    if _news_cache['fetched_at']:
        age = (now - _news_cache['fetched_at']).total_seconds()
        if age < NEWS_CACHE_TTL:
            return _news_cache['items']
    items = fetch_news_items(NEWS_FEED_URL)
    _news_cache['items'] = items
    _news_cache['fetched_at'] = now
    return items


# ── News ──────────────────────────────────────────────────────────────────────
def fetch_news_items(feed_url, limit=5):
    if not feed_url:
        return []
    try:
        response = requests.get(
            feed_url,
            timeout=5,
            headers={'User-Agent': 'SOC Dashboard/1.0'},
        )
        response.raise_for_status()
        root    = ET.fromstring(response.content)
        entries = root.findall('.//item') or root.findall('.//entry')
        news_items = []

        for entry in entries[:limit]:
            title    = entry.find('title')
            link     = entry.find('link')
            pub_date = entry.find('pubDate') or entry.find('updated')

            news_items.append({
                'title':   title.text.strip() if title is not None and title.text else 'Untitled',
                'link':    (link.text or link.get('href', '') if link is not None else '') or '#',
                'pubDate': pub_date.text.strip() if pub_date is not None and pub_date.text else '',
            })

        return news_items
    except Exception as e:
        app.logger.warning('News feed fetch failed: %s', e)
        return []


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_elapsed_seconds(state, category):
    start_time      = state.get('current_category_start')
    stored_category = state.get('current_category', 'Unknown')

    if stored_category != category or not start_time:
        return 0

    try:
        started = datetime.fromisoformat(start_time.rstrip('Z'))
        return int((datetime.utcnow() - started).total_seconds())
    except ValueError:
        return 0


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template(
        'index.html',
        refresh_seconds=REFRESH_SECONDS,
        google_calendar_embed_url=GOOGLE_CALENDAR_EMBED_URL,
    )


@app.route('/api/dashboard')
def dashboard_data():
    try:
        processes            = get_active_processes()
        classified_processes = classify_all_processes(processes)
        category_summary     = build_category_summary(classified_processes)
        category             = get_primary_activity(category_summary)
        connection_summary   = get_connection_summary()
        ip_info              = get_cached_ip_info()

        # Load state BEFORE update so elapsed time is accurate
        state           = load_state()
        elapsed_seconds = get_elapsed_seconds(state, category)

        update_usage_tracking(category, seconds=REFRESH_SECONDS)
        evaluate_alerts(ip_info, category, connection_summary)

        # Reload after mutations
        state      = load_state()
        news_items = get_cached_news()

        return jsonify({
            'ip_info':             ip_info,
            'current_category':    category,
            'category_summary':    category_summary,
            'processes':           classified_processes,
            'connection_summary':  connection_summary,
            'alerts_history':      state.get('alerts_history', []),
            'usage_seconds':       state.get('usage_seconds', {}),
            'history':             state.get('history', []),
            'elapsed_seconds':     elapsed_seconds,
            'news_items':          news_items,
            'refresh_seconds':     REFRESH_SECONDS,
        })
    except Exception as e:
        app.logger.error('Dashboard error: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/simulate_alert', methods=['POST'])
def simulate_alert():
    try:
        state = load_state()
        fake_alert = {
            'timestamp':   datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'),
            'severity':    'High',
            'description': 'Simulated suspicious activity: unusual outbound connection burst',
        }
        alerts = state.get('alerts_history', [])
        alerts.append(fake_alert)
        state['alerts_history'] = alerts[-100:]
        save_state(state)
        return jsonify({'status': 'ok'})
    except Exception as e:
        app.logger.error('Simulate alert error: %s', e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)