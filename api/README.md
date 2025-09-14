- Base path: https://thebiaslens.onrender.com
- Endpoints to implement today:
  - GET /health → returns { status: "ok" }
  - GET /search?q=… → returns a list of normalized articles with fields:
    title, source, publishedAt, url, and either body or extractStatus
  - POST /extract with { url } → returns { body, extractStatus }
- Notes: rate limits and caching will be added later.
