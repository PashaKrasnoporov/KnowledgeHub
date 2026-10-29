import http from "k6/http";
import { check, sleep } from "k6";

const baseUrl = (__ENV.BASE_URL || "").replace(/\/+$/, "");

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

export default function () {
    const response = http.get(
        `${baseUrl}/api/v1/health`,
        {
            headers: {
                "User-Agent":
                    "KnowledgeHub-Lab4-k6/1.0",
            },
            tags: {
                endpoint: "health",
            },
        }
    );

    check(
        response,
        {
            "HTTP 200": (r) =>
                r.status === 200,

            "KnowledgeHub status ok": (r) =>
                r.body.includes(
                    '"status":"ok"'
                ),
        }
    );

    sleep(1);
}
