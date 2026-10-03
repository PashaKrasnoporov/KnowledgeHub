import {
    request
} from "./client.js"

import {
    getCsrfToken
} from "./csrf.js"


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
        `/api/v1/collections/${collectionId}`
        + `/documents/${documentId}`,
        {
            method: "DELETE",

            headers: {
                "X-CSRF-Token":
                    csrfToken
            }
        }
    )
}


export function getDocument(
    collectionId,
    documentId
) {
    return request(
        `/api/v1/collections/${collectionId}`
        + `/documents/${documentId}`
    )
}


export function getDocumentContentUrl(
    collectionId,
    documentId
) {
    return (
        `/api/v1/collections/${collectionId}`
        + `/documents/${documentId}/content`
    )
}


export function getDocumentDownloadUrl(
    collectionId,
    documentId
) {
    return (
        `/api/v1/collections/${collectionId}`
        + `/documents/${documentId}/download`
    )
}
