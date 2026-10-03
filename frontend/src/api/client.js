async function parseResponse(
    response
) {
    if (response.status === 204) {
        return null
    }

    const contentType =
        response.headers.get(
            "content-type"
        ) || ""

    if (
        contentType.includes(
            "application/json"
        )
    ) {
        return response.json()
    }

    return response.text()
}


export async function request(
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
        await parseResponse(
            response
        )

    if (!response.ok) {
        let detail = null

        if (
            data
            && typeof data === "object"
        ) {
            detail = data.detail
        }
        else {
            detail = data
        }

        const error = new Error(
            detail
            || `HTTP error ${response.status}`
        )

        error.status =
            response.status

        throw error
    }

    return data
}
