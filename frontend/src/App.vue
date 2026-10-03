<script setup>
import AppFooter from "./components/layout/AppFooter.vue"
import AppHeader from "./components/layout/AppHeader.vue"
</script>

<template>
    <AppHeader />

    <main class="container">
        <RouterView />
    </main>

    <AppFooter />
</template>
