// Конфігурація: які фігури є, які в них задачі, і які поля треба малювати
const uiConfig = {
    triangle: {
        name: "Трикутник",
        tasks: {
            "SSS": {
                name: "За трьома сторонами (SSS)",
                inputs: [
                    { id: "a", label: "Сторона a" },
                    { id: "b", label: "Сторона b" },
                    { id: "c", label: "Сторона c" }
                ]
            }
            // Тут потім додамо SAS, ASA...
        }
    },
    circle: {
        name: "Коло та Круг",
        tasks: {
            "RADIUS": {
                name: "Відомий радіус (r)",
                inputs: [
                    { id: "radius", label: "Радіус r" }
                ]
            }
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

    const tasks = uiConfig[figure].tasks;
    taskSelect.innerHTML = Object.keys(tasks).map(taskKey =>
        `<option value="${taskKey}">${tasks[taskKey].name}</option>`
    ).join('');

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
    // Очищуємо старі помилки і ховаємо результати
    document.getElementById('error-msg').innerText = '';
    document.getElementById('results').style.display = 'none';

    const figure = document.getElementById('figure-select').value;
    const task = document.getElementById('task-select').value;

    // Збираємо числа з динамічних полів у словник params
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

    // Формуємо універсальний DTO для нашого API
    const requestData = {
        figure: figure,
        task_type: task,
        target: "all",
        params: params
    };

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        /** * JSDoc: Підказуємо редактору структуру об'єкта, який повертає наш Python API.
         * Це виправляє помилку "Unresolved variable".
         * @type {{success: boolean, error?: string, data?: Object, steps?: string[], image?: string}}
         */
        const result = await response.json();

        if (!result.success) {
            document.getElementById('error-msg').innerText = result.error;
        } else {
            // Успіх! Показуємо блок результатів
            document.getElementById('results').style.display = 'block';

            // Виправлення 1: Пряме присвоєння без зайвої змінної (і захист через || {})
            document.getElementById('params-list').innerHTML = Object.entries(result.data || {}).map(([key, val]) =>
                `<li><b>${key}</b>: <span style="color:#007bff; font-weight:bold;">${val}</span></li>`
            ).join('');

            // Виправлення 2: Пряме присвоєння без зайвої змінної (і захист через || [])
            document.getElementById('steps-list').innerHTML = (result.steps || []).map(s => {
                if (s.startsWith("➤")) return `<div class="step-header">${s}</div>`;
                if (s.startsWith("Правило:")) return `<div class="step-rule">${s}</div>`;
                return `<div class="step-text">${s}</div>`;
            }).join('');

            // Відображення картинки (перевірка result.image більше не підсвічується як помилка)
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