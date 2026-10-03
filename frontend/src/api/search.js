import {
    request
} from "./client.js"


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
        `/api/v1/collections/${collectionId}`
        + `/search?${params.toString()}`
    )
}
