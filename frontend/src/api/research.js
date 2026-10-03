import {
    request
} from "./client.js"


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
