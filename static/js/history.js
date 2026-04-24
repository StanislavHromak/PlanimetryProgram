const FIGURE_NAMES = {
    triangle:       "Трикутник",
    circle:         "Коло",
    sector:         "Сектор / Сегмент",
    ellipse:        "Еліпс",
    regular_polygon:"Правильний багатокутник",
    quadrangle:     "Чотирикутник",
};

const TASK_NAMES = {
    RIGHT_LEGS:                    "Два катети",
    RIGHT_LEG_HYPOTENUSE:          "Катет і гіпотенуза",
    SSS:                           "Три сторони",
    SAS:                           "Дві сторони і кут",
    ASA:                           "Сторона і два кути",
    ISOSCELES_BASE_SIDE:           "Основа та бічна сторона",
    EQUILATERAL_SIDE:              "Сторона",
    RADIUS:                        "Радіус",
    DIAMETER:                      "Діаметр",
    CIRCUMFERENCE:                 "Довжина кола",
    AREA:                          "Площею",
    SECTOR_AND_ARC:                "Радіус та кут",
    ELLIPSE_AXES:                  "Пів вісі a та b",
    REGULAR_SIDE:                  "Сторона",
    REGULAR_R_CIRCUM:              "R описаного кола",
    RECTANGLE_SIDES:               "Обидві сторони",
    RECTANGLE_AREA_SIDE:           "Площа і сторона",
    RECTANGLE_PERIMETER_SIDE:      "Периметр і сторона",
    RECTANGLE_DIAGONAL_SIDE:       "Діагональ і сторона",
    SQUARE_SIDE:                   "Сторона",
    SQUARE_AREA:                   "Площа",
    SQUARE_PERIMETER:              "Периметр",
    SQUARE_DIAGONAL:               "Діагональ",
    RHOMBUS_DIAGONALS:             "Діагоналі",
    RHOMBUS_SIDE_ANGLE:            "Сторона і кут",
    RHOMBUS_AREA_SIDE:             "Площа і сторона",
    RHOMBUS_DIAGONAL_SIDE:         "Діагональ і сторона",
    PARALLELOGRAM_S_A:             "Дві сторони і кут",
    PARALLELOGRAM_D_A:             "Діагоналі і кут",
    TRAPEZOID_ABH:                 "Основи і висота",
    TRAPEZOID_AREA_BASES:          "Площа і основи",
    TRAPEZOID_MIDLINE_HEIGHT:      "Середня лінія і висота",
    ISOSCELES_TRAPEZOID_BASES_LEG: "Рівнобічна: основи і бічна",
    ARB_SIDES_ANGLES:              "4 сторони та кут",
};

// Завантаження та відображення історії
export async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div class="history-loading">⏳ Завантаження...</div>';

    let data;
    try {
        const res = await fetch('/api/history');
        const json = await res.json();
        data = json.success ? json.data : [];
    } catch (e) {
        console.error('Помилка завантаження історії:', e);
        container.innerHTML = '<div class="history-empty">❌ Помилка завантаження історії</div>';
        return;
    }

    if (data.length === 0) {
        container.innerHTML = '<div class="history-empty">📭 Історія порожня. Розв\'яжіть першу задачу!</div>';
        return;
    }

    container.innerHTML = data.map(item => renderHistoryCard(item)).join('');
}

function renderHistoryCard(item) {
    const figureName = FIGURE_NAMES[item.figure]   ?? item.figure;
    const taskName   = TASK_NAMES[item.task_type]  ?? item.task_type;
    // created_at приходить з сервера як відформатований рядок "dd.mm.yyyy HH:MM"
    const dateLabel  = item.created_at ?? '';

    const paramsHtml = Object.entries(item.params)
        .map(([k, v]) => `<span class="param-chip">${k} = ${v}</span>`)
        .join('');

    const resultEntries = Object.entries(item.result);
    const visibleResults = resultEntries.slice(0, 3)
        .map(([k, v]) => `<span class="result-chip">${k} = <b>${v}</b></span>`)
        .join('');
    const moreResults = resultEntries.length > 3
        ? `<span class="result-chip result-chip--more">+${resultEntries.length - 3} ще</span>`
        : '';

    return `
        <div class="history-card" data-id="${item.id}">
            <div class="history-card__header">
                <div class="history-card__meta">
                    <span class="history-badge">${figureName}</span>
                    <span class="history-task">${taskName}</span>
                </div>
                <span class="history-date">${dateLabel}</span>
            </div>

            <div class="history-card__params">${paramsHtml}</div>
            <div class="history-card__results">${visibleResults}${moreResults}</div>

            <div class="history-card__actions">
                <button class="btn-history btn-history--view"
                        onclick="window.repeatSolution(${item.id})">
                    🔄 Повторити
                </button>
                <button class="btn-history btn-history--export"
                        onclick="window.exportPDF(${item.id})">
                    📄 Експорт PDF
                </button>
                <button class="btn-history btn-history--delete"
                        onclick="window.deleteSolution(${item.id}, this)">
                    🗑 Видалити
                </button>
            </div>
        </div>
    `;
}

// Повторення задачі
export async function repeatSolution(id) {
    let item;
    try {
        const res  = await fetch(`/api/history/${id}`);
        const json = await res.json();
        if (!json.success) return;
        item = json.data;
    } catch (e) {
        console.error('Помилка завантаження розв\'язку:', e);
        return;
    }

    // Перемикаємось на вкладку "Розв'язувач"
    switchTab('solver');

    // Чекаємо поки DOM оновиться
    await new Promise(resolve => setTimeout(resolve, 50));

    // Заповнюємо форму
    const figureSelect = document.getElementById('figure-select');
    figureSelect.value = item.figure;
    figureSelect.dispatchEvent(new Event('change'));

    await new Promise(resolve => setTimeout(resolve, 50));

    const taskSelect = document.getElementById('task-select');
    taskSelect.value = item.task_type;
    taskSelect.dispatchEvent(new Event('change'));

    await new Promise(resolve => setTimeout(resolve, 50));

    Object.entries(item.params).forEach(([key, val]) => {
        const input = document.getElementById(key);
        if (input) input.value = val;
    });

    document.querySelectorAll('#target-checkboxes input[type="checkbox"]').forEach(cb => {
        cb.checked = item.targets.includes(cb.value);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Експорт PDF
export async function exportPDF(id) {
    const card = document.querySelector(`.history-card[data-id="${id}"]`);
    const btn  = card ? card.querySelector('.btn-history--export') : null;

    if (btn) {
        btn.textContent = '⏳ Генерація...';
        btn.disabled = true;
    }

    try {
        const res = await fetch(`/api/export/pdf/${id}`);
        if (!res.ok) {
            console.error('Сервер повернув помилку:', res.status);
            alert('Не вдалося згенерувати PDF. Спробуйте ще раз.');
            return;
        }

        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href     = url;
        a.download = `rozviazok_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

    } catch (e) {
        console.error('Помилка експорту PDF:', e);
        alert('Не вдалося згенерувати PDF. Спробуйте ще раз.');
    } finally {
        if (btn) {
            btn.textContent = '📄 Експорт PDF';
            btn.disabled = false;
        }
    }
}

// Видалення
export async function deleteSolution(id, btnEl) {
    if (!confirm('Видалити цей розв\'язок з історії?')) return;

    try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        if (!res.ok) {
            console.error('Помилка видалення:', res.status);
            alert('Помилка видалення');
            return;
        }

        const card = btnEl.closest('.history-card');
        card.style.transition = 'opacity 0.3s, transform 0.3s';
        card.style.opacity    = '0';
        card.style.transform  = 'translateX(20px)';
        setTimeout(() => {
            card.remove();
            const container = document.getElementById('history-list');
            if (!container.querySelector('.history-card')) {
                container.innerHTML = '<div class="history-empty">📭 Історія порожня.</div>';
            }
        }, 300);

    } catch (e) {
        console.error('Помилка видалення:', e);
        alert('Помилка видалення');
    }
}

// Перемикання вкладок
export function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('tab-btn--active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = content.id === `tab-${tabName}` ? 'block' : 'none';
    });

    if (tabName === 'history') {
        loadHistory().catch(e => console.error('loadHistory failed:', e));
    }
}