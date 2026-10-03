import {
    request
} from "./client.js"


export function getSystemHealth() {
    return request(
        "/api/v1/health"
    )
}
