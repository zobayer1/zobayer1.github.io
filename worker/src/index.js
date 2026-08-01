/**
 * Fresh GoatCounter view counts for zobayer.net.
 *
 * Why this exists: GoatCounter's public `/counter/<path>.json` endpoint is served
 * with `Expires: +4h` from their edge, so counts shown on the site lag by up to
 * four hours. The authenticated API has no such cache, but a static site can't
 * hold an API token — hence this Worker, which holds the token and re-exposes the
 * data as a single public JSON blob.
 *
 * Two wins over calling `/counter/` directly:
 *   - staleness drops from ~4h to CACHE_TTL (5 min)
 *   - the home page makes 1 request instead of one per card
 *
 * Response: {"/posts/matrix-exponentiation": 74, "/about": 5, ...}
 */

const CACHE_KEY = 'counts';
const CACHE_TTL = 300;

const BROWSER_TTL = 60;
const START = '2023-01-01';

const PAGE_LIMIT = 50;
const MAX_PAGES = 5;
const ALLOWED_ORIGINS = new Set([
  'https://zobayer.net',
  'http://localhost:4000',
  'http://127.0.0.1:4000'
]);

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return cors(new Response(null, { status: 204 }), request);
    }

    if (request.method !== 'GET') {
      return cors(new Response('method not allowed', { status: 405 }), request);
    }

    const cached = await env.PV_CACHE.get(CACHE_KEY, 'text');

    if (cached !== null) {
      return cors(json(cached), request);
    }

    let counts;

    try {
      counts = await fetchCounts(env);
    } catch (err) {
      return cors(json(JSON.stringify({ error: String(err) }), 502), request);
    }

    const body = JSON.stringify(counts);

    ctx.waitUntil(
      env.PV_CACHE.put(CACHE_KEY, body, { expirationTtl: CACHE_TTL })
    );

    return cors(json(body), request);
  }
};

async function fetchCounts(env) {
  const token = env.GOATCOUNTER_TOKEN;

  if (!token) {
    throw new Error(
      'GOATCOUNTER_TOKEN is not set - run `wrangler secret put GOATCOUNTER_TOKEN`'
    );
  }

  const counts = {};
  const seen = [];

  for (let page = 0; page < MAX_PAGES; page++) {
    const url = new URL(
      `https://${env.GOATCOUNTER_SITE}.goatcounter.com/api/v0/stats/hits`
    );

    url.searchParams.set('start', START);
    url.searchParams.set('limit', String(PAGE_LIMIT));

    if (seen.length > 0) {
      url.searchParams.set('exclude_paths', seen.join(','));
    }

    const response = await fetch(url, {
      headers: {
        authorization: `Bearer ${token}`,
        'content-type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(
        `goatcounter ${response.status}: ${(await response.text()).slice(0, 200)}`
      );
    }

    const data = await response.json();

    for (const hit of data.hits ?? []) {
      counts[hit.path.replace(/(.)\/$/, '$1')] = hit.count;
      seen.push(hit.path_id);
    }

    if (!data.more) {
      break;
    }
  }

  return counts;
}

function cors(response, request) {
  const origin = request.headers.get('origin');

  if (origin !== null && ALLOWED_ORIGINS.has(origin)) {
    response.headers.set('access-control-allow-origin', origin);
    response.headers.set('access-control-allow-methods', 'GET');
    response.headers.set('access-control-max-age', '86400');
  }

  response.headers.set('vary', 'Origin');

  return response;
}

function json(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      'content-type': 'application/json',
      'cache-control':
        status === 200 ? `public, max-age=${BROWSER_TTL}` : 'no-store'
    }
  });
}
