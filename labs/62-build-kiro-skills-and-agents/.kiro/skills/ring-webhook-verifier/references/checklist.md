# Ring webhook endpoint checklist (from the Ring Partner API docs)

- [ ] Reads the **raw bytes** of the body and verifies `X-Signature` before JSON parsing
- [ ] Uses a constant-time comparison (`hmac.compare_digest` / `crypto.timingSafeEqual`)
- [ ] Hex-encodes the HMAC for `X-Signature` (nonces use URL-safe Base64 — don't mix them up)
- [ ] Returns 2xx within **5 seconds**; heavy work goes to a queue
- [ ] Dedupes on `meta.request_id` (retries: 1s, 5s, 30s, 2m, 10m, 1h; 4xx is not retried)
- [ ] Handles event types it doesn't know without failing (e.g. new types added later)
- [ ] Keys users by Ring **account ID**, not email or name
- [ ] Calls the API server-to-server only, with `User-Agent` and `Hardware_Id` headers and a static egress IP
- [ ] Keeps the Ring watermark on every image it shows
