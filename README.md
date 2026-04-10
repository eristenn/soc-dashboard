# Behavior-Based SOC Dashboard

A Python-based SOC (Security Operations Center) simulation tool that monitors system and network activity, classifies user behavior, and detects suspicious patterns.

## Features

- Process monitoring using `psutil`
- Activity classification (Browsing, Gaming, Work, etc.)
- Network connection tracking
- Public IP + location enrichment
- Simple SOC-style alert detection
- Real-time dashboard with Flask
- Data visualization with Chart.js

## Tech Stack

- Python
- Flask
- psutil
- requests
- Chart.js

## How to Run

```bash
git clone https://github.com/YOUR_USERNAME/soc-dashboard.git
cd soc-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Google Calendar Embed

The dashboard can show a Google Calendar using a public embed URL. Set this environment variable if you want a custom calendar:

- `GOOGLE_CALENDAR_EMBED_URL`

If you do not set it, the app will use a default public embed sample.

Example (PowerShell):

```powershell
$env:GOOGLE_CALENDAR_EMBED_URL = 'https://calendar.google.com/calendar/embed?src=your-calendar-id&ctz=America%2FChicago'
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.
