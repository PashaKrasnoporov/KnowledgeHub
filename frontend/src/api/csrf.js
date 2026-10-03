import {
    request
} from "./client.js"


export async function getCsrfToken() {
    const data = await request(
        "/api/v1/csrf"
    )

    return data.csrf_token
}


export async function getAuthCsrfToken() {
    const data = await request(
        "/api/v1/auth/csrf"
    )

    return data.csrf_token
}
