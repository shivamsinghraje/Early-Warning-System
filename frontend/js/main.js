// Global configuration
const API_BASE_URL = 'http://localhost:8080/api';

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token && !window.location.pathname.includes('login.html')) {
        window.location.href = 'login.html';
    }
}

// Setup axios-like fetch wrapper
async function apiRequest(url, options = {}) {
    const token = localStorage.getItem('authToken');

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };

    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    });

    if (response.status === 401) {
        localStorage.removeItem('authToken');
        window.location.href = 'login.html';
        return;
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
    }

    return data;
}

// Logout functionality
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await apiRequest('/auth/logout', { method: 'POST' });
            } catch (error) {
                console.error('Logout error:', error);
            }

            localStorage.removeItem('authToken');
            window.location.href = 'login.html';
        });
    }

    // Check auth on page load
    checkAuth();
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function formatNumber(num) {
    return Number(num).toFixed(2);
}

// File validation
function validateFile(file) {
    const validTypes = ['text/csv', 'application/vnd.ms-excel',
                       'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];

    if (!validTypes.includes(file.type) &&
        !file.name.match(/\.(csv|xlsx|xls)$/i)) {
        throw new Error('Invalid file type. Please upload CSV or Excel file.');
    }

    if (file.size > 100 * 1024 * 1024) { // 100MB
        throw new Error('File size exceeds 100MB limit.');
    }

    return true;
}