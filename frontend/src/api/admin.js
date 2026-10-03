import {
    request
} from "./client.js"

import {
    getCsrfToken
} from "./csrf.js"


export function getAdminUsers() {
    return request(
        "/api/v1/admin/users"
    )
}


export async function setUserActiveStatus(
    userId,
    isActive
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        `/api/v1/admin/users/${userId}/active`,
        {
            method: "PATCH",

            headers: {
                "Content-Type":
                    "application/json",

                "X-CSRF-Token":
                    csrfToken
            },

            body: JSON.stringify({
                is_active: isActive
            })
        }
    )
}
