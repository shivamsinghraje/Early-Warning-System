function createDashboardPlot(data) {
    const plotDiv = document.getElementById('mainPlot');

    // Prepare data for plotting
    const timestamps = data.map(d => d.timestamp);
    const actualValues = data.map(d => d.actualValue);
    const forecastedValues = data.map(d => d.forecastedValue);
    const anomalies = data.filter(d => d.status === 'Anomaly');

    // Actual values trace (dotted line)
    const actualTrace = {
        x: timestamps,
        y: actualValues,
        type: 'scatter',
        mode: 'lines',
        name: 'Actual',
        line: {
            dash: 'dot',
            color: '#64748b',
            width: 2
        }
    };

    // Forecasted values trace (solid line)
    const forecastTrace = {
        x: timestamps,
        y: forecastedValues,
        type: 'scatter',
        mode: 'lines',
        name: 'Forecasted',
        line: {
            color: '#2563eb',
            width: 2
        }
    };

    // Anomalies trace (red dots)
    const anomalyTrace = {
        x: anomalies.map(a => a.timestamp),
        y: anomalies.map(a => a.actualValue),
        type: 'scatter',
        mode: 'markers',
        name: 'Anomalies',
        marker: {
            color: '#ef4444',
            size: 8,
            symbol: 'circle'
        }
    };

    const traces = [actualTrace, forecastTrace];
    if (anomalies.length > 0) {
        traces.push(anomalyTrace);
    }

    const layout = {
        title: 'Time Series Analysis',
        xaxis: {
            title: 'Timestamp',
            type: 'date',
            rangeslider: { visible: true }
        },
        yaxis: {
            title: 'Value'
        },
        hovermode: 'x unified',
        legend: {
            x: 0,
            y: 1,
            bgcolor: 'rgba(255, 255, 255, 0.8)'
        },
        margin: {
            l: 50,
            r: 50,
            t: 50,
            b: 50
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape'],
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    Plotly.newPlot(plotDiv, traces, layout, config);
}

// Additional plotting utilities
function createComparisonPlot(beforeData, afterData, divId) {
    const trace1 = {
        y: beforeData,
        type: 'box',
        name: 'Before Cleaning',
        marker: { color: '#64748b' }
    };

    const trace2 = {
        y: afterData,
        type: 'box',
        name: 'After Cleaning',
        marker: { color: '#2563eb' }
    };

    const layout = {
        title: 'Data Distribution Comparison',
        yaxis: { title: 'Values' }
    };

    Plotly.newPlot(divId, [trace1, trace2], layout);
}

function createHistogram(data, divId, title) {
    const trace = {
        x: data,
        type: 'histogram',
        marker: {
            color: '#2563eb',
            line: {
                color: '#1e40af',
                width: 1
            }
        }
    };

    const layout = {
        title: title,
        xaxis: { title: 'Value' },
        yaxis: { title: 'Frequency' },
        bargap: 0.05
    };

    Plotly.newPlot(divId, [trace], layout);
}

// Auto-refresh for live data
let autoRefreshInterval = null;

function startAutoRefresh(projectId, intervalSeconds = 30) {
    stopAutoRefresh(); // Clear any existing interval

    autoRefreshInterval = setInterval(async () => {
        try {
            await api.fetchLiveAndPredict(projectId);
            const timeRange = document.getElementById('timeRange').value;
            await loadDashboardData(projectId, timeRange);

            // Update live indicator
            const indicator = document.getElementById('liveIndicator');
            if (indicator) {
                indicator.textContent = '● Live';
                indicator.style.color = '#22c55e';
            }
        } catch (error) {
            console.error('Auto-refresh error:', error);
        }
    }, intervalSeconds * 1000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;

        const indicator = document.getElementById('liveIndicator');
        if (indicator) {
            indicator.textContent = '○ Paused';
            indicator.style.color = '#64748b';
        }
    }
}