// 1. Ініціалізація сторінки
import { uiConfig } from './config.js';
import { openImageModal, initModalListeners } from './modal.js';
import { renderStep } from './renderer.js';

// Робимо функції доступними глобально для inline-обробників у HTML
window.solve = solve;
window.openImageModal = openImageModal;

window.onload = function() {
    // Ініціалізуємо слухачі для модального вікна
    initModalListeners();

    const figureSelect = document.getElementById('figure-select');
    figureSelect.innerHTML = Object.keys(uiConfig).map(key =>
        `<option value="${key}">${uiConfig[key].name}</option>`
    ).join('');

    // Прив'язуємо події до селектів напряму з JS (краща практика, ніж onclick в HTML)
    figureSelect.addEventListener('change', updateUI);
    document.getElementById('sub-figure-select').addEventListener('change', updateTasks);
    document.getElementById('task-select').addEventListener('change', updateInputs);

    updateUI();
};

function getActiveConfigNode() {
    const figure = document.getElementById('figure-select').value;
    if (uiConfig[figure].hasSubFigures) {
        const subFigure = document.getElementById('sub-figure-select').value;
        return uiConfig[figure].subFigures[subFigure];
    }
    return uiConfig[figure];
}

// 2. Оновлення списку задач при зміні фігури
function updateUI() {
    const figure = document.getElementById('figure-select').value;
    const subFigureGroup = document.getElementById('sub-figure-group');
    const subFigureSelect = document.getElementById('sub-figure-select');

    if (uiConfig[figure].hasSubFigures) {
        // Показуємо вибір виду і заповнюємо його
        subFigureGroup.style.display = 'flex';
        const subFigures = uiConfig[figure].subFigures;
        subFigureSelect.innerHTML = Object.keys(subFigures).map(subKey =>
            `<option value="${subKey}">${subFigures[subKey].name}</option>`
        ).join('');
    } else {
        // Ховаємо вибір виду для простих фігур (коло, трикутник)
        subFigureGroup.style.display = 'none';
    }

    updateTasks(); // Одразу оновлюємо задачі
}

// 3. Оновлення списку задач (Що відомо?)
function updateTasks() {
    const configNode = getActiveConfigNode();
    const taskSelect = document.getElementById('task-select');

    taskSelect.innerHTML = Object.keys(configNode.tasks).map(taskKey =>
        `<option value="${taskKey}">${configNode.tasks[taskKey].name}</option>`
    ).join('');

    updateInputs(); // Одразу оновлюємо інпути та чекбокси
}

// 4. Оновлення полів вводу та чекбоксів при зміні задачі
function updateInputs() {
    const configNode = getActiveConfigNode();
    const task = document.getElementById('task-select').value;

    if (!configNode.tasks[task]) return;

    const inputsDiv = document.getElementById('dynamic-inputs');
    const targetsDiv = document.getElementById('target-checkboxes');

    // Оновлюємо інпути
    const requiredInputs = configNode.tasks[task].inputs;
    inputsDiv.innerHTML = requiredInputs.map(inp => `
        <div class="input-group">
            <label for="${inp.id}">${inp.label}</label>
            <input type="number" id="${inp.id}" step="0.1" placeholder="0.0">
        </div>
    `).join('');

    // Оновлюємо чекбокси з фільтрацією
    const allTargets = configNode.targets;
    const validTargetIds = configNode.tasks[task].validTargets;
    const filteredTargets = allTargets.filter(t => validTargetIds.includes(t.id));

    targetsDiv.innerHTML = filteredTargets.map(t => `
        <label class="chip-checkbox">
            <input type="checkbox" value="${t.id}" ${t.checked ? 'checked' : ''}>
            <span class="chip-label">${t.label}</span>
        </label>
    `).join('');
}

/**
 * @typedef {Object} SolveResponse
 * @property {boolean} success
 * @property {string} [error]
 * @property {Object} [data]
 * @property {string[]} [steps]
 * @property {string} [image]
 */

// 5. Головна функція відправки даних на сервер
async function solve() {
    document.getElementById('error-msg').innerText = '';
    document.getElementById('results').style.display = 'none';

    const figure = document.getElementById('figure-select').value;
    const task = document.getElementById('task-select').value;

    let params = {};
    let hasEmptyFields = false;

    // Отримуємо правильний конфіг
    const configNode = getActiveConfigNode();

    // Використовуємо configNode замість жорсткого uiConfig[figure]
    const requiredInputs = configNode.tasks[task].inputs;

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

        /** @type {SolveResponse} */
        const result = await response.json();

        if (!result.success) {
            document.getElementById('error-msg').innerText = result.error;
        } else {
            document.getElementById('results').style.display = 'block';

            document.getElementById('params-list').innerHTML = Object.entries(result.data || {}).map(([key, val]) =>
                `<li><b>${key}</b>: <span style="color:#007bff; font-weight:bold;">${val}</span></li>`
            ).join('');

            document.getElementById('steps-list').innerHTML = (result.steps || [])
                .map(renderStep)
                .join('');

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
