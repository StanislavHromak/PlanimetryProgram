import { uiConfig, TARGET_NAMES } from '/static/js/config.js';
import { openImageModal, initModalListeners } from '/static/js/modal.js';
import { renderStep } from '/static/js/renderer.js';
import {
    switchTab,
    repeatSolution, exportPDF, deleteSolution
} from '/static/js/history.js';

// Глобальні функції
window.solve               = solve;
window.openImageModal      = openImageModal;
window.switchTab           = switchTab;
window.repeatSolution      = repeatSolution;
window.exportPDF           = exportPDF;
window.deleteSolution      = deleteSolution;
window.exportCurrentResult = exportCurrentResult;

// ID останнього збереженого розв'язку (для кнопки експорту)
let lastSolutionId = null;

window.onload = function () {
    initModalListeners();

    const figureSelect = document.getElementById('figure-select');
    figureSelect.innerHTML = Object.keys(uiConfig).map(key =>
        `<option value="${key}">${uiConfig[key].name}</option>`
    ).join('');

    figureSelect.addEventListener('change', updateUI);
    document.getElementById('sub-figure-select').addEventListener('change', updateTasks);
    document.getElementById('task-select').addEventListener('change', updateInputs);

    updateUI();
};

// Конфігурація UI
function getActiveConfigNode() {
    const figure = document.getElementById('figure-select').value;
    if (uiConfig[figure].hasSubFigures) {
        const subFigure = document.getElementById('sub-figure-select').value;
        return uiConfig[figure].subFigures[subFigure];
    }
    return uiConfig[figure];
}

function updateUI() {
    const figure = document.getElementById('figure-select').value;
    const subFigureGroup  = document.getElementById('sub-figure-group');
    const subFigureSelect = document.getElementById('sub-figure-select');

    if (uiConfig[figure].hasSubFigures) {
        subFigureGroup.style.display = 'flex';
        const subFigures = uiConfig[figure].subFigures;
        subFigureSelect.innerHTML = Object.keys(subFigures).map(subKey =>
            `<option value="${subKey}">${subFigures[subKey].name}</option>`
        ).join('');
    } else {
        subFigureGroup.style.display = 'none';
    }
    updateTasks();
}

function updateTasks() {
    const configNode = getActiveConfigNode();
    const taskSelect = document.getElementById('task-select');

    taskSelect.innerHTML = Object.keys(configNode.tasks).map(taskKey =>
        `<option value="${taskKey}">${configNode.tasks[taskKey].name}</option>`
    ).join('');

    updateInputs();
}

function updateInputs() {
    const configNode = getActiveConfigNode();
    const task = document.getElementById('task-select').value;
    if (!configNode.tasks[task]) return;

    const inputsDiv  = document.getElementById('dynamic-inputs');
    const targetsDiv = document.getElementById('target-checkboxes');

    inputsDiv.innerHTML = configNode.tasks[task].inputs.map(inp => `
        <div class="input-group">
            <label for="${inp.id}">${inp.label}</label>
            <input type="number" id="${inp.id}" step="0.1" placeholder="0.0">
        </div>
    `).join('');

    const allTargets     = configNode.targets;
    const validTargetIds = configNode.tasks[task].validTargets;
    const filtered       = allTargets.filter(t => validTargetIds.includes(t.id));

    targetsDiv.innerHTML = filtered.map(t => `
        <label class="chip-checkbox">
            <input type="checkbox" value="${t.id}" ${t.checked ? 'checked' : ''}>
            <span class="chip-label">${t.label}</span>
        </label>
    `).join('');
}

// Розв'язання
async function solve() {
    document.getElementById('error-msg').innerText = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('export-btn').style.display = 'none';
    lastSolutionId = null;

    const figure     = document.getElementById('figure-select').value;
    const task       = document.getElementById('task-select').value;
    const configNode = getActiveConfigNode();

    let params = {};
    let hasEmptyFields = false;

    configNode.tasks[task].inputs.forEach(inp => {
        const val = document.getElementById(inp.id).value;
        if (val === '') hasEmptyFields = true;
        params[inp.id] = parseFloat(val);
    });

    if (hasEmptyFields) {
        document.getElementById('error-msg').innerText = 'Будь ласка, заповніть усі поля!';
        return;
    }

    const targets = Array.from(
        document.querySelectorAll('#target-checkboxes input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    if (targets.length === 0) {
        document.getElementById('error-msg').innerText = 'Оберіть хоча б один параметр для пошуку!';
        return;
    }

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ figure, task_type: task, targets, params }),
        });

        const result = await response.json();

        if (!result.success) {
            document.getElementById('error-msg').innerText = result.error;
            return;
        }

        // Відображаємо результати
        document.getElementById('results').style.display = 'block';

        document.getElementById('params-list').innerHTML =
            Object.entries(result.data || {}).map(([key, val]) => {
                // Використовуємо словник, якщо ключа немає - виводимо оригінальний ключ
                const beautifulName = TARGET_NAMES[key] || key;
                return `<li><b>${beautifulName}</b>: <span style="color:#007bff;font-weight:bold;">${val}</span></li>`;
            }).join('');

        document.getElementById('steps-list').innerHTML =
            (result.steps || []).map(renderStep).join('');

        const plotSection = document.getElementById('plot-section');
        if (result.image) {
            document.getElementById('plot-container').innerHTML =
                `<img class="geometry-plot"
                      src="data:image/svg+xml;base64,${result.image}"
                      alt="Креслення"
                      style="cursor:zoom-in"
                      onclick="openImageModal(this.src)">`;
            plotSection.style.display = 'block';
        } else {
            plotSection.style.display = 'none';
        }

        // Отримуємо ID збереженого запису для кнопки експорту
        try {
            const histRes  = await fetch('/api/history');
            const histJson = await histRes.json();
            if (histJson.success && histJson.data.length > 0) {
                lastSolutionId = histJson.data[0].id;
                document.getElementById('export-btn').style.display = 'inline-flex';
            }
        } catch (histErr) {
            console.warn('Не вдалося отримати ID для експорту:', histErr);
        }

    } catch (e) {
        console.error(e);
        document.getElementById('error-msg').innerText = "Внутрішня помилка з'єднання з сервером.";
    }
}

// Експорт поточного результату
async function exportCurrentResult() {
    if (!lastSolutionId) return;
    await exportPDF(lastSolutionId);
}
