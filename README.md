# smart-pet-device-decisions

Static site for pillar 3 (smart devices) of the Pet Care Decisions project:
**Pet Smart Device Decisions** — https://smart-pet-device-decisions.pages.dev

Rules (same as the sibling sites):
- Pure static: `build.py` renders `data/brands.json` + `data/articles.json` into `site/`
  (JSON-LD, canonical, sitemap.xml, robots.txt, real 404 via the generated `_worker.js`).
- English pages only. Every fact carries its official source URL and check date;
  a missing source fails the build. Prices/promos are never invented — if the brand's
  own site doesn't publish it, the page says so.
- Source domains are whitelisted in `build.py` (`OFFICIAL_HOSTS`) and re-checked by
  `selfcheck.py` (four checks: no Chinese output, fact provenance, rendered
  provenance per page, JSON-LD/canonical/nav).
- Currencies are reported as each brand's own store prints them: USD
  (litter-robot.com, furbo.com, petcube.com), EUR (tractive.com/en), GBP
  (pawfit.com UK store). They are never converted or compared across currencies.

Build locally:

```
python build.py
python selfcheck.py
```

Deploy: GitHub Actions (`.github/workflows`, wrangler) → Cloudflare Pages project
`smart-pet-device-decisions`. For a local deploy set the canonical host first, e.g.
`PET_SITE_CANONICAL_HOST=smart-pet-device-decisions.pages.dev python build.py`.

Sites: [Litter-Robot](/litter-robot), [Furbo](/furbo), [Petcube](/petcube),
[Tractive](/tractive), [Pawfit](/pawfit).
