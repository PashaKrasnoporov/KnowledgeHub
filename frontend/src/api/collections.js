import {
    request
} from "./client.js"

import {
    getCsrfToken
} from "./csrf.js"


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
