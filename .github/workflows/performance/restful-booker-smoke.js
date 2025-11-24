import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL =
  __ENV.BASE_URL || "https://restful-booker.herokuapp.com";

export const options = {
  vus: 5,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],      // < 1% failures
    http_req_duration: ["p(95)<800"],    // 95% under 800 ms
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/ping`);

  check(res, {
    "status is 201": (r) => r.status === 201,
    "latency < 800ms": (r) => r.timings.duration < 800,
  });

  sleep(1);
}