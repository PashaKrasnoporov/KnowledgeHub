<script setup>
import {
    useAuth
} from "../../composables/useAuth.js"

const {
    currentUser
} = useAuth()
</script>

<template>
    <header class="site-header">
        <div class="container header-content">
            <RouterLink
                class="logo"
                :to="{ name: 'home' }"
            >
                KnowledgeHub
            </RouterLink>

            <nav
                class="navigation"
                aria-label="Основна навігація"
            >
                <RouterLink :to="{ name: 'home' }">
                    Головна
                </RouterLink>

                <RouterLink :to="{ name: 'about' }">
                    Про систему
                </RouterLink>

                <template v-if="currentUser">
                    <RouterLink :to="{ name: 'collections' }">
                        Колекції
                    </RouterLink>

                    <RouterLink :to="{ name: 'profile' }">
                        Профіль
                    </RouterLink>

                    <RouterLink
                        v-if="currentUser.role === 'admin'"
                        :to="{ name: 'admin' }"
                    >
                        Адмін
                    </RouterLink>
                </template>

                <template v-else>
                    <RouterLink :to="{ name: 'register' }">
                        Реєстрація
                    </RouterLink>

                    <RouterLink :to="{ name: 'login' }">
                        Вхід
                    </RouterLink>
                </template>
            </nav>
        </div>
    </header>
</template>
