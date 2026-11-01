function friendlyMessage(detail, status) {
    const source = typeof detail === "string"
        ? detail.trim()
        : ""

    const messages = {
        "Authentication required.":
            "Потрібно увійти в систему.",

        "Invalid or expired session.":
            "Сесію завершено. Увійдіть повторно.",

        "User account is inactive.":
            "Обліковий запис деактивовано.",

        "Administrator access required.":
            "Для цієї дії потрібні права адміністратора.",

        "Collection not found.":
            "Колекцію не знайдено.",

        "Document not found.":
            "Документ не знайдено.",

        "Document file not found.":
            "Файл документа не знайдено.",

        "Database error.":
            "Виникла помилка під час роботи з базою даних.",

        "Document is too large.":
            "Файл перевищує максимально дозволений розмір.",

        "Invalid document.":
            "Некоректний або непідтримуваний файл.",

        "Search query cannot be empty.":
            "Введіть пошуковий запит.",

        "Semantic and hybrid search are disabled in the lightweight cloud deployment.":
            "Семантичний та гібридний пошук недоступні у поточному хмарному профілі."
    }

    if (messages[source]) {
        return messages[source]
    }

    if (source) {
        return source
    }

    if (status === 500) {
        return "Виникла внутрішня помилка сервера."
    }

    return `Не вдалося виконати запит. HTTP ${status}`
}


function isNormalAuthProbe(path) {
    return (
        path === "/api/v1/me"
        || path === "/api/v1/auth/login"
        || path === "/api/v1/auth/register"
        || path === "/api/v1/auth/csrf"
    )
}


function notifyExpiredSession(path) {
    if (
        typeof window === "undefined"
        || isNormalAuthProbe(path)
    ) {
        return
    }

    window.dispatchEvent(
        new CustomEvent(
            "knowledgehub:auth-expired"
        )
    )
}


async function parseResponse(response) {
    if (response.status === 204) {
        return null
    }

    const contentType = response.headers.get(
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


export async function request(path, options = {}) {
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

    const data = await parseResponse(response)

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

        if (response.status === 401) {
            notifyExpiredSession(path)
        }

        const error = new Error(
            friendlyMessage(
                detail,
                response.status
            )
        )

        error.status = response.status
        error.detail = detail

        throw error
    }

    return data
}
