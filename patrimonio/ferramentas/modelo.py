"""Experimento: renda, custo de vida e patrimônio declarado de Flávio Bolsonaro (2003 a agosto de 2026).

Tudo em reais correntes (nominais), sem correção pela inflação. Cada dado tem a fonte ao lado;
o que é premissa está em PREMISSAS e nos cenários. Uso: python3 modelo.py -> imprime as contas e grava dados.json.
"""
import json, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))

# ================================================================ dados documentados
# Subsídio bruto mensal e início de vigência. Deputado estadual = 75% do subsídio de deputado federal.
SUBSIDIO = [
    (date(2003, 2, 1), 9635.40),     # ALERJ: 75% de R$ 12.847,20
    (date(2007, 4, 1), 12384.06),    # ALERJ: 75% de R$ 16.512,09
    (date(2011, 2, 1), 20042.34),    # ALERJ: 75% de R$ 26.723,13
    (date(2015, 2, 1), 25322.25),    # ALERJ: 75% de R$ 33.763,00
    (date(2019, 2, 1), 33763.00),    # Senado
    (date(2023, 1, 1), 39293.32),
    (date(2023, 4, 1), 41650.92),
    (date(2024, 2, 1), 44008.52),
    (date(2025, 2, 1), 46366.19),
]
FIM = date(2026, 8, 13)              # registro da candidatura e declaração de bens de 2026
MESES_2026 = 7.4                     # janeiro até 13 de agosto

# Renda bruta anual de 2010 a 2014 pelas declarações de IR citadas na denúncia (p. 51); é maior que a conta pelo subsídio
RENDA_FLAVIO_IR = {2010: 183153.10, 2011: 280642.67, 2012: 295098.60, 2013: 275997.65, 2014: 274889.21}
RENDA_FERNANDA_IR = {2010: 84163.84, 2011: 87532.08, 2012: 99470.24, 2013: 103171.03, 2014: 119880.92}
FERNANDA_MENSAL_2021 = 8650.00       # renda declarada no processo do financiamento (Poder360, 1/6/2022)

# Salário mínimo necessário do DIEESE (família de 2 adultos e 2 crianças), dezembro de cada ano; 2026 = setembro
DIEESE = {2003: 1420.61, 2004: 1468.08, 2005: 1607.11, 2006: 1564.52, 2007: 1803.11, 2008: 2141.08,
          2009: 1995.91, 2010: 2227.53, 2011: 2329.35, 2012: 2561.47, 2013: 2765.44, 2014: 2975.55, 2015: 3518.51,
          2016: 3856.23, 2017: 3585.05, 2018: 3960.57, 2019: 4342.57, 2020: 5304.90, 2021: 5800.98, 2022: 6647.63,
          2023: 6439.62, 2024: 7067.68, 2025: 7106.83, 2026: 7750.01}
# CDI acumulado no ano (%); 2026 = janeiro a setembro
CDI = {2003: 23.25, 2004: 16.17, 2005: 19.00, 2006: 15.03, 2007: 11.82, 2008: 12.38, 2009: 9.88, 2010: 9.75, 2011: 11.60,
       2012: 8.40, 2013: 8.06, 2014: 10.81, 2015: 13.24, 2016: 14.00, 2017: 9.93, 2018: 6.42, 2019: 5.96, 2020: 2.76,
       2021: 4.42, 2022: 12.39, 2023: 13.04, 2024: 10.88, 2025: 14.32, 2026: 10.51}

# IPCA acumulado no ano (%); 2026 = janeiro a setembro
IPCA = {2003: 9.30, 2004: 7.60, 2005: 5.69, 2006: 3.14, 2007: 4.46, 2008: 5.90, 2009: 4.31, 2010: 5.91, 2011: 6.50,
        2012: 5.84, 2013: 5.91, 2014: 6.41, 2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31, 2020: 4.52,
        2021: 10.06, 2022: 5.78, 2023: 4.62, 2024: 4.83, 2025: 4.26, 2026: 3.95}

# Patrimônio declarado ao TSE: só bens em nome de Flávio, pelo valor de compra, sem dívidas
TSE = [
    (2002, date(2002, 7, 5), 25500.00, 'Um carro Gol 1.0 (Folha, citada pelo Poder360)'),
    (2006, date(2006, 7, 5), 385000.00, 'Poder360, série do TSE'),
    (2010, date(2010, 7, 5), 691000.00, 'Poder360, série do TSE'),
    (2014, date(2014, 7, 5), 714000.00, 'Poder360, série do TSE'),
    (2016, date(2016, 8, 15), 1500000.00, 'Poder360, série do TSE'),
    (2018, date(2018, 8, 15), 1741758.15, 'TSE (Suno, Metrópoles)'),
    (2026, date(2026, 8, 13), 8186555.83, 'TSE (Suno, Metrópoles)'),
]

# Custos da família documentados na denúncia (anos 2014-2018), em R$ por mês, a preços de 2016
CUSTO_DOC = {'escola': 4000.0, 'saude': 950.0, 'domesticas': 3333.0, 'iptu': 800.0}
CUSTO_DOC_ANO = 2016

# Eventos documentados que mudam o patrimônio fora do salário (entram na conta "com eventos").
# valor > 0 aumenta o que sobra; < 0 diminui. Ganhos de imóveis = venda menos compra, pelos valores declarados.
EVENTOS = [
    (2008, -90000.00, 'Perda na bolsa de valores, 2007-2008', 'denúncia, p. 16'),
    (2010, +209768.73, 'Ganho na venda dos direitos das 12 salas da Barra (R$ 854 mil, pagas R$ 644 mil)', 'denúncia, pp. 52 e 54; Estadão'),
    (2010, -733390.00, 'Doação declarada de Flávio à mãe', 'denúncia, p. 54'),
    (2010, -52732.35, 'ITBI das salas e IR sobre o ganho', 'denúncia, p. 54'),
    (2012, +405613.00, 'Doações recebidas por Fernanda (da sogra e da mãe)', 'denúncia, pp. 52-53'),
    (2012, -49026.33, 'ITBI e cartório dos imóveis de Copacabana e Laranjeiras', 'denúncia, p. 56'),
    (2013, +403000.00, 'Ganho declarado: apto. da Rua Barata Ribeiro (comprado a R$ 170 mil, vendido a R$ 573 mil)', 'denúncia, pp. 25, 29 e 53'),
    (2013, -60450.00, 'IR sobre esse ganho', 'denúncia, p. 57'),
    (2014, +410000.00, 'Ganho declarado: apto. da Av. Prado Júnior (R$ 140 mil para R$ 550 mil)', 'denúncia, pp. 25, 29 e 53'),
    (2014, +1125000.00, 'Ganho declarado: apto. de Botafogo (comprado em 2005 a R$ 350 mil, vendido a R$ 1,475 milhão)', 'Estadão, 26/5/2019; denúncia, p. 53'),
    (2014, -112500.00, 'IR e ITBI dos negócios de 2014', 'denúncia, p. 57'),
    (2017, -36000.00, 'ITBI da troca da cobertura de Laranjeiras', 'denúncia, p. 62'),
    (2021, +309000.00, 'Loja de chocolates: R$ 909 mil recebidos em 2020-2021 menos R$ 600 mil postos pelo casal em 2015', 'Estadão, 10/11/2023'),
    (2021, -181111.85, 'ITBI e cartório da casa em Brasília', 'Estadão, 6/3/2021'),
]

PREMISSAS = dict(
    liquido_alerj=0.75,      # líquido / bruto: IR de 27,5% e INSS com teto
    liquido_senado=0.735,    # R$ 33.763 brutos = R$ 24,9 mil líquidos (Estadão / Brasil de Fato, 2021)
    liquido_fernanda=0.85,
    alto_padrao=1.5,         # cenário 3 = cenário 2 x 1,5
    ir_aplicacao=0.15,       # IR sobre rendimento de aplicação (CDI líquido)
)


def subsidio(d):
    v = None
    for ini, val in SUBSIDIO:
        if d >= ini:
            v = val
    return v


def bruto_flavio(ano):
    if ano in RENDA_FLAVIO_IR:
        return RENDA_FLAVIO_IR[ano]
    tot = sum(subsidio(date(ano, m, 1)) for m in range(1, 13) if date(2003, 2, 1) <= date(ano, m, 1) <= FIM)
    if ano < 2026:
        tot += subsidio(date(ano, 12, 1))      # 13º
    return tot


def liquido_flavio(ano, P):
    f = P['liquido_alerj'] if ano < 2019 else P['liquido_senado']
    if ano == 2019:
        f = (P['liquido_alerj'] + 11 * P['liquido_senado']) / 12
    return bruto_flavio(ano) * f


def bruto_fernanda(ano):
    if ano < 2010:
        return 0.0
    if ano in RENDA_FERNANDA_IR:
        return RENDA_FERNANDA_IR[ano]
    return FERNANDA_MENSAL_2021 * (8 if ano == 2026 else 13)


def meses(ano):
    return 11 if ano == 2003 else (MESES_2026 if ano == 2026 else 12)


def dieese(ano):
    return (DIEESE[ano - 1] + DIEESE[ano]) / 2 if ano - 1 in DIEESE else DIEESE[ano]


def custo_vida(ano, cen, P):
    """Cenário 1: o salário mínimo necessário do DIEESE para o tamanho da família (o mínimo para viver).
    Na conta do DIEESE, 2 adultos + 2 crianças valem 3 adultos: solteiro = 1/3, casal = 2/3, família de quatro = 1.
    Cenário 2: o 1 mais os gastos documentados na denúncia (escola e domésticas desde 2014, plano de saúde desde 2013,
    IPTU desde 2010); de 2003 a 2009, solteiro, mais 2/3 do DIEESE para moradia e transporte.
    Cenário 3: o 2 vezes 1,5 (viagens, carros, condomínio, restaurantes: gastos que o MP deixou de fora)."""
    n = meses(ano)
    ae = 1 / 3 if ano < 2010 else (2 / 3 if ano < 2014 else 1.0)
    base = dieese(ano) * ae * n
    if cen == 1:
        return base
    if ano < 2010:
        extra = dieese(ano) * (2 / 3) * n
    else:
        k = dieese(ano) / dieese(CUSTO_DOC_ANO)
        m = CUSTO_DOC['iptu'] + (CUSTO_DOC['saude'] if ano >= 2013 else 0)
        if ano >= 2014:
            m += CUSTO_DOC['escola'] + CUSTO_DOC['domesticas']
        extra = m * k * n
    tot = base + extra
    return tot * P['alto_padrao'] if cen == 3 else tot


def taxa(ano, ret, P):
    if ret == 'zero':
        return 0.0
    t = (IPCA if ret == 'ipca' else CDI)[ano] / 100
    if ano == 2026:
        t *= MESES_2026 / 9
    if ret == 'cdi_liq':
        t *= 1 - P['ir_aplicacao']
    if ano == 2003:
        t *= 11 / 12
    return t


POR_FORA = (2012, -638400.00, 'Dinheiro vivo "por fora" na compra dos apartamentos de Copacabana, se a tese do MP estiver certa', 'denúncia, pp. 31-35')


def serie(P, cen, ret, com_eventos):
    """com_eventos: 0 = só salários; 1 = com ganhos e perdas documentados; 2 = idem, mais o "por fora" da tese do MP"""
    ev = {}
    if com_eventos:
        for a, v, *_ in EVENTOS + ([POR_FORA] if com_eventos == 2 else []):
            ev[a] = ev.get(a, 0.0) + v
    rows, acc = [], 0.0
    for ano in range(2003, 2027):
        lf, le = liquido_flavio(ano, P), bruto_fernanda(ano) * P['liquido_fernanda']
        cv = custo_vida(ano, cen, P)
        sobra = lf + le - cv
        e = ev.get(ano, 0.0)
        r = taxa(ano, ret, P)
        rend = acc * r + (sobra + e) * r / 2        # sobra do ano entra ao longo do ano: meio ano de rendimento
        acc += sobra + e + rend
        rows.append(dict(ano=ano, liq_flavio=round(lf), liq_fernanda=round(le), vida=round(cv), sobra=round(sobra),
                         eventos=round(e), rend=round(rend), acum=round(acc)))
    return rows


def na_data(rows, d):
    prev = 0
    for r in rows:
        if r['ano'] == d.year:
            frac = min(1.0, ((d - date(d.year, 1, 1)).days + 1) / 365) if d.year != 2026 else 1.0
            return prev + (r['acum'] - prev) * frac
        prev = r['acum']
    return prev


# ================================================================ 2019 a agosto de 2026: o dinheiro do senador
def caixa_senado(P, cen, venda_barra=1961000.0, parcelas=True, outras_vendas=0.0, outras_rendas=0.0, ret='cdi_liq'):
    """Fontes e usos de dinheiro entre jan/2019 e ago/2026. Devolve (fontes, usos, falta); itens = (id, nome, valor, fonte)."""
    anos = range(2019, 2027)
    sal_f = sum(liquido_flavio(a, P) for a in anos)
    sal_e = sum(bruto_fernanda(a) * P['liquido_fernanda'] for a in anos)
    vida = sum(custo_vida(a, cen, P) for a in anos)
    # rendimento: aplicações de 2018 rendendo em 2019-2020 e metade do saldo final de 2026 rendendo em 2025-2026
    rend = 558200.0 * ((1 + taxa(2019, ret, P)) * (1 + taxa(2020, ret, P)) - 1) + 0.5 * 1771263.03 * (taxa(2025, ret, P) + taxa(2026, ret, P))
    fontes = [
        ('aplic2018', 'Aplicações declaradas em 2018', 558200.00, 'TSE 2018 (Brasil de Fato, 2/3/2021)'),
        ('sal_f', 'Salário líquido de senador, fev/2019 a ago/2026', sal_f, 'Subsídio do Senado, 73,5% líquido'),
        ('sal_e', 'Renda líquida de Fernanda no período', sal_e, 'R$ 8.650 por mês, 85% líquido (Poder360, 1/6/2022)'),
        ('loja', 'Loja de chocolates: transferências a Flávio, out/2020 a mar/2021', 909000.00, 'Estadão (Jornal de Brasília, 10/11/2023)'),
        ('barra', 'Venda do apartamento da Barra (valor não divulgado)', venda_barra, 'Premissa: o que falta para a entrada, como diz Flávio'),
        ('brb', 'Financiamento do BRB', 3100000.00, 'Poder360, 1/6/2022; Estadão, 6/3/2021'),
        ('rend', 'Rendimento das aplicações (estimado)', rend, 'CDI líquido de IR'),
        ('sala_volvo', 'Sala comercial e Volvo declarados em 2018 (não aparecem em 2026)', 150000.00 + 66500.00, 'TSE 2018, pelo valor declarado'),
    ]
    if outras_vendas:
        fontes.append(('outras_vendas', 'Outras vendas de imóveis', outras_vendas, 'Premissa'))
    if outras_rendas:
        fontes.append(('outras_rendas', 'Outras rendas (advocacia, negócios)', outras_rendas, 'Premissa'))
    usos = [
        ('entrada', 'Entrada da casa no Lago Sul', 2870000.00, 'Escritura (Estadão, 6/3/2021)'),
        ('financiada', 'Parte financiada da casa', 3100000.00, 'Escritura'),
        ('itbi', 'ITBI e cartório da casa', 181111.85, 'Estadão, 6/3/2021'),
        ('extras', 'Seis pagamentos extras ao BRB até mar/2024 (quitação)', 3400000.00, 'Congresso em Foco e O Globo, 3 e 4/7/2024'),
    ]
    if parcelas:
        usos.append(('parcelas', 'Prestações de R$ 18,7 mil, mar/2021 a mar/2024 (36)', 18700.00 * 36, 'Estadão, 6/3/2021; número de prestações estimado'))
    usos += [
        ('aplic2026', 'Aplicações e contas declaradas em 2026', 1771263.03, 'TSE 2026: fundo, contas, poupança e CDB'),
        ('cotas', 'Cotas de empresas declaradas em 2026', 56249.00, 'TSE 2026'),
        ('veiculo', 'Veículo declarado em 2026 (ano 2014)', 133000.00, 'TSE 2026'),
        ('vida', 'Custo de vida da família no período', vida, f'Cenário {cen} desta conta'),
    ]
    falta = sum(i[2] for i in usos) - sum(i[2] for i in fontes)
    return fontes, usos, falta


# ================================================================ 2003 a 2006: o primeiro mandato
def primeiro_mandato(P, cen, ret):
    rows = serie(P, cen, ret, 0)
    d = date(2006, 7, 5)
    return na_data(rows, d), 385000.0


if __name__ == '__main__':
    P = PREMISSAS
    print('Salário líquido somado de Flávio, 2003-2026: R$ {:,.0f}'.format(sum(liquido_flavio(a, P) for a in range(2003, 2027))))
    print('Renda líquida somada de Fernanda, 2010-2026: R$ {:,.0f}'.format(sum(bruto_fernanda(a) * P['liquido_fernanda'] for a in range(2003, 2027))))
    for cen in (1, 2, 3):
        print(f'Custo de vida somado, cenário {cen}: R$ {sum(custo_vida(a, cen, P) for a in range(2003, 2027)):,.0f}')
    print('Eventos documentados, saldo: R$ {:,.0f}'.format(sum(v for _, v, *_ in EVENTOS)))

    print('\n== Quanto daria para ter em ago/2026 (máximo, se tudo o que sobrou fosse guardado) x R$ 8,19 milhões declarados')
    grid = {}
    for ev in (0, 1, 2):
        for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
            linha = []
            for cen in (1, 2, 3):
                rows = serie(P, cen, ret, ev)
                v = rows[-1]['acum']
                grid[f'{ev}-{ret}-{cen}'] = rows
                linha.append(v)
            print(f"eventos={ev} rend={ret:8} " + '  '.join(f'c{c}: {v/1e6:5.2f} mi ({(v-8186555.83)/1e6:+5.2f})' for c, v in zip((1, 2, 3), linha)))

    print('\n== Primeiro mandato: declarado em 2006 x máximo juntado até jul/2006')
    for ret in ('zero', 'ipca', 'cdi_liq', 'cdi'):
        print(ret, '  '.join(f'c{c}: {primeiro_mandato(P, c, ret)[0]:,.0f}' for c in (1, 2, 3)), '| declarado 385.000')

    print('\n== 2019 a ago/2026: dinheiro que falta para fechar a conta')
    for cen in (1, 2, 3):
        f, u, falta = caixa_senado(P, cen)
        print(f'cenário {cen}: fontes {sum(i[2] for i in f):,.0f} | usos {sum(i[2] for i in u):,.0f} | falta {falta:,.0f}')
    f, u, falta = caixa_senado(P, 2)
    for _i, n, v, src in f: print(f'  + {v:>12,.0f}  {n}  [{src}]')
    for _i, n, v, src in u: print(f'  - {v:>12,.0f}  {n}  [{src}]')
    f2, u2, falta2 = caixa_senado(P, 1, parcelas=False)
    print(f'mais favorável (cenário 1, sem prestações mensais): falta {falta2:,.0f}')

    json.dump(dict(premissas=P, grid=grid, tse=[(a, d.isoformat(), v, s) for a, d, v, s in TSE],
                   eventos=EVENTOS,
                   caixa={c: caixa_senado(P, c) for c in (1, 2, 3)},
                   caixa_sem_parcelas={c: caixa_senado(P, c, parcelas=False) for c in (1, 2, 3)},
                   primeiro={f'{ret}-{c}': primeiro_mandato(P, c, ret)[0] for ret in ('zero', 'ipca', 'cdi_liq', 'cdi') for c in (1, 2, 3)}),
              open(os.path.join(HERE, 'dados.json'), 'w'), ensure_ascii=False, indent=1, default=str)
