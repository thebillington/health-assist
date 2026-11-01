/**
 * Minimal Home Assistant webhook receiver for App Review.
 *
 * Deploy with Cloudflare Workers (or any runtime that can return JSON):
 *
 *   cd appstore/demo-webhook
 *   npx wrangler deploy
 *
 * It accepts any POST, discards the body without logging or storing it, and
 * returns the JSON shape the app expects. It is intentionally stateless.
 */
export default {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204 });
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    // Read and discard. Never log or persist health payloads.
    await request.arrayBuffer();

    return new Response(JSON.stringify({ accepted: 1, ignored: 0 }), {
      status: 200,
      headers: {
        "content-type": "application/json",
        "cache-control": "no-store",
      },
    });
  },
};
