import {
    createRouter,
    createWebHistory
} from "vue-router"

import AboutView from "../views/AboutView.vue"
import AdminView from "../views/AdminView.vue"
import CollectionDetailView from "../views/CollectionDetailView.vue"
import CollectionsView from "../views/CollectionsView.vue"
import DocumentView from "../views/DocumentView.vue"
import ForbiddenView from "../views/ForbiddenView.vue"
import HomeView from "../views/HomeView.vue"
import InternalErrorView from "../views/InternalErrorView.vue"
import LoginView from "../views/LoginView.vue"
import NotFoundView from "../views/NotFoundView.vue"
import ProfileView from "../views/ProfileView.vue"
import RegisterView from "../views/RegisterView.vue"

import {
    useAuth
} from "../composables/useAuth.js"

const routes = [
    {
        path: "/",
        name: "home",
        component: HomeView,
        meta: {
            title: "KnowledgeHub — Головна"
        }
    },
    {
        path: "/about",
        name: "about",
        component: AboutView,
        meta: {
            title: "Про систему — KnowledgeHub"
        }
    },
    {
        path: "/login",
        name: "login",
        component: LoginView,
        meta: {
            guestOnly: true,
            title: "Вхід — KnowledgeHub"
        }
    },
    {
        path: "/register",
        name: "register",
        component: RegisterView,
        meta: {
            guestOnly: true,
            title: "Реєстрація — KnowledgeHub"
        }
    },
    {
        path: "/profile",
        name: "profile",
        component: ProfileView,
        meta: {
            requiresAuth: true,
            title: "Профіль — KnowledgeHub"
        }
    },
    {
        path: "/collections",
        name: "collections",
        component: CollectionsView,
        meta: {
            requiresAuth: true,
            title: "Колекції — KnowledgeHub"
        }
    },
    {
        path: "/collections/:collectionId",
        name: "collection-detail",
        component: CollectionDetailView,
        meta: {
            requiresAuth: true
        }
    },
    {
        path: "/collections/:collectionId/documents/:documentId",
        name: "document",
        component: DocumentView,
        meta: {
            requiresAuth: true
        }
    },
    {
        path: "/admin",
        name: "admin",
        component: AdminView,
        meta: {
            requiresAuth: true,
            requiresAdmin: true,
            title: "Адміністрування — KnowledgeHub"
        }
    },
    {
        path: "/403",
        name: "forbidden",
        component: ForbiddenView,
        meta: {
            title: "403 — Доступ заборонено"
        }
    },
    {
        path: "/500",
        name: "internal-error",
        component: InternalErrorView,
        meta: {
            title: "500 — Внутрішня помилка"
        }
    },
    {
        path: "/:pathMatch(.*)*",
        name: "not-found",
        component: NotFoundView,
        meta: {
            title: "404 — Сторінку не знайдено"
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,

    scrollBehavior() {
        return {
            top: 0
        }
    }
})

router.beforeEach(
    async to => {
        const {
            currentUser,
            ensureAuthReady
        } = useAuth()

        try {
            await ensureAuthReady()
        }
        catch {
            if (
                to.meta.requiresAuth
                || to.meta.requiresAdmin
            ) {
                return {
                    name: "login",
                    query: {
                        redirect: to.fullPath
                    }
                }
            }

            return true
        }

        if (
            to.meta.requiresAuth
            && !currentUser.value
        ) {
            return {
                name: "login",
                query: {
                    redirect: to.fullPath
                }
            }
        }

        if (
            to.meta.requiresAdmin
            && currentUser.value?.role !== "admin"
        ) {
            return {
                name: "forbidden"
            }
        }

        if (
            to.meta.guestOnly
            && currentUser.value
        ) {
            return {
                name: "collections"
            }
        }

        return true
    }
)

router.afterEach(
    to => {
        if (
            typeof to.meta.title === "string"
        ) {
            document.title =
                to.meta.title
        }
    }
)

export default router
