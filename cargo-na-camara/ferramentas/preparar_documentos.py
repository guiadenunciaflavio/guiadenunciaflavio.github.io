"""Prepara os documentos do guia do cargo na Câmara: PDFs, texto para a busca e caixas das palavras.

Uso:  TESSDATA_PREFIX=/pasta/com/por.traineddata python3 -I ferramentas/preparar_documentos.py PASTA_DAS_FONTES

PASTA_DAS_FONTES precisa ter:
  boletins/Ba19981113.pdf, boletins/Ba20001227.pdf, boletins/Ba20020731.pdf   (site da Câmara, sem alteração)
  DCD06NOV1996SUP.pdf                                   (Diário da Câmara, suplemento de 6/11/1996)
  "Assembleia Legislativa do Estado do Rio de Janeiro.pdf"   (perfil na Alerj, Wayback Machine, 30/1/2019)
  "Flávio Bolsonaro (PSL) — Senado Notícias.pdf"            (Agência Senado, Wayback Machine, 3/2/2019)
  certificado_UCAM.pdf, certificado_UPPG.pdf, certificado_FGV.pdf  (diplomas publicados por Flávio em 12/8/2026)

Grava pdf/<doc>.pdf, data/chunks.json, data/search.json, data/paginas.json e data/boxes/<doc>/pNNN.json.
As páginas escaneadas (Diário e diplomas) passam por OCR (tesseract, português) só para a busca e o marca-texto;
os PDFs publicados ficam como imagem. Os boletins vão como saem do site da Câmara. Nos outros PDFs os metadados
são apagados; no perfil da Alerj, os contatos do gabinete (telefone, e-mail e endereço) são cobertos e o texto
deles é removido do arquivo.
"""
import csv, io, json, os, re, shutil, subprocess, sys, tempfile
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = lambda *p: os.path.join(SRC, *p)

# documento principal primeiro (é o que o endereço #p=N abre)
DOCS = ['b2000', 'b1998', 'b2002', 'ato', 'alerj', 'senado', 'diplomas']


def clean_save(doc, path):
    """grava sem metadados (programa, data e fuso de quem gerou o arquivo) e com novo identificador"""
    doc.set_metadata({k: '' for k in ('title', 'author', 'subject', 'keywords', 'creator', 'producer', 'creationDate', 'modDate', 'trapped')})
    try:
        doc.xref_set_key(-1, 'Info', 'null')
    except Exception:
        pass
    try:
        doc.del_xml_metadata()
    except Exception:
        pass
    doc.save(path, garbage=4, deflate=True, clean=True)


def words_pdf(path):
    """palavras de cada página de um PDF com texto: [[texto, x0, y0, x1, y1], ...] em pontos, origem no alto"""
    out = []
    with pdfplumber.open(path) as d:
        for p in d.pages:
            ws = p.extract_words(use_text_flow=True, keep_blank_chars=False)
            out.append({'w': float(p.width), 'h': float(p.height),
                        'words': [[w['text'], round(w['x0'], 1), round(w['top'], 1), round(w['x1'], 1), round(w['bottom'], 1)] for w in ws]})
    return out


def ocr(img, scale):
    """OCR de uma imagem (PIL); devolve palavras com caixas já divididas por `scale` (pixels -> pontos)"""
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, 'p.png'); img.save(f)
        subprocess.run(['tesseract', f, os.path.join(td, 'o'), '-l', 'por', '--psm', '4', 'tsv'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rows = list(csv.DictReader(open(os.path.join(td, 'o.tsv'), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE))
    words = []
    for r in rows:
        t = (r.get('text') or '').strip()
        if r['level'] != '5' or not t or float(r['conf']) < 20:
            continue
        x, y, w, h = (int(r[k]) for k in ('left', 'top', 'width', 'height'))
        words.append([t, round(x / scale, 1), round(y / scale, 1), round((x + w) / scale, 1), round((y + h) / scale, 1)])
    return words


def boletim(doc_id, name):
    dst = os.path.join(OUT, 'pdf', doc_id + '.pdf')
    shutil.copyfile(S('boletins', name), dst)      # o arquivo da Câmara, sem alteração
    pages = words_pdf(dst)
    labels = {}
    for i, pg in enumerate(pages, 1):
        top = [w for w in pg['words'] if w[2] < 45]
        m = next((w[0] for w in top if re.fullmatch(r'\d{3,4}', w[0])), None)
        if m:
            labels[i] = m
    return pages, labels


def ato():
    """capa e páginas 69 a 81 do suplemento do Diário da Câmara de 6/11/1996 (o Ato da Mesa nº 45 inteiro)"""
    src = fitz.open(S('DCD06NOV1996SUP.pdf'))
    out = fitz.open()
    sel = [1] + list(range(70, 83))
    for p in sel:
        out.insert_pdf(src, from_page=p - 1, to_page=p - 1)
    dst = os.path.join(OUT, 'pdf', 'ato.pdf')
    clean_save(out, dst)
    d = fitz.open(dst)
    pages = []
    for pg in d:
        z = 300 / 72
        pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csGRAY)
        img = Image.open(io.BytesIO(pix.tobytes('png')))
        pages.append({'w': round(pg.rect.width, 1), 'h': round(pg.rect.height, 1), 'words': ocr(img, z)})
    labels = {1: 'capa'}
    labels.update({i: str(68 + i - 1) for i in range(2, 15)})     # 2 -> 69 ... 14 -> 81
    return pages, labels


# contatos do gabinete no perfil da Alerj (pontos, página: retângulos)
ALERJ_COBRIR = {
    1: [(294, 223.5, 352, 235.5)],                  # telefone e e-mail, no alto à direita
    2: [(129, 174.5, 382, 241.5)],                  # e-mail, endereço, telefone e fax, no fim
}


def alerj():
    d = fitz.open(S('Assembleia Legislativa do Estado do Rio de Janeiro.pdf'))
    for pg in d:
        for l in list(pg.get_links()):
            pg.delete_link(l)
        for r in ALERJ_COBRIR.get(pg.number + 1, []):
            pg.add_redact_annot(fitz.Rect(*r), fill=(0, 0, 0))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    dst = os.path.join(OUT, 'pdf', 'alerj.pdf')
    clean_save(d, dst)
    return words_pdf(dst), {}


def senado():
    d = fitz.open(S('Flávio Bolsonaro (PSL) — Senado Notícias.pdf'))
    for pg in d:
        for l in list(pg.get_links()):
            pg.delete_link(l)
    dst = os.path.join(OUT, 'pdf', 'senado.pdf')
    clean_save(d, dst)
    return words_pdf(dst), {}


def diplomas():
    """os três diplomas publicados por Flávio (os números de documento já aparecem cobertos nas imagens)"""
    out = fitz.open()
    pages = []
    for nome in ('certificado_UCAM.pdf', 'certificado_UPPG.pdf', 'certificado_FGV.pdf'):
        src = fitz.open(S(nome))
        img = Image.open(io.BytesIO(src.extract_image(src[0].get_images()[0][0])['image'])).convert('RGB')
        k = 0.75                                     # 1 pixel = 0,75 ponto (96 dpi)
        pg = out.new_page(width=img.width * k, height=img.height * k)
        buf = io.BytesIO(); img.save(buf, 'JPEG', quality=88, optimize=True)
        pg.insert_image(pg.rect, stream=buf.getvalue())
        big = img.convert('L').resize((img.width * 3, img.height * 3), Image.LANCZOS)
        pages.append({'w': round(img.width * k, 1), 'h': round(img.height * k, 1), 'words': ocr(big, 3 / k)})
    clean_save(out, os.path.join(OUT, 'pdf', 'diplomas.pdf'))
    return pages, {}


def main():
    os.makedirs(os.path.join(OUT, 'pdf'), exist_ok=True)
    shutil.rmtree(os.path.join(OUT, 'data', 'boxes'), ignore_errors=True)
    built = {
        'b2000': boletim('b2000', 'Ba20001227.pdf'),
        'b1998': boletim('b1998', 'Ba19981113.pdf'),
        'b2002': boletim('b2002', 'Ba20020731.pdf'),
        'ato': ato(),
        'alerj': alerj(),
        'senado': senado(),
        'diplomas': diplomas(),
    }
    chunks, search, paginas = {}, {}, {}
    for d in DOCS:
        pages, labels = built[d]
        chunks[d] = [{'file': f'pdf/{d}.pdf', 'from': 1, 'to': len(pages)}]
        search[d] = {str(i): ' '.join(w[0] for w in pg['words']) for i, pg in enumerate(pages, 1)}
        paginas[d] = {'n': len(pages), 'labels': {str(k): v for k, v in labels.items()},
                      'sizes': [[pg['w'], pg['h']] for pg in pages]}
        bd = os.path.join(OUT, 'data', 'boxes', d)
        os.makedirs(bd, exist_ok=True)
        for i, pg in enumerate(pages, 1):
            with open(os.path.join(bd, f'p{i:03d}.json'), 'w', encoding='utf-8') as f:
                json.dump(pg, f, ensure_ascii=False, separators=(',', ':'))
        print(f'{d}: {len(pages)} páginas, {sum(len(p["words"]) for p in pages)} palavras')
    for name, obj in (('chunks.json', chunks), ('search.json', search), ('paginas.json', paginas)):
        with open(os.path.join(OUT, 'data', name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    main()
