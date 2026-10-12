"""Gera as imagens de prévia de link (og/*.jpg) da página "O cargo de Flávio na Câmara".

Uso:  python3 ferramentas/gerar_previas.py
Precisa do Playwright com Chromium. As imagens são desenhadas pela própria página (assets/card.js),
abrindo index.html?gerar=1 num navegador sem janela, como nos outros guias. Rode depois de
ferramentas/montar.py sempre que os textos mudarem.
"""
import asyncio, base64, functools, http.server, json, os, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(ROOT)            # a raiz do site, para os caminhos relativos funcionarem
PORT = 8791


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    h = functools.partial(Quiet, directory=SITE_ROOT)
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


async def main():
    from playwright.async_api import async_playwright
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    dados = json.loads(html.split('<script type="application/json" id="dados">', 1)[1].split('</script>', 1)[0].replace('<\\/', '</'))
    ids = ['pagina'] + list(dados['itens'])
    os.makedirs(os.path.join(ROOT, 'og'), exist_ok=True)
    httpd = serve()
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page()
            await pg.goto(f'http://127.0.0.1:{PORT}/{os.path.basename(ROOT)}/?gerar=1', wait_until='networkidle')
            await pg.wait_for_function('typeof window.__cargoCard === "function"')
            for i in ids:
                data = await pg.evaluate('(i) => window.__cargoCard(i, "og", 0.86)', i)
                with open(os.path.join(ROOT, 'og', i + '.jpg'), 'wb') as f:
                    f.write(base64.b64decode(data.split(',', 1)[1]))
            await b.close()
    finally:
        httpd.shutdown()
    print(f'{len(ids)} imagens em og/')


if __name__ == '__main__':
    asyncio.run(main())
