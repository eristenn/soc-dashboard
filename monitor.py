import json
import os
from datetime import datetime

import psutil
import requests

from config import PROCESS_CATEGORIES, STATE_FILE


def ensure_state_file():
    os.makedirs(os.path.dirname(STATE_FILE) or '.', exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'last_ip': None,
                    'last_location': None,
                    'last_category': 'Unknown',
                    'usage_seconds': {},
                    'history': [],
                    'alerts_history': [],
                },
                f,
                indent=2,
            )


def load_state():
    ensure_state_file()
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_state(state):
    ensure_state_file()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def get_active_processes(limit=30):
    processes = []
    seen = set()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = (proc.info['name'] or '').lower()
            if name and name not in seen:
                seen.add(name)
                processes.append({'pid': proc.info['pid'], 'name': name})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes = sorted(processes, key=lambda x: x['name'])
    return processes[:limit]


def classify_process(process_name):
    process_name = process_name.lower()

    for category, keywords in PROCESS_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in process_name:
                return category

    return 'Unknown'


def classify_all_processes(processes):
    classified = []

    for proc in processes:
        category = classify_process(proc['name'])
        classified.append({'pid': proc['pid'], 'name': proc['name'], 'category': category})

    return classified


def build_category_summary(classified_processes):
    summary = {
        'Gaming': 0,
        'Browsing': 0,
        'School/Work': 0,
        'Job Search': 0,
        'Unknown': 0,
    }

    for proc in classified_processes:
        summary[proc['category']] = summary.get(proc['category'], 0) + 1

    return summary


def get_primary_activity(category_summary):
    priority_order = ['Gaming', 'School/Work', 'Job Search', 'Browsing', 'Unknown']

    best_category = 'Unknown'
    best_score = -1

    for category in priority_order:
        if category_summary.get(category, 0) > best_score:
            best_score = category_summary.get(category, 0)
            best_category = category

    return best_category


def get_connection_summary():
    try:
        connections = psutil.net_connections(kind='inet')
    except Exception:
        connections = []

    established = 0
    listening = 0
    process_connection_counts = {}
    top_connection_processes = []

    for conn in connections:
        status = getattr(conn, 'status', '')
        pid = getattr(conn, 'pid', None)

        if status == 'ESTABLISHED':
            established += 1
        elif status == 'LISTEN':
            listening += 1

        if pid:
            process_connection_counts[pid] = process_connection_counts.get(pid, 0) + 1

    for pid, count in process_connection_counts.items():
        try:
            proc = psutil.Process(pid)
            name = (proc.name() or '').lower()
            top_connection_processes.append({'pid': pid, 'name': name, 'count': count})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    top_connection_processes = sorted(
        top_connection_processes,
        key=lambda x: x['count'],
        reverse=True,
    )

    return {
        'total_connections': len(connections),
        'established': established,
        'listening': listening,
        'top_connection_processes': top_connection_processes[:10],
    }


def get_public_ip_info(token=''):
    url = 'https://ipinfo.io/json'
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        org = data.get('org', 'Unknown')
        lower_org = org.lower()
        vpn_detected = any(
            keyword in lower_org
            for keyword in [
                'vpn',
                'hosting',
                'digitalocean',
                'amazon',
                'aws',
                'microsoft',
                'google cloud',
                'oracle',
            ]
        )

        return {
            'ip': data.get('ip', 'Unknown'),
            'city': data.get('city', 'Unknown'),
            'region': data.get('region', 'Unknown'),
            'country': data.get('country', 'Unknown'),
            'org': org,
            'vpn_detected': vpn_detected,
        }
    except Exception:
        return {
            'ip': 'Unavailable',
            'city': 'Unavailable',
            'region': 'Unavailable',
            'country': 'Unavailable',
            'org': 'Unavailable',
            'vpn_detected': False,
        }


def update_usage_tracking(category, seconds=5):
    state = load_state()

    usage = state.get('usage_seconds', {})
    usage[category] = usage.get(category, 0) + seconds
    state['usage_seconds'] = usage

    history = state.get('history', [])
    history.append({'timestamp': datetime.now().strftime('%H:%M:%S'), 'category': category})

    state['history'] = history[-60:]
    save_state(state)
