// frontend/js/auth.js
document.addEventListener('DOMContentLoaded', async () => {
    const loginForm = document.getElementById('loginForm');
    const setupForm = document.getElementById('setupForm');
    const setupSection = document.getElementById('setupSection');
    const errorMessage = document.getElementById('errorMessage');

    // Check if admin exists
    try {
        const response = await fetch(`${API_BASE_URL}/auth/setup`, {
            method: 'GET'
        });

        if (response.status === 404) {
            // No admin exists, show setup form
            loginForm.style.display = 'none';
            setupSection.style.display = 'block';
        }
    } catch (error) {
        console.error('Error checking admin status:', error);
    }

    // Handle login
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMessage.textContent = '';

            const formData = new FormData(loginForm);
            const loginData = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(loginData)
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('authToken', data.token);
                    localStorage.setItem('username', data.username);
                    window.location.href = 'index.html';
                } else {
                    errorMessage.textContent = data.detail || 'Login failed';
                }
            } catch (error) {
                errorMessage.textContent = 'Network error. Please try again.';
            }
        });
    }

    // Handle setup
    if (setupForm) {
        setupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            errorMessage.textContent = '';

            const password = document.getElementById('setupPassword').value;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/setup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password })
                });

                const data = await response.json();

                if (response.ok) {
                    showNotification('Admin account created successfully', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    errorMessage.textContent = data.detail || 'Setup failed';
                }
            } catch (error) {
                errorMessage.textContent = 'Network error. Please try again.';
            }
        });
    }
});