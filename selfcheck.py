# Four self-checks before delivery:
# (1) no Chinese in generated output (2) every fact has official source + check date
# (3) rendered pages show source links + dates (4) JSON-LD + canonical per page
import json, re, pathlib

site = pathlib.Path(__file__).parent / "site"
data = json.loads((pathlib.Path(__file__).parent / "data" / "brands.json").read_text(encoding="utf-8"))
articles_path = pathlib.Path(__file__).parent / "data" / "articles.json"
articles = json.loads(articles_path.read_text(encoding="utf-8"))["articles"] if articles_path.exists() else []
fails = []

# (1) Chinese anywhere in site output
cn = []
for p in site.rglob("*"):
    if p.is_file() and p.suffix in {".html", ".css", ".js", ".xml", ".txt", ".svg"}:
        if re.search(r"[\u4e00-\u9fff]", p.read_text(encoding="utf-8", errors="ignore")):
            cn.append(str(p))
print("[1] Chinese in output:", len(cn), cn[:5])
if cn:
    fails.append("chinese-in-output")

# (2) every fact + faq has official source + check date
official = {"litter-robot.com", "www.litter-robot.com",
            "furbo.com", "www.furbo.com",
            "petcube.com", "www.petcube.com",
            "tractive.com", "www.tractive.com",
            "pawfit.com", "www.pawfit.com",
            "catgenie.com", "www.catgenie.com",
            "petkit.com", "www.petkit.com",
            "meowant.com", "www.meowant.com"}
# 允许品牌官方站的子域（如 blog.justfoodfordogs.com），但域名主体必须在上面的白名单里
OFFICIAL_LINK = r'href="https://(?:[a-z0-9-]+\.)*(?:www\.)?(?:litter-robot|furbo|petcube|tractive|pawfit|catgenie|petkit|meowant)[^"]*"'
n = bad = offsite = 0
for b in data["brands"]:
    for f in b["facts"] + b["faqs"]:
        n += 1
        u = f.get("source_url", "")
        if not u.startswith("http") or not f.get("checked"):
            bad += 1
        if u.split("/")[2] not in official:
            offsite += 1
            print("   non-official source:", u)

# articles.json: facts + FAQs + per-cell compare sources must be official and complete
for a in articles:
    for f in a["facts"] + a["faqs"]:
        n += 1
        u = f.get("source_url", "")
        if not u.startswith("http") or not f.get("checked"):
            bad += 1
            print("   article fact missing source/date:", a["slug"], f.get("fact") or f.get("q"))
        if u.startswith("http") and u.split("/")[2] not in official:
            offsite += 1
            print("   non-official article source:", u)
    ncols = len(a["columns"])
    for r in a["rows"]:
        if len(r["cells"]) != ncols or len(r.get("sources", [])) != ncols:
            bad += 1
            print("   compare shape mismatch:", a["slug"], r["label"])
            continue
        for i, u in enumerate(r["sources"]):
            cell = r["cells"][i]
            if u and u.split("/")[2] not in official:
                offsite += 1
                print("   non-official compare source:", u)
            if not u and not cell.strip().lower().startswith("not published"):
                bad += 1
                print("   compare cell has no source and is not a 'not published' cell:", a["slug"], r["label"])
            if u and cell.strip().lower().startswith("not published"):
                bad += 1
                print("   compare cell claims 'not published' but links a source:", a["slug"], r["label"])
print(f"[2] facts+faqs={n} missing_source_or_date={bad} non_official_domain={offsite}")
if bad or offsite:
    fails.append("fact-provenance")

# (3) rendered pages show source link + date per fact row; check dates == today
for slug in ("litter-robot", "furbo", "petcube", "tractive", "pawfit"):
    html = (site / f"{slug}.html").read_text(encoding="utf-8")
    rows = html.count("<tr>") - (1 if "<th>" in html else 0)
    srcs = len(re.findall(OFFICIAL_LINK, html))
    dates = html.count(data["site"]["checked"])
    print(f"[3] {slug}: rows={rows} official_source_links={srcs} check_dates={dates}")
    if srcs < rows or dates < rows:
        fails.append(f"render-provenance-{slug}")

# (3b) rendered article pages: every fact row carries an official source link + its own check date
for a in articles:
    html = (site / f"{a['slug']}.html").read_text(encoding="utf-8")
    fact_rows = len(a["facts"])
    srcs = len(re.findall(OFFICIAL_LINK, html))
    dated = [f for f in a["facts"] + a["faqs"] if (f.get("checked") or "\u0000") in html]
    dates = len(dated)
    expected = len(a["facts"]) + len(a["faqs"])
    in_sitemap = f"/{a['slug']}" in (site / "sitemap.xml").read_text(encoding="utf-8")
    print(f"[3b] {a['slug']}: facts={fact_rows} official_source_links={srcs} dated_items={dates}/{expected} in_sitemap={in_sitemap}")
    if srcs < fact_rows or dates < expected or not in_sitemap:
        fails.append(f"render-provenance-{a['slug']}")

# (4) JSON-LD + canonical on every page; sitemap/robots present
for p in sorted(site.glob("*.html")):
    h = p.read_text(encoding="utf-8")
    ld = "application/ld+json" in h
    ca = 'rel="canonical"' in h
    print(f"[4] {p.name}: jsonld={ld} canonical={ca}")
    if not (ld and ca):
        fails.append(f"meta-{p.name}")
for f in ("sitemap.xml", "robots.txt", "_worker.js", "assets/style.css"):
    ok = (site / f).exists()
    print(f"[4] {f}: {'ok' if ok else 'MISSING'}")
    if not ok:
        fails.append(f"missing-{f}")

# nav reaches all three utility pages from every page
for p in sorted(site.glob("*.html")):
    h = p.read_text(encoding="utf-8")
    for link in ("/about", "/privacy", "/contact"):
        if link not in h:
            fails.append(f"nav-{p.name}-{link}")

print("RESULT:", "PASS" if not fails else "FAIL " + ",".join(sorted(set(fails))))
