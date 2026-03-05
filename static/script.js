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
            "SSS": { name: "Три сторони (SSS)", inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "c", label: "Сторона c" } ] },
            "SAS": { name: "Дві сторони і кут (SAS)", inputs: [ { id: "a", label: "Сторона a" }, { id: "b", label: "Сторона b" }, { id: "angle_c", label: "Кут між ними γ (°)" } ] },
            "ASA": { name: "Сторона і два кути (ASA)", inputs: [ { id: "a", label: "Сторона a" }, { id: "angle_b", label: "Прилеглий кут β (°)" }, { id: "angle_c", label: "Прилеглий кут γ (°)" } ] }
        }
    },
    circle: {
        name: "Коло та Круг",
        targets: [
            { id: "area", label: "Площу круга (S)", checked: true },
            { id: "perimeter", label: "Довжину кола (C)", checked: true },
            { id: "arc", label: "Довжину дуги (L)", checked: false },         // <--- НОВЕ
            { id: "sector_area", label: "Площу сектора", checked: false },    // <--- НОВЕ
            { id: "chord", label: "Довжину хорди (c)", checked: false }       // <--- НОВЕ
        ],
        tasks: {
            "RADIUS": { name: "Відомий радіус (r)", inputs: [ { id: "radius", label: "Радіус r" } ] },
            "DIAMETER": { name: "Відомий діаметр (d)", inputs: [ { id: "diameter", label: "Діаметр d" } ] },
            "CIRCUMFERENCE": { name: "Відома довжина кола (C)", inputs: [ { id: "circumference", label: "Довжина C" } ] },
            "AREA": { name: "Відома площа (S)", inputs: [ { id: "area", label: "Площа S" } ] },
            "SECTOR_ANGLE": { name: "Сектор: Радіус і Кут", inputs: [ { id: "radius", label: "Радіус r" }, { id: "angle", label: "Кут α (°)" } ] } // <--- НОВЕ
        }
    }
};

// 1. Ініціалізація сторінки (заповнюємо список фігур)
window.onload = function() {
    const figureSelect = document.getElementById('figure-select');
    figureSelect.innerHTML = Object.keys(uiConfig).map(key =>
        `<option value="${key}">${uiConfig[key].name}</option>`
    ).join('');

    updateUI(); // Запускаємо оновлення інтерфейсу
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

    // Оновлюємо чекбокси "Що знайти"
    const targetsDiv = document.getElementById('target-checkboxes');
    const targets = uiConfig[figure].targets;
    targetsDiv.innerHTML = targets.map(t => `
        <label><input type="checkbox" value="${t.id}" ${t.checked ? 'checked' : ''}> ${t.label}</label>
    `).join('');

    updateInputs();
}

// 3. Оновлення полів вводу при зміні задачі
function updateInputs() {
    const figure = document.getElementById('figure-select').value;
    const task = document.getElementById('task-select').value;
    const inputsDiv = document.getElementById('dynamic-inputs');

    const requiredInputs = uiConfig[figure].tasks[task].inputs;

    inputsDiv.innerHTML = requiredInputs.map(inp => `
        <div class="input-group">
            <label for="${inp.id}">${inp.label}</label>
            <input type="number" id="${inp.id}" step="0.1" placeholder="0.0">
        </div>
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

        /** * @type {{success: boolean, error?: string, data?: Object, steps?: string[], image?: string}}
         */
        const result = await response.json();

        if (!result.success) {
            document.getElementById('error-msg').innerText = result.error;
        } else {
            document.getElementById('results').style.display = 'block';

            document.getElementById('params-list').innerHTML = Object.entries(result.data || {}).map(([key, val]) =>
                `<li><b>${key}</b>: <span style="color:#007bff; font-weight:bold;">${val}</span></li>`
            ).join('');

            document.getElementById('steps-list').innerHTML = (result.steps || []).map(s => {
                if (s.startsWith("➤")) return `<div class="step-header">${s}</div>`;
                if (s.startsWith("Правило:")) return `<div class="step-rule">${s}</div>`;
                return `<div class="step-text">${s}</div>`;
            }).join('');

            const plotSection = document.getElementById('plot-section');
            if (result.image) {
                document.getElementById('plot-container').innerHTML = `<img src="data:image/png;base64,${result.image}" alt="Креслення" />`;
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