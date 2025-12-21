// frontend/js/projects.js
document.addEventListener('DOMContentLoaded', () => {
    // Check which page we're on
    if (document.getElementById('addProjectForm')) {
        initAddProject();
    } else if (document.getElementById('projectsGrid')) {
        loadProjects();
    }
});

// Add Project Page
function initAddProject() {
    const form = document.getElementById('addProjectForm');
    const liveCheckbox = document.getElementById('isLiveEnabled');
    const liveConfig = document.getElementById('liveConfig');
    const progressSection = document.getElementById('progressSection');

    // Toggle live config
    liveCheckbox.addEventListener('change', (e) => {
        liveConfig.style.display = e.target.checked ? 'block' : 'none';
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fileInput = document.getElementById('dataFile');
        const file = fileInput.files[0];

        if (!file) {
            showNotification('Please select a file', 'error');
            return;
        }

        try {
            validateFile(file);

            const formData = new FormData();
            formData.append('file', file);

            // Get form values
            const projectData = {
                projectName: document.getElementById('projectName').value,
                projectId: document.getElementById('projectId').value,
                datetimeCol: document.getElementById('datetimeCol').value,
                targetCol: document.getElementById('targetCol').value,
                gndCols: document.getElementById('gndCols').value.split(',').map(s => s.trim()),
                isLiveEnabled: document.getElementById('isLiveEnabled').checked,
                apiUrl: document.getElementById('apiUrl').value,
                apiToken: document.getElementById('apiToken').value
            };

            formData.append('data', JSON.stringify(projectData));

            // Show progress
            form.style.display = 'none';
            progressSection.style.display = 'block';
            updateProgress(0, 'Uploading file...');

            const result = await api.addProject(formData);

            updateProgress(100, 'Project created successfully!');
            showNotification('Project created successfully', 'success');

            setTimeout(() => {
                window.location.href = 'view-projects.html';
            }, 2000);

        } catch (error) {
            showNotification(error.message, 'error');
            form.style.display = 'block';
            progressSection.style.display = 'none';
        }
    });

    function updateProgress(percent, status) {
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressStatus').textContent = status;
    }
}

// View Projects Page
async function loadProjects() {
    try {
        const projects = await api.getProjects();
        const projectsGrid = document.getElementById('projectsGrid');
        const noProjects = document.getElementById('noProjects');

        if (projects.length === 0) {
            projectsGrid.style.display = 'none';
            noProjects.style.display = 'block';
            return;
        }

        projectsGrid.innerHTML = projects.map(project => createProjectCard(project)).join('');

    } catch (error) {
        showNotification('Failed to load projects', 'error');
    }
}

function createProjectCard(project) {
    const statusClass = project.isLiveEnabled ? 'status-active' : 'status-inactive';
    const statusText = project.isLiveEnabled ? 'Live' : 'Offline';

    return `
        <div class="project-card">
            <div class="project-header">
                <h3>${project.projectName}</h3>
                <span class="project-status ${statusClass}">${statusText}</span>
            </div>
            <div class="project-info">
                <p><strong>ID:</strong> ${project.projectId}</p>
                <p><strong>Created:</strong> ${formatDate(project.createdAt)}</p>
                <p><strong>Target:</strong> ${project.targetCol}</p>
            </div>
            <div class="project-actions">
                <a href="project-dashboard.html?id=${project.projectId}" class="btn btn-primary">
                    View Dashboard
                </a>
                <button class="btn btn-danger" onclick="confirmDelete('${project.projectId}', '${project.projectName}')">
                    Delete
                </button>
            </div>
        </div>
    `;
}

// Delete functionality
function confirmDelete(projectId, projectName) {
    const modal = document.getElementById('deleteModal');
    document.getElementById('deleteProjectName').textContent = projectName;
    document.getElementById('deleteProjectId').value = projectId;
    modal.style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    document.getElementById('deletePassword').value = '';
}

// Handle delete form
document.addEventListener('DOMContentLoaded', () => {
    const deleteForm = document.getElementById('deleteForm');
    if (deleteForm) {
        deleteForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const projectId = document.getElementById('deleteProjectId').value;
            const password = document.getElementById('deletePassword').value;

            try {
                await api.deleteProject(projectId, password);
                showNotification('Project deleted successfully', 'success');
                closeDeleteModal();
                loadProjects();
            } catch (error) {
                showNotification(error.message, 'error');
            }
        });
    }
});

// Project Dashboard
async function loadProjectDashboard(projectId) {
    try {
        // Load project details
        const project = await api.getProject(projectId);
        document.getElementById('projectTitle').textContent = project.projectName;

        // Show/hide live controls
        if (project.isLiveEnabled) {
            document.getElementById('liveControls').style.display = 'block';
        }

        // Load initial data
        await loadDashboardData(projectId, 'all');

        // Setup event listeners
        setupDashboardEvents(projectId);

    } catch (error) {
        showNotification('Failed to load project', 'error');
        setTimeout(() => {
            window.location.href = 'view-projects.html';
        }, 2000);
    }
}

async function loadDashboardData(projectId, timeRange) {
    try {
        let data;
        if (timeRange === 'all') {
            const result = await api.getHistoricalData(projectId);
            data = result.data;
        } else {
            const result = await api.getLiveData(projectId, timeRange);
            data = result.data;
        }

        // Update stats
        updateDashboardStats(data);

        // Create plot
        createDashboardPlot(data);

        // Update table
        updateForecastTable(data.slice(0, 100)); // Show last 100 entries

    } catch (error) {
        showNotification('Failed to load data', 'error');
    }
}

function updateDashboardStats(data) {
    const totalPoints = data.length;
    const anomalies = data.filter(d => d.status === 'Anomaly').length;
    const lastUpdate = data.length > 0 ? formatDate(data[0].timestamp) : 'N/A';
    const currentStatus = data.length > 0 && data[0].status === 'Anomaly' ? 'Alert' : 'Normal';

    document.getElementById('totalPoints').textContent = totalPoints;
    document.getElementById('anomalyCount').textContent = anomalies;
    document.getElementById('lastUpdate').textContent = lastUpdate;
    document.getElementById('projectStatus').textContent = currentStatus;

    // Update status color
    const statusElement = document.getElementById('projectStatus');
    statusElement.className = currentStatus === 'Alert' ? 'text-danger' : 'text-success';
}

function updateForecastTable(data) {
    const tbody = document.getElementById('forecastTableBody');

    tbody.innerHTML = data.map(forecast => {
        const error = Math.abs(forecast.actualValue - forecast.forecastedValue);
        const errorPercent = (error / forecast.actualValue * 100).toFixed(2);

        return `
            <tr class="${forecast.status === 'Anomaly' ? 'anomaly-row' : ''}">
                <td>${formatDate(forecast.timestamp)}</td>
                <td>${formatNumber(forecast.actualValue)}</td>
                <td>${formatNumber(forecast.forecastedValue)}</td>
                <td>
                    <span class="status-badge ${forecast.status.toLowerCase()}">
                        ${forecast.status}
                    </span>
                </td>
                <td>${errorPercent}%</td>
            </tr>
        `;
    }).join('');
}

function setupDashboardEvents(projectId) {
    // Time range selector
    document.getElementById('timeRange').addEventListener('change', (e) => {
        loadDashboardData(projectId, e.target.value);
    });

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        const timeRange = document.getElementById('timeRange').value;
        loadDashboardData(projectId, timeRange);
        showNotification('Data refreshed', 'success');
    });

    // Fullscreen button
    document.getElementById('fullscreenBtn').addEventListener('click', () => {
        const plotContainer = document.querySelector('.plot-container');
        if (plotContainer.requestFullscreen) {
            plotContainer.requestFullscreen();
        }
    });

    // Fetch live data button
    const fetchLiveBtn = document.getElementById('fetchLiveBtn');
    if (fetchLiveBtn) {
        fetchLiveBtn.addEventListener('click', async () => {
            try {
                const result = await api.fetchLiveAndPredict(projectId);
                showNotification('Live data fetched successfully', 'success');

                // Refresh dashboard
                const timeRange = document.getElementById('timeRange').value;
                await loadDashboardData(projectId, timeRange);

            } catch (error) {
                showNotification('Failed to fetch live data', 'error');
            }
        });
    }

    // Manual entry form
    const manualForm = document.getElementById('manualEntryForm');
    manualForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const value = parseFloat(document.getElementById('manualValue').value);

        try {
            const result = await api.manualPredict(projectId, { value });

            showNotification(
                `Prediction: ${formatNumber(result.forecast)} - Status: ${result.status}`,
                result.status === 'Anomaly' ? 'warning' : 'success'
            );

            // Refresh dashboard
            const timeRange = document.getElementById('timeRange').value;
            await loadDashboardData(projectId, timeRange);

            // Clear form
            manualForm.reset();

        } catch (error) {
            showNotification('Prediction failed', 'error');
        }
    });
}