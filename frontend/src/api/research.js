import {
    request
} from "./client.js"

import {
    getCsrfToken
} from "./csrf.js"


export function researchCollection(
    collectionId,
    question,
    limit = 5
) {
    const params =
        new URLSearchParams({
            q: question,
            limit: String(limit)
        })

    return request(
        `/api/v1/collections/${collectionId}`
        + `/research?${params.toString()}`
    )
}


export async function generateResearchAnswer(
    collectionId,
    question,
    limit = 5
) {
    const csrfToken =
        await getCsrfToken()

    return request(
        `/api/v1/collections/${collectionId}`
        + "/research/answer",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",

                "X-CSRF-Token":
                    csrfToken
            },

            body: JSON.stringify({
                question,
                limit
            })
        }
    )
}
