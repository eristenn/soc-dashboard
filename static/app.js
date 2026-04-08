const categoryOrder = ['Gaming', 'Browsing', 'School/Work', 'Job Search', 'Unknown'];
const categoryMap = {
    Unknown: 0,
    Browsing: 1,
    'Job Search': 2,
    'School/Work': 3,
    Gaming: 4,
};
const categoryColor = {
    Gaming: '#ef4444',
    Browsing: '#2563eb',
    'School/Work': '#10b981',
    'Job Search': '#f59e0b',
    Unknown: '#94a3b8',
};

let usageChart;
let activityChart;

function init() {
    document.getElementById('simulate-btn').addEventListener('click', simulateAlert);
    initCharts();
    fetchDashboard();
    setInterval(fetchDashboard, window.REFRESH_SECONDS * 1000);
}

function initCharts() {
    const usageCtx = document.getElementById('usageChart').getContext('2d');
    const activityCtx = document.getElementById('activityChart').getContext('2d');

    usageChart = new Chart(usageCtx, {
        type: 'doughnut',
        data: {
            labels: categoryOrder,
            datasets: [
                {
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: categoryOrder.map((cat) => categoryColor[cat]),
                    borderWidth: 0,
                },
            ],
        },
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0',
                    },
                },
            },
        },
    });

    activityChart = new Chart(activityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Activity',
                    data: [],
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96, 165, 250, 0.2)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                },
            ],
        },
        options: {
            scales: {
                x: {
                    ticks: {
                        color: '#cbd5e1',
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        callback: (value) => {
                            return Object.keys(categoryMap).find((key) => categoryMap[key] === value) || '';
                        },
                        color: '#cbd5e1',
                    },
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
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
            if (!response.ok) {
                throw new Error('Simulate alert request failed');
            }
            return response.json();
        })
        .then(() => fetchDashboard())
        .catch((error) => console.error('Failed to simulate alert:', error));
}

function updateUI(data) {
    if (data.error) {
        console.error('API error:', data.error);
        return;
    }

    document.getElementById('ip').textContent = data.ip_info?.ip || 'Unavailable';
    document.getElementById('location').textContent = `${data.ip_info?.city || 'Unknown'}, ${data.ip_info?.region || 'Unknown'}, ${data.ip_info?.country || 'Unknown'}`;
    document.getElementById('org').textContent = data.ip_info?.org || 'Unknown';
    document.getElementById('vpn-status').textContent = data.ip_info?.vpn_detected ? 'Yes' : 'No';
    document.getElementById('category').textContent = data.current_category || 'Unknown';
    document.getElementById('total-connections').textContent = data.connection_summary?.total_connections || 0;
    document.getElementById('established').textContent = data.connection_summary?.established || 0;
    document.getElementById('listening').textContent = data.connection_summary?.listening || 0;

    updateList('category-summary', categoryOrder.map((category) => `${category}: ${data.category_summary[category] || 0}`));
    updateList('alerts-history', data.alerts_history.length ? data.alerts_history.slice(-10).map(formatAlert) : ['No alerts yet']);
    updateList(
        'processes',
        data.processes.slice(0, 15).map((proc) => `${proc.name} (PID ${proc.pid}) — ${proc.category}`),
    );
    updateList(
        'top-network-processes',
        data.connection_summary.top_connection_processes.length
            ? data.connection_summary.top_connection_processes.map((proc) => `${proc.name} (PID ${proc.pid}) — ${proc.count} conns`)
            : ['No network process activity'],
    );

    usageChart.data.datasets[0].data = categoryOrder.map((category) => data.usage_seconds[category] || 0);
    usageChart.update();

    const history = data.history.slice(-12);
    activityChart.data.labels = history.map((entry) => entry.timestamp);
    activityChart.data.datasets[0].data = history.map((entry) => categoryMap[entry.category] ?? 0);
    activityChart.update();
}

function formatAlert(alert) {
    return `${alert.timestamp} [${alert.severity}] ${alert.description}`;
}

function updateList(elementId, items) {
    const container = document.getElementById(elementId);
    container.innerHTML = items
        .map((item) => `<li>${item}</li>`)
        .join('');
}

document.addEventListener('DOMContentLoaded', init);
