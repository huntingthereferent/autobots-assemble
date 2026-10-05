import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "20s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

export default function () {
  const health = http.get("http://api:8000/api/health");
  check(health, {
    "health status 200": (r) => r.status === 200,
    "health payload ok": (r) => r.json("status") === "ok",
  });

  const metrics = http.get("http://api:8000/metrics");
  check(metrics, {
    "metrics status 200": (r) => r.status === 200,
    "metrics expose platform counters": (r) =>
      r.body.includes("platform_source_runs_total"),
  });

  sleep(0.1);
}
