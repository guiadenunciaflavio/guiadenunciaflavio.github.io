"""Gera as imagens de prévia: patrimonio/og.jpg (1200x630, para WhatsApp, Facebook, X) e inicio/patrimonio.jpg
(cartão da página inicial). Uso: python3 -I ferramentas/previa.py PASTA_DAS_CONTAS (Playwright com Chromium)."""
import asyncio, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import montar as M  # noqa: E402

RAIZ = M.RAIZ
SITE_RAIZ = os.path.dirname(RAIZ)
FONTE = ('font-family:Charter,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif')

OG = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;width:1200px;height:630px;background:#16202e;font-family:system-ui,"Segoe UI",Roboto,Arial,sans-serif;color:#16202e}}
.card{{position:absolute;inset:26px;background:#fff;border-radius:22px;padding:40px 52px}}
.top{{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:25px}}
.brand{{display:flex;align-items:center;gap:14px}}
.mk{{width:32px;height:32px;border-radius:5px;background:linear-gradient(transparent 55%,#ffe14d 55% 88%,transparent 88%),#16202e}}
.host{{color:#0b4fa8;font-size:23px}}
.k{{margin:30px 0 4px;color:#4a5568;font-weight:600;font-size:25px}}
h1{{{FONTE};font-size:60px;line-height:1.1;margin:0 0 30px}}
h1 span{{background:linear-gradient(transparent 58%,#ffe14d 58% 92%,transparent 92%)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:34px}}
.p{{border-left:8px solid var(--c);padding:2px 0 2px 22px}}
.p h2{{margin:0 0 10px;font-size:29px;color:var(--c)}}
.row{{display:flex;gap:28px}}
.row b{{display:block;font-size:42px;line-height:1.05;color:#16202e}}
.row span{{display:block;font-size:20px;color:#4a5568;margin-top:4px;max-width:12.5em}}
.fl{{--c:#0e7479}} .lu{{--c:#7a4ab0}}
.foot{{position:absolute;left:52px;right:52px;bottom:36px;border-top:2px solid #d8dee7;padding-top:18px;font-size:24px;font-weight:600;color:#16202e}}
</style></head><body><div class="card">
<div class="top"><div class="brand"><div class="mk"></div>Guias de leitura</div><div class="host">guiadenunciaflavio.github.io/patrimonio</div></div>
<p class="k">Salário e patrimônio declarado, de 2002 a 2026, com as fontes</p>
<h1><span>Flávio e Lula, conta por conta</span></h1>
<div class="two">
 <div class="p fl"><h2>Flávio Bolsonaro</h2><div class="row"><div><b>{M.mi(M.f_sal, 1, True)}</b><span>de salário desde 2003</span></div>
   <div><b>{M.mi(M.TSE_F[2026], 2, True)}</b><span>de patrimônio declarado em 2026</span></div></div></div>
 <div class="p lu"><h2>Lula</h2><div class="row"><div><b>{M.mi(M.l_sal, 1, True)}</b><span>de salário e aposentadoria desde 2003</span></div>
   <div><b>{M.mi(M.TSE_L[2026], 2, True)}</b><span>de patrimônio declarado em 2026</span></div></div></div>
</div><div class="foot">Os picos que pedem explicação, o que a Justiça decidiu e a fonte de cada número</div></div></body></html>"""

CARTAO = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;width:961px;height:601px;background:#fff;font-family:system-ui,"Segoe UI",Roboto,Arial,sans-serif;--fl:#0e7479;--fl-soft:#dcf0f0;--lu:#7a4ab0;--lu-soft:#ece4f6;--grid:#e8ecf2;--ink-2:#4a5568;--card:#fff}}
.wrap{{padding:58px 18px 10px 4px}}
svg{{display:block;width:100%;height:auto}}
.grid{{stroke:var(--grid)}} .vgrid{{stroke:var(--grid);opacity:.6}} .vgrid.vd{{opacity:1}} .ax{{fill:var(--ink-2);font-size:13px}} .ax.yd{{fill:#16202e;font-weight:700}} .band{{opacity:.55}} .lu-band{{fill:var(--lu-soft)}} .fl-band{{fill:var(--fl-soft)}}
.band-t{{fill:var(--ink-2);font-size:12.5px;font-weight:600}} .ln{{stroke-width:3;stroke-linecap:round}} .ln.dash{{stroke-dasharray:2 7}}
.ln.fl{{stroke:var(--fl)}} .ln.lu{{stroke:var(--lu)}} .pt{{stroke:#fff;stroke-width:2}} .pt.fl{{fill:var(--fl)}} .pt.lu{{fill:var(--lu)}}
.vl{{font-size:14px;font-weight:700}} .vl.fl{{fill:var(--fl)}} .vl.lu{{fill:var(--lu)}}
</style></head><body><div class="wrap">{M.grafico()}</div></body></html>"""


async def main():
    from playwright.async_api import async_playwright
    tmp = os.path.join(AQUI, '_tmp')
    os.makedirs(tmp, exist_ok=True)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch()
            for html_, w, h, out in ((OG, 1200, 630, os.path.join(RAIZ, 'og.jpg')), (CARTAO, 961, 601, os.path.join(SITE_RAIZ, 'inicio', 'patrimonio.jpg'))):
                f = os.path.join(tmp, 'p.html')
                open(f, 'w', encoding='utf-8').write(html_)
                pg = await b.new_page(viewport={'width': w, 'height': h})
                await pg.goto('file://' + f)
                await pg.screenshot(path=out, type='jpeg', quality=86, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
                await pg.close()
                print(out, round(os.path.getsize(out) / 1024), 'KB')
            await b.close()
    finally:
        for n in os.listdir(tmp):
            os.remove(os.path.join(tmp, n))
        os.rmdir(tmp)


if __name__ == '__main__':
    asyncio.run(main())
