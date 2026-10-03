<script setup>
import {
    useAuth
} from "../composables/useAuth.js"

const {
    currentUser
} = useAuth()
</script>

<template>
    <section class="error-page">
        <div class="error-card">
            <div class="error-code">
                403
            </div>

            <p class="eyebrow">
                KNOWLEDGEHUB
            </p>

            <h1>
                Доступ заборонено
            </h1>

            <p class="error-description">
                У вас немає дозволу
                на виконання цієї дії
                або перегляд цього ресурсу.
            </p>

            <div class="error-actions">
                <RouterLink
                    v-if="currentUser"
                    class="error-primary-button"
                    :to="{ name: 'collections' }"
                >
                    До колекцій
                </RouterLink>

                <RouterLink
                    class="error-secondary-button"
                    :to="{ name: 'home' }"
                >
                    На головну
                </RouterLink>
            </div>
        </div>
    </section>
</template>
