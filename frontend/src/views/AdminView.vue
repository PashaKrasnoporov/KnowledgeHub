<script setup>
import {
    onMounted,
    ref
} from "vue"

import {
    getAdminUsers,
    setUserActiveStatus
} from "../api/index.js"

import {
    useAuth
} from "../composables/useAuth.js"


const {
    currentUser
} = useAuth()

const users = ref([])
const loading = ref(true)
const changingUserId = ref(null)
const errorMessage = ref("")
const successMessage = ref("")

const confirmDialog = ref(null)
const pendingUser = ref(null)


function roleLabel(role) {
    return role === "admin"
        ? "Адміністратор"
        : "Користувач"
}


async function loadUsers() {
    loading.value = true
    errorMessage.value = ""

    try {
        users.value = await getAdminUsers()
    }
    catch (error) {
        errorMessage.value = error.message
    }
    finally {
        loading.value = false
    }
}


function requestStatusChange(user) {
    pendingUser.value = user
    confirmDialog.value?.showModal()
}


function closeConfirmation() {
    if (changingUserId.value !== null) {
        return
    }

    confirmDialog.value?.close()
    pendingUser.value = null
}


async function changeStatus(user) {
    changingUserId.value = user.id
    errorMessage.value = ""
    successMessage.value = ""

    try {
        const updated = await setUserActiveStatus(
            user.id,
            !user.is_active
        )

        const index = users.value.findIndex(
            item => item.id === updated.id
        )

        if (index !== -1) {
            users.value[index] = updated
        }

        successMessage.value = updated.is_active
            ? "Користувача активовано."
            : "Користувача деактивовано."
    }
    catch (error) {
        errorMessage.value = error.message
            || "Не вдалося виконати адміністративну дію."
    }
    finally {
        changingUserId.value = null
    }
}


async function confirmStatusChange() {
    if (!pendingUser.value) {
        return
    }

    const user = pendingUser.value

    await changeStatus(user)

    confirmDialog.value?.close()
    pendingUser.value = null
}


onMounted(loadUsers)
</script>

<template>
    <section class="admin-page">
        <header class="admin-header">
            <p class="eyebrow">
                ADMIN
            </p>

            <h1>
                Панель адміністратора
            </h1>

            <p>
                Керування користувачами KnowledgeHub.
            </p>
        </header>

        <div
            v-if="successMessage"
            class="message message-success"
        >
            <p>{{ successMessage }}</p>
        </div>

        <div
            v-if="errorMessage"
            class="message message-error"
        >
            <p>{{ errorMessage }}</p>
        </div>

        <div
            v-if="loading"
            class="empty-state"
        >
            <h2>Завантаження...</h2>
        </div>

        <div
            v-else
            class="admin-table-wrapper"
        >
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Користувач</th>
                        <th>Email</th>
                        <th>Роль</th>
                        <th>Статус</th>
                        <th>Дія</th>
                    </tr>
                </thead>

                <tbody>
                    <tr
                        v-for="user in users"
                        :key="user.id"
                    >
                        <td>{{ user.id }}</td>
                        <td>{{ user.name }}</td>
                        <td>{{ user.email }}</td>

                        <td>
                            <span
                                class="role-badge"
                                :class="{
                                    'role-admin': user.role === 'admin'
                                }"
                            >
                                {{ roleLabel(user.role) }}
                            </span>
                        </td>

                        <td>
                            <span
                                v-if="user.is_active"
                                class="status-active"
                            >
                                Активний
                            </span>

                            <span
                                v-else
                                class="status-inactive"
                            >
                                Неактивний
                            </span>
                        </td>

                        <td>
                            <span
                                v-if="user.id === currentUser?.id"
                                class="admin-current-user"
                            >
                                Поточний адміністратор
                            </span>

                            <button
                                v-else-if="user.is_active"
                                class="admin-deactivate-button"
                                type="button"
                                @click="requestStatusChange(user)"
                            >
                                Деактивувати
                            </button>

                            <button
                                v-else
                                class="admin-activate-button"
                                type="button"
                                @click="requestStatusChange(user)"
                            >
                                Активувати
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <dialog
            ref="confirmDialog"
            class="admin-confirm-dialog"
        >
            <div
                v-if="pendingUser"
                class="admin-confirm-content"
            >
                <p class="eyebrow">
                    ПІДТВЕРДЖЕННЯ
                </p>

                <h2>
                    {{
                        pendingUser.is_active
                            ? "Деактивувати користувача?"
                            : "Активувати користувача?"
                    }}
                </h2>

                <p>
                    <strong>{{ pendingUser.name }}</strong>
                    ·
                    {{ pendingUser.email }}
                </p>

                <p v-if="pendingUser.is_active">
                    Користувач втратить доступ до KnowledgeHub,
                    доки його акаунт не буде активовано знову.
                </p>

                <div class="admin-confirm-actions">
                    <button
                        class="secondary-button"
                        type="button"
                        :disabled="changingUserId !== null"
                        @click="closeConfirmation"
                    >
                        Скасувати
                    </button>

                    <button
                        :class="
                            pendingUser.is_active
                                ? 'danger-button'
                                : 'admin-activate-button'
                        "
                        type="button"
                        :disabled="changingUserId !== null"
                        @click="confirmStatusChange"
                    >
                        {{
                            changingUserId !== null
                                ? "Збереження..."
                                : (
                                    pendingUser.is_active
                                        ? "Деактивувати"
                                        : "Активувати"
                                )
                        }}
                    </button>
                </div>
            </div>
        </dialog>
    </section>
</template>

<style scoped>
.admin-confirm-dialog {
    width: min(92vw, 520px);
    padding: 0;

    border: 1px solid var(--mezha);
    border-radius: 14px;
    background: var(--poverkhna-svitla);
    color: var(--tekst-osnovnyi);
    box-shadow: 0 22px 70px rgba(38, 60, 67, 0.20);
}

.admin-confirm-dialog::backdrop {
    background: rgba(38, 60, 67, 0.36);
}

.admin-confirm-content {
    padding: 26px;
}

.admin-confirm-content h2 {
    margin: 6px 0 14px;
}

.admin-confirm-content > p {
    color: var(--tekst-drugoryadnyi);
    line-height: 1.6;
}

.admin-confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 24px;
}

@media (max-width: 520px) {
    .admin-confirm-actions {
        flex-direction: column-reverse;
    }

    .admin-confirm-actions button {
        width: 100%;
    }
}
</style>
