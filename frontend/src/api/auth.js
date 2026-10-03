import {
    request
} from "./client.js"

import {
    getAuthCsrfToken
} from "./csrf.js"


export function getCurrentUser() {
    return request(
        "/api/v1/me"
    )
}


export async function registerAccount(
    payload
) {
    const csrfToken =
        await getAuthCsrfToken()

    return request(
        "/api/v1/auth/register",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",

                "X-CSRF-Token":
                    csrfToken
            },

            body: JSON.stringify(
                payload
            )
        }
    )
}


export async function loginAccount(
    payload
) {
    const csrfToken =
        await getAuthCsrfToken()

    return request(
        "/api/v1/auth/login",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",

                "X-CSRF-Token":
                    csrfToken
            },

            body: JSON.stringify(
                payload
            )
        }
    )
}


export async function logoutAccount() {
    const csrfToken =
        await getAuthCsrfToken()

    return request(
        "/api/v1/auth/logout",
        {
            method: "POST",

            headers: {
                "X-CSRF-Token":
                    csrfToken
            }
        }
    )
}
