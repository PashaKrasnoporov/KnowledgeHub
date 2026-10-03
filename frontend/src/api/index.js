async function parseResponse(response) {
    if (response.status === 204) {
        return null
    }

    const contentType =
        response.headers.get("content-type") || ""

    if (
        contentType.includes(
            "application/json"
        )
    ) {
        return response.json()
    }

    return response.text()
}


async function request(
    path,
    options = {}
) {
    const response = await fetch(
        path,
        {
            credentials: "include",

            ...options,

            headers: {
                ...(options.headers || {})
            }
        }
    )

    const data =
        await parseResponse(response)

    if (!response.ok) {
        let detail = null

        if (
            data &&
            typeof data === "object"
        ) {
            detail = data.detail
        }
        else {
            detail = data
        }

        const error = new Error(
            detail ||
            `HTTP error ${response.status}`
        )

        error.status =
            response.status

        throw error
    }

    return data
}


export function getCurrentUser() {
    return request(
        "/api/v1/me"
    )
}


export function getCollections() {
    return request(
        "/api/v1/collections"
    )
}


export function getCollection(
    collectionId
) {
    return request(
        `/api/v1/collections/${collectionId}`
    )
}


export async function getCsrfToken() {
    const data = await request(
        "/api/v1/csrf"
    )

    return data.csrf_token
}


export async function createCollection(
    payload
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        "/api/v1/collections",
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


export async function updateCollection(
    collectionId,
    payload
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        `/api/v1/collections/${collectionId}`,
        {
            method: "PATCH",

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


export async function deleteCollection(
    collectionId
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        `/api/v1/collections/${collectionId}`,
        {
            method: "DELETE",

            headers: {
                "X-CSRF-Token":
                    csrfToken
            }
        }
    )
}


export function getDocuments(
    collectionId
) {
    return request(
        `/api/v1/collections/${collectionId}/documents`
    )
}


export async function uploadDocument(
    collectionId,
    file
) {
    const csrfToken =
        await getCsrfToken()

    const formData =
        new FormData()

    formData.append(
        "document_file",
        file
    )

    return request(
        `/api/v1/collections/${collectionId}/documents`,
        {
            method: "POST",

            headers: {
                "X-CSRF-Token":
                    csrfToken
            },

            body: formData
        }
    )
}


export async function deleteDocument(
    collectionId,
    documentId
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        `/api/v1/collections/${collectionId}` +
        `/documents/${documentId}`,
        {
            method: "DELETE",

            headers: {
                "X-CSRF-Token":
                    csrfToken
            }
        }
    )
}


export function getDocumentDownloadUrl(
    collectionId,
    documentId
) {
    return (
        `/api/v1/collections/${collectionId}` +
        `/documents/${documentId}/download`
    )
}


export function searchCollection(
    collectionId,
    query,
    mode
) {
    const params =
        new URLSearchParams({
            q: query,
            mode: mode,
            limit: "50"
        })

    return request(
        `/api/v1/collections/${collectionId}` +
        `/search?${params.toString()}`
    )
}

export async function getAuthCsrfToken() {
    const data = await request(
        "/api/v1/auth/csrf"
    )

    return data.csrf_token
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


export function getSystemHealth() {
    return request(
        "/api/v1/health"
    )
}


export function getDocument(
    collectionId,
    documentId
) {
    return request(
        `/api/v1/collections/${collectionId}` +
        `/documents/${documentId}`
    )
}


export function getDocumentContentUrl(
    collectionId,
    documentId
) {
    return (
        `/api/v1/collections/${collectionId}` +
        `/documents/${documentId}/content`
    )
}


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
