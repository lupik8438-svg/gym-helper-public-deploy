const calculatorTabs = [...document.querySelectorAll('.tab-btn')];
const progressSteps = [...document.querySelectorAll('.progress-step')];

function setActiveCalculator(tabName) {
    calculatorTabs.forEach(button => {
        const active = button.dataset.tab === tabName;
        button.classList.toggle('active', active);
        button.setAttribute('aria-selected', String(active));
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
    progressSteps.forEach((step, index) => step.classList.toggle('active', index <= ['bmi', 'calories', 'supplements'].indexOf(tabName)));
}

calculatorTabs.forEach(button => button.addEventListener('click', () => setActiveCalculator(button.dataset.tab)));

function setLoading(form, loading) {
    const button = form.querySelector('button[type="submit"]');
    if (!button) return;
    if (loading) {
        button.dataset.label = button.innerHTML;
        button.innerHTML = '<span class="button-spinner" aria-hidden="true"></span> Считаю…';
        button.disabled = true;
    } else {
        button.innerHTML = button.dataset.label || button.innerHTML;
        button.disabled = false;
    }
}

function showResult(element, html) {
    element.innerHTML = html;
    element.classList.add('show');
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function number(value) { return Number(value).toLocaleString('ru-RU'); }

const bmiForm = document.getElementById('bmi-form');
bmiForm?.addEventListener('submit', async event => {
    event.preventDefault();
    setLoading(bmiForm, true);
    try {
        const response = await fetch('/api/calculate/bmi', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weight: Number(document.getElementById('bmi-weight').value),
                height: Number(document.getElementById('bmi-height').value)
            })
        });
        if (!response.ok) throw new Error('Не удалось выполнить расчёт');
        const data = await response.json();
        showResult(document.getElementById('bmi-result'), `
            <h3>Результат BMI</h3>
            <div class="result-kpi"><strong>${data.bmi}</strong><span>индекс массы тела</span></div>
            <p><strong>${data.category}</strong></p>
            <p>${data.recommendation}</p>
        `);
        window.showToast?.('BMI рассчитан');
    } catch (error) {
        window.showToast?.(error.message || 'Ошибка при расчёте BMI', 'error');
    } finally { setLoading(bmiForm, false); }
});

const caloriesForm = document.getElementById('calories-form');
caloriesForm?.addEventListener('submit', async event => {
    event.preventDefault();
    setLoading(caloriesForm, true);
    try {
        const response = await fetch('/api/calculate/calories', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weight: Number(document.getElementById('cal-weight').value),
                height: Number(document.getElementById('cal-height').value),
                age: Number(document.getElementById('cal-age').value),
                gender: document.getElementById('cal-gender').value,
                activity_level: document.getElementById('cal-activity').value,
                goal: document.getElementById('cal-goal').value
            })
        });
        if (!response.ok) throw new Error('Не удалось выполнить расчёт');
        const data = await response.json();
        const macros = data.macros;
        showResult(document.getElementById('calories-result'), `
            <h3>Твоя дневная цель</h3>
            <div class="result-kpi"><strong>${number(data.target_calories)}</strong><span>ккал / день</span></div>
            <p><strong>${data.goal_description}</strong> · ${data.activity_description}</p>
            <div class="result-grid">
                <div class="result-stat"><b>${macros.protein} г</b><span>Белки · ${macros.protein_percent}%</span></div>
                <div class="result-stat"><b>${macros.fat} г</b><span>Жиры · ${macros.fat_percent}%</span></div>
                <div class="result-stat"><b>${macros.carbs} г</b><span>Углеводы · ${macros.carbs_percent}%</span></div>
            </div>
            <p><strong>BMR:</strong> ${number(data.bmr)} ккал · <strong>TDEE:</strong> ${number(data.tdee)} ккал</p>
        `);
        window.showToast?.('Цель по калориям рассчитана');
    } catch (error) {
        window.showToast?.(error.message || 'Ошибка при расчёте калорий', 'error');
    } finally { setLoading(caloriesForm, false); }
});

const supplementsForm = document.getElementById('supplements-form');
supplementsForm?.addEventListener('submit', async event => {
    event.preventDefault();
    setLoading(supplementsForm, true);
    try {
        const response = await fetch('/api/calculate/supplements', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                weight: Number(document.getElementById('sup-weight').value),
                goal: document.getElementById('sup-goal').value,
                activity_level: document.getElementById('sup-activity').value
            })
        });
        if (!response.ok) throw new Error('Не удалось получить рекомендации');
        const data = await response.json();
        const priorityClass = { 'Высокий': 'high', 'Средний': 'medium', 'Низкий': 'low' };
        const recommendations = data.recommendations.map(item => `
            <div class="result-stat"><b>${item.name}</b><span class="supplement-badge ${priorityClass[item.priority] || ''}">${item.priority} приоритет</span><p>${item.dosage} · ${item.timing}</p></div>
        `).join('');
        showResult(document.getElementById('supplements-result'), `
            <h3>Рекомендации под твою цель</h3>
            <div class="result-grid">${recommendations}</div>
            <p><strong>Ориентировочная стоимость:</strong> ${data.monthly_cost_estimate}</p>
            <p>${data.disclaimer}</p>
            ${data.hormone_warning ? `<p class="hormone-warning">${data.hormone_warning}</p>` : ''}
        `);
        window.showToast?.('Рекомендации готовы');
    } catch (error) {
        window.showToast?.(error.message || 'Ошибка при расчёте добавок', 'error');
    } finally { setLoading(supplementsForm, false); }
});
