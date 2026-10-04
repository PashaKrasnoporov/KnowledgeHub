import {
    request
} from "./client.js"


export function getSystemHealth() {
    return request(
        "/api/v1/health"
    )
}


function sleep(
    milliseconds
) {
    return new Promise(
        resolve => {
            window.setTimeout(
                resolve,
                milliseconds
            )
        }
    )
}


export async function waitForSystemHealth({
    attempts = 16,
    delayMs = 700,
    onWaiting = null
} = {}) {
    let lastError = null

    for (
        let attempt = 1;
        attempt <= attempts;
        attempt += 1
    ) {
        try {
            return await getSystemHealth()
        }
        catch (error) {
            lastError = error

            if (
                typeof onWaiting
                === "function"
            ) {
                onWaiting(
                    attempt,
                    attempts
                )
            }

            if (attempt < attempts) {
                await sleep(
                    delayMs
                )
            }
        }
    }

    const error = new Error(
        "Backend KnowledgeHub ще не готовий. "
        + "Зачекайте кілька секунд і повторіть вхід."
    )

    error.cause = lastError

    throw error
}
