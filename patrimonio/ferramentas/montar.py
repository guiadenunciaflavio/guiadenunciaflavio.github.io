"""Monta a página "Flávio e Lula, conta por conta" (patrimonio/index.html) e as duas contas completas
(patrimonio/flavio/ e patrimonio/lula/).

Uso:  python3 -I ferramentas/montar.py PASTA_DAS_CONTAS
PASTA_DAS_CONTAS tem conta-patrimonio.html e conta-patrimonio-lula.html (montadas por build.py e build_lula.py).
Os números vêm dos mesmos modelos das duas contas (modelo.py e modelo_lula.py, nesta pasta), no cenário padrão
delas: gastos documentados (ou estimados, no caso de Lula), dinheiro guardado rendendo a inflação, com os ganhos e
as saídas documentados.
"""
import html, json, os, re, sys
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import modelo as F            # noqa: E402
import modelo_lula as L       # noqa: E402

RAIZ = os.path.dirname(AQUI)
CONTAS = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/patrimonio'
SITE = 'https://guiadenunciaflavio.github.io/'
URL = SITE + 'patrimonio/'
PF, PL = F.PREMISSAS, L.PREMISSAS
ANOS = range(2003, 2027)

# ---------------------------------------------------------------- números (cenário padrão das duas contas)
f_sal = sum(F.liquido_flavio(a, PF) for a in ANOS)
f_esposa = sum(F.bruto_fernanda(a) * PF['liquido_fernanda'] for a in ANOS)
f_imoveis = 209768.73 + 403000.00 + 410000.00 + 1125000.00          # lucros declarados com imóveis, 2010 a 2014
f_copa_bota = 403000.00 + 410000.00 + 1125000.00                      # 2013 e 2014
f_2006_max = F.primeiro_mandato(PF, 2, 'ipca')[0]
f_2015 = F.liquido_flavio(2015, PF) + F.bruto_fernanda(2015) * PF['liquido_fernanda']
f_falta = [F.caixa_senado(PF, 1, parcelas=False)[2], F.caixa_senado(PF, 2)[2], F.caixa_senado(PF, 3)[2]]

l_pres = sum(L.liquido_presidente(a, PL) for a in ANOS)
l_apos = sum(L.aposentadoria(a) for a in ANOS)
l_pt = sum(L.salario_pt(a) for a in ANOS)
l_sal = l_pres + l_apos + l_pt
l_pal = sum(L.PALESTRAS.values())
l_2006_max = L.na_data(L.serie(PL, 2, 'ipca', 1, 1), date(2006, 7, 5))
l_2018_sem = L.na_data(L.serie(PL, 2, 'ipca', 0, 1), date(2018, 8, 15))
l_sobra = [L.caixa_mandato(PL, c)[2] for c in (3, 2, 1)]

TSE_F = {a: v for a, _d, v, _s in F.TSE}
TSE_L = {a: v for a, _d, v, _s in L.TSE}


def num(v, d):
    s = f'{v:,.{d}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def mi(v, d=1, curto=False):
    """R$ 5,5 milhões / R$ 1,74 milhão / R$ 5,5 mi"""
    n = num(v / 1e6, d)
    if curto:
        return f'R$ {n} mi'
    return f'R$ {n} {"milhão" if v < 2e6 else "milhões"}'


def mil(v):
    return f'R$ {num(v / 1e3, 0)} mil'


def curto(v):
    """para a tabela: R$ 25,5 mil, R$ 385 mil, R$ 1,74 mi"""
    if v >= 1e6:
        return mi(v, 2, curto=True)
    n = num(v / 1e3, 1)
    return 'R$ ' + (n[:-2] if n.endswith(',0') else n) + ' mil'


def faixa(a, b):
    return f'R$ {num(a / 1e6, 1)} a {num(b / 1e6, 1)} milhões'


salto_f = TSE_F[2026] / TSE_F[2018]
salto_l = TSE_L[2018] / TSE_L[2006]
queda_l = 1 - TSE_L[2026] / TSE_L[2022]
dif_2026 = TSE_F[2026] - TSE_L[2026]
assert 4.6 < salto_f < 4.8 and 9.4 < salto_l < 9.6 and 0.34 < queda_l < 0.37
assert 5.4e6 < f_sal < 5.6e6 and 5.4e6 < l_sal < 5.5e6

# ---------------------------------------------------------------- fontes
S = {
    'den': ('Denúncia do MPRJ (2020), no guia de leitura', SITE + 'denuncia/'),
    'den_salas': ('denúncia, pp. 16 e 17: as salas da Barra', SITE + 'denuncia/ponto/imo-salas-extrato/'),
    'den_saldo': ('denúncia, pp. 51 a 59: o saldo a descoberto', SITE + 'denuncia/ponto/fluxo-saldo/'),
    'den_hsbc': ('denúncia: os depósitos de R$ 638,4 mil', SITE + 'denuncia/ponto/imo-dia-hsbc/'),
    'den_141': ('denúncia, p. 44: os 141 depósitos', SITE + 'denuncia/ponto/lav-141/'),
    'den_boletos': ('denúncia: os boletos', SITE + 'denuncia/ponto/lav15-247/'),
    'den_video': ('denúncia: o vídeo', SITE + 'denuncia/ponto/lav15-video/'),
    'den_desfecho': ('guia da denúncia: o que aconteceu depois', SITE + 'denuncia/#desfecho'),
    'cargo': ('guia do cargo na Câmara', SITE + 'cargo-na-camara/'),
    'p360_f': ('Poder360: patrimônio declarado de 2006 a 2026', 'https://www.poder360.com.br/poder-eleicoes-2026/patrimonio-declarado-de-flavio-sobe-211-desde-2018/'),
    'p360_carro': ('Poder360: o carro de 2002 e o Coaf', 'https://www.poder360.com.br/governo/flavio-bolsonaro-fez-patrimonio-antes-de-se-declarar-empresario-diz-jornal/'),
    'metro_f': ('Metrópoles: bens declarados em 2026', 'https://www.metropoles.com/brasil/patrimonio-de-flavio-bolsonaro-cresceu-370-em-8-anos'),
    'terra': ('Estadão (Terra): o apartamento de Botafogo', 'https://www.terra.com.br/noticias/brasil/politica/investigacao-sobre-flavio-bolsonaro-alcanca-37-imoveis,2abe06c8757663d9825f769039f61896ggu4ah4o.html'),
    'loja': ('Estadão (Jornal de Brasília): a loja de chocolates', 'https://jornaldebrasilia.com.br/noticias/politica-e-poder/flavio-bolsonaro-e-ex-socio-receberam-r-14-mi-de-chocolataria-antes-de-venderem-o-ponto/'),
    'casa': ('Estadão (Bem Paraná): a compra da casa', 'https://www.bemparana.com.br/noticia/flavio-bolsonaro-pagou-r-181-mil-a-vista-em-imposto-e-taxas-em-compra-de-mansao-295'),
    'casa_renda': ('Poder360: as rendas no processo do financiamento', 'https://www.poder360.com.br/justica/flavio-bolsonaro-cita-renda-de-advogado-para-pagar-financiamento/'),
    'quita': ('Congresso em Foco: a quitação com seis pagamentos extras', 'https://www.congressoemfoco.com.br/noticia/29101/flavio-bolsonaro-quita-mansao-com-seis-pagamentos-extras-de-r-34-milhoes'),
    'pf_brb': ('Diario de Pernambuco: a PF e o financiamento do BRB', 'https://www.diariodepernambuco.com.br/politica/2026/10/11725606-pf-apura-condicoes-de-financiamento-do-brb-a-flavio-bolsonaro-para-mansao-de-rs-6-milhoes.html'),
    'senado': ('Agência Senado (18/1/2019), no guia do cargo', SITE + 'cargo-na-camara/#d=senado&p=1'),
    'stj': ('A Gazeta: o STJ anula a investigação', 'https://www.agazeta.com.br/brasil/stj-anula-investigacao-contra-flavio-bolsonaro-em-caso-das-rachadinhas-1121'),
    'coaf': ('Poder360: o STF anula quatro relatórios do Coaf', 'https://www.poder360.com.br/justica/stf-anula-4-relatorios-do-coaf-que-miravam-flavio-no-caso-das-rachadinhas/'),
    'gilmar': ('InfoMoney: Gilmar mantém o caso arquivado', 'https://www.infomoney.com.br/politica/gilmar-nega-recursos-e-mantem-arquivado-caso-das-rachadinhas-de-flavio-bolsonaro/'),
    'metro_l': ('Metrópoles: a trajetória de Lula (30/10/2022)', 'https://www.metropoles.com/brasil/eleicoes-2022/a-trajetoria-de-lula-duas-prisoes-e-tres-mandatos-para-presidente'),
    'cf_2006': ('Congresso em Foco: patrimônio de 2002 e 2006', 'https://www.congressoemfoco.com.br/noticia/97675/pt-justifica-evolucao-patrimonial-de-lula'),
    'cf_2018': ('Congresso em Foco: bens declarados em 2018', 'https://congressoemfoco.com.br/eleicoes/patrimonio-de-lula-cresce-5-vezes-em-12-anos-aplicada-a-correcao-veja-a-relacao-de-bens'),
    'cf_2022': ('Congresso em Foco: bens declarados em 2022', 'https://www.congressoemfoco.com.br/noticia/11316/o-patrimonio-declarado-de-lula'),
    'sbt': ('SBT News: bens declarados em 2026', 'https://sbtnews.sbt.com.br/noticia/politica/patrimonio-de-lula-tem-queda-real-de-quase-50-em-4-anos'),
    'suno': ('Suno: os planos de previdência', 'https://www.suno.com.br/noticias/?p=666127'),
    'bpm': ('BPMoney: a coluna de O Globo e os extratos da CPMI do INSS', 'https://bpmoney.com.br/economia/heranca-de-lula-presidente-antecipa-patrimonio-para-os-filhos/'),
    'p360_pal': ('Poder360: as 72 palestras', 'https://www.poder360.com.br/brasil/presidenciaveis-e-ex-presidentes-faturam-alto-com-palestras/'),
    'istoe': ('Estadão (IstoÉ): receita de 2015 e planos bloqueados', 'https://istoe.com.br/empresa-de-lula-recebeu-r-27-mi-por-palestras/'),
    'bloqueio': ('Congresso em Foco: o bloqueio de 2017', 'https://www.congressoemfoco.com.br/noticia/28869/justica-mantem-bloqueio-de-r-16-milhoes-do-ex-presidente-lula'),
    'arquiva_pal': ('Poder360: palestras arquivadas', 'https://www.poder360.com.br/lava-jato/lava-jato-justica-reconhece-legalidade-de-palestras-realizadas-por-lula/'),
    'folhape': ('Folha de Pernambuco: o arquivamento', 'https://www.folhape.com.br/politica/investigacao-sobre-palestras-de-lula-e-arquivada-e-juiza-manda/157013/'),
    'susp': ('guia da suspeição', SITE + 'suspeicao/'),
    'susp_quatro': ('decisão de Fachin: os quatro processos', SITE + 'suspeicao/ponto/fa-quatro/'),
    'susp_merito': ('acórdão: o STF não julgou se Lula era culpado', SITE + 'suspeicao/ponto/dec-nao-merito/'),
    'triplex': ('Poder360: o triplex prescreve', 'https://www.poder360.com.br/justica/mpf-pede-arquivamento-de-caso-do-triplex-contra-lula/'),
    'onze': ('Poder360: os 11 processos', 'https://www.poder360.com.br/justica/lula-se-livra-de-processos-mas-teve-so-3-absolvicoes/'),
    'onu': ('Poder360: o Comitê da ONU', 'https://www.poder360.com.br/justica/onu-conclui-que-moro-foi-parcial-no-julgamento-de-lula/'),
    'fachin': ('Poder360: Fachin anula os atos de Curitiba', 'https://www.poder360.com.br/justica/fachin-anula-todos-os-atos-processuais-contra-lula-realizados-em-curitiba/'),
    'aosfatos': ('Aos Fatos: a aposentadoria de anistiado', 'https://www.aosfatos.org/noticias/lula-nao-recebe-r-35-mil-de-aposentadoria-de-anistiado-politico/'),
    'pt_sal': ('Poder360: o salário do PT e as dívidas com advogados', 'https://www.poder360.com.br/brasil/lula-diz-que-vive-com-salario-de-r-27-mil-do-pt-e-compara-bolsonaro-a-hitler/'),
    'conta_f': ('A conta completa de Flávio, com todas as premissas', 'flavio/'),
    'conta_l': ('A conta completa de Lula, com todas as premissas', 'lula/'),
}

TAG = {'doc': ('t-doc', 'documentado'), 'ale': ('t-all', 'alegado'), 'rep': ('t-rep', 'reportagem'),
       'est': ('t-est', 'estimado'), 'int': ('t-int', 'interpretação')}
e = html.escape


def tag(k):
    c, t = TAG[k]
    return f'<span class="tag {c}">{t}</span>'


def fontes(*ks):
    return '<p class="src">' + ' '.join(f'<a href="{e(S[k][1])}"{ext(S[k][1])}>{e(S[k][0])}</a>' for k in ks) + '</p>'


def ext(u):
    return ' rel="noopener noreferrer nofollow" target="_blank"' if u.startswith('http') and not u.startswith(SITE) else ''


def rich(t):
    """[doc] no texto vira a etiqueta"""
    return re.sub(r'\[(doc|ale|rep|est|int)\]', lambda m: tag(m.group(1)), t)


# ---------------------------------------------------------------- gráfico (SVG)
def grafico():
    """patrimônio declarado em cada eleição, com todos os anos no eixo (os anos com declaração em negrito)"""
    W, H, L0, R0, T0, B0 = 820, 420, 74, 650, 34, 352
    x = lambda a: L0 + (a - 2002) * (R0 - L0) / 24
    y = lambda v: B0 - v / 9e6 * (B0 - T0)
    decl = set(TSE_F) | set(TSE_L)
    g = []
    g.append(f'<rect x="{x(2011):.1f}" y="{T0}" width="{x(2015) - x(2011):.1f}" height="{B0 - T0}" class="band lu-band"/>')
    g.append(f'<text x="{(x(2011) + x(2015)) / 2:.1f}" y="{T0 - 10}" class="band-t" text-anchor="middle">palestras de Lula</text>')
    g.append(f'<rect x="{x(2021):.1f}" y="{T0}" width="{x(2024) - x(2021):.1f}" height="{B0 - T0}" class="band fl-band"/>')
    g.append(f'<text x="{(x(2021) + x(2024)) / 2:.1f}" y="{T0 - 10}" class="band-t" text-anchor="middle">casa de Flávio</text>')
    for a in range(2002, 2027):
        g.append(f'<line x1="{x(a):.1f}" x2="{x(a):.1f}" y1="{T0}" y2="{B0 + 5}" class="vgrid{" vd" if a in decl else ""}"/>')
        g.append(f'<text transform="translate({x(a) + 4:.1f} {B0 + 14}) rotate(-45)" class="ax{" yd" if a in decl else ""}" text-anchor="end">{a}</text>')
    for v in range(0, 10, 2):
        g.append(f'<line x1="{L0}" x2="{R0}" y1="{y(v * 1e6):.1f}" y2="{y(v * 1e6):.1f}" class="grid"/>')
        g.append(f'<text x="{L0 - 10}" y="{y(v * 1e6) + 5:.1f}" class="ax" text-anchor="end">{"R$ 0" if v == 0 else f"R$ {v} mi"}</text>')

    def serie(pts, cls, quebras):
        out = []
        for (a1, v1), (a2, v2) in zip(pts, pts[1:]):
            tr = ' dash' if (a1, a2) in quebras else ''
            out.append(f'<line x1="{x(a1):.1f}" y1="{y(v1):.1f}" x2="{x(a2):.1f}" y2="{y(v2):.1f}" class="ln {cls}{tr}"/>')
        for a, v in pts:
            out.append(f'<circle cx="{x(a):.1f}" cy="{y(v):.1f}" r="5" class="pt {cls}"><title>{a}: {mi(v, 2) if v >= 1e6 else mil(v)}</title></circle>')
        return out
    pf = sorted(TSE_F.items())
    pl = sorted(TSE_L.items())
    g += serie(pl, 'lu', {(2006, 2018)})
    g += serie(pf, 'fl', {(2018, 2026)})
    for a, v, cls, t, dy in ((2018, TSE_L[2018], 'lu', 'R$ 7,99 mi', -14), (2018, TSE_F[2018], 'fl', 'R$ 1,74 mi', 24)):
        g.append(f'<text x="{x(a):.1f}" y="{y(v) + dy:.1f}" class="vl {cls}" text-anchor="middle">{t}</text>')
    for nome, v, cls in (('Flávio', TSE_F[2026], 'fl'), ('Lula', TSE_L[2026], 'lu')):
        g.append(f'<text x="{x(2026) + 12:.1f}" y="{y(v) + 5:.1f}" class="vl {cls}">{nome}, {mi(v, 2, curto=True)}</text>')
    desc = ('Patrimônio declarado ao TSE. Flávio: ' + '; '.join(f'{a}, {mi(v, 2) if v >= 1e6 else mil(v)}' for a, v in pf)
            + '. Lula: ' + '; '.join(f'{a}, {mi(v, 2) if v >= 1e6 else mil(v)}' for a, v in pl) + '.')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="gT gD"><title id="gT">Patrimônio declarado de Flávio e de Lula, '
            f'de 2002 a 2026</title><desc id="gD">{e(desc)}</desc>' + ''.join(g) + '</svg>')


def tabela_decl():
    anos = sorted(set(TSE_F) | set(TSE_L))
    cel = lambda d, a: curto(d[a]) if a in d else '<span class="muted">não disputou</span>'
    linhas = ''.join(f'<tr><th scope="row">{a}</th><td>{cel(TSE_F, a)}</td><td>{cel(TSE_L, a)}</td></tr>' for a in anos)
    return ('<table class="decl"><caption class="sr">Patrimônio declarado em cada eleição</caption><thead><tr><th scope="col">Eleição</th>'
            '<th scope="col" class="fl">Flávio</th><th scope="col" class="lu">Lula</th></tr></thead><tbody>' + linhas + '</tbody></table>')


# ---------------------------------------------------------------- lado a lado
LADO = [
    ('Hoje', 'Senador desde 2019. Candidato a presidente em 2026.', 'Presidente desde 2023. Candidato à reeleição em 2026.'),
    ('Salário e aposentadoria, de 2003 a 2026 (líquido, estimado)',
     f'{mi(f_sal)}, como deputado estadual e senador.',
     f'{mi(l_sal)}: salário de presidente ({mi(l_pres)}), aposentadoria de anistiado ({mi(l_apos)}) e salário do PT ({mi(l_pt)}).'),
    ('Outras rendas conhecidas',
     f'{mi(f_imoveis)} de lucro declarado com imóveis, de 2010 a 2014. R$ 909 mil recebidos da loja de chocolates em 2020 e 2021. A esposa teve cerca de {mi(f_esposa)} de renda líquida, de 2010 a 2026.',
     f'{mi(l_pal)} de receita da empresa de palestras, de 2011 a 2015, antes de impostos.'),
    ('Primeira declaração à Justiça Eleitoral', 'R$ 25,5 mil em 2002: um carro.', 'R$ 422,9 mil em 2002.'),
    ('Última declaração', f'{mi(TSE_F[2026], 2)} em 2026.', f'{mi(TSE_L[2026], 2)} em 2026.'),
    ('Maior salto entre duas declarações',
     f'De {mi(TSE_F[2018], 2)} em 2018 para {mi(TSE_F[2026], 2)} em 2026: {num(salto_f, 1)} vezes, já como senador.',
     f'De R$ 839 mil em 2006 para {mi(TSE_L[2018], 2)} em 2018: {num(salto_l, 1)} vezes, depois das palestras.'),
    ('No último mandato [est]',
     f'Faltam de {faixa(f_falta[0], f_falta[2])} para explicar o que ele comprou, pagou e declarou desde 2019.',
     f'Sobram de {faixa(l_sobra[0], l_sobra[2])} sem destino declarado entre 2022 e 2026.'),
    ('Acusação', 'Rachadinha: peculato, lavagem de dinheiro e organização criminosa (MPRJ, 2020).',
     'Corrupção e lavagem de dinheiro na Lava Jato: o triplex, o sítio de Atibaia e o Instituto Lula (de 2016 em diante).'),
    ('Como terminou', 'Provas anuladas (STJ e STF, 2021) e caso arquivado (TJ-RJ, 2022). Sem condenação.',
     'Condenações anuladas (STF, 2021) e Moro declarado parcial. Sem condenação.'),
]


def lado_a_lado():
    rows = ''.join(f'<tr><th scope="row">{rich(e(r[0]))}</th><td data-who="Flávio">{e(r[1])}</td><td data-who="Lula">{e(r[2])}</td></tr>' for r in LADO)
    return ('<table class="cmp"><thead><tr><th scope="col"><span class="sr">Item</span></th><th scope="col" class="fl">Flávio Bolsonaro</th>'
            '<th scope="col" class="lu">Lula</th></tr></thead><tbody>' + rows + '</tbody></table>')


# ---------------------------------------------------------------- trajetória
TRAJ = [
    ('1945', '', 'Nasce em Caetés, em Pernambuco. Aos 5 anos, a família se muda para São Paulo.'),
    ('1975', '', 'Assume a presidência do Sindicato dos Metalúrgicos de São Bernardo do Campo e Diadema.'),
    ('1980', '', 'Ajuda a fundar o PT. Fica 31 dias preso no Dops, em São Paulo.'),
    ('1981', 'Nasce em Resende, no Rio de Janeiro.', ''),
    ('1986', '', 'Eleito deputado federal por São Paulo.'),
    ('1989 a 1998', '', 'Perde três eleições para presidente: em 1989, para Collor; em 1994 e 1998, para Fernando Henrique.'),
    ('2000 a 2002', 'Assistente técnico de gabinete na liderança do PPB na Câmara, em Brasília, enquanto cursava Direito e estagiava no Rio. Sai a pedido em 2002.', ''),
    ('2002', 'Eleito deputado estadual no Rio. Declara um carro de R$ 25,5 mil.', 'Eleito presidente. Declara R$ 422,9 mil.'),
    ('2005', 'Compra um apartamento em Botafogo por R$ 350 mil.', ''),
    ('2006', 'Reeleito deputado. Declara R$ 385 mil.', 'Reeleito presidente. Declara R$ 839 mil.'),
    ('2008', 'Compra 12 salas comerciais na Barra da Tijuca. Segundo o MP, cerca de 65% foram pagos com cheques de terceiros e dinheiro vivo.', ''),
    ('2010', 'Reeleito deputado. Declara R$ 691 mil.', 'Termina o segundo mandato.'),
    ('2011 a 2015', '', f'Faz 72 palestras. A empresa dele recebe {mi(l_pal)}.'),
    ('2012 a 2014', f'Compra e revende apartamentos em Copacabana e vende o de Botafogo: {mi(f_copa_bota)} de lucro declarado.', ''),
    ('2014', 'Reeleito deputado. Declara R$ 714 mil.', ''),
    ('2015', 'Abre uma loja de chocolates, com R$ 200 mil em dinheiro vivo.', ''),
    ('2016', 'Candidato a prefeito do Rio. Declara R$ 1,5 milhão.', 'Alvo da Lava Jato. É levado a depor em condução coercitiva.'),
    ('2017', '', 'Condenado por Moro no caso do triplex. Mais de R$ 9,6 milhões bloqueados, quase tudo em previdência. A mulher, Marisa Letícia, morre.'),
    ('2018', 'Eleito senador. Declara R$ 1,74 milhão.', 'Preso em abril. Declara R$ 7,99 milhões. A candidatura é barrada.'),
    ('2019', '', 'Solto em novembro, depois de 580 dias preso.'),
    ('2020', 'Denunciado pelo Ministério Público do Rio no caso das rachadinhas.', 'A investigação das palestras é arquivada.'),
    ('2021', 'Compra uma casa de R$ 5,97 milhões em Brasília, com financiamento do BRB. O STJ anula as quebras de sigilo e as decisões do caso.',
     'Fachin anula as condenações, e o STF declara Moro parcial.'),
    ('2022', 'O Tribunal de Justiça do Rio arquiva o caso.', 'Eleito presidente pela terceira vez. Declara R$ 7,42 milhões. O Comitê de Direitos Humanos da ONU conclui que o processo violou direitos dele.'),
    ('2024', 'Quita a casa com seis pagamentos extras, que somam R$ 3,4 milhões.', ''),
    ('2025', 'Gilmar Mendes nega os recursos do MP para reabrir o caso.', ''),
    ('2026', 'Candidato a presidente. Declara R$ 8,19 milhões. A Polícia Federal apura as condições do financiamento da casa.',
     'Candidato à reeleição. Declara R$ 4,78 milhões.'),
]


def trajetoria():
    li = []
    for ano, f, l in TRAJ:
        cf = f'<div class="fl">{e(f)}</div>' if f else '<div class="fl vazio" aria-hidden="true"></div>'
        cl = f'<div class="lu">{e(l)}</div>' if l else '<div class="lu vazio" aria-hidden="true"></div>'
        li.append(f'<li><span class="yr">{e(ano)}</span>{cf}{cl}</li>')
    return ('<ol class="lanes"><li class="lane-head" aria-hidden="true"><span></span><span class="who fl">Flávio Bolsonaro</span>'
            '<span class="who lu">Lula</span></li>' + ''.join(li) + '</ol>')


# ---------------------------------------------------------------- picos
PICOS_F = [
    ('2005 e 2006', 'Um apartamento de R$ 350 mil com dois anos e meio de mandato',
     f'[est] Em 2006, Flávio declarou R$ 385 mil. A maior parte era um apartamento em Botafogo comprado em 2005 por R$ 350 mil, segundo ele. '
     f'Até julho de 2006, o salário líquido de deputado permitia juntar, no máximo, {mil(f_2006_max)} no cenário padrão; só chega perto se ele vivesse com o mínimo '
     f'do DIEESE e aplicasse todo o resto no CDI. Não se sabe se houve financiamento ou ajuda da família.',
     ('p360_f', 'terra')),
    ('2008', 'Doze salas pagas com dinheiro que não saiu da conta dele',
     '[doc] Em dezembro de 2008 foram pagos R$ 262.298,68 por 12 salas comerciais na Barra. Naquele mês, Flávio sacou só R$ 21 mil. '
     'Segundo o MP, cerca de 65% foram pagos com cheques de terceiros e depósitos em dinheiro.',
     ('den_salas',)),
    ('2012 a 2014', 'Dois apartamentos comprados por R$ 310 mil e revendidos por R$ 1,12 milhão',
     '[doc] Pelas declarações, os apartamentos da Rua Barata Ribeiro e da Avenida Prado Júnior, em Copacabana, foram comprados em 2012 por R$ 170 mil e R$ 140 mil '
     'e revendidos por R$ 573 mil e R$ 550 mil. [ale] Para o MP, o preço pago foi maior: R$ 638 mil teriam sido pagos em dinheiro vivo, por fora, e o lucro foi simulado.',
     ('den_hsbc',)),
    ('2010 a 2014', 'O próprio MP fez a conta e achou R$ 977,6 mil a descoberto',
     '[ale] Somando salários, resgates, empréstimos, doações, vendas de imóveis e o financiamento, e tirando os gastos rastreados nos extratos, o MP chegou a um saldo negativo de '
     'R$ 977.611,26. A conta não incluiu condomínio, luz, viagens nem restaurantes. [doc] No mesmo período, Flávio declarou ter doado R$ 733.390 à própria mãe.',
     ('den_saldo',)),
    ('2014 a 2018', 'Dinheiro vivo na conta e nos boletos da família',
     '[doc] A conta de Flávio recebeu 141 depósitos em dinheiro, R$ 275.500, muitos de exatamente R$ 2 mil. Mensalidades escolares e o plano de saúde somaram '
     'R$ 247.570,51 em boletos sem débito nas contas do casal. Em outubro de 2018, a câmera de uma agência filmou Queiroz pagando dois desses boletos em dinheiro.',
     ('den_141', 'den_boletos', 'den_video')),
    ('2015', 'R$ 200 mil em espécie numa loja de chocolates',
     f'[doc] A loja abriu com R$ 800 mil: R$ 400 mil do sócio, R$ 350 mil da esposa e R$ 50 mil de Flávio, que depois pôs mais R$ 200 mil em dinheiro vivo. '
     f'A renda líquida do casal naquele ano era de cerca de {mil(f_2015)}. O MP investigou a loja por suspeita de lavagem, mas ela não entrou na denúncia.',
     ('loja',)),
    ('2019 a 2026', 'Uma casa de R$ 5,97 milhões e R$ 3,4 milhões pagos ao banco em três anos',
     f'[doc] Já senador, Flávio comprou em 2021 uma casa em Brasília, com R$ 3,1 milhões financiados pelo BRB em 30 anos. A dívida foi quitada até março de 2024, com seis pagamentos '
     f'extras que somaram R$ 3,4 milhões. [est] Somando os salários do casal, o dinheiro da loja e a venda de um apartamento, faltam de {faixa(f_falta[0], f_falta[2])} '
     f'para fechar a conta, conforme os gastos da família. Flávio diz que é advogado e empresário e que todo o dinheiro é lícito; a Polícia Federal apura as condições do financiamento.',
     ('casa', 'casa_renda', 'quita', 'pf_brb', 'metro_f')),
]
PICOS_L = [
    ('2002 a 2006', 'O patrimônio quase dobrou no primeiro mandato, e a conta fecha',
     f'[est] Lula declarou R$ 422,9 mil em 2002 e R$ 839 mil em 2006. O PT atribuiu o aumento à poupança do salário de presidente, à aposentadoria e a aplicações. '
     f'Com moradia, comida e transporte pagos pelo Estado, o patrimônio podia chegar a cerca de {mi(l_2006_max, 2)} em julho de 2006, contando o que ele já tinha em 2002.',
     ('cf_2006',)),
    ('2011 a 2015', f'{mi(l_pal)} em palestras, quase metade de empresas investigadas',
     '[doc] Depois de deixar a Presidência, Lula fez 72 palestras para 45 empresas, pela LILS, empresa da qual tem 98%. Segundo a Lava Jato, a LILS recebeu R$ 21 milhões de 2011 a 2014, '
     'R$ 9,9 milhões (47%) de empresas investigadas. [ale] O MPF suspeitava que parte das palestras disfarçava propina. [doc] Em 2020, a investigação foi arquivada: a Polícia Federal '
     'concluiu que não havia indícios de crime, e o MPF concordou.',
     ('p360_pal', 'istoe', 'arquiva_pal', 'folhape')),
    ('2006 a 2018', 'Patrimônio 9,5 vezes maior, a maior parte em previdência',
     f'[doc] O declarado foi de R$ 839 mil para {mi(TSE_L[2018], 2)}, dos quais R$ 6,3 milhões em planos de previdência. Em 2017, Moro bloqueou R$ 606,7 mil em contas e mais '
     f'de R$ 9 milhões nesses planos. [est] Sem as palestras, o patrimônio poderia chegar a cerca de {mi(l_2018_sem)} em 2018, contando o que ele já tinha em 2002; com elas, a conta fecha com folga.',
     ('cf_2018', 'bloqueio', 'istoe')),
    ('2016 a 2021', 'Os bens das acusações nunca estiveram no nome dele',
     '[ale] As acusações falavam em benefícios: o triplex do Guarujá, a reforma do sítio de Atibaia, um terreno para o Instituto Lula e quatro doações de R$ 1 milhão da Odebrecht ao instituto. '
     'Nada disso esteve em nome de Lula. [doc] Em 2021, as condenações foram anuladas e o STF declarou Moro parcial. O triplex prescreveu. Dos 11 processos mais conhecidos, '
     'Lula foi absolvido no mérito em 3; os outros terminaram por anulação, prescrição, suspensão ou trancamento.',
     ('susp_quatro', 'susp_merito', 'triplex', 'onze')),
    ('2018 a 2022', 'A metade de Marisa foi para os herdeiros',
     '[doc] Marisa Letícia morreu em 2017. Na declaração de 2022, terrenos, apartamentos e as cotas da LILS aparecem exatamente pela metade: R$ 579.639,37 a menos, a parte dos herdeiros. '
     'O total passou de R$ 7,99 milhões para R$ 7,42 milhões. Em 2021, Lula disse que o dinheiro das palestras seguia bloqueado e que devia a maior parte aos advogados.',
     ('cf_2018', 'cf_2022', 'pt_sal')),
    ('2022 a 2026', 'R$ 2,65 milhões a menos, sem dizer para onde foram',
     f'[doc] Em 2026, Lula declarou {mi(TSE_L[2026], 2)}, R$ 2,65 milhões a menos que em 2022. Quase toda a queda veio da previdência, que foi de R$ 5,57 milhões para R$ 3,30 milhões. '
     f'[rep] Segundo a colunista Malu Gaspar, de O Globo, Lula antecipou cerca de R$ 2,2 milhões aos cinco filhos, como herança. [doc] Extratos obtidos pela CPMI do INSS mostram '
     f'R$ 721 mil de Lula para um dos filhos entre 2022 e 2023. [est] Mesmo descontando a herança, ficam sem destino conhecido de {faixa(l_sobra[0], l_sobra[2])}.',
     ('sbt', 'suno', 'bpm')),
]


def picos(lista):
    return ''.join(f'<article class="pico"><p class="when">{e(a)}</p><h4>{e(t)}</h4><p>{rich(e(x))}</p>{fontes(*fs)}</article>'
                   for a, t, x, fs in lista)


# ---------------------------------------------------------------- Justiça e explicações
JUST_F = [
    ('19/10/2020', 'O Ministério Público do Rio denuncia Flávio e mais 16 pessoas no caso das rachadinhas.'),
    ('fevereiro de 2021', 'O STJ anula as quebras de sigilo bancário e fiscal, por falta de fundamentação.'),
    ('9/11/2021', 'O STJ anula as decisões do juiz de primeira instância: Flávio tinha foro como deputado estadual.'),
    ('30/11/2021', 'O STF anula quatro relatórios do Coaf. O primeiro, que apontou R$ 1,2 milhão atípico de Queiroz, foi mantido.'),
    ('maio de 2022', 'O Tribunal de Justiça do Rio arquiva o caso.'),
    ('26/2/2025', 'Gilmar Mendes nega os recursos do MP para reabrir o caso. O arquivamento vale, a menos que surjam provas novas.'),
    ('2026', 'A Polícia Federal apura as condições do financiamento da casa, com juros abaixo da média do BRB. Sem conclusão.'),
]
JUST_L = [
    ('12/7/2017', 'Moro condena Lula no caso do triplex. Em 2018, o TRF-4 confirma, e Lula fica 580 dias preso.'),
    ('setembro de 2020', 'A investigação das palestras é arquivada, com a concordância do MPF.'),
    ('8/3/2021', 'Fachin anula as condenações: a Justiça de Curitiba não era competente para os quatro processos.'),
    ('23/6/2021', 'O plenário do STF confirma que Moro foi parcial no caso do triplex.'),
    ('dezembro de 2021', 'Recomeçado em Brasília, o caso do triplex prescreve, e o MPF pede o arquivamento.'),
    ('março de 2022', 'Dos 11 processos mais conhecidos, Lula foi absolvido no mérito em 3. Os outros terminaram por anulação, prescrição, suspensão ou trancamento.'),
    ('abril de 2022', 'O Comitê de Direitos Humanos da ONU conclui que o processo violou direitos de Lula.'),
]
JUST_F_SRC = ('den', 'stj', 'coaf', 'gilmar', 'pf_brb', 'den_desfecho')
JUST_L_SRC = ('susp', 'fachin', 'triplex', 'onu', 'onze', 'folhape')

EXPL_F = [
    ('Bens em nome da esposa.', 'A declaração ao TSE lista só o que está em nome de Flávio. A cobertura de Laranjeiras foi trocada em 2017 por um apartamento e uma sala; o apartamento nunca apareceu nas declarações dele.'),
    ('Rendas fora do salário.', 'Honorários de advocacia, lucros da loja entre 2015 e 2020 e a renda da esposa, dentista, podem ser maiores do que os valores públicos usados aqui.'),
    ('Ganhos com imóveis.', f'As vendas declaradas de 2010 a 2014 deram cerca de {mi(f_imoveis)} de lucro. O MP sustenta que parte foi simulada; se for verdade, o lucro real foi menor.'),
    ('Empréstimos e ajuda da família.', 'A declaração usa o valor de compra e não mostra dívidas, então um bem financiado aparece pelo valor cheio.'),
]
EXPL_L = [
    ('A previdência entra pelo valor aplicado.', 'Os rendimentos não aparecem na declaração. Em 2017, os planos valiam R$ 9 milhões; em 2018, foram declarados por R$ 6,3 milhões.'),
    ('O dinheiro que ficou na empresa.', 'A LILS entra na declaração só pelo valor das cotas, não pelo que tem aplicado.'),
    ('Advogados.', 'Lula respondeu a mais de dez processos entre 2016 e 2022 e disse, em 2021, que devia à defesa a maior parte do dinheiro bloqueado. Os valores não são públicos.'),
    ('Família.', 'A metade de Marisa foi para os herdeiros, e parte da previdência teria sido antecipada aos filhos. A data e o valor exato não são públicos.'),
]


def justica(lista):
    return '<ol class="steps">' + ''.join(f'<li><span class="d">{e(d)}</span> {e(t)}</li>' for d, t in lista) + '</ol>'


def explica(lista):
    return '<ul class="expl">' + ''.join(f'<li><b>{e(a)}</b> {e(b)}</li>' for a, b in lista) + '</ul>'


# ---------------------------------------------------------------- textos de compartilhar
SHARE_TITLE = 'Flávio e Lula, conta por conta'
SHARE_TEXT = (f'Desde 2003, Flávio e Lula receberam cerca de R$ 5,5 milhões cada em salário e aposentadoria. '
              f'Em 2026, Flávio declarou {mi(TSE_F[2026], 2)}; Lula, {mi(TSE_L[2026], 2)}. Onde a conta de cada um não fecha, com as fontes:')
DESC = ('O que Flávio Bolsonaro e Lula ganharam desde 2003, o que declararam à Justiça Eleitoral em cada eleição e onde a conta de cada um não fecha. '
        'Mesmo método, mesmas premissas, só dados públicos e com as fontes.')

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flávio e Lula, conta por conta | Guias de leitura</title>
<meta name="description" content="__DESC__">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="__URL__">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Guias de leitura">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="Flávio e Lula, conta por conta">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__URL__">
<meta property="og:image" content="__URL__og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Salário desde 2003 e patrimônio declarado em 2026 de Flávio Bolsonaro e de Lula">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{
  --paper:#f3f5f8;--card:#fff;--ink:#16202e;--ink-2:#4a5568;--line:#d8dee7;--grid:#e8ecf2;
  --mark:#ffe14d;--link:#0b4fa8;--focus:#0b4fa8;
  --fl:#0e7479;--fl-soft:#dcf0f0;--lu:#7a4ab0;--lu-soft:#ece4f6;
  --serif:Charter,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --tag-doc:#0b6b5c;--tag-doc-bg:#dff3ee;--tag-all:#9a4a00;--tag-all-bg:#fdebd3;--tag-int:#5b3ba8;--tag-int-bg:#ebe5f8;
  --tag-rep:#1d4f91;--tag-rep-bg:#e2ebf8;--tag-est:#4a5568;--tag-est-bg:#e8ecf2;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0f1520;--card:#18212f;--ink:#eef2f7;--ink-2:#aeb9c9;--line:#2a3547;--grid:#243042;--link:#8cb8ff;--focus:#8cb8ff;
    --fl:#4fc3c7;--fl-soft:#123638;--lu:#b993ea;--lu-soft:#2b2340;
    --tag-doc:#7fd9c4;--tag-doc-bg:#123a33;--tag-all:#ffc58a;--tag-all-bg:#3d2a14;--tag-int:#c9b6ff;--tag-int-bg:#2c2347;
    --tag-rep:#9cc2ff;--tag-rep-bg:#182a45;--tag-est:#c3ccd8;--tag-est-bg:#2a3547;
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#0f1520;--card:#18212f;--ink:#eef2f7;--ink-2:#aeb9c9;--line:#2a3547;--grid:#243042;--link:#8cb8ff;--focus:#8cb8ff;
  --fl:#4fc3c7;--fl-soft:#123638;--lu:#b993ea;--lu-soft:#2b2340;
  --tag-doc:#7fd9c4;--tag-doc-bg:#123a33;--tag-all:#ffc58a;--tag-all-bg:#3d2a14;--tag-int:#c9b6ff;--tag-int-bg:#2c2347;
  --tag-rep:#9cc2ff;--tag-rep-bg:#182a45;--tag-est:#c3ccd8;--tag-est-bg:#2a3547;
  color-scheme:dark;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 var(--sans)}
a{color:var(--link)}
:focus-visible{outline:3px solid var(--focus);outline-offset:2px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:-999px;top:0;background:var(--ink);color:var(--paper);padding:.6rem 1rem;z-index:10}
.skip:focus{left:0}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
.muted{color:var(--ink-2)}
.top{border-bottom:1px solid var(--line);background:var(--card)}
.top .wrap{display:flex;align-items:center;gap:1rem;min-height:58px}
.brand{display:flex;align-items:center;gap:.6rem;font-weight:700;color:var(--ink);text-decoration:none;white-space:nowrap}
.brand-mark{width:22px;height:22px;background:linear-gradient(transparent 55%,var(--mark) 55% 88%,transparent 88%),#16202e;border-radius:3px;box-shadow:inset 0 0 0 2px #16202e}
.top nav{margin-left:auto;display:flex;gap:.2rem;overflow-x:auto;scrollbar-width:none}
.top nav a{padding:.35rem .55rem;border-radius:6px;color:var(--ink-2);text-decoration:none;font-size:.92rem;white-space:nowrap}
.top nav a:hover{background:var(--paper);color:var(--ink)}
@media (max-width:900px){.top nav{display:none}}

.intro{padding:3rem 0 1.4rem;max-width:48rem}
h1{font-family:var(--serif);font-weight:700;font-size:clamp(2.2rem,5.6vw,3.6rem);line-height:1.1;margin:0 0 1rem;letter-spacing:-.01em}
h1 .mk{background:linear-gradient(transparent 58%,var(--mark) 58% 92%,transparent 92%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 .08em}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) h1 .mk{background:linear-gradient(transparent 58%,rgba(255,225,77,.38) 58% 92%,transparent 92%)}}
.lead{font-family:var(--serif);font-size:1.22rem;line-height:1.55;margin:0 0 .9rem;max-width:42rem}
.fine{font-size:.9rem;color:var(--ink-2);margin:0;max-width:46rem}
section{padding:2.4rem 0 .4rem}
h2{font-family:var(--serif);font-size:clamp(1.55rem,3.4vw,2.05rem);line-height:1.15;margin:0 0 .6rem}
h3{font:700 1.08rem var(--sans);margin:0 0 .7rem}
.who{display:inline-flex;align-items:center;gap:.45rem;font-weight:700}
.who::before{content:"";width:.85rem;height:.85rem;border-radius:3px;background:var(--c)}
.fl{--c:var(--fl);--soft:var(--fl-soft)} .lu{--c:var(--lu);--soft:var(--lu-soft)}
.tag{display:inline-block;font:700 .76rem/1 var(--sans);padding:.28rem .5rem;border-radius:999px;margin-right:.3rem;vertical-align:.1em;white-space:nowrap}
.t-doc{color:var(--tag-doc);background:var(--tag-doc-bg)} .t-all{color:var(--tag-all);background:var(--tag-all-bg)}
.t-int{color:var(--tag-int);background:var(--tag-int-bg)} .t-rep{color:var(--tag-rep);background:var(--tag-rep-bg)}
.t-est{color:var(--tag-est);background:var(--tag-est-bg)}

/* gráfico */
.chart{margin:1rem 0 0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:1rem 1rem .6rem}
.chart svg{display:block;width:100%;height:auto;font-family:var(--sans)}
.chart .grid{stroke:var(--grid);stroke-width:1}
.chart .vgrid{stroke:var(--grid);stroke-width:1;opacity:.6} .chart .vgrid.vd{opacity:1}
.chart .ax{fill:var(--ink-2);font-size:13px} .chart .ax.yd{fill:var(--ink);font-weight:700}
.chart .band{opacity:.55} .chart .lu-band{fill:var(--lu-soft)} .chart .fl-band{fill:var(--fl-soft)}
.chart .band-t{fill:var(--ink-2);font-size:12.5px;font-weight:600}
.chart .ln{stroke-width:3;stroke-linecap:round} .chart .ln.dash{stroke-dasharray:2 7}
.chart .ln.fl{stroke:var(--fl)} .chart .ln.lu{stroke:var(--lu)}
.chart .pt{stroke:var(--card);stroke-width:2} .chart .pt.fl{fill:var(--fl)} .chart .pt.lu{fill:var(--lu)}
.chart .vl{font-size:14px;font-weight:700} .chart .vl.fl{fill:var(--fl)} .chart .vl.lu{fill:var(--lu)}
.chart figcaption{font-size:.86rem;color:var(--ink-2);margin-top:.4rem}
.chart .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.chart .hint{display:none;margin:0 0 .4rem;font-size:.84rem;color:var(--ink-2)}
@media (max-width:640px){.chart{padding:.8rem .6rem .6rem}.chart .scroll svg{width:660px;max-width:none}.chart .hint{display:block}}
.gwrap{display:grid;grid-template-columns:minmax(0,1fr);gap:1.2rem;align-items:start}
.gwrap>*{min-width:0}
@media (min-width:980px){.gwrap{grid-template-columns:minmax(0,1fr) 300px}}
.decl{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:.95rem}
.decl th,.decl td{padding:.5rem .7rem;border-bottom:1px solid var(--line);text-align:right}
.decl th:first-child{text-align:left}
.decl thead th{font-size:.85rem}
.decl thead .fl,.decl thead .lu{color:var(--c)}
.decl tr:last-child th,.decl tr:last-child td{border-bottom:0;font-weight:700}
.decl .muted{font-size:.82rem}
.callout{margin:1.1rem 0 0;font-family:var(--serif);font-size:1.18rem;max-width:44rem}

/* lado a lado */
.cmp{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.cmp th,.cmp td{padding:.75rem .9rem;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
.cmp tbody tr:last-child th,.cmp tbody tr:last-child td{border-bottom:0}
.cmp thead th{font-size:1rem;border-bottom:3px solid var(--c,var(--line))}
.cmp thead th.fl,.cmp thead th.lu{color:var(--c)}
.cmp tbody th{width:24%;font-size:.92rem;color:var(--ink-2);font-weight:600}
.cmp td{width:38%}
@media (max-width:760px){
  .cmp thead{display:none}
  .cmp,.cmp tbody,.cmp tr,.cmp th,.cmp td{display:block;width:auto}
  .cmp tr{border-bottom:1px solid var(--line);padding:.6rem .9rem}
  .cmp tbody th,.cmp td{border:0;padding:.2rem 0;width:auto}
  .cmp tbody th{font-size:.88rem}
  .cmp td::before{content:attr(data-who);display:block;font-size:.8rem;font-weight:700}
  .cmp td:nth-child(2)::before{color:var(--fl)} .cmp td:nth-child(3)::before{color:var(--lu)}
}

/* trajetória */
.lanes{list-style:none;margin:1rem 0 0;padding:0}
.lanes li{display:grid;grid-template-columns:6.4rem minmax(0,1fr) minmax(0,1fr);gap:0 1.2rem;padding:.55rem 0;border-top:1px solid var(--line)}
.lanes .lane-head{border-top:0;padding-bottom:.3rem;position:sticky;top:0;background:var(--paper);z-index:2}
.lanes .yr{font-weight:700;font-variant-numeric:tabular-nums}
.lanes li>div{padding-left:.75rem;border-left:3px solid var(--c)}
.lanes li>div.vazio{border-left-color:var(--grid)}
@media (max-width:700px){
  .lanes .lane-head{display:none}
  .lanes li{grid-template-columns:4.6rem minmax(0,1fr);gap:.35rem .8rem}
  .lanes li>div{grid-column:2}
  .lanes li>div.vazio{display:none}
  .lanes li>div::before{display:block;font-size:.78rem;font-weight:700;color:var(--c)}
  .lanes li>div.fl::before{content:"Flávio"} .lanes li>div.lu::before{content:"Lula"}
}

/* duas colunas */
.two{display:grid;gap:1.4rem;margin-top:1rem}
@media (min-width:860px){.two{grid-template-columns:1fr 1fr}}
.col>h3{padding-bottom:.45rem;border-bottom:3px solid var(--c)}
.pico{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--c);border-radius:10px;padding:.85rem 1rem;margin-bottom:.8rem}
.pico .when{margin:0;font-size:.86rem;font-weight:700;color:var(--ink-2)}
.pico h4{font:700 1.04rem/1.3 var(--sans);margin:.15rem 0 .4rem}
.pico p{margin:.2rem 0 .5rem}
.src{font-size:.85rem;margin:.4rem 0 0;display:flex;flex-wrap:wrap;gap:.2rem .9rem}
.steps{list-style:none;margin:0;padding:0}
.steps li{padding:.5rem 0 .5rem .9rem;border-left:3px solid var(--c);margin-left:.1rem}
.steps .d{display:block;font-size:.84rem;font-weight:700;color:var(--ink-2)}
.expl{list-style:none;margin:0;padding:0}
.expl li{margin:0 0 .7rem}
.verdict{margin:.8rem 0 0;padding:.7rem .9rem;background:var(--soft);border-radius:10px;font-weight:600}

/* a pergunta */
.question{margin-top:2.6rem;padding:1.6rem 1.4rem;background:var(--card);border:2px solid var(--ink);border-radius:16px;box-shadow:5px 5px 0 var(--ink)}
.question p{max-width:46rem}
.question .big{font-family:var(--serif);font-size:clamp(1.5rem,3.6vw,2.1rem);line-height:1.25;margin:1.2rem 0 .8rem}
.question .big b{background:linear-gradient(transparent 58%,var(--mark) 58% 92%,transparent 92%);-webkit-box-decoration-break:clone;box-decoration-break:clone}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .question .big b{background:linear-gradient(transparent 58%,rgba(255,225,77,.38) 58% 92%,transparent 92%)}}
.question .ask-share{margin:1.1rem 0 0}

/* compartilhar */
.share{display:grid;gap:1.2rem;align-items:start}
@media (min-width:760px){.share{grid-template-columns:minmax(0,1fr) auto}}
.btns{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:.6rem}
.sh{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:.45rem .9rem;border:2px solid var(--ink);border-radius:10px;background:var(--card);color:var(--ink);font:700 .95rem var(--sans);text-decoration:none;cursor:pointer}
.sh:hover{background:var(--mark);color:#16202e}
.sh.main{background:var(--mark);color:#16202e;box-shadow:3px 3px 0 var(--ink)}
.qr{background:#fff;border:1px solid var(--line);border-radius:12px;padding:.7rem;text-align:center;width:max-content}
.qr svg{display:block;width:150px;height:150px}
.qr p{margin:.3rem 0 0;font-size:.8rem;color:#4a5568}
.toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;pointer-events:none;background:var(--ink);color:var(--paper);padding:.6rem 1rem;border-radius:10px;font:600 .92rem var(--sans);transition:opacity .2s,transform .2s}
.toast.on{opacity:1;transform:translate(-50%,0)}

.method ul{padding-left:1.1rem} .method li{margin:.35rem 0;max-width:48rem}
.srcs{columns:2 22rem;column-gap:2rem;padding-left:1.1rem;font-size:.9rem}
.srcs li{break-inside:avoid;margin:.2rem 0}
.foot{border-top:1px solid var(--line);margin-top:2.4rem;padding:1.2rem 0 2.4rem;font-size:.9rem;color:var(--ink-2)}
.foot p{margin:.3rem 0;max-width:48rem}
@media print{.top nav,.share,.toast{display:none}.question{box-shadow:none}}
</style>
<link rel="stylesheet" href="../compartilhar/compartilhar.css">
</head>
<body>
<a class="skip" href="#conteudo">Ir para o conteúdo</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="../"><span class="brand-mark" aria-hidden="true"></span><span>Guias de leitura</span></a>
    <nav aria-label="Seções">
      <a href="#grafico">Gráfico</a><a href="#lado-a-lado">Lado a lado</a><a href="#trajetoria">Trajetória</a><a href="#picos">Picos</a>
      <a href="#justica">Justiça</a><a href="#pergunta">A pergunta</a><a href="#como">Como fizemos</a>
    </nav>
  </div>
</header>
<main class="wrap" id="conteudo">
  <section class="intro">
    <h1><span class="mk">Flávio e Lula, conta por conta</span></h1>
    <p class="lead">O que cada um ganhou desde 2003, o que declarou à Justiça Eleitoral em cada eleição e onde a conta não fecha. O mesmo método e as mesmas premissas para os dois, só com dados públicos. A conclusão fica com você.</p>
    <p class="fine">Valores em reais da época, sem correção pela inflação. As contas completas, com todas as premissas e os cenários, estão em <a href="flavio/">a conta de Flávio</a> e <a href="lula/">a conta de Lula</a>. Etiquetas: __TAGDOC__ está em documento (declaração, decisão, extrato); __TAGALE__ é acusação de uma das partes; __TAGREP__ foi apurado pela imprensa; __TAGEST__ é conta nossa; __TAGINT__ é leitura nossa.</p>
  </section>

  <section id="grafico" aria-labelledby="h-graf">
    <h2 id="h-graf">O patrimônio declarado, eleição por eleição</h2>
    <p class="muted">Bens em nome de cada um, pelo valor declarado ao TSE, sem dívidas. A linha pontilhada liga eleições que eles não disputaram no meio do caminho.</p>
    <div class="gwrap">
      <figure class="chart"><p class="hint">Deslize o gráfico para o lado para ver todos os anos.</p><div class="scroll">__SVG__</div><figcaption>Os candidatos só declaram os bens nos anos em que disputam eleição, marcados em negrito. Lula não disputou em 2010, 2014 e 2016; Flávio, em 2022. Fontes: Poder360, Metrópoles, Congresso em Foco e SBT News, a partir das declarações ao TSE.</figcaption></figure>
      __DECL__
    </div>
    <p class="callout">Em 2018, Lula declarava __L18__ e Flávio, __F18__. Em 2026, Flávio declarou __F26__, __DIF__ a mais que Lula.</p>
  </section>

  <section id="lado-a-lado" aria-labelledby="h-lado">
    <h2 id="h-lado">Lado a lado</h2>
    <p class="muted">Desde 2003, os dois receberam quase o mesmo em salário e aposentadoria. O resto da conta é que muda.</p>
    __LADO__
  </section>

  <section id="trajetoria" aria-labelledby="h-traj">
    <h2 id="h-traj">A trajetória dos dois</h2>
    <p class="muted">Cargos, dinheiro e processos, ano a ano.</p>
    __TRAJ__
    __TRAJSRC__
  </section>

  <section id="picos" aria-labelledby="h-picos">
    <h2 id="h-picos">Os picos que pedem explicação</h2>
    <p class="muted">Os momentos em que o patrimônio salta ou em que o dinheiro gasto não bate com a renda.</p>
    <div class="two">
      <div class="col fl"><h3 class="who">Flávio Bolsonaro</h3>__PICOSF__</div>
      <div class="col lu"><h3 class="who">Lula</h3>__PICOSL__</div>
    </div>
  </section>

  <section id="justica" aria-labelledby="h-just">
    <h2 id="h-just">O que a Justiça decidiu</h2>
    <p class="muted">__TAGDOC__ Os dois foram acusados, e nenhum dos dois tem condenação.</p>
    <div class="two">
      <div class="col fl"><h3 class="who">Flávio Bolsonaro</h3>__JUSTF__<p class="verdict">Sem condenação. Flávio nega irregularidades.</p>__JUSTFSRC__</div>
      <div class="col lu"><h3 class="who">Lula</h3>__JUSTL__<p class="verdict">Sem condenação. Lula nega irregularidades.</p>__JUSTLSRC__</div>
    </div>
  </section>

  <section id="explicacoes" aria-labelledby="h-expl">
    <h2 id="h-expl">O que pode explicar as diferenças</h2>
    <p class="muted">Explicações possíveis para o que não fecha, que os documentos públicos não confirmam nem descartam.</p>
    <div class="two">
      <div class="col fl"><h3 class="who">Flávio Bolsonaro</h3>__EXPLF__</div>
      <div class="col lu"><h3 class="who">Lula</h3>__EXPLL__</div>
    </div>
  </section>

  <section id="pergunta" class="question" aria-labelledby="h-perg">
    __TAGINT__
    <h2 id="h-perg">A pergunta que fica</h2>
    <p>Desde 2003, os dois receberam quase o mesmo em salário e aposentadoria: cerca de R$ 5,5 milhões cada. Os dois foram acusados, os dois negam e nenhum tem condenação.</p>
    <p>A diferença está no tipo de buraco. Na conta de Lula, o salto do patrimônio tem origem conhecida, as palestras, que foram investigadas e arquivadas; o que falta explicar é para onde foram de __LSOBRA__ no terceiro mandato. Na de Flávio, o que falta explicar é de onde veio o dinheiro: salas pagas com cheques de terceiros, 141 depósitos em espécie, R$ 247 mil em mensalidades e plano de saúde pagos sem sair das contas do casal, R$ 200 mil em espécie numa loja de chocolates e, desde que ele virou senador, de __FFALTA__ a mais do que as fontes conhecidas.</p>
    <p class="big">Um patrimônio encolheu um terço em quatro anos de Presidência. O outro quase quintuplicou desde que o dono se elegeu senador. <b>Quem será que roubou mesmo?</b></p>
    <p class="fine">Nada aqui prova crime de ninguém. São as contas, com as fontes, para você tirar a sua conclusão.</p>
    <p class="ask-share"><a class="sh main" href="../compartilhar/patrimonio-feed.jpg" data-insta="patrimonio">Postar a pergunta no Instagram</a></p>
  </section>

  <section id="compartilhar" aria-labelledby="h-share">
    <h2 id="h-share">Compartilhe</h2>
    <div class="share">
      <div>
        <p class="muted">O link leva a esta página, com todas as fontes.</p>
        <div class="btns">
          <a class="sh main" id="shWa" href="__WA__" target="_blank" rel="noopener noreferrer">WhatsApp</a>
          <a class="sh" href="__TG__" target="_blank" rel="noopener noreferrer">Telegram</a>
          <a class="sh" href="__TW__" target="_blank" rel="noopener noreferrer">X (Twitter)</a>
          <a class="sh" href="__FB__" target="_blank" rel="noopener noreferrer">Facebook</a>
          <a class="sh" href="../compartilhar/patrimonio-feed.jpg" data-insta="patrimonio">Instagram</a>
          <button class="sh" type="button" id="shCopy">Copiar link</button>
          <button class="sh" type="button" id="shNative" hidden>Outros apps</button>
        </div>
      </div>
      <figure class="qr" id="qr" aria-label="QR code com o link desta página"><p>Aponte a câmera do celular</p></figure>
    </div>
  </section>

  <section id="como" class="method" aria-labelledby="h-como">
    <h2 id="h-como">Como fizemos</h2>
    <ul>
      <li>Para cada um, somamos o salário líquido e a aposentadoria de cada ano, de 2003 a agosto de 2026, e as outras rendas conhecidas. Para Lula, as palestras entram pela receita da empresa menos 18% de impostos, como se tudo tivesse ido para ele.</li>
      <li>Estimamos o custo de vida em três cenários, a partir do salário mínimo necessário do DIEESE para o tamanho de cada família; na Presidência e na prisão, só uma parte, porque moradia, comida e transporte são pagos pelo Estado.</li>
      <li>Comparamos o que sobrava com o patrimônio declarado à Justiça Eleitoral, que lista só os bens em nome de cada um, pelo valor de compra ou aplicado e sem dívidas.</li>
      <li>Os números desta página usam o cenário padrão das duas contas: gastos documentados (ou estimados, no caso de Lula) e dinheiro guardado rendendo a inflação. As faixas vão do cenário mais barato ao mais caro. Em cada conta completa você muda as premissas e vê o resultado.</li>
      <li>As contas são estimativas com dados públicos e podem estar erradas. Os documentos da denúncia das rachadinhas citados aqui são de provas que a Justiça anulou.</li>
    </ul>
    <p><a class="sh" href="flavio/">A conta completa de Flávio</a> <a class="sh" href="lula/">A conta completa de Lula</a></p>
    <h3>Fontes</h3>
    <ul class="srcs">__SRCS__</ul>
  </section>

  <section class="divulgue" aria-labelledby="h-divulgue">
    <h2 id="h-divulgue">Divulgue também</h2>
    <ul>
      <li><a href="https://comitepopular.com.br/" target="_blank" rel="noopener noreferrer"><b>Comitês Populares</b><span>Agenda, petições, materiais e como criar um comitê.</span><span class="url">comitepopular.com.br</span></a></li>
      <li><a href="https://censuradigital.lula.com.br/" target="_blank" rel="noopener noreferrer"><b>Censura Digital</b><span>Teve post derrubado ou conta restringida nas redes? Denuncie no canal da campanha de Lula.</span><span class="url">censuradigital.lula.com.br</span></a></li>
    </ul>
  </section>

  <footer class="foot">
    <p>Outros guias neste site: <a href="../denuncia/">A denúncia das rachadinhas</a>, <a href="../suspeicao/">Por que o STF declarou Moro parcial</a> e <a href="../cargo-na-camara/">O cargo de Flávio na Câmara</a>. <a href="../">Página inicial</a>.</p>
    <p>Página feita só com documentos e reportagens públicos. Nada neste site coleta dados de quem visita; os sites indicados em “Divulgue também” têm regras próprias.</p>
  </footer>
</main>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script type="module">
const URL_ = __URLJS__;
const $ = s => document.querySelector(s);
function toast(m) { const t = $('#toast'); t.textContent = m; t.classList.add('on'); clearTimeout(toast.k); toast.k = setTimeout(() => t.classList.remove('on'), 2000); }
$('#shCopy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(URL_); } catch (_) { const a = document.createElement('textarea'); a.value = URL_; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); } catch (e) { } a.remove(); }
  toast('Link copiado');
});
if (navigator.share) { const b = $('#shNative'); b.hidden = false; b.addEventListener('click', () => navigator.share({ title: __TITLEJS__, text: __TEXTJS__, url: URL_ }).catch(() => { })); }
import('./vendor/qrcode.mjs').then(({ default: qrcode }) => {
  const q = qrcode(0, 'M'); q.addData(URL_); q.make();
  const n = q.getModuleCount(), m = 2; let d = '';
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) d += `M${c + m},${r + m}h1v1h-1z`;
  $('#qr').insertAdjacentHTML('afterbegin', `<svg viewBox="0 0 ${n + 2 * m} ${n + 2 * m}" role="img" aria-label="QR code"><rect width="100%" height="100%" fill="#fff"/><path d="${d}" fill="#16202e"/></svg>`);
}).catch(() => { $('#qr').hidden = true; });
</script>
<script type="module" src="../compartilhar/insta.js"></script>
</body>
</html>
"""


def fontes_lista():
    ordem = ['conta_f', 'conta_l', 'den', 'cargo', 'susp', 'senado', 'p360_f', 'p360_carro', 'metro_f', 'terra', 'loja', 'casa', 'casa_renda', 'quita',
             'pf_brb', 'stj', 'coaf', 'gilmar', 'metro_l', 'cf_2006', 'cf_2018', 'cf_2022', 'sbt', 'suno', 'bpm', 'p360_pal', 'istoe', 'bloqueio',
             'arquiva_pal', 'folhape', 'fachin', 'triplex', 'onze', 'onu', 'aosfatos', 'pt_sal']
    return ''.join(f'<li><a href="{e(S[k][1])}"{ext(S[k][1])}>{e(S[k][0])}</a></li>' for k in ordem)


def main():
    from urllib.parse import quote
    wa = 'https://wa.me/?text=' + quote(f'*{SHARE_TITLE}*\n{SHARE_TEXT}\n{URL}')
    tg = 'https://t.me/share/url?url=' + quote(URL) + '&text=' + quote(f'{SHARE_TITLE}. {SHARE_TEXT}')
    tw = 'https://twitter.com/intent/tweet?text=' + quote(f'{SHARE_TITLE}: em 2026, Flávio declarou {mi(TSE_F[2026], 2)}; Lula, {mi(TSE_L[2026], 2)}. Onde a conta não fecha, com as fontes.') + '&url=' + quote(URL)
    fb = 'https://www.facebook.com/sharer/sharer.php?u=' + quote(URL)
    rep = {
        '__DESC__': e(DESC), '__URL__': URL, '__SVG__': grafico(), '__DECL__': tabela_decl(),
        '__L18__': mi(TSE_L[2018], 2), '__F18__': mi(TSE_F[2018], 2), '__F26__': mi(TSE_F[2026], 2), '__DIF__': mi(dif_2026, 2),
        '__LADO__': lado_a_lado(), '__TRAJ__': trajetoria(),
        '__TRAJSRC__': fontes('metro_l', 'senado', 'cargo', 'p360_f', 'cf_2006', 'den', 'susp'),
        '__PICOSF__': picos(PICOS_F), '__PICOSL__': picos(PICOS_L),
        '__JUSTF__': justica(JUST_F), '__JUSTL__': justica(JUST_L), '__JUSTFSRC__': fontes(*JUST_F_SRC), '__JUSTLSRC__': fontes(*JUST_L_SRC),
        '__EXPLF__': explica(EXPL_F), '__EXPLL__': explica(EXPL_L),
        '__LSOBRA__': faixa(l_sobra[0], l_sobra[2]), '__FFALTA__': faixa(f_falta[0], f_falta[2]),
        '__WA__': e(wa), '__TG__': e(tg), '__TW__': e(tw), '__FB__': e(fb), '__SRCS__': fontes_lista(),
        '__URLJS__': json.dumps(URL), '__TITLEJS__': json.dumps(SHARE_TITLE), '__TEXTJS__': json.dumps(SHARE_TEXT, ensure_ascii=False),
        '__TAGDOC__': tag('doc'), '__TAGALE__': tag('ale'), '__TAGREP__': tag('rep'), '__TAGEST__': tag('est'), '__TAGINT__': tag('int'),
    }
    s = PAGE
    for k, v in rep.items():
        s = s.replace(k, v)
    assert '__' not in re.sub(r'__(proto|init)__', '', s), re.findall(r'__[A-Z]+__', s)
    with open(os.path.join(RAIZ, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(s)
    contas()
    print('patrimonio/index.html', round(len(s.encode()) / 1024), 'KB')
    print(f'Flávio: salário {mi(f_sal, 2)}, esposa {mi(f_esposa, 2)}, imóveis {mi(f_imoveis, 2)}, 2006 máx {mil(f_2006_max)}, 2015 casal {mil(f_2015)}, '
          f'falta {[round(x) for x in f_falta]}, salto {salto_f:.2f}')
    print(f'Lula: presidente {mi(l_pres, 2)}, aposentadoria {mi(l_apos, 2)}, PT {mi(l_pt, 2)}, total {mi(l_sal, 2)}, palestras {mi(l_pal, 2)}, '
          f'2006 máx {mi(l_2006_max, 2)}, 2018 sem palestras {mi(l_2018_sem, 2)}, sobra {[round(x) for x in l_sobra]}, salto {salto_l:.2f}, queda {queda_l:.3f}')


# ---------------------------------------------------------------- as duas contas completas
VOLTA = ('<p style="margin:0 0 1.4rem;font-size:.95rem"><a href="../">Flávio e Lula, conta por conta</a>: a comparação das duas contas. '
         '<a href="../{outra}/">{nome_outra}</a></p>')


def contas():
    for arq, pasta, outra, nome_outra, titulo, desc in (
        ('conta-patrimonio.html', 'flavio', 'lula', 'A conta de Lula', 'A conta do patrimônio de Flávio Bolsonaro',
         'Quanto Flávio Bolsonaro e a esposa ganharam de 2003 a 2026, quanto a família gastou em três cenários e como isso se compara ao patrimônio declarado à Justiça Eleitoral.'),
        ('conta-patrimonio-lula.html', 'lula', 'flavio', 'A conta de Flávio', 'A conta do patrimônio de Lula',
         'Quanto Lula ganhou como presidente, aposentado e palestrante de 2002 a 2026, quanto gastou em três cenários e como isso se compara ao patrimônio declarado à Justiça Eleitoral.'),
    ):
        s = open(os.path.join(CONTAS, arq), encoding='utf-8').read()
        s, n = re.subn(r'<title>[^<]*</title>', f'<title>{titulo} | Guias de leitura</title>', s, count=1)
        assert n == 1
        meta = (f'<link rel="canonical" href="{URL}{pasta}/">\n<meta property="og:type" content="article">\n'
                f'<meta property="og:site_name" content="Guias de leitura">\n<meta property="og:title" content="{e(titulo)}">\n'
                f'<meta property="og:description" content="{e(desc)}">\n<meta property="og:url" content="{URL}{pasta}/">\n'
                f'<meta property="og:image" content="{URL}og.jpg">\n<meta name="twitter:card" content="summary_large_image">\n')
        assert s.count('<meta name="referrer" content="no-referrer">') == 1
        s = s.replace('<meta name="referrer" content="no-referrer">', '<meta name="referrer" content="no-referrer">\n' + meta, 1)
        assert s.count('<main>') == 1
        s = s.replace('<main>', '<main>\n  ' + VOLTA.format(outra=outra, nome_outra=nome_outra), 1)
        os.makedirs(os.path.join(RAIZ, pasta), exist_ok=True)
        with open(os.path.join(RAIZ, pasta, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(s)


if __name__ == '__main__':
    main()
