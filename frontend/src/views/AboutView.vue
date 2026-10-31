<script setup>
const SYSTEM_VERSION = "v1"
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
            <strong>{{ SYSTEM_VERSION }}</strong>.
        </p>

        <p>
            Надалі система розширюватиметься засобами
            семантичного пошуку, аналізу документів
            та технологіями штучного інтелекту.
        </p>
    </section>
</template>
