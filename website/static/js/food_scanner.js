const foodDatabase = {
    'куриная грудка': { calories: 165, protein: 31, fats: 3.6, carbs: 0 },
    'рис': { calories: 130, protein: 2.7, fats: 0.3, carbs: 28 },
    'яйца': { calories: 155, protein: 13, fats: 11, carbs: 1.1 },
    'банан': { calories: 89, protein: 1.1, fats: 0.3, carbs: 23 },
    'овсянка': { calories: 389, protein: 16.9, fats: 6.9, carbs: 66 },
    'творог': { calories: 98, protein: 18, fats: 0.6, carbs: 3.3 },
    'говядина': { calories: 250, protein: 26, fats: 15, carbs: 0 },
    'брокколи': { calories: 34, protein: 2.8, fats: 0.4, carbs: 7 }
};

const form = document.getElementById('food-form');
form?.addEventListener('submit', event => {
    event.preventDefault();
    analyzeFoodFromDatabase(document.getElementById('food-name').value, Number(document.getElementById('food-weight').value) || 100);
});

document.querySelectorAll('.food-card').forEach(card => card.addEventListener('click', () => {
    const name = card.dataset.food;
    document.getElementById('food-name').value = name;
    analyzeFoodFromDatabase(name, Number(document.getElementById('food-weight').value) || 100);
}));

function analyzeFoodFromDatabase(rawName, weight) {
    const foodName = rawName.toLowerCase().trim();
    const food = foodDatabase[foodName];
    const result = document.getElementById('food-result');
    if (!result) return;
    if (!food) {
        result.innerHTML = '<h3>Продукт не найден</h3><p>Попробуй один из вариантов из списка — так результат будет точнее.</p>';
        result.classList.add('show');
        window.showToast?.('Выбери продукт из базы', 'error');
        return;
    }
    const multiplier = weight / 100;
    const name = foodName.charAt(0).toUpperCase() + foodName.slice(1);
    result.innerHTML = `
        <h3>Пищевая ценность порции</h3>
        <div class="result-kpi"><strong>${Math.round(food.calories * multiplier)}</strong><span>ккал · ${weight} г</span></div>
        <div class="result-grid">
            <div class="result-stat"><b>${Math.round(food.protein * multiplier * 10) / 10} г</b><span>Белки</span></div>
            <div class="result-stat"><b>${Math.round(food.fats * multiplier * 10) / 10} г</b><span>Жиры</span></div>
            <div class="result-stat"><b>${Math.round(food.carbs * multiplier * 10) / 10} г</b><span>Углеводы</span></div>
        </div>
        <p><strong>${name}</strong> · ориентировочные значения на выбранный вес.</p>
    `;
    result.classList.add('show');
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    window.showToast?.('Порция рассчитана');
}
