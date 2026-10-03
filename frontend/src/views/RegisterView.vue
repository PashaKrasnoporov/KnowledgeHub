<script setup>
import {
    ref
} from "vue"

import {
    registerAccount
} from "../api/index.js"

const name = ref("")
const email = ref("")
const password = ref("")
const passwordConfirmation = ref("")

const submitting = ref(false)
const success = ref(false)
const errors = ref([])

async function submitRegistration() {
    errors.value = []

    if (
        password.value
        !== passwordConfirmation.value
    ) {
        errors.value = [
            "Паролі не збігаються."
        ]

        return
    }

    submitting.value = true

    try {
        await registerAccount({
            name: name.value,
            email: email.value,
            password: password.value,
            password_confirmation:
                passwordConfirmation.value
        })

        success.value = true
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
                    Створення облікового запису
                </h1>

                <p>
                    Зареєструйтеся, щоб створювати
                    власні колекції та працювати
                    з документами.
                </p>
            </div>

            <template v-if="success">
                <div class="message message-success">
                    <strong>
                        Реєстрацію успішно завершено.
                    </strong>

                    <p>
                        Обліковий запис створено.
                        Далі ми підключимо вхід
                        у систему.
                    </p>
                </div>

                <RouterLink
                    class="button primary"
                    :to="{ name: 'home' }"
                >
                    Перейти на головну
                </RouterLink>
            </template>

            <template v-else>
                <div
                    v-if="errors.length"
                    class="message message-error"
                >
                    <strong>
                        Не вдалося завершити
                        реєстрацію.
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
                    @submit.prevent="submitRegistration"
                >
                    <div class="form-field">
                        <label for="name">
                            Ім'я
                        </label>

                        <input
                            id="name"
                            v-model="name"
                            name="name"
                            type="text"
                            minlength="2"
                            maxlength="50"
                            autocomplete="name"
                            required
                        >
                    </div>

                    <div class="form-field">
                        <label for="email">
                            Email
                        </label>

                        <input
                            id="email"
                            v-model="email"
                            name="email"
                            type="email"
                            maxlength="255"
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
                            minlength="8"
                            maxlength="128"
                            autocomplete="new-password"
                            required
                        >

                        <p class="form-hint">
                            Мінімум 8 символів.
                        </p>
                    </div>

                    <div class="form-field">
                        <label for="password_confirmation">
                            Повторіть пароль
                        </label>

                        <input
                            id="password_confirmation"
                            v-model="passwordConfirmation"
                            name="password_confirmation"
                            type="password"
                            minlength="8"
                            maxlength="128"
                            autocomplete="new-password"
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
                                ? "Реєстрація..."
                                : "Зареєструватися"
                        }}
                    </button>
                </form>
            </template>
        </div>
    </section>
</template>
