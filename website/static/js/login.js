const loginForm = document.getElementById('phone-login-form');
loginForm?.addEventListener('submit', async event => {
    event.preventDefault();
    const error = document.getElementById('login-error');
    const button = loginForm.querySelector('button');
    error.textContent = '';
    button.disabled = true;
    const original = button.innerHTML;
    button.textContent = 'Проверяю…';
    try {
        const response = await fetch('/api/auth/verify', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ phone: document.getElementById('login-phone').value, code: document.getElementById('login-code').value }) });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.error || 'Не удалось выполнить вход');
        window.location.href = '/account';
    } catch (err) { error.textContent = err.message; }
    finally { button.disabled = false; button.innerHTML = original; }
});
