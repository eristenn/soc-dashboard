\# Behavior-Based SOC Dashboard



A Python-based SOC (Security Operations Center) simulation tool that monitors system and network activity, classifies user behavior, and detects suspicious patterns.



\## Features



\- Process monitoring using psutil

\- Activity classification (Browsing, Gaming, Work, etc.)

\- Network connection tracking

\- Public IP + location enrichment

\- Simple SOC-style alert detection

\- Real-time dashboard with Flask

\- Data visualization with Chart.js



\## Tech Stack



\- Python

\- Flask

\- psutil

\- requests

\- Chart.js



\## How to Run



```bash

git clone https://github.com/YOUR\_USERNAME/soc-dashboard.git

cd soc-dashboard

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

python app.py

