const categoryOrder = ['Gaming', 'Browsing', 'School/Work', 'Job Search'];
const categoryMap = {
    Browsing: 0,
    'Job Search': 1,
    'School/Work': 2,
    Gaming: 3,
};
const categoryColor = {
    Gaming: '#ef4444',
    Browsing: '#2563eb',
    'School/Work': '#10b981',
    'Job Search': '#f59e0b',
};

let usageChart;

function init() {
    document.getElementById('simulate-btn').addEventListener('click', simulateAlert);
    initCharts();
    fetchDashboard();
    setInterval(fetchDashboard, window.REFRESH_SECONDS * 1000);
}

function initCharts() {
    const usageCtx = document.getElementById('usageChart').getContext('2d');

    usageChart = new Chart(usageCtx, {
        type: 'bar',
        data: {
            labels: categoryOrder,
            datasets: [
                {
                    label: 'Minutes spent',
                    data: [0, 0, 0, 0],
                    backgroundColor: categoryOrder.map((cat) => categoryColor[cat]),
                    borderRadius: 12,
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    ticks: {
                        color: '#cbd5e1',
                        maxRotation: 0,
                        minRotation: 0,
                    },
                    grid: { display: false },
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(148, 163, 184, 0.08)' },
                },
            },
            plugins: {
                legend: { display: false },
            },
        },
    });
}

async function fetchDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        if (!response.ok) {
            throw new Error('Dashboard request failed');
        }
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Unable to load dashboard data:', error);
    }
}

function simulateAlert() {
    fetch('/api/simulate_alert')
        .then((response) => {
            if (!response.ok) throw new Error('Simulate alert request failed');
            return response.json();
        })
        .then(() => fetchDashboard())
        .catch((error) => console.error('Failed to simulate alert:', error));
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
}

function updateUI(data) {
    if (data.error) {
        console.error('API error:', data.error);
        return;
    }

    const currentCategory = data.current_category === 'Unknown' ? 'No activity' : data.current_category;
    document.getElementById('current-activity').textContent = currentCategory;
    document.getElementById('elapsed-time').textContent = formatDuration(data.elapsed_seconds || 0);
    document.getElementById('ip').textContent = data.ip_info?.ip || 'Unavailable';
    document.getElementById('location').textContent = `${data.ip_info?.city || 'Unknown'}, ${data.ip_info?.region || 'Unknown'}, ${data.ip_info?.country || 'Unknown'}`;
    document.getElementById('org').textContent = data.ip_info?.org || 'Unknown';
    document.getElementById('vpn-status').textContent = data.ip_info?.vpn_detected ? 'Yes' : 'No';
    document.getElementById('category').textContent = currentCategory;
    document.getElementById('total-connections').textContent = data.connection_summary?.total_connections || 0;
    document.getElementById('established').textContent = data.connection_summary?.established || 0;
    document.getElementById('listening').textContent = data.connection_summary?.listening || 0;

    updateList('category-summary', ['Gaming: ' + (data.category_summary['Gaming'] || 0), 'Browsing: ' + (data.category_summary['Browsing'] || 0), 'School/Work: ' + (data.category_summary['School/Work'] || 0), 'Job Search: ' + (data.category_summary['Job Search'] || 0), 'Unknown: ' + (data.category_summary['Unknown'] || 0)]);
    updateList('alerts-history', data.alerts_history.length ? data.alerts_history.slice(-10).map(formatAlert) : ['No alerts yet']);
    updateList('processes', data.processes.slice(0, 15).map((proc) => `${proc.name} (PID ${proc.pid}) — ${proc.category}`));
    updateList('top-network-processes', data.connection_summary.top_connection_processes.length ? data.connection_summary.top_connection_processes.map((proc) => `${proc.name} (PID ${proc.pid}) — ${proc.count} conns`) : ['No network process activity']);
    updateNewsFeed(data.news_items || []);

    usageChart.data.datasets[0].data = categoryOrder.map((category) => Math.round((data.usage_seconds[category] || 0) / 60));
    usageChart.update();
}


function updateNewsFeed(newsItems) {
    if (!newsItems || !newsItems.length) {
        updateList('news-feed', ['Unable to fetch news at the moment.']);
        return;
    }

    const items = newsItems.map((item) => {
        const date = item.pubDate ? `<span class="news-date">${item.pubDate}</span>` : '';
        return `<li><a href="${item.link}" target="_blank" rel="noreferrer">${item.title}</a>${date}</li>`;
    });
    document.getElementById('news-feed').innerHTML = items.join('');
}

function formatAlert(alert) {
    return `${alert.timestamp} [${alert.severity}] ${alert.description}`;
}

function updateList(elementId, items) {
    const container = document.getElementById(elementId);
    container.innerHTML = items.map((item) => `<li>${item}</li>`).join('');
}

document.addEventListener('DOMContentLoaded', init);
