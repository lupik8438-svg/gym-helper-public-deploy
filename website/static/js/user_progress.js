const form = document.getElementById('progress-form');
form?.addEventListener('submit', async event => {
    event.preventDefault();
    const id = document.getElementById('telegram-id').value;
    const adminKey = document.getElementById('admin-key').value;
    const error = document.getElementById('progress-error');
    const result = document.getElementById('progress-result');
    error.textContent = '';
    try {
        const response = await fetch(`/api/user-dashboard/${encodeURIComponent(id)}`, { headers: { 'X-Admin-Key': adminKey } });
        if (!response.ok) throw new Error('Не удалось загрузить пользователя');
        const data = await response.json();
        if (!data.profile) throw new Error('Профиль ещё не создан');
        const summary = data.summary;
        result.innerHTML = `<div class="user-progress-head"><div><span class="eyebrow">Профиль</span><h2>${escapeHtml(data.user.first_name || 'Пользователь')}</h2><p>Telegram ID: ${data.user.user_id}</p></div><div class="progress-kpi"><strong>${summary.goal_progress || 0}%</strong><span>путь к цели</span></div></div><div class="progress-result-grid"><div><b>${summary.streak_days}</b><span>дней серия</span></div><div><b>${summary.weight_entries}</b><span>замеров</span></div><div><b>${summary.food_entries}</b><span>записей еды</span></div><div><b>${summary.active_days}</b><span>активных дней</span></div></div><h3>По месяцам</h3><div class="public-months">${data.monthly.slice(-12).reverse().map(item => `<div><b>${item.label}</b><span>${item.active_days} активных дней · ${item.food_entries} записей еды</span><strong>${item.weight_change > 0 ? '+' : ''}${item.weight_change.toFixed(1)} кг</strong></div>`).join('')}</div><h3>Достижения</h3><div class="public-achievements">${data.achievements.map(item => `<span class="${item.done ? 'done' : ''}">${item.done ? item.icon : '⬜️'} ${item.title}</span>`).join('')}</div>`;
    } catch (err) { error.textContent = err.message; result.innerHTML = ''; }
});
function escapeHtml(value) { return String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char])); }
