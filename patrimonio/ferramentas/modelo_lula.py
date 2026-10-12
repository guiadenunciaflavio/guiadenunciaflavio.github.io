"""Experimento: renda, custo de vida e patrimônio declarado de Lula (2002 a agosto de 2026).

Mesmo método da conta de Flávio Bolsonaro (modelo.py): reais correntes, sem correção pela inflação; cada dado
com a fonte ao lado; o que é premissa fica em PREMISSAS e nos cenários.
Uso: python3 modelo_lula.py -> imprime as contas e grava dados_lula.json.
"""
import json, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))

# ================================================================ dados documentados
# Subsídio bruto mensal de presidente e início de vigência (0 = fora do cargo).
PRESIDENTE = [
    (date(2003, 1, 1), 8885.45),     # R$ 8.500 desde 1995 + revisões gerais de 2002 e 2003 (Congresso em Foco, 12/4/2007; JB, 9/5/2007)
    (date(2007, 4, 1), 11420.21),    # Câmara aprova, retroativo a abril de 2007 (JB, 9/5/2007); "R$ 11,4 mil" em dez/2010
    (date(2011, 1, 1), 0.0),         # deixa o cargo; ex-presidente não recebe salário nem pensão
    (date(2023, 1, 1), 39293.32),    # mesmo subsídio de deputados e senadores (Decreto Legislativo 172/2022; Gazeta SP)
    (date(2023, 4, 1), 41650.92),
    (date(2024, 2, 1), 44008.52),
    (date(2025, 2, 1), 46366.19),
]
FIM = date(2026, 8, 7)               # registro da candidatura e declaração de bens de 2026
MESES_2026 = 7.2                     # janeiro até 7 de agosto

# Aposentadoria excepcional de anistiado (INSS, retroativa a 1988; isenta de IR): R$ 8.902,04 por mês em 2017 e
# R$ 10.354,22 em 2021 (escritório de Lula e informes de IR, Aos Fatos, 17/11/2021). Os outros anos seguem os
# reajustes do INSS para benefícios acima do mínimo, que reproduzem exatamente a passagem de 2017 para 2021.
APOS_2017 = 8902.04
REAJ_INSS = [(date(2003, 6, 1), 19.71), (date(2004, 5, 1), 4.53), (date(2005, 5, 1), 6.355), (date(2006, 4, 1), 5.01),
             (date(2007, 4, 1), 3.30), (date(2008, 3, 1), 5.00), (date(2009, 2, 1), 5.92), (date(2010, 1, 1), 7.72),
             (date(2011, 1, 1), 6.47), (date(2012, 1, 1), 6.08), (date(2013, 1, 1), 6.20), (date(2014, 1, 1), 5.56),
             (date(2015, 1, 1), 6.23), (date(2016, 1, 1), 11.28), (date(2017, 1, 1), 6.58), (date(2018, 1, 1), 2.07),
             (date(2019, 1, 1), 3.43), (date(2020, 1, 1), 4.48), (date(2021, 1, 1), 5.45), (date(2022, 1, 1), 10.16),
             (date(2023, 1, 1), 5.93), (date(2024, 1, 1), 3.71), (date(2025, 1, 1), 4.77), (date(2026, 1, 1), 3.90)]

# Salário pago pelo PT como dirigente remunerado, desde janeiro de 2020 (nota do PT); cerca de R$ 22 mil por mês nos
# registros do partido no TSE (CNN Brasil, citada pela Revista Oeste, 2/10/2021). Lula falou em "R$ 27 mil" (9/9/2021):
# tomamos R$ 22 mil como o valor líquido de um bruto perto disso.
PT_MENSAL_LIQ = 22000.0
PT_ANOS = (2020, 2021, 2022)

# Palestras: receita da LILS Palestras (98% de Lula). R$ 21 milhões de 2011 a 2014, segundo a força-tarefa da
# Lava Jato (Poder360, 14/10/2017), dividida igualmente pelos quatro anos, e R$ 2.923.993,50 em 2015, informados pela
# própria LILS (Estadão, na IstoÉ, 20/11/2017). 72 palestras a US$ 200 mil, para 45 empresas.
PALESTRAS = {2011: 5250000.0, 2012: 5250000.0, 2013: 5250000.0, 2014: 5250000.0, 2015: 2923993.50}

# Salário mínimo necessário do DIEESE (2 adultos e 2 crianças), dezembro de cada ano; 2026 = setembro
DIEESE = {2003: 1420.61, 2004: 1468.08, 2005: 1607.11, 2006: 1564.52, 2007: 1803.11, 2008: 2141.08,
          2009: 1995.91, 2010: 2227.53, 2011: 2329.35, 2012: 2561.47, 2013: 2765.44, 2014: 2975.55, 2015: 3518.51,
          2016: 3856.23, 2017: 3585.05, 2018: 3960.57, 2019: 4342.57, 2020: 5304.90, 2021: 5800.98, 2022: 6647.63,
          2023: 6439.62, 2024: 7067.68, 2025: 7106.83, 2026: 7750.01}
CDI = {2003: 23.25, 2004: 16.17, 2005: 19.00, 2006: 15.03, 2007: 11.82, 2008: 12.38, 2009: 9.88, 2010: 9.75, 2011: 11.60,
       2012: 8.40, 2013: 8.06, 2014: 10.81, 2015: 13.24, 2016: 14.00, 2017: 9.93, 2018: 6.42, 2019: 5.96, 2020: 2.76,
       2021: 4.42, 2022: 12.39, 2023: 13.04, 2024: 10.88, 2025: 14.32, 2026: 10.51}
IPCA = {2003: 9.30, 2004: 7.60, 2005: 5.69, 2006: 3.14, 2007: 4.46, 2008: 5.90, 2009: 4.31, 2010: 5.91, 2011: 6.50,
        2012: 5.84, 2013: 5.91, 2014: 6.41, 2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31, 2020: 4.52,
        2021: 10.06, 2022: 5.78, 2023: 4.62, 2024: 4.83, 2025: 4.26, 2026: 3.95}

# Patrimônio declarado ao TSE (bens em nome de Lula, pelo valor de compra ou aplicado, sem dívidas)
TSE = [
    (2002, date(2002, 7, 5), 422949.32, 'Congresso em Foco, 5/7/2006'),
    (2006, date(2006, 7, 5), 839033.52, 'Congresso em Foco, 5/7/2006'),
    (2018, date(2018, 8, 15), 7987921.57, 'Congresso em Foco, 15/8/2018'),
    (2022, date(2022, 8, 15), 7423725.78, 'Congresso em Foco, 9/8/2022'),
    (2026, date(2026, 8, 7), 4775650.64, 'SBT News, 8/8/2026; Suno, 4/10/2026'),
]
INICIO = 422949.32                   # ponto de partida: o declarado em 2002

# Saídas conhecidas que tiram dinheiro do patrimônio sem ser gasto do dia a dia
SAIDAS = [
    (2021, -579639.37, 'Metade de Marisa Letícia nos imóveis e nas cotas da LILS, que passou aos herdeiros',
     'TSE 2018 x 2022: terrenos, apartamentos e cotas aparecem pela metade (valor declarado)'),
    (2024, -2200000.00, 'Antecipação de herança aos cinco filhos, a partir dos planos de previdência (data não informada)',
     'O Globo (coluna de Malu Gaspar), citado por BPMoney e NC News, 17/8/2026'),
]

# Custos estimados (não há documento sobre os gastos da família), em R$ por mês, a preços de 2016
CUSTO_EST = {'apto': 2000.0, 'saude_pessoa': 2000.0, 'domestica': 3333.0}
CUSTO_EST_ANO = 2016

PREMISSAS = dict(
    liquido_pres1=0.75,      # 2003-2010: IR de 27,5% e INSS com teto
    liquido_pres2=0.735,     # 2023-2026: mesmo subsídio de senador (R$ 33.763 brutos = R$ 24,9 mil líquidos)
    imposto_lils=0.18,       # impostos da empresa sobre a receita (lucro presumido e ISS), estimado
    frac_estado=0.25,        # na Presidência e na prisão: parte do mínimo que sai do bolso (moradia, comida, transporte e saúde pagos pelo Estado)
    alto_padrao=1.5,
    ir_aplicacao=0.15,
)


# ================================================================ funções
def subsidio(d):
    v = 0.0
    for ini, val in PRESIDENTE:
        if d >= ini:
            v = val
    return v


def meses_ano(ano):
    return MESES_2026 if ano == 2026 else 12


def bruto_presidente(ano):
    if ano == 2026:
        return subsidio(date(2026, 7, 1)) * MESES_2026
    tot = sum(subsidio(date(ano, m, 1)) for m in range(1, 13))
    return tot + subsidio(date(ano, 12, 1))          # 13º


def liquido_presidente(ano, P):
    return bruto_presidente(ano) * (P['liquido_pres1'] if ano < 2015 else P['liquido_pres2'])


def apos_mes(d):
    """Valor mensal da aposentadoria na data d, ancorado em janeiro de 2017."""
    v = APOS_2017
    ref = date(2017, 1, 1)
    for dt, pct in REAJ_INSS:
        if ref < dt <= d:
            v *= 1 + pct / 100
        elif d < dt <= ref:
            v /= 1 + pct / 100
    return v


def aposentadoria(ano, m_ini=1, m_fim=12):
    """Soma de m_ini a m_fim, com 13º quando dezembro entra. 2026 vai até 7 de agosto."""
    if ano == 2026:
        return sum(apos_mes(date(2026, m, 1)) for m in range(1, 8)) + 0.2 * apos_mes(date(2026, 8, 1))
    tot = sum(apos_mes(date(ano, m, 1)) for m in range(m_ini, m_fim + 1))
    if m_fim == 12:
        tot += apos_mes(date(ano, 12, 1))
    return tot


def salario_pt(ano):
    return PT_MENSAL_LIQ * 12 if ano in PT_ANOS else 0.0


def palestras_liq(ano, P):
    return PALESTRAS.get(ano, 0.0) * (1 - P['imposto_lils'])


def fases(ano):
    """Meses do ano por situação: (meses, tipo, adultos). tipo: 'pres' (Presidência), 'casa', 'prisao'."""
    if 2003 <= ano <= 2010:
        return [(12, 'pres', 2)]
    if 2011 <= ano <= 2016:
        return [(12, 'casa', 2)]
    if ano == 2017:                                   # Marisa Letícia morre em fevereiro
        return [(1, 'casa', 2), (11, 'casa', 1)]
    if ano == 2018:                                   # prisão a partir de 7 de abril
        return [(3, 'casa', 1), (9, 'prisao', 1)]
    if ano == 2019:                                   # solto em 8 de novembro
        return [(10, 'prisao', 1), (2, 'casa', 1)]
    if ano in (2020, 2021):
        return [(12, 'casa', 1)]
    if ano == 2022:                                   # casa-se com Rosângela da Silva em maio
        return [(4, 'casa', 1), (8, 'casa', 2)]
    return [(meses_ano(ano), 'pres', 2)]               # 2023-2026


def dieese(ano):
    return (DIEESE[ano - 1] + DIEESE[ano]) / 2 if ano - 1 in DIEESE else DIEESE[ano]


def custo_mes(ano, tipo, adultos, cen, P):
    base = dieese(ano) * adultos / 3                  # DIEESE: 2 adultos + 2 crianças = 3 adultos
    if tipo in ('pres', 'prisao'):
        base *= P['frac_estado']
    if cen == 1:
        return base
    k = dieese(ano) / dieese(CUSTO_EST_ANO)
    extra = CUSTO_EST['apto']
    if tipo != 'pres':
        extra += CUSTO_EST['saude_pessoa'] * adultos
    if tipo == 'casa':
        extra += CUSTO_EST['domestica']
    tot = base + extra * k
    return tot * P['alto_padrao'] if cen == 3 else tot


def custo_vida(ano, cen, P, so_meses=None):
    """so_meses: (m_ini, m_fim) para somar só parte do ano."""
    tot, m0 = 0.0, 1
    for n, tipo, ad in fases(ano):
        for i in range(int(round(n * 10))):          # passos de 0,1 mês, para 2026
            mes = m0 + i / 10
            if so_meses and not (so_meses[0] <= int(mes) <= so_meses[1]):
                continue
            tot += custo_mes(ano, tipo, ad, cen, P) / 10
        m0 += n
    return tot


def taxa(ano, ret, P):
    if ret == 'zero':
        return 0.0
    t = (IPCA if ret == 'ipca' else CDI)[ano] / 100
    if ano == 2026:
        t *= MESES_2026 / 9
    if ret == 'cdi_liq':
        t *= 1 - P['ir_aplicacao']
    return t


def serie(P, cen, ret, pal, sai):
    """pal: conta as palestras; sai: conta as saídas conhecidas (metade de Marisa e antecipação de herança)."""
    ev = {}
    if sai:
        for a, v, *_ in SAIDAS:
            ev[a] = ev.get(a, 0.0) + v
    rows, acc = [], INICIO
    for ano in range(2003, 2027):
        sal = liquido_presidente(ano, P) + salario_pt(ano)
        ap = aposentadoria(ano)
        pl = palestras_liq(ano, P) if pal else 0.0
        cv = custo_vida(ano, cen, P)
        sobra = sal + ap + pl - cv
        e = ev.get(ano, 0.0)
        r = taxa(ano, ret, P)
        rend = acc * r + (sobra + e) * r / 2
        acc += sobra + e + rend
        rows.append(dict(ano=ano, sal=round(sal), apos=round(ap), pal=round(pl), vida=round(cv), sobra=round(sobra),
                         eventos=round(e), rend=round(rend), acum=round(acc)))
    return rows


def na_data(rows, d):
    prev = INICIO
    for r in rows:
        if r['ano'] == d.year:
            frac = min(1.0, ((d - date(d.year, 1, 1)).days + 1) / 365) if d.year != 2026 else 1.0
            return prev + (r['acum'] - prev) * frac
        prev = r['acum']
    return prev


# ================================================================ agosto de 2022 a agosto de 2026, linha a linha
def caixa_mandato(P, cen, heranca=2200000.0, advogados=0.0, outras=0.0, pt_ate_dez=True, ret='cdi_liq'):
    sal = sum(liquido_presidente(a, P) for a in (2023, 2024, 2025, 2026))
    apos = aposentadoria(2022, 9, 12) + sum(aposentadoria(a) for a in (2023, 2024, 2025, 2026))
    pt = 4 * PT_MENSAL_LIQ if pt_ate_dez else 0.0
    vida = custo_vida(2022, cen, P, so_meses=(9, 12)) + sum(custo_vida(a, cen, P) for a in (2023, 2024, 2025, 2026))
    # aplicações fora da previdência: R$ 212.872,60 em 2022 (contas, poupança, CDB e fundos) e cerca de R$ 390 mil em 2026
    media = (212872.60 + 390717.40) / 2
    f = (1 + taxa(2022, ret, P) * 4 / 12)
    for a in (2023, 2024, 2025, 2026):
        f *= 1 + taxa(a, ret, P)
    rend = media * (f - 1)
    fontes = [
        ('decl2022', 'Patrimônio declarado em agosto de 2022', 7423725.78, 'TSE 2022 (Congresso em Foco, 9/8/2022)'),
        ('sal', 'Salário líquido de presidente, jan/2023 a ago/2026', sal, 'Subsídio de R$ 39,3 mil a R$ 46,4 mil, com 13º, 73,5% líquido'),
        ('apos', 'Aposentadoria de anistiado, set/2022 a ago/2026', apos, 'R$ 10.354,22 em 2021 (Aos Fatos), com os reajustes do INSS; isenta de IR'),
    ]
    if pt_ate_dez:
        fontes.append(('pt', 'Salário do PT, set a dez/2022', pt, 'R$ 22 mil por mês; supõe que continuou até a posse'))
    fontes.append(('rend', 'Rendimento das aplicações fora da previdência (estimado)', rend, 'CDI sem o IR sobre a média de R$ 0,3 milhão declarada'))
    usos = [
        ('decl2026', 'Patrimônio declarado em agosto de 2026', 4775650.64, 'TSE 2026 (SBT News, 8/8/2026)'),
        ('heranca', 'Antecipação de herança aos cinco filhos', heranca, 'Valor citado por O Globo; não está em documento público'),
        ('vida', 'Custo de vida pago do próprio bolso no período', vida, f'Cenário {cen} desta conta'),
    ]
    if advogados:
        usos.append(('advogados', 'Honorários de advogados', advogados, 'Premissa'))
    if outras:
        usos.append(('outras', 'Outras saídas', outras, 'Premissa'))
    sobra = sum(i[2] for i in fontes) - sum(i[2] for i in usos)
    return fontes, usos, sobra


if __name__ == '__main__':
    P = PREMISSAS
    anos = range(2003, 2027)
    print('Aposentadoria mensal: 2003-01 {:,.2f} | 2010 {:,.2f} | 2017 {:,.2f} | 2021 {:,.2f} | 2026 {:,.2f}'.format(
        apos_mes(date(2003, 1, 1)), apos_mes(date(2010, 6, 1)), apos_mes(date(2017, 6, 1)), apos_mes(date(2021, 6, 1)), apos_mes(date(2026, 6, 1))))
    tot_pres = sum(liquido_presidente(a, P) for a in anos)
    tot_pt = sum(salario_pt(a) for a in anos)
    tot_apos = sum(aposentadoria(a) for a in anos)
    tot_pal = sum(palestras_liq(a, P) for a in anos)
    print(f'Salário líquido de presidente: R$ {tot_pres:,.0f}  (2003-2010: {sum(liquido_presidente(a, P) for a in range(2003, 2011)):,.0f})')
    print(f'Salário do PT: R$ {tot_pt:,.0f} | Aposentadoria: R$ {tot_apos:,.0f} | Palestras líquidas: R$ {tot_pal:,.0f} (bruto {sum(PALESTRAS.values()):,.0f})')
    for cen in (1, 2, 3):
        print(f'Custo de vida, cenário {cen}: R$ {sum(custo_vida(a, cen, P) for a in anos):,.0f}')

    grid = {}
    for pal in (0, 1):
        for sai in (0, 1):
            for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
                for cen in (1, 2, 3):
                    grid[f'{pal}{sai}-{ret}-{cen}'] = serie(P, cen, ret, pal, sai)

    d06, d18, d22, d26 = (t[1] for t in TSE[1:])
    print('\n== Máximo nas datas das declarações (cenário 2) x declarado')
    for pal in (0, 1):
        for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
            rows = grid[f'{pal}1-{ret}-2']
            print(f'palestras={pal} {ret:8}', ' | '.join(f'{d.year}: {na_data(rows, d)/1e6:6.2f} x {v/1e6:5.2f}' for (_, d, v, _s) in TSE[1:]))

    print('\n== 2018 sem palestras: máximo x 7,99 mi')
    for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
        print(ret, '  '.join(f'c{c}: {na_data(grid[f"01-{ret}-{c}"], d18)/1e6:5.2f}' for c in (1, 2, 3)))

    print('\n== 2006: máximo x 839 mil')
    for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
        print(ret, '  '.join(f'c{c}: {na_data(grid[f"01-{ret}-{c}"], d06):,.0f}' for c in (1, 2, 3)))

    print('\n== ago/2022 a ago/2026, linha a linha')
    for cen in (1, 2, 3):
        f, u, s = caixa_mandato(P, cen)
        print(f'cenário {cen}: fontes {sum(i[2] for i in f):,.0f} | usos {sum(i[2] for i in u):,.0f} | sem destino {s:,.0f}')
    f, u, s = caixa_mandato(P, 2)
    for _i, n, v, src in f: print(f'  + {v:>12,.0f}  {n}  [{src}]')
    for _i, n, v, src in u: print(f'  - {v:>12,.0f}  {n}  [{src}]')

    marcos = {}
    for key, rows in grid.items():
        marcos[key] = [round(na_data(rows, d)) for d in (d06, d18, d22, d26)]
    json.dump(dict(premissas=P, grid=grid, marcos=marcos, tse=[(a, d.isoformat(), v, s) for a, d, v, s in TSE],
                   saidas=SAIDAS, inicio=INICIO,
                   caixa={c: caixa_mandato(P, c) for c in (1, 2, 3)},
                   caixa_sem_pt={c: caixa_mandato(P, c, pt_ate_dez=False) for c in (1, 2, 3)},
                   totais=dict(pres=tot_pres, pt=tot_pt, apos=tot_apos, pal=tot_pal, pal_bruto=sum(PALESTRAS.values()),
                               vida={c: sum(custo_vida(a, c, P) for a in anos) for c in (1, 2, 3)},
                               pres_1=sum(liquido_presidente(a, P) for a in range(2003, 2011)),
                               pres_2=sum(liquido_presidente(a, P) for a in range(2023, 2027)),
                               apos_mes={'2003': apos_mes(date(2003, 1, 1)), '2017': APOS_2017, '2026': apos_mes(date(2026, 6, 1))})),
              open(os.path.join(HERE, 'dados_lula.json'), 'w'), ensure_ascii=False, separators=(',', ':'), default=str)
    print('\ndados_lula.json', round(os.path.getsize(os.path.join(HERE, 'dados_lula.json')) / 1024), 'KB')
