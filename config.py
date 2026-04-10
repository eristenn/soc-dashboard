import os

PROCESS_CATEGORIES = {
    'Gaming': [
        'steam.exe', 'epicgameslauncher.exe', 'riotclientservices.exe',
        'valorant.exe', 'eldenring.exe', 'game.exe',
    ],
    'Browsing': [
        'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe',
    ],
    'School/Work': [
        'code.exe', 'devenv.exe', 'winword.exe', 'excel.exe',
        'powerpnt.exe', 'acrobat.exe', 'acrord32.exe', 'notepad++.exe',
    ],
    'Job Search': [
        'outlook.exe', 'teams.exe', 'slack.exe',
    ],
}

KNOWN_SAFE_PROCESSES = {
    'system', 'svchost.exe', 'chrome.exe', 'firefox.exe', 'msedge.exe',
    'brave.exe', 'steam.exe', 'code.exe', 'devenv.exe', 'explorer.exe',
    'discord.exe', 'outlook.exe', 'teams.exe', 'slack.exe', 'python.exe',
}

CONNECTION_THRESHOLD = 40
STATE_FILE = 'data/state.json'
ALERT_LOG_FILE = 'logs/alerts.log'
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN', '')
REFRESH_SECONDS = int(os.getenv('REFRESH_SECONDS', '5'))
NEWS_FEED_URL = os.getenv('NEWS_FEED_URL', 'https://threatpost.com/feed/')
GOOGLE_CALENDAR_EMBED_URL = os.getenv('GOOGLE_CALENDAR_EMBED_URL', 'https://calendar.google.com/calendar/embed?src=eristenf%40gmail.com&ctz=America%2FChicago')
