<script setup>
import {
    ref
} from "vue"

import {
    useRoute,
    useRouter
} from "vue-router"

import {
    useAuth
} from "../composables/useAuth.js"

const route = useRoute()
const router = useRouter()

const {
    login
} = useAuth()

const email = ref("")
const password = ref("")
const submitting = ref(false)
const errors = ref([])

async function submitLogin() {
    submitting.value = true
    errors.value = []

    try {
        await login(
            email.value,
            password.value
        )

        const redirect =
            typeof route.query.redirect === "string"
                ? route.query.redirect
                : "/collections"

        await router.push(
            redirect
        )
    }
    catch (error) {
        errors.value = [
            error.message
        ]
    }
    finally {
        submitting.value = false
    }
}
</script>

<template>
    <section class="register-page">
        <div class="register-card">
            <div class="register-header">
                <p class="eyebrow">
                    KNOWLEDGEHUB
                </p>

                <h1>
                    Вхід у систему
                </h1>

                <p>
                    Введіть email та пароль
                    вашого облікового запису.
                </p>
            </div>

            <div
                v-if="errors.length"
                class="message message-error"
            >
                <strong>
                    Не вдалося виконати вхід.
                </strong>

                <ul>
                    <li
                        v-for="error in errors"
                        :key="error"
                    >
                        {{ error }}
                    </li>
                </ul>
            </div>

            <form
                class="standard-form"
                @submit.prevent="submitLogin"
            >
                <div class="form-field">
                    <label for="email">
                        Email
                    </label>

                    <input
                        id="email"
                        v-model="email"
                        name="email"
                        type="email"
                        autocomplete="email"
                        required
                    >
                </div>

                <div class="form-field">
                    <label for="password">
                        Пароль
                    </label>

                    <input
                        id="password"
                        v-model="password"
                        name="password"
                        type="password"
                        autocomplete="current-password"
                        required
                    >
                </div>

                <button
                    class="form-submit"
                    type="submit"
                    :disabled="submitting"
                >
                    {{
                        submitting
                            ? "Вхід..."
                            : "Увійти"
                    }}
                </button>
            </form>
        </div>
    </section>
</template>
