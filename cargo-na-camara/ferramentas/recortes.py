"""Recorta os documentos da página "O cargo na Câmara" e calcula os trechos marcados.

Uso:  python3 -I ferramentas/recortes.py PASTA_DAS_FONTES

PASTA_DAS_FONTES precisa ter:
  boletins/Ba19981113.pdf, boletins/Ba20001227.pdf   (Boletim Administrativo da Câmara, baixados do site da Câmara)
  DCD06NOV1996SUP.pdf                                (Diário da Câmara, suplemento de 6/11/1996)
  "Assembleia Legislativa do Estado do Rio de Janeiro.pdf"  (perfil na Alerj, cópia do Wayback Machine de 30/1/2019)
  "Flávio Bolsonaro (PSL) — Senado Notícias.pdf"            (Senado Notícias, cópia do Wayback Machine de 3/2/2019)
  certificado_UCAM.pdf                               (diploma publicado por Flávio Bolsonaro em 12/8/2026)

Grava docs/*.webp (os recortes, sem nenhum dado embutido) e data/docs.json, com o tamanho de cada
recorte e os retângulos do marca-texto em frações da imagem. As coordenadas abaixo estão em pontos
da página (1/72 de polegada); nas páginas escaneadas do Diário vêm da leitura por OCR a 300 dpi.
"""
import io, json, os, re, sys
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXW = 1360          # largura máxima dos recortes (2x a coluna da página)
PX = 72 / 300        # pixel a 300 dpi -> ponto
PAD = 1.6            # folga do marca-texto, em pontos

BOL98 = 'boletins/Ba19981113.pdf'
BOL00 = 'boletins/Ba20001227.pdf'
DCD = 'DCD06NOV1996SUP.pdf'
ALERJ = 'Assembleia Legislativa do Estado do Rio de Janeiro.pdf'
SENADO = 'Flávio Bolsonaro (PSL) — Senado Notícias.pdf'
UCAM = 'certificado_UCAM.pdf'


def words(path, page):
    with pdfplumber.open(os.path.join(SRC, path)) as d:
        return d.pages[page - 1].extract_words(use_text_flow=True)


def phrase(path, page, first, last, ylim):
    """retângulos (um por linha) do trecho que vai da palavra `first` até a palavra `last`, dentro de ylim"""
    ws = sorted((w for w in words(path, page) if ylim[0] <= w['top'] <= ylim[1]), key=lambda w: w['top'])
    lines = []                       # agrupa por linha, com tolerância de 3 pt (o marcador § fica um pouco abaixo)
    for w in ws:
        if lines and abs(w['top'] - lines[-1][0]['top']) < 3:
            lines[-1].append(w)
        else:
            lines.append([w])
    flat = [w for l in lines for w in sorted(l, key=lambda w: w['x0'])]
    i = next(k for k, w in enumerate(flat) if w['text'].startswith(first))
    j = next(k for k in range(i, len(flat)) if flat[k]['text'].endswith(last))
    keep = {id(w) for w in flat[i:j + 1]}
    out = []
    for l in lines:
        sel = [w for w in l if id(w) in keep]
        if sel:
            out.append((min(w['x0'] for w in sel), min(w['top'] for w in sel), max(w['x1'] for w in sel), max(w['bottom'] for w in sel)))
    return out


def px(*r):
    return tuple(v * PX for v in r)


def render(path, page, clip, dpi):
    if path == UCAM:   # o diploma é uma imagem; aqui as coordenadas são pixels da própria imagem
        doc = fitz.open(os.path.join(SRC, path))
        img = Image.open(io.BytesIO(doc.extract_image(doc[0].get_images()[0][0])['image'])).convert('RGB')
        return img.crop(tuple(int(v) for v in clip)), 1.0
    doc = fitz.open(os.path.join(SRC, path))
    z = dpi / 72
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(z, z), clip=fitz.Rect(*clip), colorspace=fitz.csGRAY, alpha=False)
    return Image.open(io.BytesIO(pix.tobytes('png'))).convert('L'), z


def seg(doc_id, n, path, page, clip, dpi=220, hl=()):
    img, z = render(path, page, clip, dpi)
    if img.width > MAXW:
        img = img.resize((MAXW, round(img.height * MAXW / img.width)), Image.LANCZOS)
    name = f'{doc_id}-{n}.webp'
    img.save(os.path.join(OUT, 'docs', name), 'WEBP', quality=82, method=6)
    cw, ch = clip[2] - clip[0], clip[3] - clip[1]
    pad = PAD if path != UCAM else 3
    rects = []
    for (x0, y0, x1, y1) in hl:
        x0, y0, x1, y1 = max(clip[0], x0 - pad), max(clip[1], y0 - pad), min(clip[2], x1 + pad), min(clip[3], y1 + pad)
        rects.append([round((x0 - clip[0]) / cw, 4), round((y0 - clip[1]) / ch, 4), round((x1 - x0) / cw, 4), round((y1 - y0) / ch, 4)])
    return {'src': 'docs/' + name, 'w': img.width, 'h': img.height, 'hl': rects}


def build():
    os.makedirs(os.path.join(OUT, 'docs'), exist_ok=True)
    D = {}

    # Boletim Administrativo nº 246, 27/12/2000, p. 3384: nomeação de Flávio
    D['nomeacao'] = {'groups': [{'label': 'Boletim Administrativo da Câmara nº 246, de 27/12/2000, página 3384', 'segs': [
        seg('nomeacao', 1, BOL00, 12, (38, 22, 559, 50)),
        seg('nomeacao', 2, BOL00, 12, (38, 146, 559, 252), hl=phrase(BOL00, 12, 'FLÁVIO', '15/12/2000).', (170, 252))),
        seg('nomeacao', 3, BOL00, 12, (38, 803, 559, 826)),
    ]}]}

    # mesmo boletim, p. 3380: exoneração de Ana Cristina, na mesma data
    D['exoneracao-ana'] = {'groups': [{'label': 'Boletim Administrativo da Câmara nº 246, de 27/12/2000, página 3380', 'segs': [
        seg('exoneracao-ana', 1, BOL00, 8, (38, 22, 559, 50)),
        seg('exoneracao-ana', 2, BOL00, 8, (38, 159, 559, 179)),
        seg('exoneracao-ana', 3, BOL00, 8, (38, 353, 559, 454), hl=phrase(BOL00, 8, 'ANA', '15/12/2000).', (380, 452))),
        seg('exoneracao-ana', 4, BOL00, 8, (38, 803, 559, 826)),
    ]}]}

    # Boletim Administrativo nº 215, 13/11/1998, p. 3197: nomeação de Ana Cristina
    D['nomeacao-ana'] = {'groups': [{'label': 'Boletim Administrativo da Câmara nº 215, de 13/11/1998, página 3197', 'segs': [
        seg('nomeacao-ana', 1, BOL98, 1, (59, 10, 560, 50)),
        seg('nomeacao-ana', 2, BOL98, 1, (59, 92, 560, 213)),
        seg('nomeacao-ana', 3, BOL98, 1, (59, 373, 560, 501), hl=phrase(BOL98, 1, 'ANA', '11/11/98).', (420, 499))),
        seg('nomeacao-ana', 4, BOL98, 1, (59, 792, 560, 822)),
    ]}]}

    # Ato da Mesa nº 45/1996, no Diário da Câmara (suplemento de 6/11/1996): capa, p. 69, p. 75 e p. 80
    D['atribuicoes'] = {'groups': [
        {'label': 'Diário da Câmara dos Deputados, suplemento de 6/11/1996, capa', 'segs': [
            seg('atribuicoes', 1, DCD, 1, px(90, 2470, 2400, 2975), dpi=300)]},
        {'label': 'Página 69: o Ato da Mesa nº 45, de 1996', 'segs': [
            seg('atribuicoes', 2, DCD, 70, px(300, 175, 2380, 800), dpi=300)]},
        {'label': 'Página 75: as atribuições do cargo', 'segs': [
            seg('atribuicoes', 3, DCD, 76, px(260, 180, 2330, 275), dpi=300),
            seg('atribuicoes', 4, DCD, 76, px(260, 1165, 2330, 2895), dpi=300,
                hl=[px(600, 1397, 1783, 1454), px(600, 1467, 2184, 1524), px(300, 1529, 1943, 1594),
                    px(590, 1605, 2183, 1662), px(300, 1675, 559, 1727)])]},
        {'label': 'Página 80: onde o cargo existe', 'segs': [
            seg('atribuicoes', 5, DCD, 81, px(200, 180, 2300, 270), dpi=300),
            seg('atribuicoes', 6, DCD, 81, px(200, 1950, 2300, 2175), dpi=300,
                hl=[px(340, 1964, 1592, 2020), px(340, 2040, 1429, 2096)])]},
    ]}

    # perfil na Alerj, cópia do Wayback Machine de 30/1/2019
    D['alerj'] = {'groups': [
        {'label': 'Cópia do Wayback Machine, de 30/1/2019', 'segs': [
            seg('alerj', 1, ALERJ, 1, (30, 33, 392, 46), dpi=600)]},
        {'label': 'Perfil de Flávio Bolsonaro no site da Alerj', 'segs': [
            seg('alerj', 2, ALERJ, 1, (45, 52, 382, 152.5), dpi=600),
            seg('alerj', 3, ALERJ, 1, (125, 259, 382, 447), dpi=600,
                hl=phrase(ALERJ, 1, 'Bacharel', 'RJ.', (386, 394)) + phrase(ALERJ, 1, 'Defensoria', 'Penitenciário)', (430, 445)))]},
    ]}

    # diploma de Direito, publicado por Flávio Bolsonaro (coordenadas em pixels da imagem)
    D['diploma'] = {'groups': [{'label': 'Diploma de Direito da Universidade Candido Mendes, publicado por Flávio Bolsonaro em 12/8/2026', 'segs': [
        seg('diploma', 1, UCAM, 1, (25, 55, 1000, 385), hl=[(291, 246, 373, 269), (90, 282, 321, 306), (457, 281, 541, 305)]),
    ]}]}

    # Senado Notícias, cópia do Wayback Machine de 3/2/2019
    D['senado'] = {'groups': [
        {'label': 'Cópia do Wayback Machine, de 3/2/2019', 'segs': [
            seg('senado', 1, SENADO, 1, (10, 57, 586, 76), dpi=300)]},
        {'label': 'Senado Notícias, perfil publicado em 18/1/2019', 'segs': [
            seg('senado', 2, SENADO, 1, (20, 90, 576, 263), dpi=300,
                hl=phrase(SENADO, 1, 'bacharel', 'políticas.', (195, 226)))]},
    ]}

    with open(os.path.join(OUT, 'data', 'docs.json'), 'w', encoding='utf-8') as f:
        json.dump(D, f, ensure_ascii=False, indent=1)
    n = sum(len(g['segs']) for d in D.values() for g in d['groups'])
    print(f'{len(D)} documentos, {n} recortes')
    fontes()
    inicio()


def fontes():
    """cópias guardadas no site: os boletins como saem do site da Câmara e as quatro páginas do Diário com o ato"""
    os.makedirs(os.path.join(OUT, 'fontes'), exist_ok=True)
    for b in (BOL98, BOL00):
        with open(os.path.join(SRC, b), 'rb') as a, open(os.path.join(OUT, 'fontes', os.path.basename(b)), 'wb') as z:
            z.write(a.read())
    src = fitz.open(os.path.join(SRC, DCD))
    out = fitz.open()
    for p in (1, 70, 76, 81):   # capa e páginas 69, 75 e 80 do suplemento
        out.insert_pdf(src, from_page=p - 1, to_page=p - 1)
    out.set_metadata({'title': 'Diário da Câmara dos Deputados, suplemento de 6/11/1996: capa e pp. 69, 75 e 80 (Ato da Mesa nº 45, de 1996)'})
    out.del_xml_metadata()
    out.save(os.path.join(OUT, 'fontes', 'ato-da-mesa-45-1996.pdf'), garbage=4, deflate=True, clean=True)
    print('fontes/: 2 boletins e o Ato da Mesa')


def inicio():
    """imagem do cartão na página inicial (961x601): o cabeçalho da página, o ato de nomeação e o rodapé do boletim,
    separados por […] como na página, para não mostrar os atos de outras pessoas"""
    from PIL import ImageChops, ImageDraw
    x0, x1, W, H, GAP = 30, 566, 961, 601, 40
    s = W / (x1 - x0)
    parts = []
    for (ya, yb, hl) in ((22, 50, False), (146, 252, True), (803, 826, False)):
        img, _ = render(BOL00, 12, (x0, ya, x1, yb), 300)
        img = img.convert('RGB').resize((W, round((yb - ya) * s)), Image.LANCZOS)
        if hl:
            lay = Image.new('RGB', img.size, (255, 255, 255)); dr = ImageDraw.Draw(lay)
            for (a, b, c, d) in phrase(BOL00, 12, 'FLÁVIO', '15/12/2000).', (170, 252)):
                dr.rectangle([(a - PAD - x0) * s, (b - PAD - ya) * s, (c + PAD - x0) * s, (d + PAD - ya) * s], fill=(255, 225, 77))
            img = ImageChops.multiply(img, lay)
        parts.append(img)
    total = sum(p.height for p in parts) + GAP * (len(parts) - 1)
    out = Image.new('RGB', (W, H), (255, 255, 255)); dr = ImageDraw.Draw(out)
    y = (H - total) // 2
    for i, p in enumerate(parts):
        if i:   # linha tracejada de trecho omitido
            yy = y - GAP // 2
            for xx in range(0, W, 18):
                dr.line([(xx, yy), (xx + 10, yy)], fill=(195, 202, 213), width=2)
        out.paste(p, (0, y)); y += p.height + GAP
    out.save(os.path.join(os.path.dirname(OUT), 'inicio', 'cargo.jpg'), 'JPEG', quality=86, optimize=True, progressive=True)
    print('inicio/cargo.jpg')


if __name__ == '__main__':
    build()
