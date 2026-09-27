// ILANG
// TYPE:worker ROLE:canonical-host-and-real-404
const CANONICAL_HOST = "smart-pet-device-decisions.pages.dev";
const VALID_PATHS = new Set(["/", "/about", "/assets/favicon.svg", "/assets/style.css", "/contact", "/furbo", "/litter-robot", "/pawfit", "/petcube", "/privacy", "/robots.txt", "/sitemap.xml", "/tractive"]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname !== CANONICAL_HOST) {
      return Response.redirect(new URL(url.pathname + url.search, `https://${CANONICAL_HOST}`).toString(), 301);
    }

    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (path.endsWith(".html")) {
      const bare = path === "/index.html" ? "/" : path.slice(0, -5);
      if (VALID_PATHS.has(bare)) {
        return Response.redirect(new URL(bare + url.search, `https://${CANONICAL_HOST}`).toString(), 308);
      }
    }

    if (VALID_PATHS.has(path)) {
      return env.ASSETS.fetch(request);
    }

    const notFound = await env.ASSETS.fetch(new URL("/404.html", url));
    return new Response(notFound.body, {
      status: 404,
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "no-store",
        "x-robots-tag": "noindex",
      },
    });
  },
};
