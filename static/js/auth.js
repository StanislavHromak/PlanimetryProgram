const TOKEN_KEY = 'planimetry_token';

export function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

export function isLoggedIn() {
    return !!getToken();
}

export function authHeaders() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function extractErrorMessage(data) {
    if (!data) return 'Сталася невідома помилка.';
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map(e => e.msg).join(' ');
    }
    return 'Сталася невідома помилка.';
}

async function register(username, password) {
    const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(extractErrorMessage(data));
    return data;
}

async function login(username, password) {
    const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(extractErrorMessage(data));
    return data;
}

async function fetchMe() {
    const res = await fetch('/api/auth/me', { headers: authHeaders() });
    if (!res.ok) return null;
    return res.json();
}

let currentMode = 'login'; // 'login' | 'register'
let currentUser = null;    // { id, username } | null

const el = (id) => document.getElementById(id);

// ===== Маленька прикріплена панель (тільки для залогінених — швидке меню сесії) =====

function renderLoggedInPanel() {
    el('profile-panel').innerHTML = `
        <div class="profile-user-info">
            <span class="profile-username">${currentUser.username}</span>
            <span class="profile-role-badge">Користувач</span>
        </div>
        <button class="profile-btn-logout" id="profile-logout-btn">Вийти</button>
    `;

    el('profile-logout-btn').addEventListener('click', () => {
        clearToken();
        currentUser = null;
        closeProfilePanel();
        updateAuthUI();
        window.dispatchEvent(new CustomEvent('auth-changed'));
    });
}

function closeProfilePanel() {
    el('profile-panel').classList.remove('profile-panel--open');
}

function toggleProfilePanel() {
    el('profile-panel').classList.toggle('profile-panel--open');
}

// ===== Модальне вікно логіну/реєстрації (доступне з будь-якого місця сторінки) =====

function renderAuthModalBody() {
    const isRegister = currentMode === 'register';
    el('auth-modal-body').innerHTML = `
        <h3>${isRegister ? 'Реєстрація' : 'Вхід'}</h3>
        <p class="profile-guest-hint">Гості можуть розв'язувати задачі лише про трикутники.</p>
        <div class="profile-field">
            <label for="auth-username">Ім'я користувача</label>
            <input type="text" id="auth-username" placeholder="username">
        </div>
        <div class="profile-field">
            <label for="auth-password">Пароль</label>
            <input type="password" id="auth-password" placeholder="••••••">
        </div>
        <button class="profile-btn-submit" id="auth-submit-btn">
            ${isRegister ? 'Зареєструватися' : 'Увійти'}
        </button>
        <div id="auth-error" class="profile-error"></div>
        <div class="profile-switch-mode">
            ${isRegister
                ? 'Вже маєте акаунт? <a id="auth-switch-link">Увійти</a>'
                : 'Немає акаунта? <a id="auth-switch-link">Зареєструватися</a>'}
        </div>
    `;

    el('auth-switch-link').addEventListener('click', () => {
        currentMode = isRegister ? 'login' : 'register';
        renderAuthModalBody();
    });

    el('auth-submit-btn').addEventListener('click', handleAuthSubmit);

    ['auth-username', 'auth-password'].forEach(id => {
        el(id).addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleAuthSubmit();
        });
    });

    el('auth-username').focus();
}

async function handleAuthSubmit() {
    const username = el('auth-username').value.trim();
    const password = el('auth-password').value;
    const errorEl = el('auth-error');
    errorEl.innerText = '';

    if (!username || !password) {
        errorEl.innerText = 'Заповніть обидва поля.';
        return;
    }

    try {
        const data = currentMode === 'register'
            ? await register(username, password)
            : await login(username, password);

        setToken(data.access_token);
        currentUser = await fetchMe();
        closeAuthModal();
        updateAuthUI();
        window.dispatchEvent(new CustomEvent('auth-changed'));
    } catch (e) {
        errorEl.innerText = e.message;
    }
}

/** Відкриває модалку логіну/реєстрації. Викликається і з іконки, і з кнопки на заблокованому розділі. */
export function openAuthModal(mode = 'login') {
    currentMode = mode;
    renderAuthModalBody();
    el('auth-modal').style.display = 'flex';
}

function closeAuthModal() {
    el('auth-modal').style.display = 'none';
}

function updateAuthUI() {
    const btn = el('profile-btn');
    btn.classList.toggle('profile-btn--logged-in', !!currentUser);
}

export async function initAuth() {
    // Клік на іконку: залогінений → прикріплене меню, гість → модалка
    el('profile-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentUser) {
            toggleProfilePanel();
        } else {
            openAuthModal('login');
        }
    });

    // Закриття прикріпленого меню при кліку поза ним
    document.addEventListener('click', (e) => {
        const panel = el('profile-panel');
        const btn = el('profile-btn');
        if (!panel.contains(e.target) && !btn.contains(e.target)) {
            closeProfilePanel();
        }
    });
    el('profile-panel').addEventListener('click', (e) => e.stopPropagation());

    // Закриття модалки: хрестик або клік по затемненому фону
    el('auth-modal-close').addEventListener('click', closeAuthModal);
    el('auth-modal').addEventListener('click', (e) => {
        if (e.target.id === 'auth-modal') closeAuthModal();
    });

    if (isLoggedIn()) {
        currentUser = await fetchMe();
        if (!currentUser) {
            clearToken();
        }
    }

    updateAuthUI();
    if (currentUser) {
        renderLoggedInPanel();
    }
}