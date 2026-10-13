"""Gera os posts de Instagram (Feed 1080x1350 e Stories 1080x1920) das quatro páginas
e o arquivo posts.json usado por compartilhar/insta.js (legendas, textos alternativos).

Uso, a partir da raiz do site:
    python3 compartilhar/ferramentas/gerar_posts.py

Precisa de Python com Playwright (Chromium) e Pillow. Os textos ficam todos aqui:
edite POSTS e rode de novo.
"""
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / 'compartilhar'
FONTES = RAIZ / 'denuncia' / 'vendor' / 'fonts'
SITE = 'https://guiadenunciaflavio.github.io/'
VERSAO = '1'

FORMATOS = {'feed': (1080, 1350), 'stories': (1080, 1920)}

LEGENDA_FIM = (
    'Teve post derrubado ou conta restringida? Denuncie: censuradigital.lula.com.br\n'
    'Comitês Populares: comitepopular.com.br'
)

POSTS = {
    'denuncia': {
        'rotulo': 'A denúncia das rachadinhas',
        'pagina': 'denuncia/',
        'nome': 'a denúncia das rachadinhas',
        'kicker': 'A denúncia do MP do Rio contra Flávio Bolsonaro, de 2020',
        'titulo': 'Para o MP, Flávio nomeou\n12 funcionários fantasmas', 'hfs': 71,
        'trecho': {'img': 'inicio/denuncia.jpg', 'feed': (0, 0, 961, 425), 'stories': (0, 0, 961, 425),
                   'fonte': 'Denúncia do MPRJ, p. 9',
                   'alt': 'trecho da denúncia com “rachadinha” e “funcionários fantasmas” marcados'},
        'fatos': [('R$ 2,08 milhões', 'depositados na conta de Queiroz'),
                  ('R$ 247 mil', 'em escola e plano de saúde, pagos em dinheiro vivo')],
        'nota': 'Segundo a denúncia. A Justiça anulou provas e arquivou o caso sem julgar o mérito. Flávio nega.',
        'cta': 'Leia a denúncia, página por página',
        'legenda': (
            'Para o Ministério Público do Rio, Flávio Bolsonaro nomeou 12 funcionários fantasmas na Alerj, '
            'que repassavam parte do salário a Fabrício Queiroz.\n\n'
            'O que a denúncia de 2020 diz:\n'
            '- R$ 6,1 milhões pagos pela Alerj aos 12 assessores\n'
            '- R$ 2,08 milhões depositados na conta de Queiroz\n'
            '- R$ 247 mil em escola e plano de saúde, pagos em dinheiro vivo\n\n'
            'A Justiça anulou provas e arquivou o caso sem julgar o mérito. Flávio nega. '
            'A denúncia continua pública: o guia abre cada página com o trecho marcado.\n\n'
            'Leia: guiadenunciaflavio.github.io/denuncia\n\n'
            + LEGENDA_FIM + '\n\n#rachadinha #FlavioBolsonaro #Queiroz'
        ),
    },
    'suspeicao': {
        'rotulo': 'A suspeição de Moro',
        'pagina': 'suspeicao/',
        'nome': 'a suspeição de Moro',
        'kicker': 'Lula, Sergio Moro e o processo do triplex',
        'titulo': 'Moro foi parcial.\nQuem decidiu foi o STF.', 'hfs': 80,
        'trecho': {'img': 'inicio/suspeicao.jpg', 'feed': (0, 176, 961, 458), 'stories': (0, 96, 961, 458),
                   'fonte': 'Acórdão do STF no HC 164.493, p. 1',
                   'alt': 'trecho do acórdão com “violação do dever de imparcialidade do magistrado” marcado'},
        'fatos_titulo': '3 dos 7 fatos apontados na decisão:',
        'fatos': [('25 advogados', 'da defesa grampeados por quase 30 dias'),
                  ('6 dias', 'antes do 1º turno de 2018, Moro tornou pública parte da delação de Palocci'),
                  ('Depois da eleição,', 'Moro aceitou ser ministro de Bolsonaro')],
        'nota': '3 a 2 na Segunda Turma, em 2021; o plenário confirmou por 7 a 4. '
                'O STF anulou o processo, sem julgar se houve crime.',
        'cta': 'Leia o acórdão, página por página',
        'legenda': (
            'O STF decidiu em 2021 que Sergio Moro foi parcial ao julgar Lula no caso do triplex: '
            '3 a 2 na Segunda Turma, confirmado por 7 a 4 no plenário.\n\n'
            'Três dos sete fatos apontados na decisão:\n'
            '- 25 advogados da defesa grampeados por quase 30 dias\n'
            '- Moro tornou pública parte da delação de Palocci 6 dias antes do 1º turno de 2018\n'
            '- Depois da eleição, Moro aceitou ser ministro de Bolsonaro\n\n'
            'O STF anulou o processo, sem julgar se houve crime. '
            'O guia abre cada página do acórdão com o trecho marcado.\n\n'
            'Leia: guiadenunciaflavio.github.io/suspeicao\n\n'
            + LEGENDA_FIM + '\n\n#Moro #STF #Lula'
        ),
    },
    'cargo': {
        'rotulo': 'O cargo na Câmara',
        'pagina': 'cargo-na-camara/',
        'nome': 'o cargo de Flávio na Câmara',
        'kicker': 'Flávio Bolsonaro, de dezembro de 2000 a junho de 2002',
        'titulo': 'Cargo em Brasília.\nFaculdade e estágio no Rio.\nAo mesmo tempo.', 'hfs': 70,
        'trecho': {'img': 'inicio/cargo.jpg', 'feed': (0, 112, 961, 412), 'stories': (0, 112, 961, 482),
                   'fonte': 'Boletim Administrativo da Câmara de 27/12/2000, p. 3384',
                   'alt': 'trecho do boletim da Câmara com a nomeação de Flávio marcada'},
        'fatos': [('19 anos', 'a idade dele na nomeação, na liderança do partido do pai'),
                  ('10 meses', 'com cargo, faculdade e estágio ao mesmo tempo, segundo o currículo dele')],
        'nota': 'À BBC, a Câmara disse que o cargo não pode ser exercido fora de Brasília. '
                'Os documentos não mostram onde ele estava a cada dia; procurado em 2019, Flávio não quis responder.',
        'cta': 'Veja os atos da Câmara e o currículo dele',
        'legenda': (
            'Em dezembro de 2000, aos 19 anos, Flávio Bolsonaro foi nomeado para um cargo na liderança do PPB, '
            'o partido do pai, na Câmara dos Deputados, em Brasília. Ficou até junho de 2002.\n\n'
            'No mesmo período, segundo o próprio currículo, ele cursava Direito e estagiava no Rio. '
            'Foram 10 meses com cargo, faculdade e estágio ao mesmo tempo. '
            'O currículo dele na Alerj não cita o cargo na Câmara.\n\n'
            'À BBC, a Câmara disse que esse tipo de cargo não pode ser exercido fora de Brasília. '
            'Os documentos não mostram onde ele estava a cada dia. Procurado em 2019, Flávio não quis responder.\n\n'
            'Veja os atos da Câmara, o currículo e os diplomas: guiadenunciaflavio.github.io/cargo-na-camara\n\n'
            + LEGENDA_FIM + '\n\n#FlavioBolsonaro #Camara'
        ),
    },
    'patrimonio': {
        'rotulo': 'As contas de Flávio e Lula',
        'pagina': 'patrimonio/',
        'nome': 'as contas de Flávio e Lula',
        'kicker': 'Flávio e Lula: salário desde 2003 e patrimônio declarado ao TSE',
        'titulo': 'Quem será que\nroubou mesmo?', 'hfs': 96,
        'grafico': {'fonte': 'Declarações ao TSE, segundo Poder360, Metrópoles, Congresso em Foco e SBT News',
                    'alt': 'gráfico do patrimônio declarado: Flávio, de R$ 1,74 milhão em 2018 para R$ 8,19 milhões em 2026; '
                           'Lula, de R$ 7,99 milhões para R$ 4,78 milhões'},
        'fatos': [('R$ 5,5 milhões cada', 'em salário e aposentadoria, desde 2003'),
                  ('De R$ 1,6 a 4,5 milhões', 'a mais do que as rendas conhecidas de Flávio explicam, '
                                              'desde que ele virou senador (estimativa)')],
        'nota': 'Declarações ao TSE e contas com dados públicos. Nada aqui prova crime de ninguém.',
        'cta': 'Veja as contas, ano a ano, com as fontes',
        'legenda': (
            'Desde 2003, Flávio Bolsonaro e Lula receberam quase o mesmo em salário e aposentadoria: '
            'cerca de R$ 5,5 milhões cada.\n\n'
            'Patrimônio declarado à Justiça Eleitoral:\n'
            '- Flávio: R$ 1,74 milhão em 2018 e R$ 8,19 milhões em 2026\n'
            '- Lula: R$ 7,99 milhões em 2018, R$ 7,42 milhões em 2022 e R$ 4,78 milhões em 2026\n\n'
            'O de Lula encolheu um terço em quatro anos de Presidência. O de Flávio quase quintuplicou desde que '
            'ele virou senador: de R$ 1,6 a 4,5 milhões a mais do que as rendas conhecidas explicam, '
            'pela nossa estimativa.\n\n'
            'Quem será que roubou mesmo?\n\n'
            'Os dois foram acusados, os dois negam e nenhum tem condenação. Nada aqui prova crime de ninguém. '
            'As contas, ano a ano e com as fontes: guiadenunciaflavio.github.io/patrimonio\n\n'
            + LEGENDA_FIM + '\n\n#FlavioBolsonaro #Lula'
        ),
    },
}


def b64(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(Path(p).read_bytes()).decode()


def recorte(img, caixa):
    im = Image.open(RAIZ / img).convert('RGB').crop(caixa)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=92)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), im.size


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def grafico(fmt):
    """Gráfico de inclinação: patrimônio declarado em 2018 e em 2026."""
    w, h = (936, 380) if fmt == 'feed' else (936, 450)
    top, bot = 70, 58
    x0, x1 = 238, 590
    fs = 30 if fmt == 'feed' else 34

    def y(v):
        return top + (9 - v) * (h - top - bot) / 9

    fl, lu = '#0e7479', '#7a4ab0'
    s = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="SS3" role="img">']
    s.append(f'<text x="34" y="44" font-size="26" font-weight="600" fill="#4a5568">Patrimônio declarado</text>')
    for xx, ano in ((x0, '2018'), (x1, '2026')):
        s.append(f'<line x1="{xx}" y1="{top - 8}" x2="{xx}" y2="{h - bot + 6}" stroke="#d8dee7" stroke-width="2"/>')
        s.append(f'<text x="{xx}" y="{h - 16}" font-size="28" font-weight="700" fill="#16202e" text-anchor="middle">{ano}</text>')
    for a, b, cor in ((1.74, 8.19, fl), (7.99, 4.78, lu)):
        s.append(f'<line x1="{x0}" y1="{y(a):.1f}" x2="{x1}" y2="{y(b):.1f}" stroke="{cor}" stroke-width="9" stroke-linecap="round"/>')
        for xx, v in ((x0, a), (x1, b)):
            s.append(f'<circle cx="{xx}" cy="{y(v):.1f}" r="12" fill="{cor}" stroke="#fff" stroke-width="4"/>')
    lab = [(x0 - 24, 1.74, 'R$ 1,74 mi', fl, 'end'), (x0 - 24, 7.99, 'R$ 7,99 mi', lu, 'end'),
           (x1 + 24, 8.19, 'Flávio, R$ 8,19 mi', fl, 'start'), (x1 + 24, 4.78, 'Lula, R$ 4,78 mi', lu, 'start')]
    for xx, v, t, cor, anc in lab:
        s.append(f'<text x="{xx}" y="{y(v) + fs * .36:.1f}" font-size="{fs}" font-weight="700" fill="{cor}" '
                 f'text-anchor="{anc}">{t}</text>')
    s.append('</svg>')
    return '\n'.join(s)


CSS = """
@font-face{font-family:SS4;src:url(%(serif)s) format('woff2');font-weight:700}
@font-face{font-family:SS3;src:url(%(s400)s) format('woff2');font-weight:400}
@font-face{font-family:SS3;src:url(%(s600)s) format('woff2');font-weight:600}
@font-face{font-family:SS3;src:url(%(s700)s) format('woff2');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:%(h)dpx;overflow:hidden;background:#16202e}
body{font-family:SS3;color:#fff;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
p{text-wrap:pretty}
.f{position:absolute;inset:0;display:flex;flex-direction:column;padding:%(pad)s}
.f>*{flex-shrink:0}
.brand{display:flex;align-items:center;gap:16px;font-weight:600;font-size:31px;line-height:1;color:#fff}
.brand i{display:block;width:36px;height:36px;border-radius:6px;
  background:linear-gradient(transparent 55%%,#ffe14d 55%% 88%%,transparent 88%%),#16202e;box-shadow:inset 0 0 0 3px #fff}
.k{margin-top:%(kmt)dpx;font-weight:600;font-size:%(kfs)dpx;line-height:1.3;color:#c3ccd8}
h1{margin-top:18px;font-family:SS4;font-weight:700;font-size:%(hfs)dpx;line-height:1.24;white-space:nowrap;color:#16202e;letter-spacing:-.005em}
h1 span{background:#ffe14d;padding:.02em .14em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.doc{margin-top:%(dmt)dpx;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 18px 44px rgba(0,0,0,.38)}
.doc img,.doc svg{display:block;width:100%%;height:auto}
.src{margin-top:12px;font-size:%(sfs)dpx;line-height:1.3;color:#aeb9c9}
.ft{margin-top:%(fmt)dpx;font-weight:600;font-size:%(ffs)dpx;line-height:1.3;color:#c3ccd8}
.facts{margin-top:%(fmt)dpx;display:grid;gap:%(fgap)dpx}
.ft+.facts{margin-top:10px}
.facts p{font-size:%(ffs)dpx;line-height:1.28;color:#fff;padding-left:26px;border-left:6px solid #ffe14d}
.facts b{font-weight:700;color:#ffe14d}
.n{margin-top:%(nmt)dpx;font-size:%(nfs)dpx;line-height:1.38;color:#aeb9c9}
.cta{margin-top:auto;background:#fff;border-radius:18px;padding:%(cpad)s;box-shadow:6px 6px 0 #ffe14d}
.cta b{display:block;font-weight:700;font-size:%(cfs)dpx;line-height:1.25;color:#16202e}
.cta span{display:block;margin-top:6px;font-weight:700;font-size:%(cfs)dpx;line-height:1.25;color:#0b4fa8}
"""

MEDIDAS = {
    'feed': dict(h=1350, pad='60px 72px 64px', kmt=40, kfs=32, dmt=34, sfs=23, fmt=28, ffs=33, fgap=14,
                 nmt=20, nfs=25, cpad='22px 30px', cfs=31),
    'stories': dict(h=1920, pad='210px 72px 300px', kmt=48, kfs=33, dmt=44, sfs=24, fmt=36, ffs=35, fgap=18,
                    nmt=24, nfs=27, cpad='24px 32px', cfs=33),
}


def html(post, fmt, fontes):
    m = dict(MEDIDAS[fmt], hfs=post['hfs'])
    css = CSS % dict(m, **fontes)
    partes = ['<div class="f">',
              '<div class="brand"><i></i>Guias de leitura</div>',
              f'<p class="k">{esc(post["kicker"])}</p>',
              '<h1>' + '<br>'.join(f'<span>{esc(l)}</span>' for l in post['titulo'].split('\n')) + '</h1>']
    if 'trecho' in post:
        t = post['trecho']
        uri, _ = recorte(t['img'], t[fmt])
        partes.append(f'<div class="doc"><img src="{uri}" alt=""></div><p class="src">{esc(t["fonte"])}</p>')
    else:
        partes.append(f'<div class="doc">{grafico(fmt)}</div><p class="src">{esc(post["grafico"]["fonte"])}</p>')
    if post.get('fatos_titulo'):
        partes.append(f'<p class="ft">{esc(post["fatos_titulo"])}</p>')
    partes.append('<div class="facts">' + ''.join(
        f'<p><b>{esc(a)}</b> {esc(b)}</p>' for a, b in post['fatos']) + '</div>')
    partes.append(f'<p class="n">{esc(post["nota"])}</p>')
    partes.append(f'<div class="cta"><b>{esc(post["cta"])}</b><span>{esc(urltxt(post))}</span></div>')
    partes.append('</div>')
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(partes)}</body></html>'


def urltxt(post):
    return (SITE + post['pagina']).replace('https://', '').rstrip('/')


def alt(post, fmt):
    visual = post['trecho']['alt'] if 'trecho' in post else post['grafico']['alt']
    fatos = '; '.join(f'{a} {b}' for a, b in post['fatos'])
    t = post['titulo'].replace('\n', ' ')
    t = t if t.endswith(('.', '?', '!')) else t + '.'
    return (f'Post: {t} {visual[0].upper() + visual[1:]}. {fatos}. '
            f'{post["nota"]} {urltxt(post)}')


def main():
    fontes = {
        'serif': b64(FONTES / 'source-serif-4-latin-700-normal.woff2', 'font/woff2'),
        's400': b64(FONTES / 'source-sans-3-latin-400-normal.woff2', 'font/woff2'),
        's600': b64(FONTES / 'source-sans-3-latin-600-normal.woff2', 'font/woff2'),
        's700': b64(FONTES / 'source-sans-3-latin-700-normal.woff2', 'font/woff2'),
    }
    saida = {}
    problemas = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for chave, post in POSTS.items():
            item = {'url': SITE + post['pagina'], 'nome': post['nome'], 'rotulo': post['rotulo'],
                    'legenda': post['legenda']}
            for fmt, (w, h) in FORMATOS.items():
                pg = nav.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
                pg.set_content(html(post, fmt, fontes), wait_until='load')
                pg.evaluate('document.fonts.ready')
                # confere se nada passou do limite (o bloco do link precisa caber inteiro)
                folga = pg.evaluate("""() => {
                    const f = document.querySelector('.f'), c = document.querySelector('.cta');
                    const n = document.querySelector('.n');
                    const h1 = document.querySelector('h1');
                    const pb = parseFloat(getComputedStyle(f).paddingBottom);
                    return {sobra: Math.round(f.clientHeight - pb - c.getBoundingClientRect().bottom), gap: Math.round(c.getBoundingClientRect().top - n.getBoundingClientRect().bottom),
                            largura: Math.round(Math.max(...[...h1.querySelectorAll('span')].map(x => x.getBoundingClientRect().right)) - f.getBoundingClientRect().left),
                            fontes: [...document.fonts].filter(x => x.status === 'loaded').length};
                }""")
                if folga['sobra'] < 0 or folga['gap'] < 18 or folga['fontes'] < 4 or folga['largura'] > 1080 - 72:
                    problemas.append(f'{chave}/{fmt}: {folga}')
                png = pg.screenshot(type='png')
                pg.close()
                nome = f'{chave}-{fmt}.jpg'
                Image.open(io.BytesIO(png)).convert('RGB').save(SAIDA / nome, 'JPEG', quality=88, optimize=True,
                                                                progressive=True)
                item[fmt] = {'img': nome, 'w': w, 'h': h, 'alt': alt(post, fmt)}
                if fmt == 'feed':
                    mini = Image.open(io.BytesIO(png)).convert('RGB').resize((432, 540), Image.LANCZOS)
                    mini.save(SAIDA / f'{chave}-mini.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
                print(nome, folga)
            saida[chave] = item
        nav.close()
    (SAIDA / 'posts.json').write_text(json.dumps({'versao': VERSAO, 'posts': saida}, ensure_ascii=False, indent=1),
                                      encoding='utf-8')
    if problemas:
        print('ATENÇÃO, não coube:', *problemas, sep='\n  ')
        sys.exit(1)


if __name__ == '__main__':
    main()
