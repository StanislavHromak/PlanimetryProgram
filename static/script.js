// Конфігурація фігур, їхніх задач та можливих результатів
const uiConfig = {
    triangle: {
        name: "Трикутник",
        targets: [
            { id: "area", label: "Площу (S)", checked: true },
            { id: "perimeter", label: "Периметр (P)", checked: false },
            { id: "incircle", label: "Вписане коло (r)", checked: false },
            { id: "circumcircle", label: "Описане коло (R)", checked: false },
            { id: "side", label: "Невідомі сторони/кути", checked: true }
        ],
        tasks: {
            "SSS": {
                name: "Три сторони (SSS)",
                inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "c", label: "Сторона c" } ],
                validTargets: ["area", "perimeter", "incircle", "circumcircle", "side"]
            },
            "SAS": {
                name: "Дві сторони і кут (SAS)",
                inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "angle_c", label: "Кут між ними γ (°)" } ],
                validTargets: ["area", "perimeter", "incircle", "circumcircle", "side"]
            },
            "ASA": {
                name: "Сторона і два кути (ASA)",
                inputs: [ { id: "a", label: "Сторона a" }, { id: "angle_b", label: "Прилеглий кут β (°)" }, { id: "angle_c", label: "Прилеглий кут γ (°)" } ],
                validTargets: ["area", "perimeter", "incircle", "circumcircle", "side"]
            }
        }
    },
    circle: {
    name: "Коло та Круг",
    targets: [
        { id: "radius", label: "Радіус (r)", checked: false },
        { id: "diameter", label: "Діаметр (d)", checked: false },
        { id: "area", label: "Площу круга (S)", checked: true },
        { id: "perimeter", label: "Довжину кола (C)", checked: true },
        { id: "arc", label: "Довжину дуги (L)", checked: false },
        { id: "sector_area", label: "Площу сектора", checked: false },
        { id: "chord", label: "Довжину хорди (c)", checked: false }
    ],
    tasks: {
        "RADIUS": {
            name: "Відомий радіус (r)",
            inputs: [ { id: "radius", label: "Радіус r" } ],
            validTargets: ["diameter", "area", "perimeter"]
        },
        "DIAMETER": {
            name: "Відомий діаметр (d)",
            inputs: [ { id: "diameter", label: "Діаметр d" } ],
            validTargets: ["radius", "area", "perimeter"]
        },
        "CIRCUMFERENCE": {
            name: "Відома довжина кола (C)",
            inputs: [ { id: "circumference", label: "Довжина C" } ],
            validTargets: ["radius", "diameter", "area"]
        },
        "AREA": {
            name: "Відома площа (S)",
            inputs: [ { id: "area", label: "Площа S" } ],
            validTargets: ["radius", "diameter", "perimeter"]
        },
        "SECTOR_AND_ARC": {
            name: "Відомі радіус (r) і кут (α)",
            inputs: [
                { id: "radius", label: "Радіус r" },
                { id: "angle", label: "Центральний кут α (°)" }
            ],
            validTargets: ["diameter", "area", "perimeter", "arc", "sector_area", "chord"]
        }
    }
}
};

// 1. Ініціалізація сторінки
window.onload = function() {
    const figureSelect = document.getElementById('figure-select');
    figureSelect.innerHTML = Object.keys(uiConfig).map(key =>
        `<option value="${key}">${uiConfig[key].name}</option>`
    ).join('');

    updateUI();
};

// 2. Оновлення списку задач при зміні фігури
function updateUI() {
    const figure = document.getElementById('figure-select').value;
    const taskSelect = document.getElementById('task-select');

    // Оновлюємо список "Що відомо"
    const tasks = uiConfig[figure].tasks;
    taskSelect.innerHTML = Object.keys(tasks).map(taskKey =>
        `<option value="${taskKey}">${tasks[taskKey].name}</option>`
    ).join('');

    // Викликаємо оновлення інпутів ТА чекбоксів
    updateInputs();
}

// 3. Оновлення полів вводу та чекбоксів при зміні задачі
function updateInputs() {
    const figure = document.getElementById('figure-select').value;
    const task = document.getElementById('task-select').value;

    const inputsDiv = document.getElementById('dynamic-inputs');
    const targetsDiv = document.getElementById('target-checkboxes');

    // Оновлюємо поля вводу (Що відомо)
    const requiredInputs = uiConfig[figure].tasks[task].inputs;
    inputsDiv.innerHTML = requiredInputs.map(inp => `
        <div class="input-group">
            <label for="${inp.id}">${inp.label}</label>
            <input type="number" id="${inp.id}" step="0.1" placeholder="0.0">
        </div>
    `).join('');

    // Оновлюємо чекбокси (Що знайти) залежно від дозволених для цієї задачі
    const allTargets = uiConfig[figure].targets;
    const validTargetIds = uiConfig[figure].tasks[task].validTargets;

    // Фільтруємо масив цілей: залишаємо тільки ті, чий ID є у validTargets
    const filteredTargets = allTargets.filter(t => validTargetIds.includes(t.id));

    targetsDiv.innerHTML = filteredTargets.map(t => `
        <label class="chip-checkbox">
            <input type="checkbox" value="${t.id}" ${t.checked ? 'checked' : ''}>
            <span class="chip-label">${t.label}</span>
        </label>
    `).join('');
}

// 4. Головна функція відправки даних на сервер
async function solve() {
    document.getElementById('error-msg').innerText = '';
    document.getElementById('results').style.display = 'none';

    const figure = document.getElementById('figure-select').value;
    const task = document.getElementById('task-select').value;

    let params = {};
    let hasEmptyFields = false;

    const requiredInputs = uiConfig[figure].tasks[task].inputs;
    requiredInputs.forEach(inp => {
        const val = document.getElementById(inp.id).value;
        if (val === '') hasEmptyFields = true;
        params[inp.id] = parseFloat(val);
    });

    if (hasEmptyFields) {
        document.getElementById('error-msg').innerText = 'Будь ласка, заповніть усі поля!';
        return;
    }

    // Збираємо всі відмічені чекбокси у масив
    const targetCheckboxes = document.querySelectorAll('#target-checkboxes input[type="checkbox"]:checked');
    const targets = Array.from(targetCheckboxes).map(cb => cb.value);

    if (targets.length === 0) {
        document.getElementById('error-msg').innerText = 'Оберіть хоча б один параметр для пошуку!';
        return;
    }

    const requestData = {
        figure: figure,
        task_type: task,
        targets: targets,
        params: params
    };

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (!result.success) {
            document.getElementById('error-msg').innerText = result.error;
        } else {
            document.getElementById('results').style.display = 'block';

            document.getElementById('params-list').innerHTML = Object.entries(result.data || {}).map(([key, val]) =>
                `<li><b>${key}</b>: <span style="color:#007bff; font-weight:bold;">${val}</span></li>`
            ).join('');

            document.getElementById('steps-list').innerHTML = (result.steps || []).map(s => {
                if (s.startsWith("➤")) {
                    return `<div class="step-card"><div class="step-title">${s}</div></div>`;
                }
                if (s.startsWith("Формула:")) {
                    const formula = s.replace("Формула:", "").trim();
                    return `<div class="formula-box">${formula}</div>`;
                }
                if (s.startsWith("Правило:")) {
                    return `<div class="rule-box">${s}</div>`;
                }
                return `<div class="step-description">${s}</div>`;
            }).join('');

            const plotSection = document.getElementById('plot-section');
            if (result.image) {
                document.getElementById('plot-container').innerHTML =
                    `<img class="geometry-plot"
                    src="data:image/svg+xml;base64,${result.image}"
                    alt="Креслення"
                    style="cursor: zoom-in;"
                    onclick="openImageModal(this.src)" />`; // Залишив виклик модалки, яку ми зробили в минулому кроці
                plotSection.style.display = 'block';
            } else {
                plotSection.style.display = 'none';
            }
        }
    } catch (e) {
        console.error(e);
        document.getElementById('error-msg').innerText = 'Внутрішня помилка з\'єднання з сервером.';
    }
}

// --- Логіка масштабування креслення ---
let scale = 1;
let isDragging = false;
let startX, startY, translateX = 0, translateY = 0;

function openImageModal(src) {
    const modal = document.getElementById('image-modal');
    const img = document.getElementById('modal-image');
    img.src = src;
    modal.style.display = 'flex';

    scale = 1; translateX = 0; translateY = 0;
    img.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

document.getElementById('image-modal').addEventListener('click', function(e) {
    if (e.target.id === 'image-modal') {
        this.style.display = 'none';
    }
});

document.getElementById('close-modal-btn').addEventListener('click', function() {
    document.getElementById('image-modal').style.display = 'none';
});

document.getElementById('zoom-container').addEventListener('wheel', (e) => {
    e.preventDefault();
    scale += e.deltaY * -0.002;
    scale = Math.min(Math.max(0.5, scale), 10);
    document.getElementById('modal-image').style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
});

const zoomContainer = document.getElementById('zoom-container');
zoomContainer.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    zoomContainer.style.cursor = 'grabbing';
});
window.addEventListener('mouseup', () => {
    isDragging = false;
    zoomContainer.style.cursor = 'grab';
});
window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    e.preventDefault();
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    document.getElementById('modal-image').style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
});
