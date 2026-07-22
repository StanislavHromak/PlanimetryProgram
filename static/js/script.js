import { uiConfig, analyticConfig, GUEST_ALLOWED_FIGURES, TARGET_NAMES } from '/static/js/config.js';
import { initAuth, isLoggedIn, authHeaders, openAuthModal } from '/static/js/auth.js';
import { openImageModal, initModalListeners } from '/static/js/modal.js';
import { renderStep } from '/static/js/renderer.js';
import {
    switchTab,
    repeatSolution, exportPDF, deleteSolution
} from '/static/js/history.js';

// Глобальні функції
window.solve                        = solve;
window.openImageModal               = openImageModal;
window.switchTab                    = switchTab;
window.repeatSolution               = repeatSolution;
window.exportPDF                    = exportPDF;
window.deleteSolution               = deleteSolution;
window.exportCurrentResult          = exportCurrentResult;
window.solveAnalytic                = solveAnalytic;
window.exportCurrentAnalyticResult  = exportCurrentAnalyticResult;
window.findAnalyticSubFigureByTask = (taskType) => {
    return Object.keys(analyticConfig).find(
        subKey => taskType in analyticConfig[subKey].tasks
    );
};

// ID останнього збереженого розв'язку (для кнопки експорту)
let lastSolutionId = null;
let lastAnalyticSolutionId = null;

window.onload = async function () {
    initModalListeners();
    await initAuth();

    renderFigureOptions();

    const figureSelect = document.getElementById('figure-select');
    figureSelect.addEventListener('change', updateUI);
    document.getElementById('sub-figure-select').addEventListener('change', updateTasks);
    document.getElementById('task-select').addEventListener('change', updateInputs);

    updateUI();

    const lockedCta = document.getElementById('analytic-locked-cta');
    if (lockedCta) {
        lockedCta.addEventListener('click', () => openAuthModal('register'));
    }
    applyGuestRestrictions();

    const analyticSubSelect = document.getElementById('analytic-subfigure-select');
    if (analyticSubSelect) {
        analyticSubSelect.innerHTML = Object.keys(analyticConfig).map(key =>
            `<option value="${key}">${analyticConfig[key].name}</option>`
        ).join('');

        analyticSubSelect.addEventListener('change', updateAnalyticTasks);
        document.getElementById('analytic-task-select')?.addEventListener('change', updateAnalyticInputs);

        updateAnalyticTasks();
    }

    window.addEventListener('auth-changed', () => {
        renderFigureOptions();
        updateUI();
        applyGuestRestrictions();
    });
};

function renderFigureOptions() {
    const figureSelect = document.getElementById('figure-select');
    const loggedIn = isLoggedIn();
    const previousValue = figureSelect.value;
    const isAllowed = (key) => loggedIn || GUEST_ALLOWED_FIGURES.includes(key);

    figureSelect.innerHTML = Object.keys(uiConfig).map(key => {
        const allowed = isAllowed(key);
        const label = allowed ? uiConfig[key].name : `🔒 ${uiConfig[key].name}`;
        return `<option value="${key}" ${allowed ? '' : 'disabled'}>${label}</option>`;
    }).join('');

    // Якщо попередньо обрана фігура все ще доступна — лишаємо вибір, інакше беремо першу дозволену
    figureSelect.value = (previousValue && isAllowed(previousValue))
        ? previousValue
        : Object.keys(uiConfig).find(isAllowed);
}

function applyGuestRestrictions() {
    const loggedIn = isLoggedIn();
    const analyticTabBtn = document.querySelector('.tab-btn[data-tab="analytic"]');
    const lockedPanel = document.getElementById('analytic-locked');
    const contentPanel = document.getElementById('analytic-content');

    if (analyticTabBtn) {
        analyticTabBtn.innerHTML = loggedIn ? 'Аналітична геометрія' : '🔒 Аналітична геометрія';
    }
    if (lockedPanel) {
        lockedPanel.style.display = loggedIn ? 'none' : 'flex';
    }
    if (contentPanel) {
        contentPanel.style.display = loggedIn ? 'block' : 'none';
    }
}

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

/**
 * Спільна логіка рендеру полів вводу та чекбоксів цілей.
 * Використовується і для звичайного розв'язувача, і для аналітичної геометрії,
 * щоб не дублювати той самий фрагмент двічі.
 */
function renderInputsAndTargets(configNode, task, inputsDiv, targetsDiv, idPrefix) {
    if (!configNode.tasks[task]) return;

    inputsDiv.innerHTML = configNode.tasks[task].inputs.map(inp => `
        <div class="input-group">
            <label for="${idPrefix}${inp.id}">${inp.label}</label>
            <input type="number" id="${idPrefix}${inp.id}" step="0.1" placeholder="0.0">
        </div>
    `).join('');

    const validTargetIds = configNode.tasks[task].validTargets;
    const filtered = configNode.targets.filter(t => validTargetIds.includes(t.id));

    targetsDiv.innerHTML = filtered.map(t => `
        <label class="chip-checkbox">
            <input type="checkbox" value="${t.id}" ${t.checked ? 'checked' : ''}>
            <span class="chip-label">${t.label}</span>
        </label>
    `).join('');
}

function updateInputs() {
    const configNode = getActiveConfigNode();
    const task = document.getElementById('task-select').value;
    renderInputsAndTargets(
        configNode,
        task,
        document.getElementById('dynamic-inputs'),
        document.getElementById('target-checkboxes'),
        ''
    );
}

/**
 * @typedef {Object} SolveResult
 * @property {boolean} success
 * @property {string} [error]
 * @property {Object} [data]
 * @property {Array} [steps]
 * @property {string|null} [image]
 */

/** @returns {Promise<SolveResult>} */
async function requestSolve(payload) {
    const response = await fetch('/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(payload),
    });
    return response.json();
}

function renderResultCommon({ result, paramsListEl, stepsListEl, plotSectionEl, plotContainerEl }) {
    paramsListEl.innerHTML =
        Object.entries(result.data || {}).map(([key, val]) => {
            const beautifulName = TARGET_NAMES[key] || key;
            return `<li><b>${beautifulName}</b>: <span style="color:#007bff;font-weight:bold;">${val}</span></li>`;
        }).join('');

    stepsListEl.innerHTML = (result.steps || []).map(renderStep).join('');

    if (window.MathJax && window.MathJax.typeset) {
        window.MathJax.typeset();
    }

    if (result.image) {
        plotContainerEl.innerHTML =
            `<img class="geometry-plot"
                  src="data:image/svg+xml;base64,${result.image}"
                  alt="Креслення"
                  style="cursor:zoom-in"
                  onclick="openImageModal(this.src)">`;
        plotSectionEl.style.display = 'block';
    } else {
        plotSectionEl.style.display = 'none';
    }
}

// Розв'язання (вкладка "Планіметрія")
async function solve() {
    const errorMsgEl = document.getElementById('error-msg');
    errorMsgEl.innerText = '';
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
        errorMsgEl.innerText = 'Будь ласка, заповніть усі поля!';
        return;
    }

    const targets = Array.from(
        document.querySelectorAll('#target-checkboxes input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    if (targets.length === 0) {
        errorMsgEl.innerText = 'Оберіть хоча б один параметр для пошуку!';
        return;
    }

    try {
        const result = await requestSolve({ figure, task_type: task, targets, params });

        if (!result.success) {
            errorMsgEl.innerText = result.error;
            return;
        }

        document.getElementById('results').style.display = 'block';
        renderResultCommon({
            result,
            paramsListEl: document.getElementById('params-list'),
            stepsListEl: document.getElementById('steps-list'),
            plotSectionEl: document.getElementById('plot-section'),
            plotContainerEl: document.getElementById('plot-container'),
        });

        try {
            const histRes  = await fetch('/api/history', { headers: authHeaders() });
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
        errorMsgEl.innerText = "Внутрішня помилка з'єднання з сервером.";
    }
}

// Експорт поточного результату
async function exportCurrentResult() {
    if (!lastSolutionId) return;
    await exportPDF(lastSolutionId);
}

function updateAnalyticTasks() {
    const subKey = document.getElementById('analytic-subfigure-select').value;
    const configNode = analyticConfig[subKey];
    const taskSelect = document.getElementById('analytic-task-select');

    taskSelect.innerHTML = Object.keys(configNode.tasks).map(taskKey =>
        `<option value="${taskKey}">${configNode.tasks[taskKey].name}</option>`
    ).join('');

    updateAnalyticInputs();
}

function updateAnalyticInputs() {
    const subKey = document.getElementById('analytic-subfigure-select').value;
    const configNode = analyticConfig[subKey];
    const task = document.getElementById('analytic-task-select').value;
    renderInputsAndTargets(
        configNode,
        task,
        document.getElementById('analytic-dynamic-inputs'),
        document.getElementById('analytic-target-checkboxes'),
        'analytic-'
    );
}

// Розв'язання (вкладка "Аналітична геометрія")
async function solveAnalytic() {
    const errorMsgEl = document.getElementById('analytic-error-msg');
    errorMsgEl.innerText = '';
    document.getElementById('analytic-results').style.display = 'none';
    document.getElementById('analytic-export-btn').style.display = 'none';
    lastAnalyticSolutionId = null;

    const subKey     = document.getElementById('analytic-subfigure-select').value;
    const task       = document.getElementById('analytic-task-select').value;
    const configNode = analyticConfig[subKey];

    let params = {};
    let hasEmptyFields = false;

    configNode.tasks[task].inputs.forEach(inp => {
        const val = document.getElementById(`analytic-${inp.id}`).value;
        if (val === '') hasEmptyFields = true;
        params[inp.id] = parseFloat(val);
    });

    if (hasEmptyFields) {
        errorMsgEl.innerText = 'Будь ласка, заповніть усі поля!';
        return;
    }

    const targets = Array.from(
        document.querySelectorAll('#analytic-target-checkboxes input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    if (targets.length === 0) {
        errorMsgEl.innerText = 'Оберіть хоча б один параметр для пошуку!';
        return;
    }

    try {
        const result = await requestSolve({ figure: 'analytic_geometry', task_type: task, targets, params });

        if (!result.success) {
            errorMsgEl.innerText = result.error;
            return;
        }

        document.getElementById('analytic-results').style.display = 'block';
        renderResultCommon({
            result,
            paramsListEl: document.getElementById('analytic-params-list'),
            stepsListEl: document.getElementById('analytic-steps-list'),
            plotSectionEl: document.getElementById('analytic-plot-section'),
            plotContainerEl: document.getElementById('analytic-plot-container'),
        });

        try {
            const histRes  = await fetch('/api/history', { headers: authHeaders() });
            const histJson = await histRes.json();
            if (histJson.success && histJson.data.length > 0) {
                lastAnalyticSolutionId = histJson.data[0].id;
                document.getElementById('analytic-export-btn').style.display = 'inline-flex';
            }
        } catch (histErr) {
            console.warn('Не вдалося отримати ID для експорту:', histErr);
        }

    } catch (e) {
        console.error(e);
        errorMsgEl.innerText = "Внутрішня помилка з'єднання з сервером.";
    }
}

async function exportCurrentAnalyticResult() {
    if (!lastAnalyticSolutionId) return;
    await exportPDF(lastAnalyticSolutionId);
}
