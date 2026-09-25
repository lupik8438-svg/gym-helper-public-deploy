window.renderWeightChart = function renderWeightChart(history) {
    const canvas = document.getElementById('weightChart');
    if (!canvas || !history?.length) return;
    const ordered = [...history].reverse();
    const labels = ordered.map(item => new Date(item.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
    const values = ordered.map(item => item.weight);
    if (window.Chart) {
        if (window.__weightChart) window.__weightChart.destroy();
        const context = canvas.getContext('2d');
        const gradient = context.createLinearGradient(0, 0, 0, 280);
        gradient.addColorStop(0, 'rgba(91,158,92,.35)');
        gradient.addColorStop(1, 'rgba(91,158,92,0)');
        window.__weightChart = new Chart(context, {
            type: 'line',
            data: { labels, datasets: [{ data: values, borderColor: '#5b9e5c', backgroundColor: gradient, fill: true, tension: .4, pointRadius: 4, pointBackgroundColor: '#b5ed71', pointBorderColor: '#5b9e5c', pointBorderWidth: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, animation: { duration: 900, easing: 'easeOutQuart' }, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, ticks: { color: '#728078', maxTicksLimit: 5, font: { family: 'DM Sans', size: 10 } } }, y: { grid: { color: 'rgba(23,34,29,.07)' }, ticks: { color: '#728078', font: { family: 'DM Sans', size: 10 } } } } }
        });
        return;
    }
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth * devicePixelRatio;
    const height = canvas.height = canvas.offsetHeight * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);
    const w = canvas.offsetWidth, h = canvas.offsetHeight, min = Math.min(...values) - 1, max = Math.max(...values) + 1;
    ctx.clearRect(0, 0, w, h); ctx.strokeStyle = '#5b9e5c'; ctx.lineWidth = 3; ctx.beginPath();
    values.forEach((value, index) => { const x = values.length === 1 ? w / 2 : (index / (values.length - 1)) * (w - 14) + 7; const y = h - ((value - min) / (max - min)) * (h - 20) - 10; index ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke();
};
