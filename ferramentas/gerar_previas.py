"""Gera as prévias de link (og:image) e as páginas /ponto/ID/ e /tema/ID/ do guia.

Uso: python3 ferramentas/gerar_previas.py [pasta_do_site]   (padrão: a pasta do site)
Precisa do Playwright com Chromium. As imagens são desenhadas pelo próprio site
(assets/card.js), abrindo index.html?gerar=1 num navegador sem janela.
"""
import asyncio, base64, html, json, os, shutil, subprocess, sys, time

SITE = 'https://guiadenunciaflavio.github.io/'
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8790
C = json.load(open(os.path.join(ROOT, 'data/content.json'), encoding='utf-8'))
for i, e in enumerate(C['timeline']):          # mesma regra do app.js
    e.setdefault('id', 'cr-%02d' % (i + 1))
ITEMS = C['roteiro'] + C['timeline']
assert len({it['id'] for it in ITEMS}) == len(ITEMS)


def pages_txt(ps):
    ps = list(dict.fromkeys(ps))
    if not ps:
        return ''
    a = ps[:5]
    s = 'p. %s' % a[0] if len(a) == 1 else 'p. %s e %s' % (', '.join(map(str, a[:-1])), a[-1])
    return s + (' e outras' if len(ps) > 5 else '')


PESO = {'documentado': 'fato documentado, com data, valor ou registro',
        'alegado': 'acusação do Ministério Público',
        'interpretação': 'leitura que liga os fatos'}


def peso_resumo(items):
    c = {'documentado': 0, 'alegado': 0, 'interpretação': 0}
    for it in items:
        if it['label'] in c:
            c[it['label']] += 1
    parts = []
    pl = lambda n, um, varios: '%d %s' % (n, um if n == 1 else varios)
    if c['documentado']: parts.append(pl(c['documentado'], 'fato documentado', 'fatos documentados'))
    if c['alegado']: parts.append(pl(c['alegado'], 'acusação do MP', 'acusações do MP'))
    if c['interpretação']: parts.append(pl(c['interpretação'], 'leitura que liga os fatos', 'leituras que ligam os fatos'))
    return ', '.join(parts[:-1]) + ' e ' + parts[-1] if len(parts) > 1 else (parts[0] if parts else '')


def cut(s, n):
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0].rstrip(',.;:') + '…'


PAGE = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Guia da denúncia</title>
<meta name="description" content="{desc}">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Guia da denúncia">
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
<p><a href="{href}">Abrir no Guia da denúncia</a></p>
<h1>{title}</h1>
<p>{desc}</p>
</body>
</html>
'''


def write_page(path, title, desc, img_rel, alt, hash_):
    url = SITE + path
    rel_root = '../' * path.strip('/').count('/') + '../'
    href = rel_root + hash_
    out = PAGE.format(title=html.escape(title), desc=html.escape(desc), url=url, img=SITE + img_rel,
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
                data = await pg.evaluate("([k, i]) => window.__guiaCard(k, i, 'og', 0.84)", [kind, id_])
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
        pg = pages_txt([r['p'] for r in it.get('refs', [])])
        desc = cut('Segundo a denúncia do MPRJ%s: %s' % (' (%s)' % pg if pg else '', it['text']), 230) + \
            ' Base: %s.' % PESO.get(it['label'], it['label'])
        alt = 'Trecho marcado da denúncia: %s' % it['title'] if it.get('refs') else it['title']
        write_page('ponto/%s/' % it['id'], it['title'], desc, 'og/%s.jpg' % it['id'], alt, '#a=' + it['id'])
        jobs.append(('ponto', it['id'], 'og/%s.jpg' % it['id']))
    for th in C['themes']:
        n = sum(1 for r in C['roteiro'] if r['theme'] == th['id'])
        its = [r for r in C['roteiro'] if r['theme'] == th['id']]
        desc = '%s O que a denúncia do MPRJ aponta neste tema, em %d pontos com as páginas marcadas. Base: %s.' % (
            th['lay'].rstrip('.') + '.', n, peso_resumo(its))
        write_page('tema/%s/' % th['id'], th['title'], desc, 'og/tema-%s.jpg' % th['id'], th['title'], '#tema=' + th['id'])
        jobs.append(('tema', th['id'], 'og/tema-%s.jpg' % th['id']))
    print('%d páginas de prévia escritas; gerando %d imagens…' % (len(ITEMS) + len(C['themes']), len(jobs)), flush=True)
    asyncio.run(render_images(jobs))
    sizes = [os.path.getsize(os.path.join(ROOT, j[2])) for j in jobs]
    print('imagens: %d, total %.1f MB, maior %.0f KB' % (len(sizes), sum(sizes) / 1e6, max(sizes) / 1e3))


if __name__ == '__main__':
    main()
