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

async function loadUsers() {
    loading.value = true
    errorMessage.value = ""

    try {
        users.value =
            await getAdminUsers()
    }
    catch (error) {
        errorMessage.value =
            error.message
    }
    finally {
        loading.value = false
    }
}

async function changeStatus(user) {
    changingUserId.value = user.id
    errorMessage.value = ""
    successMessage.value = ""

    try {
        const updated =
            await setUserActiveStatus(
                user.id,
                !user.is_active
            )

        const index =
            users.value.findIndex(
                item =>
                    item.id === updated.id
            )

        if (index !== -1) {
            users.value[index] =
                updated
        }

        successMessage.value =
            "Статус користувача успішно оновлено."
    }
    catch (error) {
        if (user.id === currentUser.value?.id) {
            errorMessage.value =
                "Адміністратор не може деактивувати власний обліковий запис."
        }
        else {
            errorMessage.value =
                "Не вдалося виконати адміністративну дію."
        }
    }
    finally {
        changingUserId.value = null
    }
}

onMounted(
    loadUsers
)
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
            <p>
                {{ successMessage }}
            </p>
        </div>

        <div
            v-if="errorMessage"
            class="message message-error"
        >
            <p>
                {{ errorMessage }}
            </p>
        </div>

        <div
            v-if="loading"
            class="empty-state"
        >
            <h2>
                Завантаження...
            </h2>
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
                        <td>
                            {{ user.id }}
                        </td>

                        <td>
                            {{ user.name }}
                        </td>

                        <td>
                            {{ user.email }}
                        </td>

                        <td>
                            <span
                                class="role-badge"
                                :class="{
                                    'role-admin':
                                        user.role === 'admin'
                                }"
                            >
                                {{ user.role }}
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
                                v-if="
                                    user.id
                                    === currentUser?.id
                                "
                                class="admin-current-user"
                            >
                                Поточний адміністратор
                            </span>

                            <button
                                v-else-if="user.is_active"
                                class="admin-deactivate-button"
                                type="button"
                                :disabled="
                                    changingUserId === user.id
                                "
                                @click="changeStatus(user)"
                            >
                                Деактивувати
                            </button>

                            <button
                                v-else
                                class="admin-activate-button"
                                type="button"
                                :disabled="
                                    changingUserId === user.id
                                "
                                @click="changeStatus(user)"
                            >
                                Активувати
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>
