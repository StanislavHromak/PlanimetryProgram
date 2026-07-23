import { authHeaders, getCurrentUser } from '/static/js/auth.js';

export async function loadAdminUsers() {
    const container = document.getElementById('admin-users-list');
    container.innerHTML = 'Завантаження...';
    try {
        const res = await fetch('/api/admin/users', { headers: authHeaders() });
        const json = await res.json();
        if (!json.success) {
            container.innerHTML = '<div class="history-empty">Не вдалося завантажити список.</div>';
            return;
        }
        renderAdminUsers(json.data);
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="history-empty">Помилка завантаження.</div>';
    }
}

function renderAdminUsers(users) {
    const me = getCurrentUser();
    document.getElementById('admin-users-list').innerHTML = `
        <table class="admin-users-table" style="width:100%; border-collapse:collapse;">
            <thead>
                <tr>
                    <th style="text-align:left;">Ім'я</th>
                    <th style="text-align:left;">Роль</th>
                    <th style="text-align:left;">Статус</th>
                    <th style="text-align:left;">Дії</th>
                </tr>
            </thead>
            <tbody>${users.map(u => renderUserRow(u, me)).join('')}</tbody>
        </table>
    `;
}

function renderUserRow(u, me) {
    if (me && me.id === u.id) {
        return `<tr><td>${u.username}</td><td>${u.role}</td><td>${u.is_active ? 'Активний' : 'Заблокований'}</td>
                <td><span class="history-hint">Це ви</span></td></tr>`;
    }
    return `
        <tr data-id="${u.id}">
            <td>${u.username}</td>
            <td>${u.role}</td>
            <td>${u.is_active ? 'Активний' : 'Заблокований'}</td>
            <td>
                <button class="btn-history btn-history--view" onclick="window.adminShowDetails(${u.id})">
                    Повна інформація
                </button>
                <button class="btn-history btn-history--view" onclick="window.adminToggleBlock(${u.id}, ${u.is_active})">
                    ${u.is_active ? 'Заблокувати' : 'Розблокувати'}
                </button>
                <button class="btn-history btn-history--view" onclick="window.adminToggleRole(${u.id}, '${u.role}')">
                    ${u.role === 'admin' ? 'Зняти адміна' : 'Зробити адміном'}
                </button>
                <button class="btn-history btn-history--delete" onclick="window.adminDeleteUser(${u.id})">
                    Видалити
                </button>
            </td>
        </tr>`;
}

export async function adminShowDetails(userId) {
    try {
        const res = await fetch(`/api/admin/users/${userId}`, { headers: authHeaders() });
        const json = await res.json();
        if (!json.success) {
            alert('Не вдалося завантажити дані користувача.');
            return;
        }
        const u = json.data;
        alert(
            `Ім'я користувача: ${u.username}\n` +
            `Відображуване ім'я: ${u.display_name || '—'}\n` +
            `Пошта: ${u.email || '—'}\n` +
            `Роль: ${u.role}\n` +
            `Статус: ${u.is_active ? 'Активний' : 'Заблокований'}\n` +
            `Зареєстрований: ${u.created_at || '—'}`
        );
    } catch (e) {
        console.error(e);
        alert('Помилка завантаження.');
    }
}

export async function adminToggleBlock(userId, isActive) {
    await fetch(`/api/admin/users/${userId}/${isActive ? 'block' : 'unblock'}`, {
        method: 'POST', headers: authHeaders(),
    });
    await loadAdminUsers();
}

export async function adminToggleRole(userId, currentRole) {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    if (!confirm(`Змінити роль користувача на "${newRole}"?`)) return;
    await fetch(`/api/admin/users/${userId}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ role: newRole }),
    });
    await loadAdminUsers();
}

export async function adminDeleteUser(userId) {
    if (!confirm('Видалити цей акаунт і всю його історію без можливості відновлення?')) return;
    await fetch(`/api/admin/users/${userId}`, { method: 'DELETE', headers: authHeaders() });
    await loadAdminUsers();
}

