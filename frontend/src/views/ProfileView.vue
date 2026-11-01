<script setup>
import {
    computed
} from "vue"

import {
    useRouter
} from "vue-router"

import {
    useAuth
} from "../composables/useAuth.js"


const router = useRouter()

const {
    currentUser,
    logout
} = useAuth()


const roleLabel = computed(
    () => (
        currentUser.value?.role === "admin"
            ? "Адміністратор"
            : "Користувач"
    )
)


const createdAt = computed(
    () => {
        const value = currentUser.value?.created_at

        if (!value) {
            return "—"
        }

        const date = new Date(value)

        if (Number.isNaN(date.getTime())) {
            return "—"
        }

        return new Intl.DateTimeFormat(
            "uk-UA",
            {
                day: "2-digit",
                month: "long",
                year: "numeric"
            }
        ).format(date)
    }
)


async function submitLogout() {
    await logout()

    await router.push({
        name: "login"
    })
}
</script>

<template>
    <section
        v-if="currentUser"
        class="profile-page"
    >
        <header class="profile-header">
            <p class="eyebrow">
                KNOWLEDGEHUB
            </p>

            <h1>
                Профіль
            </h1>

            <p>
                Дані вашого облікового запису
                та поточної сесії.
            </p>
        </header>

        <section class="profile-card">
            <div class="profile-avatar">
                {{
                    currentUser.name
                        ?.trim()
                        ?.charAt(0)
                        ?.toUpperCase()
                    || "K"
                }}
            </div>

            <div class="profile-main">
                <h2>
                    {{ currentUser.name }}
                </h2>

                <p>
                    {{ currentUser.email }}
                </p>

                <span class="profile-role">
                    {{ roleLabel }}
                </span>
            </div>
        </section>

        <section class="profile-details">
            <article>
                <span>Email</span>
                <strong>{{ currentUser.email }}</strong>
            </article>

            <article>
                <span>Роль</span>
                <strong>{{ roleLabel }}</strong>
            </article>

            <article>
                <span>Акаунт створено</span>
                <strong>{{ createdAt }}</strong>
            </article>

            <article>
                <span>Статус</span>
                <strong>Активний</strong>
            </article>
        </section>

        <section class="profile-session">
            <div>
                <h2>
                    Поточна сесія
                </h2>

                <p>
                    Вихід завершить вашу
                    поточну авторизовану сесію.
                </p>
            </div>

            <button
                class="secondary-button"
                type="button"
                @click="submitLogout"
            >
                Вийти із системи
            </button>
        </section>
    </section>
</template>

<style scoped>
.profile-page {
    padding: 64px 0 80px;
}

.profile-header {
    max-width: 700px;
    margin-bottom: 28px;
}

.profile-header p:last-child {
    color: var(--tekst-drugoryadnyi);
}

.profile-card {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px;

    border: 1px solid var(--mezha);
    border-radius: 14px;
    background: var(--poverkhna-svitla);
}

.profile-avatar {
    display: flex;
    width: 68px;
    height: 68px;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    border-radius: 50%;
    background: var(--morska-pina);
    color: var(--morskyi-hlybokyi);

    font-size: 28px;
    font-weight: 800;
}

.profile-main h2 {
    margin: 0 0 5px;
}

.profile-main p {
    margin: 0 0 9px;
    color: var(--tekst-drugoryadnyi);
}

.profile-role {
    display: inline-flex;
    padding: 5px 9px;
    border-radius: 999px;
    background: var(--poverkhna);
    color: var(--akvamarin-temnyi);
    font-size: 12px;
    font-weight: 700;
}

.profile-details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
}

.profile-details article {
    padding: 18px;
    border: 1px solid var(--mezha);
    border-radius: 11px;
    background: var(--poverkhna-svitla);
}

.profile-details span {
    display: block;
    margin-bottom: 7px;
    color: var(--tekst-drugoryadnyi);
    font-size: 12px;
}

.profile-session {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    margin-top: 18px;
    padding: 22px;

    border: 1px solid var(--mezha);
    border-radius: 14px;
    background: var(--poverkhna-svitla);
}

.profile-session h2 {
    margin: 0 0 6px;
    font-size: 20px;
}

.profile-session p {
    margin: 0;
    color: var(--tekst-drugoryadnyi);
}

@media (max-width: 620px) {
    .profile-card,
    .profile-session {
        align-items: flex-start;
        flex-direction: column;
    }

    .profile-details {
        grid-template-columns: 1fr;
    }

    .profile-session button {
        width: 100%;
    }
}
</style>
