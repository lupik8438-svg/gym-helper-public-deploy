document.addEventListener('DOMContentLoaded', async () => {
  const root = document.getElementById('programGrid');
  try {
    const response = await fetch('/api/workout-programs');
    if (!response.ok) throw new Error('Не удалось загрузить программы');
    const {programs} = await response.json();
    root.innerHTML = programs.map(program => `
      <article class="program-card">
        <div class="program-card-top"><span class="program-icon">${iconFor(program.id)}</span><span class="program-frequency">${escapeHtml(program.frequency)}</span></div>
        <h2>${escapeHtml(program.name)}</h2><strong class="program-tagline">${escapeHtml(program.tagline)}</strong>
        <p>${escapeHtml(program.description)}</p>
        <div class="program-days">${program.days.map(day => `<details><summary><b>${escapeHtml(day.name)}</b><span>${escapeHtml(day.focus)}</span></summary><ul>${day.exercises.map(exercise => `<li>${escapeHtml(exercise)}</li>`).join('')}</ul></details>`).join('')}</div>
      </article>`).join('');
  } catch (error) { root.textContent = error.message; }
});
function iconFor(id) { return ({full_body:'◉',split:'◈',upper_lower:'↕',ppl:'↗',cardio:'⌁'}[id] || '✦'); }
function escapeHtml(value) { return String(value || '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
