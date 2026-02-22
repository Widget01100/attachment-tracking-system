// Theme management
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update active button states
    document.querySelectorAll('.theme-toggle button').forEach(btn => {
        btn.classList.remove('active');
        if(btn.dataset.theme === theme) {
            btn.classList.add('active');
        }
    });
}

// Initialize theme
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

// Toggle theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = lert alert-modern alert- fade-in;
    notification.innerHTML = 
        <div class="d-flex align-items-center">
            <i class="fas fa- me-2"></i>
            <span></span>
        </div>
    ;
    
    const container = document.getElementById('notification-container') || createNotificationContainer();
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 350px;
    ;
    document.body.appendChild(container);
    return container;
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
            
            // Add error message if not exists
            let errorDiv = input.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'This field is required';
                input.parentNode.insertBefore(errorDiv, input.nextSibling);
            }
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    
    // Add fade-in class to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize all tooltips
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        // Simple tooltip implementation
        tooltip.addEventListener('mouseenter', function(e) {
            const tip = document.createElement('div');
            tip.className = 'tooltip-modern';
            tip.textContent = this.dataset.title || this.title;
            tip.style.cssText = 
                position: absolute;
                background: var(--bg-card);
                color: var(--text-primary);
                padding: 5px 10px;
                border-radius: 6px;
                font-size: 12px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                z-index: 1000;
            ;
            
            const rect = this.getBoundingClientRect();
            tip.style.top = rect.top - 30 + 'px';
            tip.style.left = rect.left + 'px';
            
            document.body.appendChild(tip);
            
            this.addEventListener('mouseleave', function() {
                tip.remove();
            }, { once: true });
        });
    });
});

// Chart colors for consistent theming
const chartColors = {
    primary: '#2563eb',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#3b82f6',
    light: '#f1f5f9',
    dark: '#334155'
};

// Export functions for use in templates
window.UATMS = {
    setTheme,
    toggleTheme,
    showNotification,
    validateForm,
    chartColors
};
