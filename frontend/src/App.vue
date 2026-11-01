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
    <AppHeader />

    <main class="container app-main">
        <RouterView />
    </main>

    <AppFooter />
</template>
