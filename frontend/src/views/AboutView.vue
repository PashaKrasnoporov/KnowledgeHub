<script setup>
import {
    onMounted,
    ref
} from "vue"

import {
    getSystemHealth
} from "../api/index.js"


const version = ref(null)
const versionLoaded = ref(false)


onMounted(
    async () => {
        try {
            const data =
                await getSystemHealth()

            version.value =
                data.api_version || null
        }
        catch {
            version.value = null
        }
        finally {
            versionLoaded.value = true
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

        <p class="system-version">
            Поточна версія системи:

            <strong
                v-if="versionLoaded && version"
            >
                {{ version }}
            </strong>

            <span
                v-else-if="!versionLoaded"
                class="version-placeholder"
                aria-label="Завантаження версії"
            >
                …
            </span>

            <strong v-else>
                недоступна
            </strong>.
        </p>

        <p>
            Надалі система розширюватиметься засобами
            семантичного пошуку, аналізу документів
            та технологіями штучного інтелекту.
        </p>
    </section>
</template>


<style scoped>
.version-placeholder {
    display: inline-block;
    min-width: 24px;
    font-weight: 700;
}
</style>
