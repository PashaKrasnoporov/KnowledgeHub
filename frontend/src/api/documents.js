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


function parseUploadResponse(
    xhr
) {
    if (xhr.status === 204) {
        return null
    }

    const contentType =
        xhr.getResponseHeader(
            "content-type"
        ) || ""

    if (
        contentType.includes(
            "application/json"
        )
    ) {
        try {
            return JSON.parse(
                xhr.responseText
            )
        }
        catch {
            return null
        }
    }

    return xhr.responseText
}


export async function uploadDocument(
    collectionId,
    file,
    onProgress = null
) {
    const csrfToken =
        await getCsrfToken()

    const formData =
        new FormData()

    formData.append(
        "document_file",
        file
    )

    return new Promise(
        (
            resolve,
            reject
        ) => {
            const xhr =
                new XMLHttpRequest()

            xhr.open(
                "POST",
                `/api/v1/collections/${collectionId}/documents`
            )

            xhr.withCredentials = true

            xhr.setRequestHeader(
                "X-CSRF-Token",
                csrfToken
            )

            xhr.upload.onprogress =
                event => {
                    if (
                        !event.lengthComputable
                        || typeof onProgress !== "function"
                    ) {
                        return
                    }

                    const percent =
                        Math.round(
                            (
                                event.loaded
                                / event.total
                            ) * 100
                        )

                    onProgress(
                        Math.min(
                            100,
                            Math.max(
                                0,
                                percent
                            )
                        )
                    )
                }

            xhr.onload =
                () => {
                    const data =
                        parseUploadResponse(
                            xhr
                        )

                    if (
                        xhr.status >= 200
                        && xhr.status < 300
                    ) {
                        if (
                            typeof onProgress
                            === "function"
                        ) {
                            onProgress(100)
                        }

                        resolve(data)
                        return
                    }

                    let detail = data

                    if (
                        data
                        && typeof data === "object"
                    ) {
                        detail =
                            data.detail
                    }

                    const error =
                        new Error(
                            detail
                            || `HTTP error ${xhr.status}`
                        )

                    error.status =
                        xhr.status

                    reject(error)
                }

            xhr.onerror =
                () => {
                    const error =
                        new Error(
                            "Помилка мережі під час завантаження файла."
                        )

                    error.status = 0

                    reject(error)
                }

            xhr.send(
                formData
            )
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
