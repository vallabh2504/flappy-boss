/**
 * Validates the x-api-key header against the API_KEY environment variable.
 * Set API_KEY in .env.local for dev, and in Vercel dashboard for production.
 */
export function isAuthorized(headers: Headers): boolean {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    // If no key is configured, block all writes (fail-safe)
    console.error("[auth] API_KEY env var not set — rejecting request");
    return false;
  }
  return headers.get("x-api-key") === apiKey;
}
