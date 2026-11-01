<script setup>
import {
    onMounted,
    onUnmounted
} from "vue"

import {
    useRouter
} from "vue-router"

import AppFooter from "./components/layout/AppFooter.vue"
import AppHeader from "./components/layout/AppHeader.vue"

import {
    useAuth
} from "./composables/useAuth.js"


const router = useRouter()

const {
    clearAuthState
} = useAuth()


async function handleAuthExpired() {
    const current = router.currentRoute.value

    clearAuthState()

    if (
        current.name === "login"
        || current.name === "register"
    ) {
        return
    }

    await router.replace({
        name: "login",
        query: {
            redirect: current.fullPath,
            reason: "session-expired"
        }
    })
}


onMounted(
    () => {
        window.addEventListener(
            "knowledgehub:auth-expired",
            handleAuthExpired
        )
    }
)


onUnmounted(
    () => {
        window.removeEventListener(
            "knowledgehub:auth-expired",
            handleAuthExpired
        )
    }
)
</script>

<template>
    <a
        class="skip-link"
        href="#main-content"
    >
        Перейти до основного вмісту
    </a>

    <AppHeader />

    <main
        id="main-content"
        class="container app-main"
        tabindex="-1"
    >
        <RouterView />
    </main>

    <AppFooter />
</template>
