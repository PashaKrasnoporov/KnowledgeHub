<script setup>
import {
    useRouter
} from "vue-router"

import {
    useAuth
} from "../composables/useAuth.js"

const router = useRouter()

const {
    currentUser,
    logout
} = useAuth()

async function submitLogout() {
    await logout()

    await router.push({
        name: "login"
    })
}
</script>

<template>
    <section
        v-if="currentUser"
        class="hero"
    >
        <p class="eyebrow">
            KNOWLEDGEHUB
        </p>

        <h1>
            Профіль користувача
        </h1>

        <p>
            Ви успішно авторизовані.
        </p>

        <div class="feature-card">
            <p>
                <strong>ID:</strong>
                {{ currentUser.id }}
            </p>

            <p>
                <strong>Ім'я:</strong>
                {{ currentUser.name }}
            </p>

            <p>
                <strong>Email:</strong>
                {{ currentUser.email }}
            </p>

            <p>
                <strong>Роль:</strong>
                {{ currentUser.role }}
            </p>
        </div>

        <form
            style="margin-top: 24px;"
            @submit.prevent="submitLogout"
        >
            <button
                class="form-submit"
                type="submit"
            >
                Вийти
            </button>
        </form>
    </section>
</template>
