class EWSApi {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }
    // Projects API
    async getProjects() {
        return apiRequest('/projects');
    }

    async getProject(projectId) {
        return apiRequest(`/projects/${projectId}`);
    }

    async addProject(formData) {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${this.baseUrl}/projects/add`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add project');
        }

        return response.json();
    }

    async deleteProject(projectId, password) {
        return apiRequest(`/projects/${projectId}`, {
            method: 'DELETE',
            body: JSON.stringify({ password })
        });
    }

    async getHistoricalData(projectId) {
        return apiRequest(`/projects/${projectId}/historical-data`);
    }

    async getLiveData(projectId, duration = '1d') {
        return apiRequest(`/projects/${projectId}/live-data?duration=${duration}`);
    }

    // Cleaning API
    async cleanData(formData) {
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${this.baseUrl}/process/clean-only`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to clean data');
        }

        return response.json();
    }

    // Forecast API
    async fetchLiveAndPredict(projectId) {
        return apiRequest(`/forecast/live/${projectId}`, {
            method: 'POST'
        });
    }

    async manualPredict(projectId, data) {
        return apiRequest(`/forecast/manual/${projectId}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getForecastHistory(projectId) {
        return apiRequest(`/forecast/history/${projectId}`);
    }
}

const api = new EWSApi();