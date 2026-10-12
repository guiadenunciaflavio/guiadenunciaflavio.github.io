"""Gera as prévias de link (og:image) e as páginas /ponto/ID/ e /tema/ID/ do guia do cargo na Câmara.

Uso: python3 ferramentas/gerar_previas.py ENDEREÇO_DO_SITE [pasta_do_site]
     ex.: python3 ferramentas/gerar_previas.py https://exemplo.github.io/cargo-na-camara/
Precisa do Playwright com Chromium. As imagens são desenhadas pelo próprio site
(assets/card.js), abrindo index.html?gerar=1 num navegador sem janela.
Também grava os endereços antigos p/ID/ (da primeira versão desta página), que levam aos pontos novos.
"""
import asyncio, base64, html, json, os, re, shutil, subprocess, sys, time

if len(sys.argv) < 2 or not sys.argv[1].startswith('https://'):
    sys.exit(__doc__)
SITE = sys.argv[1].rstrip('/') + '/'
HOST = SITE.split('://', 1)[1].rstrip('/')
ROOT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = 'Guia do cargo na Câmara'
PORT = 8793
C = json.load(open(os.path.join(ROOT, 'data/content.json'), encoding='utf-8'))
for i, e in enumerate(C['timeline']):          # mesma regra do app.js
    e.setdefault('id', 'cr-%02d' % (i + 1))
# só os itens com trecho marcado têm página de ponto (os de reportagem ficam na página, com o link da fonte)
ITEMS = [it for it in C['roteiro'] + C['timeline'] if it.get('refs')]
assert len({it['id'] for it in ITEMS}) == len(ITEMS)
DOCS = {d['id']: d for d in C['docs']}
MAIN = C['docs'][0]['id']

# endereços da primeira versão (p/ID/) -> ponto novo ou seção da página
ANTIGOS = {
    'nomeado-aos-19': 'nom-flavio', 'cargo-era-de-ana': 'nom-ana-sai', 'tarefas-do-cargo': 'tar-plenario',
    'so-em-brasilia': 'tar-brasilia', 'estudava-no-rio': 'rio-estagio', 'aulas-diarias': 'rio-campus',
    'salario': '#extras', 'sem-resposta': '#extras', 'a-conta-nao-fecha': 'rio-distancia',
    'nomeacao': 'nom-flavio', 'exoneracao-ana': 'nom-ana-sai', 'nomeacao-ana': 'nom-ana-entra',
    'atribuicoes': 'tar-plenario', 'alerj': 'rio-estagio', 'diploma': 'rio-campus', 'senado': 'cur-senado',
    'se-invencao': '#entenda', 'se-trabalhava-do-rio': 'tar-brasilia', 'se-nao-estudava': 'rio-estagio',
    'se-parente-era-permitido': 'nom-mesmo-posto', 'se-so-estagio': 'rio-sobreposicao',
}

doc_of = lambda it: ((it.get('refs') or [{}])[0]).get('d', MAIN)
join_e = lambda a: ', '.join(a[:-1]) + ' e ' + a[-1] if len(a) > 1 else (a[0] if a else '')


def pages_txt(labels):
    if not labels:
        return ''
    a, pre = labels[:5], 'p. ' if labels[0][:1].isdigit() else ''
    s = pre + a[0] if len(a) == 1 else pre + '%s e %s' % (', '.join(a[:-1]), a[-1])
    return s + (' e outras' if len(labels) > 5 else '')


def refs_txt(refs, main):
    """mesma regra de assets/card.js: número impresso da página; o documento do ponto vai sem o nome"""
    groups = []
    for r in refs:
        d = r.get('d', MAIN)
        g = next((x for x in groups if x[0] == d), None)
        if not g:
            g = (d, []); groups.append(g)
        if r['p'] not in g[1]: g[1].append(r['p'])
    groups.sort(key=lambda g: 0 if g[0] == main else 1)
    out = []
    for d, ps in groups:
        D = DOCS[d]
        pg = '' if D['n'] == 1 or D.get('nopg') else pages_txt([D['labels'].get(str(p), str(p)) for p in sorted(ps)])
        t = pg if d == main else D['short'] + (', ' + pg if pg else '')
        if t: out.append(t)
    return '; '.join(out)


def peso(label, doc):
    D = DOCS[doc]
    return {'documentado': 'fato registrado %s, com data e página' % D['em'], 'alegado': D['aleg'],
            'reportagem': 'informação de reportagem, com link para a fonte'}.get(label, 'leitura que liga os fatos')


def peso_resumo(items):
    pl = lambda n, um, varios: '%d %s' % (n, um if n == 1 else varios)
    docs = lambda its: list(dict.fromkeys(doc_of(i) for i in its))
    by = lambda l: [i for i in items if i['label'] == l]
    parts = []
    if by('documentado'): parts.append(pl(len(by('documentado')), 'fato registrado', 'fatos registrados') + ' ' + join_e([DOCS[d]['em'] for d in docs(by('documentado'))]))
    if by('reportagem'): parts.append(pl(len(by('reportagem')), 'informação de reportagem', 'informações de reportagem'))
    if by('interpretação'): parts.append(pl(len(by('interpretação')), 'leitura que liga os fatos', 'leituras que ligam os fatos'))
    return join_e(parts)


def sujeito(items):
    ds = list(dict.fromkeys(doc_of(i) for i in items))
    return (DOCS[ds[0]]['sujeito'], bool(DOCS[ds[0]].get('pl'))) if len(ds) == 1 else (join_e([DOCS[d]['what'] for d in ds]), True)


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


def write_page(path, title, desc, img_rel, alt, hash_, canonical=None):
    url = SITE + (path if canonical is None else canonical)
    href = '../' * path.strip('/').count('/') + '../' + hash_
    out = PAGE.format(title=html.escape(title), desc=html.escape(desc), url=url, img=SITE + img_rel, brand=BRAND,
                      alt=html.escape(alt), target=json.dumps(href), href=html.escape(href))
    d = os.path.join(ROOT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


def ponto_meta(it):
    dc = doc_of(it)
    if it['label'] == 'interpretação':
        desc = cut('Leitura do guia (%s): %s' % (refs_txt(it['refs'], None), it['text']), 230) + ' Base: leitura que liga os fatos.'
    else:
        pg = refs_txt(it['refs'], dc)
        desc = cut('Segundo %s%s: %s' % (DOCS[dc]['sujeito'], ' (%s)' % pg if pg else '', it['text']), 230) + ' Base: %s.' % peso(it['label'], dc)
    alt = 'Trecho marcado %s: %s' % (DOCS[dc]['de'], it['title'])
    return desc, alt


async def render_images(jobs):
    from playwright.async_api import async_playwright
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1', '-d', ROOT],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch()
            pg = await b.new_page(viewport={'width': 1200, 'height': 800})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://127.0.0.1:%d/?gerar=1' % PORT)
            await pg.wait_for_function('window.__guiaCard && document.querySelector("#roteiroList li")')
            for n, (kind, id_, out) in enumerate(jobs, 1):
                data = await pg.evaluate("([k, i, h]) => window.__guiaCard(k, i, 'og', 0.84, h)", [kind, id_, HOST])
                open(os.path.join(ROOT, out), 'wb').write(base64.b64decode(data.split(',', 1)[1]))
                if n % 20 == 0:
                    print('  %d/%d imagens' % (n, len(jobs)), flush=True)
            await b.close()
            if errs:
                raise SystemExit('erros na página: %s' % errs[:3])
    finally:
        srv.terminate()


def main():
    for d in ('og', 'ponto', 'tema', 'p'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    os.makedirs(os.path.join(ROOT, 'og'))
    jobs = [('guia', '', 'og/guia.jpg')]
    by_id = {it['id']: it for it in ITEMS}
    for it in ITEMS:
        desc, alt = ponto_meta(it)
        write_page('ponto/%s/' % it['id'], it['title'], desc, 'og/%s.jpg' % it['id'], alt, '#a=' + it['id'])
        jobs.append(('ponto', it['id'], 'og/%s.jpg' % it['id']))
    for th in C['themes']:
        its = [r for r in C['roteiro'] if r['theme'] == th['id']]
        suj, plural = sujeito(its)
        desc = '%s O que %s %s neste tema, em %d pontos com as páginas marcadas. Base: %s.' % (
            th['lay'].rstrip('.') + '.', suj, 'apontam' if plural else 'aponta', len(its), peso_resumo(its))
        write_page('tema/%s/' % th['id'], th['title'], desc, 'og/tema-%s.jpg' % th['id'], th['title'], '#tema=' + th['id'])
        jobs.append(('tema', th['id'], 'og/tema-%s.jpg' % th['id']))
    # endereços antigos: levam ao ponto novo (com a mesma prévia) ou à seção da página
    ix = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    g_title = re.search(r'<meta property="og:title" content="([^"]*)">', ix).group(1)
    g_desc = re.search(r'<meta property="og:description" content="([^"]*)">', ix).group(1)
    for old, new in ANTIGOS.items():
        if new.startswith('#'):
            write_page('p/%s/' % old, html.unescape(g_title), html.unescape(g_desc), 'og/guia.jpg', html.unescape(g_title), new, canonical='')
        else:
            it = by_id[new]; desc, alt = ponto_meta(it)
            write_page('p/%s/' % old, it['title'], desc, 'og/%s.jpg' % new, alt, '#a=' + new, canonical='ponto/%s/' % new)
    # a página inicial aponta para a prévia no endereço final
    ixp = os.path.join(ROOT, 'index.html')
    ix = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + SITE + m.group(2), ix)
    ix = re.sub(r'(<meta property="og:image" content=")[^"]*(">)', lambda m: m.group(1) + SITE + 'og/guia.jpg' + m.group(2), ix)
    open(ixp, 'w', encoding='utf-8').write(ix)
    print('%d páginas de prévia e %d endereços antigos escritos; gerando %d imagens…' % (len(ITEMS) + len(C['themes']), len(ANTIGOS), len(jobs)), flush=True)
    asyncio.run(render_images(jobs))
    sizes = [os.path.getsize(os.path.join(ROOT, j[2])) for j in jobs]
    print('imagens: %d, total %.1f MB, maior %.0f KB' % (len(sizes), sum(sizes) / 1e6, max(sizes) / 1e3))


if __name__ == '__main__':
    main()
