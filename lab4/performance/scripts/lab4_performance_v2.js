import http from "k6/http";
import { check, fail, sleep } from "k6";
import { Counter, Rate, Trend } from "k6/metrics";

const BASE_URL = (__ENV.BASE_URL || "").replace(/\/+$/, "");
const SCENARIO = (__ENV.SCENARIO || "health").toLowerCase();
const TEST_EMAIL = __ENV.TEST_EMAIL || "";
const TEST_PASSWORD = __ENV.TEST_PASSWORD || "";
const COLLECTION_ID = __ENV.COLLECTION_ID || "";
const SEARCH_QUERY = __ENV.SEARCH_QUERY || "performance";
const SEARCH_LIMIT = Number(__ENV.SEARCH_LIMIT || 10);

const SESSION_COOKIE_NAME = "knowledgehub_session";

export const targetReqDuration = new Trend(
    "target_req_duration",
    true
);

export const targetReqFailed = new Rate(
    "target_req_failed"
);

export const targetChecksSuccess = new Rate(
    "target_checks_success"
);

export const targetReqs = new Counter(
    "target_reqs"
);

export const options = {
    vus: Number(__ENV.VUS || 1),
    duration: __ENV.DURATION || "15s",
    summaryTrendStats: [
        "avg",
        "min",
        "med",
        "max",
        "p(90)",
        "p(95)",
        "p(99)",
    ],
};

function requireBaseUrl() {
    if (!BASE_URL) {
        fail("BASE_URL is required.");
    }
}

function authenticate() {
    if (!TEST_EMAIL || !TEST_PASSWORD) {
        fail(
            "TEST_EMAIL and TEST_PASSWORD are required " +
            "for protected scenarios."
        );
    }

    const csrfResponse = http.get(
        `${BASE_URL}/api/v1/auth/csrf`,
        {
            tags: {
                phase: "authentication_setup",
            },
        }
    );

    const csrfOk = check(
        csrfResponse,
        {
            "CSRF endpoint returned HTTP 200": (r) =>
                r.status === 200,
            "CSRF response contains token": (r) => {
                try {
                    return Boolean(
                        r.json("csrf_token")
                    );
                } catch (_) {
                    return false;
                }
            },
        }
    );

    if (!csrfOk) {
        fail(
            `Cannot obtain CSRF token. ` +
            `HTTP ${csrfResponse.status}`
        );
    }

    const csrfToken = csrfResponse.json(
        "csrf_token"
    );

    const loginResponse = http.post(
        `${BASE_URL}/api/v1/auth/login`,
        JSON.stringify({
            email: TEST_EMAIL,
            password: TEST_PASSWORD,
        }),
        {
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": csrfToken,
            },
            tags: {
                phase: "authentication_setup",
            },
        }
    );

    const loginOk = check(
        loginResponse,
        {
            "Login returned HTTP 200": (r) =>
                r.status === 200,
        }
    );

    if (!loginOk) {
        fail(
            `Login failed. ` +
            `HTTP ${loginResponse.status}: ` +
            `${loginResponse.body}`
        );
    }

    const sessionCookies =
        loginResponse.cookies[
            SESSION_COOKIE_NAME
        ];

    if (
        !sessionCookies ||
        sessionCookies.length === 0 ||
        !sessionCookies[0].value
    ) {
        fail(
            `Login response did not set ` +
            `${SESSION_COOKIE_NAME}.`
        );
    }

    return sessionCookies[0].value;
}

export function setup() {
    requireBaseUrl();

    if (SCENARIO === "health") {
        return {
            sessionToken: null,
        };
    }

    return {
        sessionToken: authenticate(),
    };
}

function targetRequest(
    url,
    sessionToken,
    endpointTag
) {
    const headers = {
        "User-Agent":
            "KnowledgeHub-Lab4-k6/2.0",
    };

    if (sessionToken) {
        headers.Cookie =
            `${SESSION_COOKIE_NAME}=` +
            `${sessionToken}`;
    }

    const response = http.get(
        url,
        {
            headers,
            tags: {
                phase: "measured_request",
                scenario: SCENARIO,
                endpoint: endpointTag,
            },
        }
    );

    targetReqDuration.add(
        response.timings.duration,
        {
            scenario: SCENARIO,
            endpoint: endpointTag,
        }
    );

    const failed =
        response.status !== 200;

    targetReqFailed.add(
        failed,
        {
            scenario: SCENARIO,
            endpoint: endpointTag,
        }
    );

    targetReqs.add(
        1,
        {
            scenario: SCENARIO,
            endpoint: endpointTag,
        }
    );

    return response;
}

export default function (data) {
    let response;
    let checksOk;

    if (SCENARIO === "health") {
        response = targetRequest(
            `${BASE_URL}/api/v1/health`,
            null,
            "GET /api/v1/health"
        );

        checksOk = check(
            response,
            {
                "health: HTTP 200": (r) =>
                    r.status === 200,
                "health: status is ok": (r) => {
                    try {
                        return (
                            r.json("status") ===
                            "ok"
                        );
                    } catch (_) {
                        return false;
                    }
                },
            }
        );
    } else if (
        SCENARIO === "collections"
    ) {
        response = targetRequest(
            `${BASE_URL}/api/v1/collections`,
            data.sessionToken,
            "GET /api/v1/collections"
        );

        checksOk = check(
            response,
            {
                "collections: HTTP 200": (r) =>
                    r.status === 200,
                "collections: JSON array": (r) => {
                    try {
                        return Array.isArray(
                            r.json()
                        );
                    } catch (_) {
                        return false;
                    }
                },
            }
        );
    } else if (
        SCENARIO === "documents"
    ) {
        if (!COLLECTION_ID) {
            fail(
                "COLLECTION_ID is required " +
                "for documents scenario."
            );
        }

        response = targetRequest(
            `${BASE_URL}/api/v1/collections/` +
            `${COLLECTION_ID}/documents`,
            data.sessionToken,
            "GET /api/v1/collections/{id}/documents"
        );

        checksOk = check(
            response,
            {
                "documents: HTTP 200": (r) =>
                    r.status === 200,
                "documents: JSON array": (r) => {
                    try {
                        return Array.isArray(
                            r.json()
                        );
                    } catch (_) {
                        return false;
                    }
                },
            }
        );
    } else if (
        SCENARIO === "search"
    ) {
        if (!COLLECTION_ID) {
            fail(
                "COLLECTION_ID is required " +
                "for search scenario."
            );
        }

        const encodedQuery =
            encodeURIComponent(
                SEARCH_QUERY
            );

        response = targetRequest(
            `${BASE_URL}/api/v1/collections/` +
            `${COLLECTION_ID}/search` +
            `?q=${encodedQuery}` +
            `&mode=lexical` +
            `&limit=${SEARCH_LIMIT}`,
            data.sessionToken,
            "GET /api/v1/collections/{id}/search?mode=lexical"
        );

        checksOk = check(
            response,
            {
                "search: HTTP 200": (r) =>
                    r.status === 200,
                "search: lexical mode": (r) => {
                    try {
                        return (
                            r.json("mode") ===
                            "lexical"
                        );
                    } catch (_) {
                        return false;
                    }
                },
                "search: results field exists": (r) => {
                    try {
                        return Array.isArray(
                            r.json("results")
                        );
                    } catch (_) {
                        return false;
                    }
                },
            }
        );
    } else {
        fail(
            `Unknown SCENARIO "${SCENARIO}". ` +
            `Allowed: health, collections, ` +
            `documents, search.`
        );
    }

    targetChecksSuccess.add(
        checksOk,
        {
            scenario: SCENARIO,
        }
    );

    sleep(
        Number(
            __ENV.SLEEP_SECONDS || 1
        )
    );
}
