"""Monta data/content.json do guia do cargo na Câmara: textos e trechos marcados de cada ponto.

Uso:  python3 -I ferramentas/montar_conteudo.py
Precisa de data/boxes e data/paginas.json (gerados por ferramentas/preparar_documentos.py). Cada trecho é
achado pelas palavras da página (F: da primeira à última palavra) ou pelas linhas (Y: faixas de altura, nas
páginas escaneadas). Os retângulos ficam em pontos, com origem no alto da página, como no visualizador.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAG = json.load(open(os.path.join(ROOT, 'data/paginas.json'), encoding='utf-8'))
_B = {}


def words(d, p):
    if (d, p) not in _B:
        _B[(d, p)] = json.load(open(os.path.join(ROOT, f'data/boxes/{d}/p{p:03d}.json'), encoding='utf-8'))['words']
    return _B[(d, p)]


def _lines(ws):
    ws = sorted(ws, key=lambda w: (w[2] + w[4]) / 2)
    out = []
    for w in ws:
        cy = (w[2] + w[4]) / 2
        if out and abs(cy - out[-1][0]) < max(3, (w[4] - w[2]) * 0.45):
            out[-1][1].append(w)
        else:
            out.append([cy, [w]])
    return [sorted(l, key=lambda w: w[1]) for _, l in out]


def _box(l):
    return [round(min(w[1] for w in l), 1), round(min(w[2] for w in l), 1), round(max(w[3] for w in l), 1), round(max(w[4] for w in l), 1)]


def F(d, p, first, last, y=(0, 9999)):
    """trecho da palavra `first` até a palavra `last`, dentro da faixa de altura y (um retângulo por linha)"""
    ls = _lines([w for w in words(d, p) if y[0] <= w[2] <= y[1]])
    flat = [w for l in ls for w in l]
    i = next(k for k, w in enumerate(flat) if w[0].startswith(first))
    j = next(k for k in range(i, len(flat)) if flat[k][0].endswith(last))
    keep = {id(w) for w in flat[i:j + 1]}
    rs = [_box([w for w in l if id(w) in keep]) for l in ls if any(id(w) in keep for w in l)]
    assert rs, (d, p, first, last)
    return {'d': d, 'p': p, 'r': rs}


def Y(d, p, *faixas, x=(0, 9999), recuo=None, junta=False):
    """linhas inteiras dentro das faixas de altura (para páginas escaneadas). junta=True: o OCR de um scan torto às
    vezes parte uma linha em duas; as partes que se sobrepõem na altura viram um retângulo só. recuo=(de, até, x):
    linhas que começam entre `de` e `até` passam a começar em `x` (o OCR às vezes perde o número do item)."""
    rs = []
    for a, b in faixas:
        ws = [w for w in words(d, p) if a <= (w[2] + w[4]) / 2 <= b and x[0] <= (w[1] + w[3]) / 2 <= x[1]
              and w[4] - w[2] >= 3 and w[3] - w[1] >= 2]
        rs += [_box(l) for l in _lines(ws)]
    assert rs, (d, p, faixas)
    rs.sort(key=lambda r: r[1])
    grupos = []
    for r in rs:
        g = grupos[-1] if grupos else None
        if junta and g and min(g[-1][3], r[3]) - max(g[-1][1], r[1]) >= 0.4 * min(g[-1][3] - g[-1][1], r[3] - r[1]):
            g.append(r)
        else:
            grupos.append([r])
    out = []
    for g in grupos:
        x0 = min(r[0] for r in g)
        if recuo and recuo[0] <= x0 <= recuo[1]:
            x0 = recuo[2]
        out.append([round(x0, 1), round(sum(r[1] for r in g) / len(g), 1), round(max(r[2] for r in g), 1), round(sum(r[3] for r in g) / len(g), 1)])
    return {'d': d, 'p': p, 'r': out}


def join(*refs):
    """junta trechos da mesma página num só item"""
    out = []
    for r in refs:
        o = next((x for x in out if x['d'] == r['d'] and x['p'] == r['p']), None)
        if o:
            o['r'] += r['r']
        else:
            out.append({'d': r['d'], 'p': r['p'], 'r': list(r['r'])})
    return out


# ---------- trechos usados mais de uma vez ----------
NOMEACAO = F('b2000', 12, 'FLÁVIO', '15/12/2000).', (170, 252))
NOM_DATA = F('b2000', 12, 'Em', '15/12/2000).', (225, 252))
ANA_SAI = F('b2000', 8, 'ANA', '15/12/2000).', (380, 452))
ANA_ENTRA = F('b1998', 1, 'ANA', '11/11/98).', (420, 499))
SAIDA = F('b2002', 5, 'Exonerar,', '26/07/2002).', (676, 785))
SAIDA_DATA = F('b2002', 5, 'Em', '26/07/2002).', (770, 785))
SAIDA_PEDIDO = F('b2002', 5, 'Exonerar,', 'pedido,', (676, 690))
SAIDA_JUNHO = F('b2002', 5, 'a', 'ano.', (758, 785))
ATO_TITULO = Y('ato', 2, (64, 88), (140, 190), junta=True)
ATO_DATA = Y('ato', 2, (545, 567), junta=True)
ATR_TITULO = Y('ato', 8, (285, 299))
ATR_I_II = Y('ato', 8, (317, 349), recuo=(140, 200, 143.5), junta=True)
ATR_III_IV = Y('ato', 8, (352, 414), recuo=(140, 200, 143.5), junta=True)
ATR_V_VI = Y('ato', 8, (417, 465), recuo=(140, 200, 143.5), junta=True)
ATR_RESTO = Y('ato', 8, (466, 689), recuo=(140, 200, 143.5), junta=True)
ONDE = Y('ato', 13, (471, 504))
NASC_ALERJ = F('alerj', 1, 'NASCIMENTO', '1981', (196, 209))
NASC_DIPLOMA = Y('diplomas', 1, (291, 309.5))
DIREITO_ALERJ = F('alerj', 1, 'Bacharel', 'RJ.', (386, 394))
POS_UFRJ = F('alerj', 1, 'Pós-graduação', 'RJ.', (394, 401))
ESTAGIO = F('alerj', 1, 'Defensoria', 'Penitenciário)', (430, 445))
CARGOS = F('alerj', 1, 'Cargos', 'Familiar', (291, 358))
VIDA_PUBLICA = F('alerj', 1, 'Ingressou', 'Bolsonaro.', (466, 481))
DEP_2003 = F('alerj', 1, 'Deputado', '2007', (298, 306))
WAYBACK_ALERJ = F('alerj', 1, 'The', 'PerfilDeputa…', (36, 43))
DIPLOMA_DIREITO = Y('diplomas', 1, (185, 256))
DIPLOMA_CONCLUSAO = Y('diplomas', 1, (212, 229))
IUPERJ = Y('diplomas', 2, (205, 250), (255, 288), (289, 323), (353, 388), x=(80, 700))
FGV = Y('diplomas', 3, (316, 348), (366, 380))
SENADO_POS = F('senado', 1, 'bacharel', 'políticas.', (195, 226))
SENADO_MANDATOS = F('senado', 1, 'Exerceu', 'estadual.', (276, 290))

BBC = {'name': 'BBC News Brasil: “Como Flávio Bolsonaro ocupou um cargo na Câmara dos Deputados enquanto fazia faculdade e estágio no Rio” (23/1/2019)',
       'short': 'BBC News Brasil, 23/1/2019', 'url': 'https://www.bbc.com/portuguese/brasil-46828487'}
BAND = {'name': 'Band: “UFRJ nega pós de Flávio citada em perfis oficiais; campanha cita equívoco” (12/8/2026)',
        'short': 'Band, 12/8/2026', 'url': 'https://www.band.com.br/politica/eleicoes/2026/ufrj-nega-pos-de-flavio-citada-em-perfis-oficiais-campanha-cita-equivoco-202608121549'}
P360 = {'name': 'Poder360: “Flávio divulga diplomas para mostrar formação acadêmica” (13/8/2026)',
        'short': 'Poder360, 13/8/2026', 'url': 'https://www.poder360.com.br/poder-eleicoes-2026/flavio-divulga-diplomas-para-mostrar-formacao-academica/'}
X_POST = {'name': 'Publicação de Flávio Bolsonaro no X (12/8/2026)', 'short': 'X, 12/8/2026', 'url': 'https://x.com/FlavioBolsonaro/status/2087721700053889062'}


ALEG = {'aleg': 'afirmação que está no documento, sem ser registro oficial', 'alegCurto': 'não é registro oficial',
        'alegItem': 'afirmação, não registro oficial', 'aleg1': 'afirmação', 'alegN': 'afirmações'}


def doc(id_, color, chip, label, short, nome, sobre, when, source, src, origem, pl=False, names=None, nopg=False):
    """textos de cada documento, usados nos botões, no visualizador e nos textos de compartilhamento.
    nome: o documento com artigo ("o boletim da Câmara de 27/12/2000"); short: sem artigo, para "short, p. 3384"."""
    art, resto = nome.split(' ', 1)
    em = {'o': 'no', 'a': 'na', 'os': 'nos', 'as': 'nas'}[art] + ' ' + resto
    de = {'o': 'do', 'a': 'da', 'os': 'dos', 'as': 'das'}[art] + ' ' + resto
    d = {'id': id_, 'color': color, 'chip': chip, 'label': label, 'short': short,
         'what': nome, 'em': em, 'de': de, 'voz': 'Segundo ' + nome, 'sujeito': nome, 'pl': pl,
         'sobre': sobre, 'when': when, 'source': source, 'src': src, 'origem': origem,
         'n': PAG[id_]['n'], 'labels': PAG[id_]['labels'], 'sizes': PAG[id_]['sizes']}
    if names:
        d['names'] = {str(k): v for k, v in names.items()}
    if nopg:
        d['nopg'] = True                     # nos textos, sem "p. N" (os diplomas não têm número de página)
    d.update(ALEG)
    return d


DOCS = [
    doc('b2000', '#2f6fa3', 'Boletim 2000', 'Boletim Administrativo da Câmara nº 246, de 27/12/2000',
        'boletim da Câmara de 27/12/2000', 'o boletim da Câmara de 27/12/2000',
        'Boletim Administrativo da Câmara dos Deputados de 27/12/2000, com a nomeação de Flávio Bolsonaro e a exoneração de Ana Cristina Siqueira Valle.',
        'Câmara, dezembro de 2000',
        'Boletim Administrativo da Câmara dos Deputados nº 246, de 27/12/2000',
        'boletim da Câmara de 27/12/2000',
        'https://www.camara.leg.br/boletimadm/2000/Ba20001227.pdf'),
    doc('b1998', '#6b8fb8', 'Boletim 1998', 'Boletim Administrativo da Câmara nº 215, de 13/11/1998',
        'boletim da Câmara de 13/11/1998', 'o boletim da Câmara de 13/11/1998',
        'Boletim Administrativo da Câmara dos Deputados de 13/11/1998, com a nomeação de Ana Cristina Siqueira Valle.',
        'Câmara, novembro de 1998',
        'Boletim Administrativo da Câmara dos Deputados nº 215, de 13/11/1998',
        'boletim da Câmara de 13/11/1998',
        'https://www.camara.leg.br/boletimadm/1998/Ba19981113.pdf'),
    doc('b2002', '#b0781a', 'Boletim 2002', 'Boletim Administrativo da Câmara nº 145, de 31/7/2002',
        'boletim da Câmara de 31/7/2002', 'o boletim da Câmara de 31/7/2002',
        'Boletim Administrativo da Câmara dos Deputados de 31/7/2002, com a exoneração de Flávio Bolsonaro, a pedido.',
        'Câmara, julho de 2002',
        'Boletim Administrativo da Câmara dos Deputados nº 145, de 31/7/2002',
        'boletim da Câmara de 31/7/2002',
        'https://www.camara.leg.br/boletimadm/2002/Ba20020731.pdf'),
    doc('ato', '#a8452b', 'Ato da Mesa', 'Ato da Mesa nº 45, de 1996, no Diário da Câmara de 6/11/1996 (suplemento)',
        'Diário da Câmara de 6/11/1996', 'o Ato da Mesa nº 45, de 1996',
        'Ato da Mesa nº 45, de 1996, que define as tarefas de cada cargo em comissão da Câmara, publicado no Diário da Câmara de 6/11/1996.',
        'Câmara, 1996',
        'Ato da Mesa nº 45, de 17/10/1996, no Diário da Câmara dos Deputados de 6/11/1996 (suplemento)',
        'Diário da Câmara de 6/11/1996',
        'https://imagem.camara.leg.br/Imagem/d/pdf/DCD06NOV1996SUP.pdf',
        names={1: 'capa do Diário da Câmara'}),
    doc('alerj', '#5f7a2e', 'Perfil na Alerj', 'Perfil de Flávio Bolsonaro no site da Alerj (cópia de 30/1/2019)',
        'perfil de Flávio na Alerj', 'o perfil de Flávio no site da Alerj',
        'Perfil oficial de Flávio Bolsonaro no site da Assembleia Legislativa do Rio, como estava em 30/1/2019 (cópia do Wayback Machine).',
        'Alerj, 2019',
        'perfil de Flávio Bolsonaro no site da Alerj, cópia do Wayback Machine de 30/1/2019',
        'perfil de Flávio na Alerj (cópia de 30/1/2019)',
        'https://web.archive.org/web/20190130081742/http://www.alerj.rj.gov.br/Deputados/PerfilDeputado/275?Legislatura=18'),
    doc('senado', '#7a4fa3', 'Agência Senado', 'Agência Senado, “Flávio Bolsonaro (PSL)”, 18/1/2019 (cópia de 3/2/2019)',
        'texto da Agência Senado', 'o texto da Agência Senado de 18/1/2019',
        'Texto da Agência Senado de 18/1/2019 que apresenta o senador eleito Flávio Bolsonaro (cópia do Wayback Machine de 3/2/2019).',
        'Senado, 2019',
        'texto da Agência Senado de 18/1/2019, cópia do Wayback Machine de 3/2/2019',
        'texto da Agência Senado de 18/1/2019',
        'https://web.archive.org/web/20190203071437/https://www12.senado.leg.br/noticias/materias/2019/01/18/flavio-bolsonaro-psl'),
    doc('diplomas', '#3f7f86', 'Diplomas', 'Diplomas publicados por Flávio Bolsonaro no X (12/8/2026)',
        'diplomas publicados por Flávio', 'os diplomas publicados por Flávio',
        'Os três diplomas que Flávio Bolsonaro publicou no X em 12/8/2026: Direito, especialização em Políticas Públicas e MBA.',
        'publicados em 2026',
        'diplomas publicados por Flávio Bolsonaro no X em 12/8/2026',
        'diplomas publicados por Flávio (12/8/2026)',
        'https://x.com/FlavioBolsonaro/status/2087721700053889062',
        pl=True, nopg=True, names={1: 'diploma de Direito', 2: 'diploma da especialização', 3: 'diploma do MBA'}),
]

THEMES = [
    {'id': 'nomeacao', 'title': 'A nomeação', 'color': '#2f6fa3',
     'lay': 'Como Flávio entrou no cargo, aos 19 anos, e de quem era o posto antes.',
     'key': ['nom-flavio', 'nom-data', 'nom-idade', 'nom-ana-sai', 'nom-ana-entra']},
    {'id': 'tarefas', 'title': 'O que o cargo exige', 'color': '#a8452b',
     'lay': 'As 15 tarefas do assistente técnico de gabinete e onde esse cargo existe.',
     'key': ['tar-ato', 'tar-plenario', 'tar-votacoes', 'tar-onde']},
    {'id': 'rio', 'title': 'Enquanto isso, no Rio', 'color': '#5f7a2e',
     'lay': 'A faculdade e o estágio que o próprio currículo dele registra no mesmo período.',
     'key': ['rio-direito', 'rio-campus', 'rio-estagio', 'rio-sobreposicao']},
    {'id': 'curriculo', 'title': 'O currículo e o que ficou de fora', 'color': '#7a4fa3',
     'lay': 'O cargo que não aparece no currículo e a pós que a UFRJ diz não ter registro.',
     'key': ['cur-cargos', 'cur-ufrj', 'cur-senado', 'cur-diplomas']},
    {'id': 'saida', 'title': 'A saída e depois', 'color': '#b0781a',
     'lay': 'Como ele deixou o cargo e o que veio em seguida.',
     'key': ['sai-pedido', 'sai-ato', 'sai-tempo', 'sai-deputado']},
]

ROTEIRO = [
    # ---------- a nomeação ----------
    {'id': 'nom-flavio', 'theme': 'nomeacao', 'label': 'documentado',
     'title': 'Flávio é nomeado para a liderança do PPB',
     'text': 'O ato nomeia Flávio Nantes Bolsonaro para exercer, no gabinete do líder do Partido Progressista Brasileiro, o PPB, o cargo de assistente técnico de gabinete (CNE-09) do quadro de pessoal da Câmara.',
     'quote': 'FLÁVIO NANTES BOLSONARO para exercer, no Gabinete do Líder do Partido Progressista Brasileiro, o cargo de Assistente Técnico de Gabinete, CNE-09',
     'refs': [NOMEACAO]},
    {'id': 'nom-data', 'theme': 'nomeacao', 'label': 'documentado',
     'title': 'O ato é de 14 de dezembro de 2000',
     'text': 'A nomeação tem data de 14/12/2000 e saiu no Diário da Câmara do dia seguinte. O boletim de 27/12/2000 reproduz o ato, na página 3384.',
     'refs': [NOM_DATA]},
    {'id': 'nom-idade', 'theme': 'nomeacao', 'label': 'documentado',
     'title': 'Ele tinha 19 anos',
     'text': 'Flávio nasceu em 30 de abril de 1981, data que aparece no perfil dele na Alerj e no diploma que ele publicou. Ao ser nomeado, tinha 19 anos.',
     'refs': [NASC_ALERJ, NASC_DIPLOMA]},
    {'id': 'nom-ana-sai', 'theme': 'nomeacao', 'label': 'documentado',
     'title': 'Na mesma data, Ana Cristina sai do mesmo cargo',
     'text': 'O mesmo boletim exonera Ana Cristina Siqueira Valle Mendes do cargo de assistente técnico de gabinete, CNE-09, que ela exercia no gabinete do líder do PPB. A data é a mesma da nomeação de Flávio: 14/12/2000.',
     'quote': 'ANA CRISTINA SIQUEIRA VALLE MENDES (…) do cargo de Assistente Técnico de Gabinete, CNE-09 (…) que exerce no Gabinete do Líder do Partido Progressista Brasileiro. Em 14/12/2000.',
     'refs': [ANA_SAI]},
    {'id': 'nom-ana-entra', 'theme': 'nomeacao', 'label': 'documentado',
     'title': 'Ana Cristina estava no cargo desde 1998',
     'text': 'Ana Cristina Siqueira Valle Mendes foi nomeada para o mesmo cargo, no gabinete do líder do PPB, em 10/11/1998. Segundo a BBC, ela era então mulher de Jair Bolsonaro (fora deste documento).',
     'refs': [ANA_ENTRA]},
    {'id': 'nom-mesmo-posto', 'theme': 'nomeacao', 'label': 'interpretação',
     'title': 'O posto passou da então mulher do pai para o filho',
     'text': 'Os atos mostram o mesmo cargo, no mesmo gabinete, saindo de Ana Cristina e indo para Flávio na mesma data. Contratar parentes ainda não era proibido: a proibição veio em 2008, com uma súmula do STF.',
     'refs': [ANA_SAI, NOMEACAO]},
    # ---------- o que o cargo exige ----------
    {'id': 'tar-ato', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'Um ato da Mesa define as tarefas de cada cargo',
     'text': 'O Ato da Mesa nº 45, de 17/10/1996, estabelece as atribuições dos cargos em comissão e das funções comissionadas da Câmara, listadas no anexo. Saiu no Diário da Câmara de 18/10/1996 e de novo no suplemento de 6/11/1996, que é a cópia deste guia.',
     'refs': [join(ATO_TITULO, ATO_DATA)[0]]},
    {'id': 'tar-plenario', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'Acompanhar o plenário e as comissões',
     'text': 'São 15 as tarefas do assistente técnico de gabinete. As duas primeiras: prestar assistência regimental aos deputados e acompanhar as reuniões plenárias e de comissões.',
     'quote': 'I - prestar assistência regimental aos deputados; II - acompanhar reuniões plenárias e de comissões',
     'refs': [join(ATR_TITULO, ATR_I_II)[0]]},
    {'id': 'tar-votacoes', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'Orientar os deputados nas votações',
     'text': 'Ele deve orientar e assistir os deputados nas votações do plenário e das comissões, de acordo com a posição da liderança, e acompanhar o resultado das votações.',
     'quote': 'III - orientar e assistir os deputados nas votações de matérias no Plenário e nas Comissões, de acordo com o posicionamento da Liderança',
     'refs': [ATR_III_IV]},
    {'id': 'tar-pauta', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'Acompanhar os prazos e a pauta do dia',
     'text': 'Também deve acompanhar os prazos de emendas e informar aos deputados da bancada o que está na pauta da Ordem do Dia.',
     'refs': [ATR_V_VI]},
    {'id': 'tar-gabinete', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'E o trabalho de gabinete',
     'text': 'As outras tarefas são de gabinete: ajudar o chefe de gabinete, preparar expedientes, examinar processos, fazer relatórios das reuniões e operar o computador.',
     'refs': [ATR_RESTO]},
    {'id': 'tar-onde', 'theme': 'tarefas', 'label': 'documentado',
     'title': 'Onde esse cargo existe: na Câmara',
     'text': 'Na parte “Informações”, publicada com o ato, o assistente técnico de gabinete (CNE-09) aparece como cargo “encontrado na administração e nas lideranças” da Câmara.',
     'quote': 'ASSISTENTE TÉCNICO DE GABINETE - CNE-09 . encontrado na administração e nas lideranças.',
     'refs': [ONDE]},
    {'id': 'tar-brasilia', 'theme': 'tarefas', 'label': 'interpretação',
     'title': 'Tarefas que só se cumprem dentro da Câmara',
     'text': 'Acompanhar sessões do plenário, reuniões de comissões e votações exige estar no prédio da Câmara, em Brasília. A Câmara disse à BBC que esse tipo de cargo não pode ser exercido em outra cidade (veja Fatos extras).',
     'refs': [ATR_I_II, ATR_III_IV]},
    # ---------- enquanto isso, no Rio ----------
    {'id': 'rio-direito', 'theme': 'rio', 'label': 'documentado',
     'title': 'O curso de Direito na Candido Mendes',
     'text': 'O perfil de Flávio no site da Alerj lista o bacharelado em Direito pela Universidade Cândido Mendes, no Rio de Janeiro.',
     'refs': [DIREITO_ALERJ]},
    {'id': 'rio-campus', 'theme': 'rio', 'label': 'documentado',
     'title': 'No campus Centro, no Rio, até 2006',
     'text': 'O diploma que Flávio publicou registra a conclusão do curso de Direito em 8/2/2006, no campus Centro, no Rio. Segundo a BBC, ele começou o curso em 2000 (fora deste documento).',
     'refs': [DIPLOMA_DIREITO]},
    {'id': 'rio-estagio', 'theme': 'rio', 'label': 'documentado',
     'title': 'Estágio na Defensoria, de agosto de 2000 a outubro de 2001',
     'text': 'O mesmo perfil lista um estágio na Defensoria Pública Geral do Estado do Rio de Janeiro, no Núcleo de Sistema Penitenciário, de agosto de 2000 a outubro de 2001.',
     'quote': 'Defensoria Pública Geral do Estado do Rio de Janeiro - DPGE Ago 2000 / Out 2001 (Núcleo de Sistema Penitenciário)',
     'refs': [ESTAGIO]},
    {'id': 'rio-sobreposicao', 'theme': 'rio', 'label': 'interpretação',
     'title': 'Dez meses de cargo, faculdade e estágio ao mesmo tempo',
     'text': 'Pelas datas dos documentos, de dezembro de 2000 a outubro de 2001 Flávio tinha o cargo em Brasília, a faculdade no Rio e o estágio na Defensoria, também no Rio. Cargo e faculdade seguiram juntos até junho de 2002.',
     'refs': [NOMEACAO, ESTAGIO, SAIDA_JUNHO]},
    {'id': 'rio-distancia', 'theme': 'rio', 'label': 'interpretação',
     'title': 'A conta que não fecha',
     'text': 'Os documentos não mostram onde ele estava a cada dia, nem provam faltas. Mas ser nomeado e pago por um cargo com tarefas no plenário e nas comissões, enquanto o próprio currículo o coloca na faculdade e num estágio no Rio, a mais de 1.000 km, é o quadro que se costuma chamar de funcionário fantasma. Procurado pela BBC em 2019, ele não explicou como conciliava as atividades.',
     'refs': [ATR_I_II, join(DIREITO_ALERJ, ESTAGIO)[0]]},
    # ---------- o currículo ----------
    {'id': 'cur-cargos', 'theme': 'curriculo', 'label': 'documentado',
     'title': 'Nos cargos exercidos, só a Alerj',
     'text': 'Em “Cargos Exercidos”, o perfil da Alerj lista só os mandatos de deputado estadual (2003/2007 e 2007/2011) e as comissões que ele presidiu ou integrou. O cargo na Câmara dos Deputados não aparece.',
     'refs': [CARGOS]},
    {'id': 'cur-vida-publica', 'theme': 'curriculo', 'label': 'documentado',
     'title': '“Ingressou na vida pública” como deputado, diz o perfil',
     'text': 'Na parte “Atuação Parlamentar”, o perfil da Alerj diz que Flávio ingressou na vida pública como o deputado estadual mais jovem da legislatura 2003/2007. O cargo na Câmara, de 2000 a 2002, não é citado.',
     'quote': 'Ingressou na vida pública como o Deputado Estadual mais jovem da legislatura 2003/2007',
     'refs': [VIDA_PUBLICA]},
    {'id': 'cur-ufrj', 'theme': 'curriculo', 'label': 'documentado',
     'title': 'Uma pós em Ciências Políticas pela UFRJ',
     'text': 'O mesmo perfil lista uma pós-graduação em Ciências Políticas pela UFRJ. Em 12/8/2026, a UFRJ informou que não há registro de Flávio como aluno, e a campanha dele atribuiu a informação a um equívoco (fora deste documento).',
     'refs': [POS_UFRJ]},
    {'id': 'cur-senado', 'theme': 'curriculo', 'label': 'documentado',
     'title': 'O Senado repetiu a pós',
     'text': 'Ao apresentar o senador eleito, em 18/1/2019, a Agência Senado o descreveu como “bacharel em direito e pós-graduado em ciências políticas”, e o texto também não cita o cargo na Câmara. Em 12/8/2026, segundo a Band, a pós já tinha sido corrigida no site (fora deste documento).',
     'refs': [SENADO_POS]},
    {'id': 'cur-diplomas', 'theme': 'curriculo', 'label': 'documentado',
     'title': 'Os diplomas que ele publicou',
     'text': 'Em 12/8/2026, Flávio publicou três diplomas: Direito (Universidade Candido Mendes, 2006), especialização em Políticas Públicas (Iuperj, da Candido Mendes, com a Escola de Políticas Públicas e Governo, 2012) e MBA em Empreendedorismo e Desenvolvimento de Novos Negócios (FGV, 2015). Nenhum é da UFRJ.',
     'refs': [DIPLOMA_DIREITO, IUPERJ, FGV]},
    # ---------- a saída ----------
    {'id': 'sai-pedido', 'theme': 'saida', 'label': 'documentado',
     'title': 'Exonerado a pedido, a partir de 28 de junho de 2002',
     'text': 'O ato exonera Flávio, a pedido, do cargo de assistente técnico de gabinete que ele exercia no gabinete do líder do PPB, a partir de 28 de junho de 2002.',
     'quote': 'Exonerar, a pedido (…) FLÁVIO NANTES BOLSONARO (…) do cargo de Assistente Técnico de Gabinete, CNE-09 (…) a partir de 28 de junho do corrente ano.',
     'refs': [SAIDA]},
    {'id': 'sai-ato', 'theme': 'saida', 'label': 'documentado',
     'title': 'O ato é de 24/7/2002 e saiu no Diário Oficial',
     'text': 'A exoneração tem data de 24/7/2002 e foi publicada no Diário Oficial da União de 26/7/2002. O boletim de 31/7/2002 reproduz o ato, na página 1879.',
     'refs': [SAIDA_DATA]},
    {'id': 'sai-tempo', 'theme': 'saida', 'label': 'documentado',
     'title': 'Um ano e meio no cargo',
     'text': 'Entre a nomeação, em 14/12/2000, e a exoneração, que vale a partir de 28/6/2002, foram um ano, seis meses e catorze dias.',
     'refs': [NOM_DATA, SAIDA_JUNHO]},
    {'id': 'sai-deputado', 'theme': 'saida', 'label': 'documentado',
     'title': 'Meses depois, deputado estadual',
     'text': 'O perfil da Alerj registra o primeiro mandato de Flávio como deputado estadual, na legislatura 2003/2007. Ele foi eleito em outubro de 2002, pelo PPB (fora deste documento).',
     'refs': [DEP_2003]},
    {'id': 'sai-formado', 'theme': 'saida', 'label': 'documentado',
     'title': 'A faculdade terminou em 2006, já com mandato',
     'text': 'Segundo o diploma, o curso de Direito foi concluído em 8/2/2006, quando Flávio já era deputado estadual.',
     'refs': [DIPLOMA_CONCLUSAO, DEP_2003]},
]
IDS = {r['id'] for r in ROTEIRO}
assert len(IDS) == len(ROTEIRO)
for t in THEMES:
    assert all(k in IDS for k in t['key']), t['id']

STORIES = [{
    'id': 'cargo', 'title': 'O cargo, em 2 minutos',
    'paras': [
        '<b>A nomeação.</b> Em 14 de dezembro de 2000, a Câmara dos Deputados nomeou Flávio Bolsonaro, então com 19 anos, assistente técnico de gabinete na liderança do PPB, o partido do pai. Na mesma data, exonerou do mesmo cargo Ana Cristina Siqueira Valle, então mulher de Jair Bolsonaro, que estava nele desde 1998.',
        '<b>O cargo.</b> As 15 tarefas do cargo, definidas por um ato da Mesa da Câmara, incluem acompanhar o plenário e as comissões e orientar os deputados nas votações. A Câmara disse à BBC que esse tipo de cargo não pode ser exercido fora de Brasília.',
        '<b>O Rio.</b> No mesmo período, Flávio cursava Direito na Candido Mendes, no Centro do Rio, e, segundo o próprio currículo na Alerj, estagiava na Defensoria Pública, de agosto de 2000 a outubro de 2001. Esse currículo não cita o cargo na Câmara. Ele saiu a pedido em 28 de junho de 2002 e, meses depois, foi eleito deputado estadual.',
        '<b>O que os documentos não mostram.</b> Onde ele estava a cada dia: a presença era registrada numa folha mensal, enviada pela liderança do partido. Procurado pela BBC em 2019, Flávio não quis responder (veja <a href="#extras">Fatos extras</a>).',
    ],
    'claims': [
        {'say': 'Isso é invenção', 'label': 'documentado',
         'doc': 'Os atos estão nos boletins da própria Câmara: a nomeação no de 27/12/2000 (p. 3384) e a saída, a pedido, no de 31/7/2002 (p. 1879).',
         'refs': [NOMEACAO, SAIDA]},
        {'say': 'Ele trabalhava do Rio', 'label': 'documentado',
         'doc': 'As tarefas do cargo incluem acompanhar o plenário e as comissões e orientar os deputados nas votações. O cargo existe “na administração e nas lideranças” da Câmara. Veja também Fatos extras.',
         'refs': [join(ATR_I_II, ATR_III_IV)[0], ONDE]},
        {'say': 'Ele trabalhava em Brasília normalmente', 'label': 'documentado',
         'doc': 'O perfil dele na Alerj lista um estágio na Defensoria Pública do Rio de agosto de 2000 a outubro de 2001. O diploma de Direito é do campus Centro, no Rio.',
         'refs': [ESTAGIO, DIPLOMA_DIREITO]},
        {'say': 'Foi uma nomeação como outra qualquer', 'label': 'documentado',
         'doc': 'Os dois atos têm a mesma data, 14/12/2000: Ana Cristina sai e Flávio entra no mesmo cargo, no mesmo gabinete.',
         'refs': [ANA_SAI, NOMEACAO]},
        {'say': 'Ele sempre declarou esse cargo', 'label': 'documentado',
         'doc': 'No perfil da Alerj, entre os cargos exercidos, só aparecem os mandatos de deputado estadual, e o texto diz que ele ingressou na vida pública como deputado.',
         'refs': [join(CARGOS, VIDA_PUBLICA)[0]]},
        {'say': 'O currículo oficial dele está certo', 'label': 'documentado',
         'doc': 'O perfil da Alerj listava uma pós em Ciências Políticas pela UFRJ. Entre os três diplomas que ele publicou em 2026 para mostrar a formação, nenhum é da UFRJ.',
         'refs': [POS_UFRJ, IUPERJ]},
    ],
}]

NUMBERS = [
    {'value': '19 anos', 'label': 'idade de Flávio quando foi nomeado', 'refs': [NOMEACAO, NASC_ALERJ]},
    {'value': '1 ano e 6 meses', 'label': 'no cargo, de 14/12/2000 a 28/6/2002', 'refs': [NOM_DATA, SAIDA_JUNHO]},
    {'value': '15', 'label': 'tarefas do cargo no Ato da Mesa nº 45, do plenário e das comissões ao trabalho de gabinete', 'refs': [join(ATR_TITULO, ATR_I_II, ATR_III_IV)[0]]},
    {'value': '10 meses', 'label': 'com cargo, faculdade e estágio ao mesmo tempo (dezembro de 2000 a outubro de 2001)', 'refs': [NOMEACAO, ESTAGIO]},
    {'value': 'R$ 56.548,63', 'label': 'pagos pelo cargo em 2001, segundo a declaração de Imposto de Renda citada pela BBC', 'refs': [], 'sources': [BBC]},
    {'value': 'mais de 1.000 km', 'label': 'entre Brasília e o Rio, quase uma hora e meia de voo, segundo a BBC', 'refs': [], 'sources': [BBC]},
]

TIMELINE = [
    {'date': '17/10/1996', 'title': 'A Mesa da Câmara define as tarefas dos cargos', 'label': 'documentado',
     'text': 'O Ato da Mesa nº 45 estabelece as atribuições dos cargos em comissão, entre eles o de assistente técnico de gabinete. Sai no Diário da Câmara no dia seguinte e de novo em 6/11/1996.',
     'refs': [join(ATO_TITULO, ATO_DATA)[0]]},
    {'date': '10/11/1998', 'title': 'Ana Cristina entra no cargo', 'label': 'documentado',
     'text': 'Ana Cristina Siqueira Valle é nomeada assistente técnica de gabinete na liderança do PPB.',
     'refs': [ANA_ENTRA]},
    {'date': '2000', 'title': 'Flávio começa a faculdade de Direito', 'label': 'reportagem',
     'text': 'Na Universidade Candido Mendes, no Centro do Rio, segundo a BBC.', 'refs': [], 'sources': [BBC]},
    {'date': 'agosto de 2000', 'title': 'Começa o estágio na Defensoria', 'label': 'documentado',
     'text': 'Segundo o perfil dele na Alerj, no Núcleo de Sistema Penitenciário da Defensoria Pública do Rio.',
     'refs': [ESTAGIO]},
    {'date': '14/12/2000', 'title': 'Ana Cristina sai, Flávio entra', 'label': 'documentado',
     'text': 'Na mesma data, a Câmara exonera Ana Cristina e nomeia Flávio, aos 19 anos, para o mesmo cargo, no mesmo gabinete.',
     'refs': [ANA_SAI, NOMEACAO]},
    {'date': '2001', 'title': 'O cargo rende R$ 56.548,63 no ano', 'label': 'reportagem',
     'text': 'Segundo a declaração de Imposto de Renda de Flávio, citada pela BBC: cerca de R$ 4.712 por mês.', 'refs': [], 'sources': [BBC]},
    {'date': 'outubro de 2001', 'title': 'Termina o estágio', 'label': 'documentado',
     'text': 'Segundo o perfil da Alerj. No LinkedIn, segundo a BBC, as datas eram outras: de março de 2001 a janeiro de 2002.',
     'refs': [ESTAGIO]},
    {'date': '28/06/2002', 'title': 'Flávio deixa o cargo, a pedido', 'label': 'documentado',
     'text': 'A exoneração vale a partir desta data. O ato é de 24/7/2002 e saiu no Diário Oficial da União em 26/7/2002.',
     'refs': [SAIDA]},
    {'date': 'outubro de 2002', 'title': 'Eleito deputado estadual', 'label': 'documentado',
     'text': 'Pelo PPB. O perfil da Alerj registra o mandato de 2003 a 2007.',
     'refs': [DEP_2003]},
    {'date': '08/02/2006', 'title': 'Conclui o curso de Direito', 'label': 'documentado',
     'text': 'No campus Centro da Universidade Candido Mendes, segundo o diploma.', 'refs': [DIPLOMA_CONCLUSAO]},
    {'date': '18/01/2019', 'title': 'Agência Senado: “pós-graduado em ciências políticas”', 'label': 'documentado',
     'text': 'O texto que apresenta o senador eleito diz que ele é pós-graduado em ciências políticas. Em 2026, a UFRJ informaria não ter registro dele como aluno.', 'refs': [SENADO_POS]},
    {'date': '23/01/2019', 'title': 'A BBC publica a reportagem', 'label': 'reportagem',
     'text': 'Flávio não quis responder às perguntas sobre o cargo.', 'refs': [], 'sources': [BBC]},
    {'date': '30/01/2019', 'title': 'O Wayback Machine guarda o perfil da Alerj', 'label': 'documentado',
     'text': 'A cópia mostra a faculdade, o estágio e a pós da UFRJ, e não o cargo na Câmara.',
     'refs': [join(WAYBACK_ALERJ, CARGOS)[0]]},
    {'date': '12/08/2026', 'title': 'A UFRJ nega a pós; Flávio publica os diplomas', 'label': 'reportagem',
     'text': 'A UFRJ informa que não há registro dele como aluno. À noite, Flávio publica três diplomas, nenhum da UFRJ.',
     'refs': [], 'sources': [BAND, P360]},
]

EXTRAS = [
    {'title': 'A Câmara: o cargo não pode ser exercido fora de Brasília', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Pela Lei de Acesso à Informação, a Câmara disse à BBC que os cargos de natureza especial, como o de Flávio, “têm por finalidade a prestação de serviços de assessoramento aos órgãos da Casa, em Brasília. Desse modo, não possuem a prerrogativa de exercerem suas atividades em outra cidade além da capital federal”.',
     'note': 'Quem pode trabalhar na base eleitoral, fora de Brasília, é outro cargo: o de secretário parlamentar.', 'sources': [BBC]},
    {'title': 'Um cargo de 40 horas por semana, com presença anotada uma vez por mês', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Segundo a BBC, o cargo era de 40 horas semanais. A presença de Flávio era registrada numa folha mensal, em vez de ponto diário: todo mês, a chefia da liderança do PPB enviava à Câmara um relatório com os dias em que ele trabalhou. Esse controle mais flexível é previsto nas normas da Câmara.',
     'note': '', 'sources': [BBC]},
    {'title': 'R$ 56.548,63 em 2001', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Segundo a declaração de Imposto de Renda que Flávio entregou à Justiça Eleitoral em 2002, o cargo rendeu R$ 56.548,63 em 2001: cerca de R$ 4.712 por mês, ou R$ 13,5 mil por mês em valores de janeiro de 2019, corrigidos pelo INPC.',
     'note': '', 'sources': [BBC]},
    {'title': 'Aulas de quatro a cinco horas por dia, com chamada', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Dois ex-professores e dois ex-alunos, que disseram ter sido colegas de Flávio em disciplinas da manhã, contaram à BBC que o curso de Direito da Candido Mendes tinha de quatro a cinco horas de aula por dia, em média, nos dois primeiros anos, com presença controlada por chamada.',
     'note': 'As disciplinas podiam ser cursadas de manhã, à tarde ou à noite, e a frequência mínima é de 75%. A universidade não informou em que turnos Flávio estudou.',
     'sources': [BBC]},
    {'title': 'Estágio voluntário, duas vezes por semana', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'A Defensoria Pública disse à BBC que não há registro de atuação formal de Flávio. Um defensor do núcleo de sistema penitenciário contou que ele foi seu estagiário voluntário duas vezes por semana, sem bolsa, controle de frequência ou carga mínima, e que era “assíduo e interessado”.',
     'note': 'No LinkedIn, segundo a BBC, o estágio aparecia de março de 2001 a janeiro de 2002, outra data, mas também dentro do tempo do cargo.', 'sources': [BBC]},
    {'title': 'Mais de 1.000 km entre as duas cidades', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Brasília e o Rio ficam a mais de 1.000 km, ou quase uma hora e meia de voo. A reportagem pergunta como ele conciliava o estágio e a faculdade no Rio com o cargo em Brasília.',
     'note': '', 'sources': [BBC]},
    {'title': 'Ana Cristina era então mulher de Jair Bolsonaro', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Segundo a BBC, Ana Cristina Siqueira Valle, que ocupou o cargo antes de Flávio, era a segunda mulher de Jair Bolsonaro e já tinha trabalhado em outros gabinetes e comissões da Câmara. Contratar parentes para cargos de confiança só foi proibido em 2008, com uma súmula do STF.',
     'note': 'A BBC escreveu que ela deixou o cargo uma semana antes da chegada de Flávio. Nos atos do boletim, as duas datas são 14/12/2000.', 'sources': [BBC]},
    {'title': 'Parentes de Ana Cristina no gabinete de Jair', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'Segundo a BBC, o pai, a mãe, a irmã e o irmão de Ana Cristina também tiveram cargos na Câmara antes da proibição de 2008, no gabinete do próprio Jair Bolsonaro.',
     'note': 'Jair negou irregularidades ao jornal O Globo, que noticiou parte dessas contratações, e disse que não era casado formalmente na época.', 'sources': [BBC]},
    {'title': 'Procurado, Flávio não quis responder', 'label': 'reportagem', 'date': 'janeiro de 2019',
     'text': 'A assessoria de Flávio disse à BBC que não iria responder às perguntas. A assessoria de Jair Bolsonaro não respondeu até a publicação da reportagem.',
     'note': '', 'sources': [BBC]},
    {'title': '“Fiquei cinco anos estudando na faculdade de direito”', 'label': 'reportagem', 'date': '2008',
     'text': 'Em 2008, num discurso na Alerj contra o exame da OAB, Flávio disse: “Fiquei cinco anos estudando na faculdade de direito da Candido Mendes, aqui, no centro da cidade, dentre esses cinco anos, dois dedicados à prática forense, mais algumas centenas de horas de atividades extracurriculares, muito sacrifício, muita dedicação.”',
     'note': 'Em 2012, numa audiência na Alerj, disse: “Lembro com bastante carinho do meu período na Defensoria Pública, no início da faculdade.”', 'sources': [BBC]},
    {'title': 'A UFRJ diz que ele nunca foi aluno', 'label': 'reportagem', 'date': '12/08/2026',
     'text': 'Depois de consultar o sistema acadêmico, a UFRJ informou que “não há registro referente ao sr. Flávio Nantes Bolsonaro como discente”. A campanha atribuiu a pós citada nos perfis a “erros ou equívocos”, possivelmente tirados de páginas como a Wikipédia, e disse que pediu as correções.',
     'note': 'Segundo a Band, no mesmo dia o texto da Agência Senado já estava corrigido, e o perfil da Alerj ainda mostrava a pós à tarde.', 'sources': [BAND]},
    {'title': 'Flávio publica os diplomas', 'label': 'reportagem', 'date': '12/08/2026',
     'text': 'Na noite de 12/8/2026, Flávio publicou no X os diplomas de Direito, da especialização em Políticas Públicas e do MBA: “Para que não restem dúvidas sobre minha formação acadêmica”.',
     'note': 'Os três estão neste guia.', 'sources': [P360, X_POST]},
]

OUTCOME = [
    {'date': 'outubro de 2002', 'title': 'Eleito deputado estadual pelo PPB', 'label': 'documentado',
     'text': 'Meses depois de deixar o cargo na Câmara. O perfil da Alerj registra o mandato de 2003 a 2007.',
     'refs': [DEP_2003], 'sources': []},
    {'date': '2003 a 2019', 'title': 'Quatro mandatos na Alerj', 'label': 'documentado',
     'text': 'Segundo a Agência Senado, ele exerceu quatro mandatos de deputado estadual antes de chegar ao Senado.',
     'refs': [SENADO_MANDATOS], 'sources': []},
    {'date': 'janeiro de 2019', 'title': 'Senador, e a reportagem sobre o cargo', 'label': 'reportagem',
     'text': 'Às vésperas da posse no Senado, a BBC revela o cargo na Câmara. Flávio não responde.',
     'refs': [], 'sources': [BBC]},
    {'date': 'agosto de 2026', 'title': 'A pós da UFRJ e os diplomas', 'label': 'reportagem',
     'text': 'Já candidato a presidente, Flávio publica os diplomas depois que a UFRJ nega a pós citada nos perfis oficiais.',
     'refs': [], 'sources': [BAND, P360]},
]

GLOSSARY = [
    {'term': 'Cargo de natureza especial (CNE)', 'def': 'Cargo em comissão da Câmara, de livre nomeação, sem concurso. O número (CNE-09) indica o nível.'},
    {'term': 'Assistente técnico de gabinete', 'def': 'O cargo de Flávio. As 15 tarefas estão no Ato da Mesa nº 45, de 1996.'},
    {'term': 'Liderança partidária', 'def': 'Gabinete do líder de um partido na Câmara, com servidores próprios. Flávio estava na liderança do PPB.'},
    {'term': 'PPB', 'def': 'Partido Progressista Brasileiro, partido de Jair Bolsonaro na época. Depois virou o PP.'},
    {'term': 'Ato da Mesa', 'def': 'Norma interna aprovada pela Mesa Diretora da Câmara.'},
    {'term': 'Boletim Administrativo', 'def': 'Publicação da Câmara que reproduz os atos sobre os servidores, como nomeações e exonerações. Os boletins antigos estão no site da Câmara.'},
    {'term': 'DCD e DOU', 'def': 'Diário da Câmara dos Deputados e Diário Oficial da União, onde os atos são publicados oficialmente.'},
    {'term': 'Nomear', 'def': 'Pôr alguém num cargo. Para cargo em comissão, segue o artigo 9º, item II, da Lei nº 8.112/1990.'},
    {'term': 'Exonerar a pedido', 'def': 'Saída do cargo por vontade do próprio servidor (artigo 35, item II, da Lei nº 8.112/1990). Foi o caso de Flávio.'},
    {'term': 'Exonerar', 'def': 'Saída do cargo em comissão por decisão da autoridade (artigo 35, item I). Foi o caso de Ana Cristina.'},
    {'term': 'Ponto', 'def': 'Número de matrícula do servidor na Câmara, que aparece nos atos.'},
    {'term': 'Secretário parlamentar', 'def': 'Outro tipo de cargo, ligado ao gabinete de um deputado. Segundo a Câmara, pode trabalhar na base eleitoral, fora de Brasília.'},
    {'term': 'Wayback Machine', 'def': 'Arquivo da internet que guarda cópias de páginas como elas estavam numa data. As cópias da Alerj e do Senado deste guia vêm dele.'},
    {'term': 'Súmula Vinculante 13', 'def': 'Decisão do STF, de 2008, que proíbe nomear parentes para cargos de confiança.'},
    {'term': 'Funcionário fantasma', 'def': 'Expressão popular para quem é nomeado e recebe por um cargo que não exerce de fato.'},
]

ABOUT = '''<p>Este guia é um mapa de leitura de sete documentos públicos, com 70 páginas. Cada ponto leva à página e marca o trecho.</p>
<ul class="docs-list">
<li><b>Boletins Administrativos da Câmara</b> de 13/11/1998, 27/12/2000 e 31/7/2002: a nomeação de Ana Cristina, a saída dela e a nomeação de Flávio, e a saída de Flávio. Estão aqui como saem do <a href="https://www.camara.leg.br/boletimadm/2000/Ba20001227.pdf" rel="noopener noreferrer nofollow" target="_blank">site da Câmara</a>, sem nenhuma alteração. <button class="chip" data-open-doc="b1998">Abrir o de 1998</button> <button class="chip" data-open-doc="b2000">Abrir o de 2000</button> <button class="chip" data-open-doc="b2002">Abrir o de 2002</button></li>
<li><b>Ato da Mesa nº 45, de 1996</b>: as tarefas de cada cargo em comissão da Câmara, no <a href="https://imagem.camara.leg.br/Imagem/d/pdf/DCD06NOV1996SUP.pdf" rel="noopener noreferrer nofollow" target="_blank">Diário da Câmara de 6/11/1996</a>. Aqui estão a capa e as páginas 69 a 81, com o ato inteiro. As páginas são imagens; o texto usado na busca foi lido por computador e pode ter erros. <button class="chip" data-open-doc="ato">Abrir</button></li>
<li><b>Perfil de Flávio no site da Alerj</b>, como estava em 30/1/2019, numa <a href="https://web.archive.org/web/20190130081742/http://www.alerj.rj.gov.br/Deputados/PerfilDeputado/275?Legislatura=18" rel="noopener noreferrer nofollow" target="_blank">cópia do Wayback Machine</a>. Os contatos do gabinete (telefone, e-mail e endereço) foram cobertos. <button class="chip" data-open-doc="alerj">Abrir</button></li>
<li><b>Texto da Agência Senado</b> de 18/1/2019, numa <a href="https://web.archive.org/web/20190203071437/https://www12.senado.leg.br/noticias/materias/2019/01/18/flavio-bolsonaro-psl" rel="noopener noreferrer nofollow" target="_blank">cópia do Wayback Machine</a> de 3/2/2019. A Agência Senado autoriza a reprodução com citação. <button class="chip" data-open-doc="senado">Abrir</button></li>
<li><b>Diplomas</b> que Flávio <a href="https://x.com/FlavioBolsonaro/status/2087721700053889062" rel="noopener noreferrer nofollow" target="_blank">publicou no X</a> em 12/8/2026. Os números de documento aparecem cobertos. <button class="chip" data-open-doc="diplomas">Abrir</button></li>
</ul>
<p>A reportagem da BBC News Brasil (23/1/2019), que revelou o caso, não está hospedada aqui: é um texto protegido por direitos autorais. O que vem dela está em <a href="#extras">Fatos extras</a>, com link para a reportagem.</p>
<p>Nos arquivos que não são da Câmara, os metadados (programa e data de quem gerou o arquivo) foram apagados.</p>'''


def main():
    C = {'docs': DOCS, 'themes': THEMES, 'stories': STORIES, 'numbers': NUMBERS, 'timeline': TIMELINE,
         'roteiro': ROTEIRO, 'extras': EXTRAS, 'outcome': OUTCOME, 'glossary': GLOSSARY, 'about': ABOUT}
    with open(os.path.join(ROOT, 'data/content.json'), 'w', encoding='utf-8') as f:
        json.dump(C, f, ensure_ascii=False, indent=1)
    n = sum(len(r['refs']) for r in ROTEIRO)
    print(f'{len(ROTEIRO)} pontos ({n} trechos), {len(THEMES)} temas, {len(TIMELINE)} na cronologia, {len(EXTRAS)} fatos extras')


if __name__ == '__main__':
    main()
