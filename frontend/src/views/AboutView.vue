<script setup>
import {
    onMounted,
    ref
} from "vue"

import {
    getSystemHealth
} from "../api/index.js"

const version = ref("0.1.0")

onMounted(
    async () => {
        try {
            const data = await getSystemHealth()

            version.value =
                data.api_version || "0.1.0"
        }
        catch {
            version.value = "0.1.0"
        }
    }
)
</script>

<template>
    <section class="page-section">
        <p class="eyebrow">
            ABOUT
        </p>

        <h1>
            Про KnowledgeHub
        </h1>

        <p>
            KnowledgeHub — вебплатформа для організації,
            зберігання та пошуку інформації у персональних
            колекціях документів.
        </p>

        <p>
            Поточна версія системи:
            <strong>{{ version }}</strong>.
        </p>

        <p>
            Надалі система розширюватиметься засобами
            семантичного пошуку, аналізу документів
            та технологіями штучного інтелекту.
        </p>
    </section>
</template>
