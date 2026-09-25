let adminKey = sessionStorage.getItem('gym_helper_admin_key') || '';
let activityChart;

const loginCard = document.getElementById('loginCard');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');

loginForm?.addEventListener('submit', async event => {
    event.preventDefault();
    adminKey = document.getElementById('adminKey').value.trim();
    if (!adminKey) return;
    const ok = await loadDashboard();
    if (ok) { sessionStorage.setItem('gym_helper_admin_key', adminKey); }
});

document.getElementById('searchInput')?.addEventListener('input', debounce(loadUsers, 250));
document.getElementById('goalFilter')?.addEventListener('change', loadUsers);
document.getElementById('exportButton')?.addEventListener('click', exportCsv);

if (adminKey) loadDashboard();

async function request(path) {
    const response = await fetch(path, { headers: { 'X-Admin-Key': adminKey } });
    if (!response.ok) throw new Error((await response.json().catch(() => ({}))).error || 'Доступ запрещён');
    return response;
}

async function loadDashboard() {
    try {
        const overview = await (await request('/admin/api/overview')).json();
        loginCard.classList.add('hidden'); dashboard.classList.remove('hidden'); loginError.textContent = '';
        renderSummary(overview.totals); renderTopUsers(overview.top_users); renderChart(overview.monthly); await loadUsers();
        return true;
    } catch (error) {
        loginError.textContent = error.message;
        loginCard.classList.remove('hidden'); dashboard.classList.add('hidden');
        if (adminKey) sessionStorage.removeItem('gym_helper_admin_key');
        return false;
    }
}

function renderSummary(totals) {
    const labels = [['Пользователи', totals.users], ['Профили', totals.profiles], ['Активны сегодня', totals.active_today], ['Записи еды', totals.food_entries], ['Тренировки', totals.training_sessions || 0], ['Средний путь к цели', `${totals.average_goal_progress}%`]];
    document.getElementById('summaryCards').innerHTML = labels.map(([label, value]) => `<div class="admin-stat"><span>${label}</span><strong>${value}</strong></div>`).join('');
}

function renderTopUsers(users) {
    document.getElementById('topUsers').innerHTML = users.length ? users.map((user, index) => `<div class="top-user"><span class="top-user-rank">${index + 1}</span><div><b>${escapeHtml(user.first_name)}</b><span>${user.username ? '@' + escapeHtml(user.username) : 'Telegram ID ' + user.user_id}</span></div><strong>${user.goal_progress ?? 0}%</strong></div>`).join('') : '<p class="muted">Пока нет профилей с прогрессом.</p>';
}

function renderChart(monthly) {
    const canvas = document.getElementById('activityChart');
    if (!canvas || !window.Chart) return;
    activityChart?.destroy();
    activityChart = new Chart(canvas.getContext('2d'), { type: 'bar', data: { labels: monthly.map(x => x.label), datasets: [
        { label: 'Активные пользователи', data: monthly.map(x => x.active_users), backgroundColor: '#a6e06f', borderRadius: 6 },
        { label: 'Записи питания', data: monthly.map(x => x.food_entries), backgroundColor: '#78b9ff', borderRadius: 6 },
        { label: 'Замеры веса', data: monthly.map(x => x.weight_entries), backgroundColor: '#ff856d', borderRadius: 6 },
        { label: 'Тренировки', data: monthly.map(x => x.training_sessions || 0), backgroundColor: '#b79cff', borderRadius: 6 },
    ] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { usePointStyle: true, font: { family: 'DM Sans' } } } }, scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: 'rgba(21,33,27,.07)' } } } } });
}

async function loadUsers() {
    try {
        const search = encodeURIComponent(document.getElementById('searchInput')?.value || '');
        const goal = encodeURIComponent(document.getElementById('goalFilter')?.value || '');
        const data = await (await request(`/admin/api/users?search=${search}&goal=${goal}`)).json();
        document.getElementById('usersCount').textContent = data.users.length;
        document.getElementById('usersTable').innerHTML = data.users.map(user => `<tr><td><strong>${escapeHtml(user.first_name)}</strong><small>${user.username ? '@' + escapeHtml(user.username) : user.user_id}</small>${user.phone_number ? `<small>📱 ${escapeHtml(user.phone_number)}</small>` : ''}</td><td><span class="status-pill ${user.profile_completed ? 'done' : 'pending'}">${user.profile_completed ? 'Готов' : 'Регистрация'}</span></td><td>${goalLabel(user.goal)}</td><td>${user.current_weight ?? '—'} → ${user.target_weight ?? '—'} кг</td><td class="progress-cell"><strong>${user.goal_progress ?? 0}%</strong><div class="bar"><span style="width:${Math.min(user.goal_progress || 0, 100)}%"></span></div></td><td><small>${formatDate(user.last_active)}</small></td><td>${user.training_sessions || 0} <small>${user.cardio_minutes || 0} мин кардио</small></td><td>${user.events} <small>${user.weight_entries} веса · ${user.food_entries} еды</small></td></tr>`).join('') || '<tr><td colspan="7">Пользователи не найдены.</td></tr>';
    } catch (error) { document.getElementById('loginError').textContent = error.message; }
}

async function exportCsv() {
    const response = await request('/admin/api/export.csv');
    const blob = await response.blob(); const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'gym-helper-users.csv'; link.click(); URL.revokeObjectURL(url);
}

function goalLabel(goal) { return ({ lose_weight: 'Снижение', maintain: 'Поддержание', gain_muscle: 'Набор' }[goal] || '—'); }
function formatDate(value) { return value ? new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }) : '—'; }
function escapeHtml(value) { return String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char])); }
function debounce(fn, delay) { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); }; }
