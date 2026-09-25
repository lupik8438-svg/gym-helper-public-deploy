// Shared website enhancements. Kept dependency-free so the pages stay fast.
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', event => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                event.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    document.querySelectorAll('.reveal').forEach((element, index) => {
        element.style.animationDelay = `${Math.min(index * 55, 280)}ms`;
    });
});

window.showToast = function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast visible ${type === 'error' ? 'error' : ''}`;
    window.clearTimeout(window.__toastTimer);
    window.__toastTimer = window.setTimeout(() => toast.classList.remove('visible'), 3200);
};

function setupThemeToggle() {
    const root = document.documentElement;
    const toggle = document.getElementById('themeToggle');
    const saved = localStorage.getItem('gym-helper-theme') || 'light';
    root.dataset.theme = saved;
    if (!toggle) return;
    const update = () => {
        const dark = root.dataset.theme === 'dark';
        toggle.textContent = dark ? '☀️' : '🌙';
        toggle.setAttribute('aria-label', dark ? 'Включить светлую тему' : 'Включить тёмную тему');
        toggle.title = dark ? 'Светлая тема' : 'Тёмная тема';
    };
    update();
    toggle.addEventListener('click', () => {
        root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('gym-helper-theme', root.dataset.theme);
        update();
    });
}

document.addEventListener('DOMContentLoaded', setupThemeToggle);
