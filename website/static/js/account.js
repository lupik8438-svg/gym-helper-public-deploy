async function loadAccount() {
    const root = document.getElementById('account-content');
    try {
        const response = await fetch('/api/auth/me');
        if (response.status === 401) { window.location.href = '/login'; return; }
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Не удалось загрузить кабинет');
        const summary = data.summary || {};
        const profile = data.profile;
        document.getElementById('account-title').textContent = `Привет, ${data.user.first_name || 'спортсмен'}!`;
        document.getElementById('account-subtitle').textContent = profile ? 'Здесь собраны твой прогресс, питание и тренировки из Telegram.' : 'Профиль ещё не заполнен. Открой бота, чтобы завершить регистрацию.';
        root.innerHTML = `<article class="card account-card account-accent"><span class="eyebrow">Сводка</span><h2>${profile ? 'Твой ритм' : 'Профиль в ожидании'}</h2><p>${profile ? `${profile.current_weight} кг → ${profile.target_weight} кг · цель: ${goalLabel(profile.goal)}` : 'После регистрации здесь появятся персональные показатели.'}</p><a class="btn btn-primary btn-small" href="https://t.me/gymhelperrussia_bot?start=account" target="_blank" rel="noopener">Открыть бота ↗</a></article><article class="card account-card"><span class="eyebrow">Активность</span><div class="account-stats"><div><strong>${summary.active_days || 0}</strong><span>активных дней</span></div><div><strong>${summary.training_sessions || 0}</strong><span>тренировок</span></div><div><strong>${summary.food_entries || 0}</strong><span>записей еды</span></div><div><strong>${summary.goal_progress ?? 0}%</strong><span>путь к цели</span></div></div></article><article class="card account-card"><span class="eyebrow">Последние месяцы</span><div class="account-months">${(data.monthly || []).slice(-6).reverse().map(m => `<div><b>${m.label}</b><span>${m.active_days} активных дней · ${m.training_sessions || 0} тренировок</span><strong>${m.weight_change > 0 ? '+' : ''}${Number(m.weight_change || 0).toFixed(1)} кг</strong></div>`).join('') || '<p class="muted">История появится после первых записей.</p>'}</div></article>`;
    } catch (err) { document.getElementById('account-error').textContent = err.message; }
}
function goalLabel(goal) { return ({lose_weight:'снижение веса', maintain:'поддержание', gain_muscle:'набор массы'}[goal] || 'цель не указана'); }
loadAccount();
