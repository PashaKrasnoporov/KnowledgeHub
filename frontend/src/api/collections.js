import {
    request
} from "./client.js"

import {
    getCsrfToken
} from "./csrf.js"


export function getCollections(
    {
        q = "",
        sortBy = "created_at",
        sortOrder = "desc"
    } = {}
) {
    const params = new URLSearchParams()

    const normalizedQuery =
        q.trim()

    if (normalizedQuery) {
        params.set(
            "q",
            normalizedQuery
        )
    }

    params.set(
        "sort_by",
        sortBy
    )

    params.set(
        "sort_order",
        sortOrder
    )

    return request(
        `/api/v1/collections?${params.toString()}`
    )
}


export function getCollection(
    collectionId
) {
    return request(
        `/api/v1/collections/${collectionId}`
    )
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