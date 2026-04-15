import os

PROCESS_CATEGORIES = {
    'Gaming': [
        'steam', 'epicgameslauncher', 'riotclientservices',
        'valorant', 'eldenring', 'game',
    ],
    'Browsing': [
        'chrome', 'firefox', 'msedge', 'opera', 'brave',
    ],
    'School/Work': [
        'code', 'devenv', 'winword', 'excel',
        'powerpnt', 'acrobat', 'acrord32', 'notepad++',
    ],
    'Job Search': [
        'outlook', 'teams', 'slack',
    ],
}

KNOWN_SAFE_PROCESSES = {
    'system', 'svchost.exe', 'chrome.exe', 'firefox.exe', 'msedge.exe',
    'brave.exe', 'steam.exe', 'code.exe', 'devenv.exe', 'explorer.exe',
    'discord.exe', 'outlook.exe', 'teams.exe', 'slack.exe', 'python.exe',
}

CONNECTION_THRESHOLD = 40
UNKNOWN_PROCESS_CONNECTION_THRESHOLD = int(os.getenv('UNKNOWN_PROC_CONN_THRESHOLD', '10'))

STATE_FILE = 'data/state.json'
ALERT_LOG_FILE = 'logs/alerts.log'

IPINFO_TOKEN = os.getenv('IPINFO_TOKEN', '')
REFRESH_SECONDS = int(os.getenv('REFRESH_SECONDS', '30'))

IP_CACHE_TTL = int(os.getenv('IP_CACHE_TTL', '300'))
NEWS_CACHE_TTL = int(os.getenv('NEWS_CACHE_TTL', '600'))

NEWS_FEED_URL = os.getenv('NEWS_FEED_URL', 'https://threatpost.com/feed/')
GOOGLE_CALENDAR_EMBED_URL = os.getenv('GOOGLE_CALENDAR_EMBED_URL', '')