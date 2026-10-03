import {
    readonly,
    ref
} from "vue"

import {
    getCurrentUser,
    loginAccount,
    logoutAccount
} from "../api/index.js"


const currentUser = ref(null)
const authReady = ref(false)
const authLoading = ref(false)


async function refreshCurrentUser() {
    authLoading.value = true

    try {
        currentUser.value =
            await getCurrentUser()

        return currentUser.value
    }
    catch (error) {
        if (
            error.status === 401 ||
            error.status === 403
        ) {
            currentUser.value = null
            return null
        }

        throw error
    }
    finally {
        authReady.value = true
        authLoading.value = false
    }
}


async function ensureAuthReady() {
    if (!authReady.value) {
        await refreshCurrentUser()
    }

    return currentUser.value
}


async function login(
    email,
    password
) {
    currentUser.value =
        await loginAccount({
            email,
            password
        })

    authReady.value = true

    return currentUser.value
}


async function logout() {
    try {
        await logoutAccount()
    }
    finally {
        currentUser.value = null
        authReady.value = true
    }
}


export function useAuth() {
    return {
        currentUser: readonly(
            currentUser
        ),

        authReady: readonly(
            authReady
        ),

        authLoading: readonly(
            authLoading
        ),

        ensureAuthReady,
        refreshCurrentUser,
        login,
        logout
    }
}
