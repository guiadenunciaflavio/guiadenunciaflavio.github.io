"""Monta index.html e as páginas de prévia p/ID/ da página "O cargo de Flávio na Câmara".

Uso:  python3 -I ferramentas/montar.py
Lê data/conteudo.json (textos) e data/docs.json (recortes, gerado por ferramentas/recortes.py).
Depois de mudar textos, rode também ferramentas/gerar_previas.py para refazer as imagens de og/.
"""
import html, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, 'data/conteudo.json'), encoding='utf-8'))
D = json.load(open(os.path.join(ROOT, 'data/docs.json'), encoding='utf-8'))
SITE = C['site']
E = lambda s: html.escape(str(s), quote=True)
TAGCLS = {'documentado': 't-doc', 'reportagem': 't-rep', 'interpretação': 't-int'}
LCLS = {'documentado': 'l-doc', 'reportagem': 'l-rep', 'interpretação': 'l-int'}
FONTE = C['fontes_ext']


def tag(label):
    return f'<span class="tag {TAGCLS[label]}">{E(label)}</span>'


def cut(s, n):
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0].rstrip(',.;:') + '…'


# ---------- itens que podem ser compartilhados (resumo, documentos, respostas) ----------
ITENS = {}
for it in C['resumo']:
    ITENS[it['id']] = {'kind': 'ponto', 'title': it['titulo'], 'label': it['label'], 'text': it['texto'],
                       'fonte': FONTE[it['fonte']][0] if it.get('fonte') else (C['docs'][it['ver']]['fonte'] if it.get('ver') else ''),
                       'doc': it.get('ver')}
for k, d in C['docs'].items():
    ITENS[k] = {'kind': 'doc', 'title': d['titulo'], 'label': d['label'], 'text': d['texto'], 'fonte': d['fonte'], 'doc': k, 'data': d['data'], 'curto': d['curto']}
for r in C['respostas']:
    ITENS[r['id']] = {'kind': 'resposta', 'title': r['se'], 'label': r['label'], 'text': r['resposta'], 'fonte': r['base'], 'doc': r.get('ver')}
PAGINA = {'kind': 'pagina', 'title': C['titulo'], 'text': C['og_descricao'], 'doc': 'nomeacao', 'label': 'documentado',
          'fonte': 'Atos da Câmara dos Deputados, currículo de Flávio na Alerj, diploma publicado por ele e BBC News Brasil'}


def paper(doc_id, alt_main):
    out = [f'<figure class="paper" data-zoom="{doc_id}" tabindex="0" aria-label="Ampliar o documento">']
    for g in D[doc_id]['groups']:
        out.append(f'<figcaption class="seg-label">{E(g["label"])}</figcaption>')
        for i, s in enumerate(g['segs']):
            if i:
                out.append('<div class="omit" aria-hidden="true"><span>[…]</span></div>')
            alt = alt_main if s['hl'] else ''
            hls = ''.join(f'<i class="hl" style="left:{x*100:.2f}%;top:{y*100:.2f}%;width:{w*100:.2f}%;height:{h*100:.2f}%"></i>'
                          for x, y, w, h in s['hl'])
            out.append(f'<div class="seg"><img src="{E(s["src"])}" width="{s["w"]}" height="{s["h"]}" alt="{E(alt)}" loading="lazy" decoding="async">{hls}</div>')
    out.append('<span class="zoom-hint" aria-hidden="true">Toque para ampliar</span></figure>')
    return ''.join(out)


def share_btns(i, ver=None):
    b = f'<button class="btn-s" data-share="{i}">Compartilhar</button>'
    if ver:
        b = f'<a class="chip" href="#{ver}">Ver o documento</a>' + b
    return b


def resumo():
    out = []
    for it in C['resumo']:
        src = ''
        if it.get('fonte'):
            n, u = FONTE[it['fonte']]
            src = f'<p class="src-inline">Fonte: <a href="{E(u)}" rel="noopener noreferrer">{E(n)}</a></p>'
        wide = ' wide' if it['label'] == 'interpretação' else ''
        out.append(f'<article class="fact {LCLS[it["label"]]}{wide}" id="{it["id"]}">{tag(it["label"])}'
                   f'<h3>{E(it["titulo"])}</h3><p>{E(it["texto"])}</p>{src}'
                   f'<div class="acts">{share_btns(it["id"], it.get("ver"))}</div></article>')
    return '\n'.join(out)


def docs():
    out = []
    for g in C['grupos']:
        out.append(f'<h3 class="group-h" id="{g["id"]}">{E(g["titulo"])}</h3><p class="muted intro">{E(g["intro"])}</p><div class="docs">')
        for k in g['docs']:
            d = C['docs'][k]
            links = ''.join(f'<li><a href="{E(u)}" rel="noopener noreferrer">{E(n)}</a></li>' for n, u in d['links'])
            nota = f'<p class="doc-note">{E(d["nota"])}</p>' if d.get('nota') else ''
            alt = 'Trecho marcado do documento: ' + cut(d['transcricao'], 300)
            out.append(f'''<article class="doc" id="{k}">
  <div class="doc-top">
    <div class="doc-meta">{tag(d["label"])}<span class="doc-date">{E(d["data"])}</span></div>
    <h3>{E(d["titulo"])}</h3>
    <p>{E(d["texto"])}</p>{nota}
  </div>
  {paper(k, alt)}
  <div class="doc-bottom">
    <p class="doc-src">Fonte: {E(d["fonte"])}</p>
    <ul class="doc-links">{links}</ul>
    <div class="doc-acts"><button class="btn-s" data-share="{k}">Compartilhar</button><button class="btn-s" data-zoom="{k}">Ampliar o documento</button></div>
    <details class="transc"><summary>Ler o trecho em texto</summary><blockquote>{E(d["transcricao"])}</blockquote></details>
  </div>
</article>''')
        out.append('</div>')
    return '\n'.join(out)


def respostas():
    out = []
    for r in C['respostas']:
        out.append(f'''<article class="answer" id="{r["id"]}">
  <h3><span class="q">Se alguém disser:</span>“{E(r["se"])}”</h3>
  <p>{E(r["resposta"])}</p>
  <p class="src-inline">{tag(r["label"])} Base: {E(r["base"])}.</p>
  <div class="acts"><button class="btn-s" data-copy-answer="{r["id"]}">Copiar resposta</button>{share_btns(r["id"], r.get("ver"))}</div>
</article>''')
    return '\n'.join(out)


def linha():
    out = []
    for e in C['linha']:
        ver = f'<a class="chip" href="#{e["ver"]}">Ver o documento</a>' if e.get('ver') else ''
        out.append(f'<li class="tl"><p><span class="tl-date">{E(e["data"])}</span>{E(e["texto"])}</p><div class="tl-meta">{tag(e["label"])}{ver}</div></li>')
    return '\n'.join(out)


def dizem():
    out = []
    for s in C['dizem']:
        n, u = FONTE[s['fonte']]
        q = ' class="q"' if s.get('citacao') else ''
        txt = f'“{E(s["texto"])}”' if s.get('citacao') else E(s['texto'])
        out.append(f'<figure class="say"><figcaption>{E(s["quem"])}<span>{E(s["quando"])}</span></figcaption>'
                   f'<blockquote{q}>{txt}</blockquote><p class="src-inline">Fonte: <a href="{E(u)}" rel="noopener noreferrer">{E(n)}</a></p></figure>')
    return '\n'.join(out)


def fontes():
    return '\n'.join(f'<li><b>{E(a)}</b>: <a href="{E(u)}" rel="noopener noreferrer">{E(b)}</a></li>' for a, b, u in C['fontes'])


# ---------- três atividades no tempo (jan/2000 a jan/2003) ----------
def pos(y, m, d=1):
    import calendar
    dm = calendar.monthrange(y, m)[1]
    return ((y - 2000) * 12 + (m - 1) + (d - 1) / dm) / 36 * 100


def bar(cls, a, b, extra=''):
    return f'<span class="bar {cls}" style="left:{a:.2f}%;width:{b - a:.2f}%"{extra}></span>'


LANES = f'''<figure class="lanes" aria-labelledby="lanesCap">
  <figcaption id="lanesCap"><b>Três atividades, duas cidades</b>As datas vêm dos atos da Câmara, do perfil de Flávio na Alerj e da BBC.</figcaption>
  <p class="sr">Cargo na Câmara, em Brasília, de dezembro de 2000 a junho de 2002. Faculdade de Direito no Rio, de 2000 a 2006. Estágio na Defensoria Pública, no Rio, de agosto de 2000 a outubro de 2001, segundo o perfil na Alerj, ou de março de 2001 a janeiro de 2002, segundo o LinkedIn. As três atividades se sobrepõem de dezembro de 2000 a outubro de 2001.</p>
  <div class="lanes-plot" aria-hidden="true">
    <div class="lanes-band" style="left:{pos(2000,12,14):.2f}%;width:{pos(2001,11) - pos(2000,12,14):.2f}%"><span>as três ao mesmo tempo</span></div>
    <div class="lane"><div class="lane-head"><span class="city bsb">Brasília</span>Cargo na Câmara</div>
      <div class="lane-track">{bar('bsb', pos(2000,12,14), pos(2002,7))}</div>
      <div class="lane-note">De 14/12/2000 a junho de 2002</div></div>
    <div class="lane"><div class="lane-head"><span class="city rio">Rio</span>Faculdade de Direito, com aula todo dia</div>
      <div class="lane-track">{bar('rio start-fade', 0, 100)}</div>
      <div class="lane-note">Começou em 2000; o diploma é de 2006</div></div>
    <div class="lane has-alt"><div class="lane-head"><span class="city rio">Rio</span>Estágio na Defensoria Pública</div>
      <div class="lane-track">{bar('rio', pos(2000,8), pos(2001,11))}{bar('alt', pos(2001,3), pos(2002,2))}</div>
      <div class="lane-note">Agosto de 2000 a outubro de 2001, no perfil da Alerj. Tracejado: março de 2001 a janeiro de 2002, no LinkedIn</div></div>
    <div class="lanes-axis"><span>2000</span><span>2001</span><span>2002</span></div>
  </div>
</figure>'''

WEEK = '''<div class="week">
  <div class="week-cities">
    <div class="place"><span class="city bsb">Brasília</span><b>Câmara dos Deputados</b><p>Cargo de 40 horas por semana. As tarefas são no plenário, nas comissões e nas votações.</p></div>
    <div class="km">mais de 1.000 km<span>quase 1h30 de voo</span></div>
    <div class="place"><span class="city rio">Rio de Janeiro</span><b>Faculdade e estágio</b><p>Aula de 4 a 5 horas por dia na Candido Mendes, no Centro. Estágio na Defensoria Pública duas vezes por semana.</p></div>
  </div>
  <div class="wk" role="img" aria-label="Quadro de uma semana, de segunda a sexta: 40 horas de trabalho na Câmara, em Brasília; aula todos os dias no Rio; estágio dois dias por semana no Rio.">
    <span></span><span class="wk-d">seg</span><span class="wk-d">ter</span><span class="wk-d">qua</span><span class="wk-d">qui</span><span class="wk-d">sex</span>
    <span class="wk-l">Brasília<small>Câmara</small></span><span class="wk-bar bsb">40 horas na semana</span>
    <span class="wk-l">Rio<small>faculdade</small></span><span class="wk-c">aula<small>4 a 5 h</small></span><span class="wk-c">aula<small>4 a 5 h</small></span><span class="wk-c">aula<small>4 a 5 h</small></span><span class="wk-c">aula<small>4 a 5 h</small></span><span class="wk-c">aula<small>4 a 5 h</small></span>
    <span class="wk-l">Rio<small>estágio</small></span><span class="wk-bar est">2 dias por semana</span>
  </div>
  <p class="fine">Os horários exatos não são públicos, e o quadro não inventa nenhum: mostra só o que as fontes dizem. As 40 horas, a distância, as aulas diárias e o estágio duas vezes por semana estão na reportagem da BBC, que ouviu a Câmara, a Defensoria, ex-professores e ex-colegas. Na Câmara, a presença de Flávio era registrada numa folha mensal enviada pela chefia da liderança do PPB, e não em ponto diário.</p>
</div>'''


def dados():
    curto = {k: d['curto'] for k, d in C['docs'].items()}
    return json.dumps({'site': SITE, 'pagina': PAGINA, 'itens': ITENS, 'docs': D, 'curto': curto, 'rotulos': C['rotulos']},
                      ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


PAGE = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(C["titulo"])}: o cargo de Flávio Bolsonaro na Câmara</title>
<meta name="description" content="{E(C["descricao"])}">
<meta name="referrer" content="no-referrer">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Guias de leitura">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{E(C["titulo"])}">
<meta property="og:description" content="{E(C["og_descricao"])}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og/pagina.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Trecho marcado do Boletim Administrativo da Câmara com a nomeação de Flávio Bolsonaro">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/page.css">
</head>
<body>
<a class="skip" href="#conteudo">Ir para o conteúdo</a>
<header class="top">
  <a class="brand" href="../"><span class="brand-mark" aria-hidden="true"></span><span>Guias de leitura</span></a>
  <nav class="nav" id="nav" aria-label="Seções">
    <a href="#resumo">Em um minuto</a>
    <a href="#semana">Uma semana</a>
    <a href="#documentos">Documentos</a>
    <a href="#respostas">Se alguém disser</a>
    <a href="#linha-do-tempo">Linha do tempo</a>
    <a href="#o-que-dizem">O que dizem</a>
    <a href="#fontes">Fontes</a>
    <a href="../" class="nav-home">Todos os guias</a>
  </nav>
  <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="mobileNav">Menu</button>
</header>
<nav class="mobile-nav" id="mobileNav" hidden aria-label="Seções (celular)"></nav>

<main id="conteudo" tabindex="-1">
  <section class="hero" id="inicio">
    <div class="hero-copy">
      <h1><span class="mk">{E(C["titulo"])}</span></h1>
      <p class="lead">Em dezembro de 2000, aos 19 anos, Flávio Bolsonaro foi nomeado para um cargo na liderança do PPB, o partido do pai, na Câmara dos Deputados. A Câmara informou à BBC que esse tipo de cargo não pode ser exercido fora de Brasília. No mesmo período, segundo o currículo que ele mesmo publicou, Flávio cursava Direito e estagiava na Defensoria Pública, no Rio.</p>
      <div class="hero-actions">
        <a class="btn primary" href="#documentos">Ver os documentos</a>
        <a class="btn" href="#respostas">Respostas prontas</a>
        <button class="btn" data-share="pagina">Compartilhar</button>
      </div>
      <p class="fine">Esta página mostra documentos públicos, com o trecho que importa marcado, e o que a BBC News Brasil apurou em 2019. Procurado na época, Flávio não quis responder.</p>
      <p class="fine">Outros guias neste site: <a href="../denuncia/">A denúncia das rachadinhas</a> e <a href="../suspeicao/">Por que o STF declarou Moro parcial</a>.</p>
    </div>
    {LANES}
  </section>

  <section class="how" aria-label="Como ler esta página">
    <h2 class="sr">Como ler esta página</h2>
    <ul class="labels">
      <li>{tag("documentado")} está num documento público. O trecho aparece marcado, e o link leva ao original.</li>
      <li>{tag("reportagem")} foi apurado pela BBC News Brasil, com documentos que não são públicos (como a declaração de Imposto de Renda) e entrevistas. O link leva à reportagem.</li>
      <li>{tag("interpretação")} é uma leitura nossa, que liga os fatos. Não está escrita em nenhum documento.</li>
    </ul>
  </section>

  <section id="resumo" class="block">
    <h2>Em um minuto</h2>
    <div class="facts">
{resumo()}
    </div>
  </section>

  <section id="semana" class="block">
    <h2>Uma semana desse período</h2>
    {WEEK}
  </section>

  <section id="documentos" class="block">
    <h2>Os documentos</h2>
    <p class="muted intro">Todos são públicos e podem ser conferidos no original. Toque num documento para ampliar.</p>
{docs()}
  </section>

  <section id="respostas" class="block">
    <h2>Se alguém disser…</h2>
    <p class="muted intro">Respostas curtas, cada uma com o documento que a sustenta. Copie e cole, ou compartilhe o link.</p>
    <div class="answers">
{respostas()}
    </div>
  </section>

  <section id="linha-do-tempo" class="block">
    <h2>Linha do tempo</h2>
    <ol class="timeline">
{linha()}
    </ol>
  </section>

  <section id="o-que-dizem" class="block">
    <h2>O que dizem os citados</h2>
    <div class="said">
{dizem()}
    </div>
  </section>

  <section id="fontes" class="block about">
    <h2>Fontes</h2>
    <ol class="sources">
{fontes()}
    </ol>
    <p class="fine">Os atos da Câmara, o perfil da Alerj, o texto do Senado e o diploma aparecem aqui em recortes, com o trecho marcado em amarelo; o marca-texto é nosso. As cópias do Wayback Machine guardam as páginas como elas estavam em 2019. Da reportagem da BBC, só há citações curtas, com link.</p>
  </section>

  <footer class="foot">
    <p class="foot-nav">Outros guias neste site: <a href="../denuncia/">A denúncia das rachadinhas</a> e <a href="../suspeicao/">Por que o STF declarou Moro parcial</a>. <a href="../">Página inicial</a>.</p>
    <p>Página independente, sem vínculo com partidos, campanhas ou órgãos públicos. Os documentos são públicos. Nada neste site coleta dados de quem visita.</p>
  </footer>
</main>

<dialog id="zoomDlg" class="dlg zoom-dlg" aria-labelledby="zoomTitle">
  <form method="dialog" class="dlg-head"><h2 id="zoomTitle">Documento</h2><button>Fechar</button></form>
  <div class="zoom-body" id="zoomBody"></div>
</dialog>
<dialog id="shareDlg" class="dlg share-dlg" aria-labelledby="shTitle">
  <form method="dialog" class="dlg-head"><h2 id="shTitle">Compartilhar</h2><button>Fechar</button></form>
  <p class="sh-what" id="shWhat"></p>
  <h3 class="sh-h">Enviar o link</h3>
  <div class="sh-grid" id="shLinks"></div>
  <div class="sh-row">
    <button class="btn" id="shCopyLink">Copiar link</button>
    <button class="btn" id="shCopyText">Copiar texto</button>
    <button class="btn" id="shNative" hidden>Outros apps</button>
  </div>
  <h3 class="sh-h">Imagem para Instagram, TikTok e Stories</h3>
  <p class="fine sh-note">Essas redes não abrem links vindos de sites. A imagem leva o ponto, o trecho marcado no documento e um QR code com o link.</p>
  <div class="sh-fmt" id="shFmt" role="group" aria-label="Formato da imagem">
    <button class="chip on" data-fmt="story" aria-pressed="true">Stories (9:16)</button>
    <button class="chip" data-fmt="feed" aria-pressed="false">Feed (4:5)</button>
  </div>
  <button class="btn primary sh-make" id="shMake">Criar imagem</button>
  <figure class="sh-prev" id="shPrev" hidden><img id="shImg" alt=""></figure>
  <div class="sh-row" id="shImgActions" hidden>
    <button class="btn primary" id="shSendImg" hidden>Enviar imagem</button>
    <button class="btn" id="shSave">Baixar imagem</button>
  </div>
  <p class="fine" id="shHint" aria-live="polite"></p>
</dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script type="application/json" id="dados">{dados()}</script>
<script type="module" src="assets/page.js"></script>
</body>
</html>
'''

PREVIA = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | O cargo de Flávio na Câmara</title>
<meta name="description" content="{desc}">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Guias de leitura">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{alt}">
<meta name="twitter:card" content="summary_large_image">
<script>location.replace("../../#{id}");</script>
<style>body{{font:17px/1.6 system-ui,sans-serif;max-width:40rem;margin:3rem auto;padding:0 16px;color:#16202e}}a{{color:#0b4fa8}}</style>
</head>
<body>
<p><a href="../../#{id}">Abrir na página “O cargo de Flávio na Câmara”</a></p>
<h1>{title}</h1>
<p>{desc}</p>
</body>
</html>
'''


def previa_desc(it):
    base = C['rotulos'][it['label']]
    if it['kind'] == 'resposta':
        return cut(it['text'], 300)
    if it['label'] == 'documentado':
        return cut(f'{it["text"]} Fonte: {it["fonte"]}.', 300)
    if it['label'] == 'reportagem':
        return cut(f'Segundo a BBC News Brasil: {it["text"]}', 300)
    return cut(f'{it["text"]} ({base}).', 300)


def main():
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(PAGE)
    pdir = os.path.join(ROOT, 'p')
    if os.path.isdir(pdir):
        shutil.rmtree(pdir)
    for i, it in ITENS.items():
        os.makedirs(os.path.join(pdir, i))
        title = ('Se alguém disser: “' + it['title'] + '”') if it['kind'] == 'resposta' else it['title']
        with open(os.path.join(pdir, i, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(PREVIA.format(title=E(title), desc=E(previa_desc(it)), url=f'{SITE}p/{i}/', img=f'{SITE}og/{i}.jpg',
                                  alt=E(('Trecho marcado do documento: ' + C['docs'][it['doc']]['curto']) if it.get('doc') else ('Cartão com o texto: ' + it['title'])), id=i))
    print(f'index.html e {len(ITENS)} páginas de prévia')


if __name__ == '__main__':
    main()
