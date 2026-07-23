import { authHeaders, getCurrentUser, refreshCurrentUser } from '/static/js/auth.js';

let pendingAvatarDataUrl = null;

export function initProfileEditModal() {
    document.getElementById('profile-edit-close').addEventListener('click', closeProfileEditModal);
    document.getElementById('profile-edit-modal').addEventListener('click', (e) => {
        if (e.target.id === 'profile-edit-modal') closeProfileEditModal();
    });
}

export function openProfileEditModal() {
    const user = getCurrentUser();
    if (!user) return;
    renderProfileEditBody(user);
    document.getElementById('profile-edit-modal').style.display = 'flex';
}

function closeProfileEditModal() {
    document.getElementById('profile-edit-modal').style.display = 'none';
    pendingAvatarDataUrl = null;
}

function renderProfileEditBody(user) {
    document.getElementById('profile-edit-body').innerHTML = `
        <h3>Редагування профілю</h3>
        <div class="profile-field">
            <label for="profile-display-name">Ім'я</label>
            <input type="text" id="profile-display-name" value="${user.display_name || ''}">
        </div>
        <div class="profile-field">
            <label for="profile-username">Логін</label>
            <input type="text" id="profile-username" value="${user.username}">
        </div>
        <div class="profile-field">
            <label for="profile-email">Пошта</label>
            <input type="email" id="profile-email" value="${user.email || ''}">
        </div>
        <button class="profile-btn-submit" id="profile-save-btn">Зберегти зміни</button>
        <div id="profile-edit-error" class="profile-error"></div>
        <hr style="margin:1.2rem 0;">
        <h3>Зміна пароля</h3>
        <div class="profile-field">
            <label for="current-password">Поточний пароль</label>
            <input type="password" id="current-password">
        </div>
        <div class="profile-field">
            <label for="new-password">Новий пароль</label>
            <input type="password" id="new-password">
        </div>
        <button class="profile-btn-submit" id="password-save-btn">Змінити пароль</button>
        <div id="password-edit-error" class="profile-error"></div>
        <hr style="margin:1.2rem 0;">
        <button class="profile-btn-logout" id="delete-account-btn">Видалити акаунт</button>
    `;

    document.getElementById('profile-save-btn').addEventListener('click', handleProfileSave);
    document.getElementById('password-save-btn').addEventListener('click', handlePasswordSave);
    document.getElementById('delete-account-btn').addEventListener('click', handleDeleteAccount);
}

async function handleProfileSave() {
    const errorEl = document.getElementById('profile-edit-error');
    errorEl.innerText = '';
    const payload = {
        username: document.getElementById('profile-username').value.trim(),
        display_name: document.getElementById('profile-display-name').value.trim() || null,
        email: document.getElementById('profile-email').value.trim() || null,
    };

    try {
        const res = await fetch('/api/auth/me', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка збереження.');
        await refreshCurrentUser();
        closeProfileEditModal();
        window.dispatchEvent(new CustomEvent('auth-changed'));
    } catch (e) {
        errorEl.innerText = e.message;
    }
}

async function handlePasswordSave() {
    const errorEl = document.getElementById('password-edit-error');
    errorEl.innerText = '';
    const current_password = document.getElementById('current-password').value;
    const new_password = document.getElementById('new-password').value;
    try {
        const res = await fetch('/api/auth/me/password', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({ current_password, new_password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Помилка зміни пароля.');
        alert('Пароль успішно змінено.');
    } catch (e) {
        errorEl.innerText = e.message;
    }
}

async function handleDeleteAccount() {
    if (!confirm("Видалити акаунт назавжди? Це також видалить усю вашу історію.")) return;
    await fetch('/api/auth/me', { method: 'DELETE', headers: authHeaders() });
    localStorage.removeItem('planimetry_token');
    window.location.reload();
}