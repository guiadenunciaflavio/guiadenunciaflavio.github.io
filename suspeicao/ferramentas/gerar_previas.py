"""Gera as prévias de link (og:image) e as páginas /ponto/ID/ e /tema/ID/ do guia da suspeição.

Uso: python3 build_share.py ENDEREÇO_DO_SITE [pasta_do_site]
     ex.: python3 ferramentas/gerar_previas.py https://exemplo.github.io/suspeicao/
Precisa do Playwright com Chromium. As imagens são desenhadas pelo próprio site
(assets/card.js), abrindo index.html?gerar=1 num navegador sem janela.
"""
import asyncio, base64, html, json, os, re, shutil, subprocess, sys, time

if len(sys.argv) < 2 or not sys.argv[1].startswith('https://'):
    sys.exit(__doc__)
SITE = sys.argv[1].rstrip('/') + '/'
HOST = SITE.split('://', 1)[1].rstrip('/')
_site = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # quando o script está em ferramentas/
ROOT = sys.argv[2] if len(sys.argv) > 2 else (_site if os.path.exists(os.path.join(_site, 'data', 'content.json')) else '/home/claude/lava')
BRAND = 'Guia da suspeição'
PORT = 8793
C = json.load(open(os.path.join(ROOT, 'data/content.json'), encoding='utf-8'))
for i, e in enumerate(C['timeline']):          # mesma regra do app.js
    e.setdefault('id', 'cr-%02d' % (i + 1))
ITEMS = C['roteiro'] + C['timeline']
assert len({it['id'] for it in ITEMS}) == len(ITEMS)


def pages_txt(ps):
    ps = sorted(set(ps))
    if not ps:
        return ''
    a = ps[:5]
    s = 'p. %s' % a[0] if len(a) == 1 else 'p. %s e %s' % (', '.join(map(str, a[:-1])), a[-1])
    return s + (' e outras' if len(ps) > 5 else '')


# textos de cada documento (mesmos do site: assets/card.js)
DOCS = {d['id']: d for d in C['docs']}
doc_of = lambda it: ((it.get('refs') or [{}])[0]).get('d', 'acordao')
join_e = lambda a: ', '.join(a[:-1]) + ' e ' + a[-1] if len(a) > 1 else (a[0] if a else '')


def refs_txt(refs, main):
    groups = []
    for r in refs:
        d = r.get('d', 'acordao')
        g = next((x for x in groups if x[0] == d), None)
        if not g:
            g = (d, []); groups.append(g)
        if r['p'] not in g[1]: g[1].append(r['p'])
    groups.sort(key=lambda g: 0 if g[0] == main else 1)
    return '; '.join(('' if d == main else DOCS[d]['short'] + ', ') + pages_txt(ps) for d, ps in groups)


def peso(label, doc):
    D = DOCS[doc]
    return 'fato registrado %s, com data e página' % D['em'] if label == 'documentado' else D['aleg'] if label == 'alegado' else 'leitura que liga os fatos'


def peso_resumo(items):
    pl = lambda n, um, varios: '%d %s' % (n, um if n == 1 else varios)
    docs = lambda its: list(dict.fromkeys(doc_of(i) for i in its))
    doc = [i for i in items if i['label'] == 'documentado']
    ale = [i for i in items if i['label'] == 'alegado']
    parts = []
    if doc: parts.append(pl(len(doc), 'fato registrado', 'fatos registrados') + ' ' + join_e([DOCS[d]['em'] for d in docs(doc)]))
    if ale:
        ds = docs(ale)
        parts.append(pl(len(ale), DOCS[ds[0]]['aleg1'], DOCS[ds[0]]['alegN']) if len(ds) == 1 else pl(len(ale), 'afirmação que não é decisão', 'afirmações que não são decisões'))
    return join_e(parts)


def sujeito(items):
    ds = list(dict.fromkeys(doc_of(i) for i in items))
    return (DOCS[ds[0]]['sujeito'], False) if len(ds) == 1 else (join_e([DOCS[d]['what'] for d in ds]), True)


def cut(s, n):
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0].rstrip(',.;:') + '…'


PAGE = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {brand}</title>
<meta name="description" content="{desc}">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{brand}">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{alt}">
<meta name="twitter:card" content="summary_large_image">
<script>location.replace({target});</script>
<style>body{{font:17px/1.6 system-ui,sans-serif;max-width:40rem;margin:3rem auto;padding:0 16px;color:#16202e}}a{{color:#0b4fa8}}</style>
</head>
<body>
<p><a href="{href}">Abrir no {brand}</a></p>
<h1>{title}</h1>
<p>{desc}</p>
</body>
</html>
'''


def write_page(path, title, desc, img_rel, alt, hash_):
    url = SITE + path
    rel_root = '../' * path.strip('/').count('/') + '../'
    href = rel_root + hash_
    out = PAGE.format(title=html.escape(title), desc=html.escape(desc), url=url, img=SITE + img_rel, brand=BRAND,
                      alt=html.escape(alt), target=json.dumps(href), href=html.escape(href))
    d = os.path.join(ROOT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


async def render_images(jobs):
    from playwright.async_api import async_playwright
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', ROOT],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch()
            pg = await b.new_page(viewport={'width': 1200, 'height': 800})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:%d/?gerar=1' % PORT)
            await pg.wait_for_function('window.__guiaCard && document.querySelector("#roteiroList li")')
            for n, (kind, id_, out) in enumerate(jobs, 1):
                data = await pg.evaluate("([k, i, h]) => window.__guiaCard(k, i, 'og', 0.84, h)", [kind, id_, HOST])
                open(os.path.join(ROOT, out), 'wb').write(base64.b64decode(data.split(',', 1)[1]))
                if n % 50 == 0:
                    print('  %d/%d imagens' % (n, len(jobs)), flush=True)
            await b.close()
            if errs:
                raise SystemExit('erros na página: %s' % errs[:3])
    finally:
        srv.terminate()


def main():
    for d in ('og', 'ponto', 'tema'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    os.makedirs(os.path.join(ROOT, 'og'))
    jobs = [('guia', '', 'og/guia.jpg')]
    for it in ITEMS:
        dc = doc_of(it)
        pg = refs_txt(it.get('refs', []), dc)
        desc = cut('Segundo %s%s: %s' % (DOCS[dc]['sujeito'], ' (%s)' % pg if pg else '', it['text']), 230) + \
            ' Base: %s.' % peso(it['label'], dc)
        alt = 'Trecho marcado %s: %s' % (DOCS[dc]['de'], it['title']) if it.get('refs') else it['title']
        write_page('ponto/%s/' % it['id'], it['title'], desc, 'og/%s.jpg' % it['id'], alt, '#a=' + it['id'])
        jobs.append(('ponto', it['id'], 'og/%s.jpg' % it['id']))
    for th in C['themes']:
        n = sum(1 for r in C['roteiro'] if r['theme'] == th['id'])
        its = [r for r in C['roteiro'] if r['theme'] == th['id']]
        suj, plural = sujeito(its)
        desc = '%s O que %s %s neste tema, em %d pontos com as páginas marcadas. Base: %s.' % (
            th['lay'].rstrip('.') + '.', suj, 'apontam' if plural else 'aponta', n, peso_resumo(its))
        write_page('tema/%s/' % th['id'], th['title'], desc, 'og/tema-%s.jpg' % th['id'], th['title'], '#tema=' + th['id'])
        jobs.append(('tema', th['id'], 'og/tema-%s.jpg' % th['id']))
    # a página inicial aponta para a prévia no endereço final
    ix = os.path.join(ROOT, 'index.html'); s = open(ix, encoding='utf-8').read()
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + SITE + m.group(2), s)
    s = re.sub(r'(<meta property="og:image" content=")[^"]*(">)', lambda m: m.group(1) + SITE + 'og/guia.jpg' + m.group(2), s)
    open(ix, 'w', encoding='utf-8').write(s)
    print('%d páginas de prévia escritas; gerando %d imagens…' % (len(ITEMS) + len(C['themes']), len(jobs)), flush=True)
    asyncio.run(render_images(jobs))
    sizes = [os.path.getsize(os.path.join(ROOT, j[2])) for j in jobs]
    print('imagens: %d, total %.1f MB, maior %.0f KB' % (len(sizes), sum(sizes) / 1e6, max(sizes) / 1e3))


if __name__ == '__main__':
    main()
