const tg = window.Telegram?.WebApp || {
    initData: '', initDataUnsafe: {}, themeParams: {},
    expand() {}, enableClosingConfirmation() {},
    HapticFeedback: { impactOccurred() {} },
    showAlert(message) { window.alert(message); }
};

tg.expand?.();
tg.enableClosingConfirmation?.();
const localUserId = tg.initDataUnsafe?.user?.id || 123456789;
const API_BASE = window.location.origin;
const state = { profile: null, dashboard: null, targetCalories: 2000 };

window.addEventListener('DOMContentLoaded', async () => {
    setupTheme();
    setupTabs();
    setupHeaderScroll();
    await loadUserData();
    await loadDashboard();
    sendEvent('mini_app_open');
});

function setupTheme() {
    const colors = tg.themeParams || {};
    if (colors.button_color) document.documentElement.style.setProperty('--lime-deep', colors.button_color);
    if (colors.bg_color) document.documentElement.style.setProperty('--bg', colors.bg_color);
    if (colors.text_color) document.documentElement.style.setProperty('--ink', colors.text_color);
}

function setupHeaderScroll() {
    const header = document.getElementById('appHeader');
    window.addEventListener('scroll', () => header?.classList.toggle('scrolled', window.scrollY > 6), { passive: true });
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.addEventListener('click', async () => {
        const tabName = tab.dataset.tab;
        tabs.forEach(item => item.classList.toggle('active', item.dataset.tab === tabName));
        contents.forEach(content => content.classList.toggle('active', content.id === tabName));
        haptic();
        if (tabName === 'progress') await loadProgress();
        if (tabName === 'training') await loadTraining();
        if (tabName === 'nutrition') await loadNutrition();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }));
}

function authHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (tg.initData) headers['X-Telegram-Init-Data'] = tg.initData;
    // Only used by the local DEBUG server, never by Telegram in production.
    if (!tg.initData) headers['X-Gym-User-ID'] = String(localUserId);
    return headers;
}

async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers: { ...authHeaders(), ...(options.headers || {}) } });
    if (!response.ok) {
        let detail = 'Не удалось загрузить данные';
        try { detail = (await response.json()).detail || detail; } catch (_) { /* no-op */ }
        throw new Error(detail);
    }
    return response.json();
}

async function loadUserData() {
    try {
        const payload = await api('/api/me/profile');
        state.profile = payload.profile;
        const name = payload.user?.first_name || tg.initDataUnsafe?.user?.first_name || 'Гость';
        setText('userName', name);
        setProfileMode(Boolean(payload.profile));
    } catch (error) {
        // Не просим пользователя ничего вводить вручную: Mini App должен открываться
        // из Telegram и получать пользователя через подписанный initData.
        setText('userName', tg.initDataUnsafe?.user?.first_name || 'Гость');
        setProfileMode(false, error.message);
    }
}

function setProfileMode(_hasProfile, _errorMessage = '') {
    // Mini App is an app-first surface: never block the dashboard with registration.
    // A missing profile is represented by empty states and can be completed later in the bot.
    const gate = document.getElementById('profileGate');
    const content = document.getElementById('appContent');
    if (gate) gate.classList.add('hidden');
    if (content) content.classList.remove('hidden');
}

function profileRequired(result) {
    if (result?.error === 'Profile not found') {
        showNotification('Заполни профиль в боте — после этого расчёт станет персональным', 'info');
        return false;
    }
    return true;
}

function openBotRegistration() {
    const botUrl = 'https://t.me/gymhelperrussia_bot?start=profile';
    if (tg.openTelegramLink) tg.openTelegramLink(botUrl);
    else if (tg.openLink) tg.openLink(botUrl);
    else window.location.href = botUrl;
}

async function loadDashboard() {
    try {
        state.dashboard = await api('/api/me/dashboard');
        const profile = state.dashboard.profile;
        const summary = state.dashboard.summary || {};
        setProfileMode(Boolean(profile));
        if (profile) {
            setText('currentWeight', profile.current_weight);
            setText('targetWeight', profile.target_weight);
            setText('streakDays', summary.streak_days || 0);
            setText('goalProgress', `${summary.goal_progress || 0}%`);
            setText('activeDays', summary.active_days || 0);
            setText('trainingCount', summary.training_sessions || 0);
            setText('cardioTotal', `${summary.cardio_minutes || 0}`);
            const calories = await api('/api/me/calculators/calories');
            setText('dailyCalories', calories.target_calories);
            state.targetCalories = calories.target_calories || 2000;
            const bmi = await api('/api/me/calculators/bmi');
            setText('bmiValue', bmi.bmi);
        } else {
            document.querySelectorAll('.skeleton-value').forEach(node => { node.classList.remove('skeleton-value'); node.textContent = '—'; });
        }
        renderMonthly(state.dashboard.monthly || []);
        renderAchievements(state.dashboard.achievements || []);
        await loadTodayFood();
    } catch (error) {
        console.error(error);
        showNotification(error.message, 'error');
    }
}

async function loadTodayFood() {
    try {
        const stats = await api('/api/me/food-stats');
        setText('todayCalories', Math.round(stats.total_calories));
        const meals = document.querySelector('#mealsCount span');
        if (meals) meals.textContent = stats.meals_count;
        updateProgressRing(stats.total_calories, state.targetCalories);
    } catch (error) { console.error(error); }
}

function updateProgressRing(current, target) {
    const percent = Math.min((current / Math.max(target, 1)) * 100, 100);
    const circumference = 2 * Math.PI * 74;
    const ring = document.getElementById('caloriesProgress');
    if (ring) ring.style.strokeDashoffset = circumference - (percent / 100) * circumference;
    const track = document.getElementById('calorieTrack');
    if (track) track.style.width = `${percent}%`;
}

async function calculateBMI() {
    await runCalculation('bmi', async () => {
        const result = await api('/api/me/calculators/bmi');
        if (!profileRequired(result)) return;
        document.getElementById('bmiResult').innerHTML = `<strong>${result.bmi}</strong><span>${result.category}</span>`;
        showNotification('BMI обновлён');
    });
}

async function calculateCalories() {
    await runCalculation('calories', async () => {
        const result = await api('/api/me/calculators/calories');
        if (!profileRequired(result)) return;
        const macros = result.macros;
        state.targetCalories = result.target_calories;
        document.getElementById('macrosResult').innerHTML = `
            <div class="macro-item"><span>Белки</span><strong>${macros.protein}</strong><small>г · ${macros.protein_percent}%</small></div>
            <div class="macro-item"><span>Жиры</span><strong>${macros.fat}</strong><small>г · ${macros.fat_percent}%</small></div>
            <div class="macro-item"><span>Углеводы</span><strong>${macros.carbs}</strong><small>г · ${macros.carbs_percent}%</small></div>`;
        showNotification(`Цель: ${result.target_calories} ккал / день`);
    });
}

async function calculateSupplements() {
    await runCalculation('supplements', async () => {
        const result = await api('/api/me/calculators/supplements');
        if (!profileRequired(result)) return;
        const priorityMap = { 'Высокий': 'high', 'Средний': 'medium', 'Низкий': 'low' };
        document.getElementById('supplementsList').innerHTML = result.recommendations.map(supp => {
            const name = supp.name.replace(/[💪⚡🐟☀️🧪🏃💊]/g, '').trim();
            const icon = supp.name.match(/[💪⚡🐟☀️🧪🏃💊]/)?.[0] || '✚';
            return `<div class="supplement-item"><div class="supplement-header"><span class="supplement-icon">${icon}</span><span class="supplement-name">${name}</span><span class="supplement-priority ${priorityMap[supp.priority] || 'medium'}">${supp.priority}</span></div><div class="supplement-dosage">${supp.dosage} · ${supp.timing}</div><div class="supplement-description">${supp.description}</div></div>`;
        }).join('') + (result.hormone_warning ? `<div class="hormone-warning">${result.hormone_warning}</div>` : '');
        showNotification('Подборка готова');
    });
}

async function runCalculation(key, callback) {
    const selector = key === 'supplements' ? 'supplementsList' : key === 'bmi' ? 'bmiResult' : 'macrosResult';
    const button = document.getElementById(selector)?.closest('.calculator-card')?.querySelector('.wide-btn');
    if (button) { button.disabled = true; button.dataset.label = button.innerHTML; button.innerHTML = 'Считаю…'; }
    try { await callback(); } catch (error) { showNotification(error.message, 'error'); }
    finally { if (button) { button.disabled = false; button.innerHTML = button.dataset.label; } }
}

async function loadProgress() {
    try {
        const [dashboard, data] = await Promise.all([state.dashboard ? Promise.resolve(state.dashboard) : api('/api/me/dashboard'), api('/api/me/weight-history')]);
        renderMonthly(dashboard.monthly || []);
        renderAchievements(dashboard.achievements || []);
        const historyDiv = document.getElementById('weightHistory');
        if (!data.history.length) {
            historyDiv.innerHTML = '<div class="empty-state small"><strong>Пока нет измерений</strong><span>Добавь вес через Telegram-бота, чтобы увидеть динамику.</span></div>';
            return;
        }
        historyDiv.innerHTML = data.history.map((record, index) => {
            let change = '';
            if (index < data.history.length - 1) {
                const diff = record.weight - data.history[index + 1].weight;
                change = diff > 0 ? `<span class="history-change up">+${diff.toFixed(1)} кг</span>` : diff < 0 ? `<span class="history-change down">${diff.toFixed(1)} кг</span>` : '';
            }
            return `<div class="history-item"><span class="history-date">${formatDate(record.date)}</span><strong class="history-weight">${record.weight} кг</strong>${change}</div>`;
        }).join('');
        window.renderWeightChart?.(data.history);
    } catch (error) { showNotification(error.message, 'error'); }
}

function renderMonthly(months) {
    const node = document.getElementById('monthlyList');
    if (!node) return;
    const visible = months.slice(-6).reverse();
    node.innerHTML = visible.length ? visible.map(item => `<div class="month-row"><span class="month-label">${item.label}</span><div class="month-metric"><strong>${item.active_days} активных дней</strong><small>${item.training_sessions || 0} тренировок · ${item.cardio_minutes || 0} мин кардио · ${item.weight_entries} замеров · ${item.food_entries} записей питания</small></div><span class="month-change ${item.weight_change > 0 ? '' : item.weight_change < 0 ? 'negative' : ''}">${item.weight_change > 0 ? '+' : ''}${item.weight_change.toFixed(1)} кг</span></div>`).join('') : '<div class="empty-state small"><strong>История появится после первых записей</strong></div>';
}

function renderAchievements(achievements) {
    const node = document.getElementById('achievementList');
    if (!node) return;
    node.innerHTML = achievements.map(item => `<div class="achievement ${item.done ? 'done' : ''}"><span class="achievement-icon">${item.done ? item.icon : '⬜️'}</span><div><b>${item.title}</b><br><span>${item.done ? 'Выполнено' : 'Продолжай — всё получится'}</span></div></div>`).join('');
}

async function loadTraining() {
    try {
        const [programData, sessionData] = await Promise.all([
            api('/api/workout-programs'), api('/api/me/training')
        ]);
        renderWorkoutPrograms(programData.programs || []);
        renderTrainingSessions(sessionData.sessions || []);
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

function renderWorkoutPrograms(programs) {
    const root = document.getElementById('workoutProgramList');
    if (!root) return;
    root.innerHTML = programs.map(program => `
        <article class="training-program-card">
            <h3>${escapeHtml(program.name)}</h3>
            <p><strong>${escapeHtml(program.frequency)}</strong> · ${escapeHtml(program.description)}</p>
            ${program.days.map(day => `<details><summary><b>${escapeHtml(day.name)}</b><span>${escapeHtml(day.focus)}</span></summary><ul>${day.exercises.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul></details>`).join('')}
        </article>`).join('');
}

function renderTrainingSessions(sessions) {
    const root = document.getElementById('trainingSessionList');
    if (!root) return;
    const names = { full_body: 'Full Body', split: 'Сплит', upper_lower: 'Верх / низ', ppl: 'Жим · тяни · ноги', cardio: 'Кардио' };
    root.innerHTML = sessions.length ? sessions.slice(0, 15).map(session => `<div class="training-session-row"><div><strong>${names[session.program_type] || 'Тренировка'}</strong><small>${session.duration_minutes} мин силовая · ${session.cardio_minutes} мин кардио${session.notes ? ` · ${escapeHtml(session.notes)}` : ''}</small></div><time>${formatDate(session.date)}</time></div>`).join('') : '<div class="empty-state small"><strong>Пока нет тренировок</strong><span>Запиши первое занятие — оно попадёт в месячный прогресс.</span></div>';
}

async function saveTrainingSession() {
    const button = document.getElementById('saveTrainingButton');
    if (!button) return;
    button.disabled = true;
    const original = button.innerHTML;
    button.innerHTML = 'Сохраняю…';
    try {
        await api('/api/me/training', {
            method: 'POST',
            body: JSON.stringify({
                program_type: document.getElementById('programSelect').value,
                session_type: document.getElementById('programSelect').value === 'cardio' ? 'cardio' : 'strength',
                duration_minutes: Number(document.getElementById('trainingMinutes').value || 0),
                cardio_minutes: Number(document.getElementById('cardioMinutes').value || 0),
                notes: document.getElementById('trainingNotes').value,
            }),
        });
        document.getElementById('trainingNotes').value = '';
        showNotification('Тренировка сохранена');
        await loadTraining();
        state.dashboard = await api('/api/me/dashboard');
        renderMonthly(state.dashboard.monthly || []);
    } catch (error) { showNotification(error.message, 'error'); }
    finally { button.disabled = false; button.innerHTML = original; }
}

function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

async function loadNutrition() {
    try {
        const stats = await api('/api/me/food-stats');
        setText('nutritionCalories', `${Math.round(stats.total_calories)} ккал`);
        setText('nutritionMeals', stats.meals_count);
        const list = document.getElementById('mealsList');
        list.innerHTML = stats.logs.length ? stats.logs.map(log => `<div class="meal-item"><span class="meal-time">${log.time}</span><strong class="meal-calories">${Math.round(log.calories)} ккал</strong></div>`).join('') : '<div class="empty-state"><span class="empty-icon">◉</span><strong>Пока пусто</strong><span>Сканируй еду в боте — записи появятся здесь.</span></div>';
    } catch (error) { showNotification(error.message, 'error'); }
}

function scanFood() { showNotification('Открой бота и отправь фото еды 📸'); sendEvent('scan_food_clicked'); }
function updateWeight() { showNotification('Обнови вес в разделе профиля бота ⚖'); sendEvent('weight_update_clicked'); }
function sendEvent(event_type) { api('/api/me/events', { method: 'POST', body: JSON.stringify({ event_type }) }).catch(() => {}); }
function haptic() { tg.HapticFeedback?.impactOccurred?.('light'); }
function setText(id, value) { const node = document.getElementById(id); if (node) { node.textContent = value; node.classList.remove('skeleton-value'); } }
function showNotification(message, type = 'info') { const toast = document.getElementById('toast'); if (!toast) return; toast.textContent = `${type === 'error' ? '×' : '✓'} ${message}`; toast.className = `toast visible ${type === 'error' ? 'error' : ''}`; clearTimeout(window.__toastTimer); window.__toastTimer = setTimeout(() => toast.classList.remove('visible'), 3400); }
function formatDate(value) { return new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }); }
