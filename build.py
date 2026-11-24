#!/usr/bin/env python3
"""Gera o site estático Radar das Câmaras a partir de data/decisoes.json.
Uso: python3 build.py [--preview]   (saída em dist/)
--preview mostra os espaços de anúncio como caixas tracejadas."""
import json, os, sys, shutil, html, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'dist')
SITE_URL = 'https://radardascamaras.com.br'
PREVIEW = '--preview' in sys.argv
# Quando o AdSense for aprovado, cole aqui o seu ID (ca-pub-...). Vazio = sem anúncios.
ADSENSE_CLIENT = ''

ASSUNTOS = {
 'subsidio-vereadores': 'Subsídio dos vereadores',
 'verbas-indenizatorias': 'Verbas indenizatórias e benefícios',
 'duodecimo-limites': 'Duodécimo e limites do art. 29-A',
 'controle-interno': 'Controle interno',
 'pessoal': 'Pessoal e cargos',
 'licitacoes-contratos': 'Licitações e contratos',
 'transparencia': 'Transparência',
 'julgamento-contas-prefeito': 'Julgamento das contas do prefeito',
 'separacao-poderes': 'Separação de Poderes',
 'orcamento-emendas': 'Orçamento e emendas',
 'patrimonio': 'Patrimônio',
}
TRIBUNAIS = {
 'TCE-ES': ('tce-es', 'Tribunal de Contas do Estado do Espírito Santo'),
 'TCE-MG': ('tce-mg', 'Tribunal de Contas do Estado de Minas Gerais'),
 'TCE-SP': ('tce-sp', 'Tribunal de Contas do Estado de São Paulo'),
 'TCM-GO': ('tcm-go', 'Tribunal de Contas dos Municípios do Estado de Goiás'),
 'TCE-PR': ('tce-pr', 'Tribunal de Contas do Estado do Paraná'),
}
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

e = lambda s: html.escape(str(s), quote=True)

def dbr(iso):
    y, m, d = iso.split('-')
    return f'{int(d)}/{MESES[int(m)-1]}/{y}'

def load():
    d = json.load(open(os.path.join(BASE, 'data', 'decisoes.json'), encoding='utf-8'))
    d.sort(key=lambda x: x['data'], reverse=True)
    return d

RADAR_LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="none" stroke="#fbeff3" stroke-width="2"/><circle cx="16" cy="16" r="8" fill="none" stroke="#fbeff3" stroke-opacity=".6" stroke-width="1.5"/><path d="M16 16 L27 9" stroke="#ff5a3c" stroke-width="2.5" stroke-linecap="round"/><circle cx="22" cy="11" r="2.4" fill="#ff5a3c"/></svg>'

def page(title, desc, body, root, canonical, jsonld=None):
    ads = ''
    if ADSENSE_CLIENT and not PREVIEW:
        ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    return f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">{ads}{ld}
</head><body>
<nav class="nav" aria-label="Principal"><a class="brand" href="{root}index.html">{RADAR_LOGO}Radar das Câmaras</a>
<a href="{root}index.html#decisoes">Decisões</a><a href="{root}assuntos.html">Assuntos</a><a href="{root}tribunais.html">Tribunais</a><a href="{root}cursos.html">Cursos sob medida</a><a href="{root}sobre.html">Sobre</a></nav>
{body}
<footer class="band"><div class="wrap fgrid">
<div><b style="color:#fff">Radar das Câmaras</b><br>Jurisprudência dos Tribunais de Contas sobre a gestão das câmaras municipais, organizada por assunto.</div>
<div><a href="{root}assuntos.html">Assuntos</a><br><a href="{root}tribunais.html">Tribunais</a><br><a href="{root}sobre.html">Sobre o projeto</a></div>
<div><a href="{root}privacidade.html">Política de privacidade</a><br><a href="{root}contato.html">Contato</a></div>
</div><p class="wrap" style="margin-top:18px">Site independente, sem vínculo com os Tribunais de Contas. Os resumos não substituem o inteiro teor das decisões; consulte sempre a fonte oficial.</p></footer>
</body></html>'''

def ad_slot():
    if PREVIEW:
        return '<div class="ad">Espaço reservado para anúncio (Google AdSense)</div>'
    if ADSENSE_CLIENT:
        return f'<div class="ad" style="border:0"><ins class="adsbygoogle" style="display:block;width:100%" data-ad-client="{ADSENSE_CLIENT}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'
    return ''

def curso_box(root):
    return f'''<aside class="curso"><h3>Curso: a gestão da câmara segundo os Tribunais de Contas</h3>
<p style="margin:0 0 14px">Capacitação sob medida para a sua câmara ou para as câmaras da sua região, com as decisões do Tribunal de Contas do seu estado.</p>
<a class="btn" href="{root}cursos.html">Conhecer os cursos</a></aside>'''

def tags(d, root):
    t = [f'<a class="tag" href="{root}assunto/{a}.html">{e(ASSUNTOS[a])}</a>' for a in d['assuntos']]
    if d['escopo'] == 'aplicavel':
        t.append('<span class="tag apl" title="Decisão geral que também se aplica às câmaras">Aplicável à câmara</span>')
    return ' '.join(t)

def resumo(t, n=210):
    if len(t) <= n:
        return t
    return t[:n].rsplit(' ', 1)[0].rstrip(',;:—-') + '…'

def card(d, root):
    return f'''<article class="card" data-tri="{e(d['tribunal'])}" data-ass="{' '.join(d['assuntos'])}" data-esc="{d['escopo']}">
<div class="meta"><b>{e(d['tribunal'])}</b><span>{e(d['tipo'])} {e(d['numero'])}</span><span>{dbr(d['data'])}</span></div>
<h3><a href="{root}decisao/{d['slug']}.html">{e(d['titulo'])}</a></h3>
<p>{e(resumo(d['tese']))}</p>
<div>{tags(d, root)}</div></article>'''

def radar_svg(decs):
    import math, hashlib
    dots = []
    for d in decs:
        h = int(hashlib.md5(d['slug'].encode()).hexdigest(), 16)
        ang = (h % 360) * math.pi / 180
        r = 40 + (h // 360) % 140
        x, y = 200 + r * math.cos(ang), 200 + r * math.sin(ang)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#ff5a3c"><title>{e(d["tribunal"])}: {e(d["titulo"])}</title></circle>')
    rings = ''.join(f'<circle cx="200" cy="200" r="{r}" fill="none" stroke="#f3cdd9" stroke-opacity="{o}" stroke-width="1.2"/>' for r, o in [(185, .55), (135, .4), (85, .35), (35, .3)])
    return f'''<svg class="radar" viewBox="0 0 400 400" role="img" aria-label="Radar com {len(decs)} decisões sobre câmaras">
<defs><radialGradient id="g" cx="50%" cy="50%"><stop offset="0" stop-color="#7a2346"/><stop offset="1" stop-color="#3e0f22"/></radialGradient>
<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a3c" stop-opacity="0"/><stop offset="1" stop-color="#ff5a3c" stop-opacity=".45"/></linearGradient></defs>
<circle cx="200" cy="200" r="195" fill="url(#g)"/>{rings}
<path d="M200 15 V385 M15 200 H385" stroke="#f3cdd9" stroke-opacity=".25"/>
<g class="sweep"><path d="M200 200 L385 200 A185 185 0 0 0 330.8 69.2 Z" fill="url(#sw)"/><path d="M200 200 L385 200" stroke="#ff5a3c" stroke-width="2"/></g>
{''.join(dots)}<circle cx="200" cy="200" r="5" fill="#fbeff3"/></svg>'''

def build():
    decs = load()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    for sub in ['decisao', 'assunto', 'tribunal', 'assets']:
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    shutil.copy(os.path.join(BASE, 'assets', 'style.css'), os.path.join(OUT, 'assets', 'style.css'))
    pages = []

    # Página inicial
    tri_chips = ''.join(f'<button class="chip" data-f="tri" data-v="{t}" aria-pressed="false">{t}</button>' for t in TRIBUNAIS)
    usados = [a for a in ASSUNTOS if any(a in d['assuntos'] for d in decs)]
    ass_chips = ''.join(f'<button class="chip" data-f="ass" data-v="{a}" aria-pressed="false">{e(ASSUNTOS[a])}</button>' for a in usados)
    n_cons = sum(1 for d in decs if 'Consulta' in d['tipo'] or 'Prejulgado' in d['tipo'])
    body = f'''<header class="top band"><div class="wrap hero">
<div><h1>O que os Tribunais de Contas decidem sobre câmaras municipais</h1>
<p class="lead">Consultas, prejulgados e julgamentos sobre subsídio de vereador, duodécimo, controle interno, pessoal e licitações, resumidos em linguagem direta e com link para a fonte oficial.</p>
<form class="search" role="search" onsubmit="return false"><label for="q" class="sr" style="position:absolute;left:-9999px">Buscar decisões</label>
<input id="q" type="search" placeholder="Ex.: subsídio, duodécimo, assessor jurídico" autocomplete="off"></form>
<div class="stats"><div><b>{len(decs)}</b><span>decisões no acervo</span></div><div><b>{len(TRIBUNAIS)}</b><span>tribunais monitorados</span></div><div><b>{n_cons}</b><span>consultas e prejulgados</span></div></div></div>
{radar_svg(decs)}</div></header>
<main class="band" id="decisoes"><div class="wrap">
<p class="flabel">Tribunal</p><div class="filters">{tri_chips}</div>
<p class="flabel">Assunto</p><div class="filters">{ass_chips}</div>
<div class="filters"><button class="chip" data-f="esc" data-v="especifica" aria-pressed="false">Só decisões específicas de câmara</button></div>
<p class="aviso" id="cnt" aria-live="polite"></p>
<div class="list" id="lista">{''.join(card(d, '') for d in decs)}</div>
<div class="empty" id="vazio" hidden>Nenhuma decisão com esses filtros. Tente outro termo ou limpe os filtros.</div>
{ad_slot()}{curso_box('')}</div></main>
<script>{{
const q=document.getElementById('q'),cards=[...document.querySelectorAll('#lista .card')],cnt=document.getElementById('cnt'),vazio=document.getElementById('vazio');
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const txt=cards.map(c=>norm(c.textContent));const st={{tri:null,ass:null,esc:null}};
function apply(){{const t=norm(q.value.trim());let n=0;cards.forEach((c,i)=>{{const ok=(!t||t.split(/\\s+/).every(w=>txt[i].includes(w)))&&(!st.tri||c.dataset.tri===st.tri)&&(!st.ass||c.dataset.ass.split(' ').includes(st.ass))&&(!st.esc||c.dataset.esc===st.esc);c.hidden=!ok;if(ok)n++}});cnt.textContent=n+(n===1?' decisão':' decisões');vazio.hidden=n>0}}
document.querySelectorAll('.chip[data-f]').forEach(b=>b.addEventListener('click',()=>{{const f=b.dataset.f,on=st[f]!==b.dataset.v;document.querySelectorAll('.chip[data-f="'+f+'"]').forEach(x=>x.setAttribute('aria-pressed','false'));st[f]=on?b.dataset.v:null;if(on)b.setAttribute('aria-pressed','true');apply()}}));
q.addEventListener('input',apply);apply();
}}</script>'''
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Radar das Câmaras", "url": SITE_URL}
    write('index.html', page('Radar das Câmaras — jurisprudência dos Tribunais de Contas sobre câmaras municipais',
        'Decisões dos Tribunais de Contas sobre câmaras municipais: subsídio de vereador, duodécimo, controle interno, pessoal e licitações, com resumo e link para a fonte.', body, '', '', ld))
    pages.append('')

    # Páginas de decisão
    for d in decs:
        r = '../'
        rel = [x for x in decs if x is not d and set(x['assuntos']) & set(d['assuntos'])][:3]
        ficha = [('Tribunal', TRIBUNAIS[d['tribunal']][1]), ('Tipo', d['tipo']), ('Número', d['numero'])]
        if d['processo'] and d['processo'] != d['numero']:
            ficha.append(('Processo', d['processo']))
        if d['orgao']:
            ficha.append(('Órgão julgador', d['orgao']))
        ficha += [('Relator', d['relator']), ('Data', f"{d['data_tipo'].capitalize()} {dbr(d['data'])}"),
                  ('Escopo', 'Específica de câmara' if d['escopo'] == 'especifica' else 'Geral, aplicável à câmara')]
        dl = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in ficha)
        body = f'''<header class="top band"><div class="wrap"><p class="crumbs"><a href="../index.html">Início</a> › <a href="../tribunal/{TRIBUNAIS[d['tribunal']][0]}.html">{e(d['tribunal'])}</a></p>
<h1>{e(d['titulo'])}</h1><div class="meta" style="color:#efd2dc">{e(d['tribunal'])} · {e(d['tipo'])} {e(d['numero'])} · {e(d['data_tipo'])} {dbr(d['data'])}</div></div></header>
<main class="band"><div class="wrap grid2"><article class="prose">
<h2>O que o tribunal decidiu</h2><p class="tese">{e(d['tese'])}</p>
<h3>Contexto</h3><p>{e(d['contexto'])}</p>
<p>{tags(d, r)}</p>
<p><a class="btn" href="{e(d['fonte_url'])}" rel="noopener">Ler na fonte oficial: {e(d['fonte'])}</a></p>
<p class="aviso">Resumo elaborado pelo Radar das Câmaras a partir do informativo oficial do tribunal. Não substitui o inteiro teor da decisão.</p>
{ad_slot()}
{('<h2>Decisões relacionadas</h2><div class="list">' + ''.join(card(x, r) for x in rel) + '</div>') if rel else ''}
</article><aside><div class="box"><h3>Ficha</h3><dl class="ficha">{dl}</dl></div><div style="height:16px"></div>{curso_box(r)}</aside></div></main>'''
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": d['titulo'], "datePublished": d['data'],
              "about": [ASSUNTOS[a] for a in d['assuntos']], "isBasedOn": d['fonte_url'],
              "publisher": {"@type": "Organization", "name": "Radar das Câmaras"}}
        write(f"decisao/{d['slug']}.html", page(f"{d['titulo']} — {d['tribunal']}", d['tese'][:155], body, r, f"decisao/{d['slug']}", ld))
        pages.append(f"decisao/{d['slug']}")

    # Assuntos
    items = ''
    for a, nome in ASSUNTOS.items():
        sel = [d for d in decs if a in d['assuntos']]
        if not sel:
            continue
        items += f'<a class="card" style="text-decoration:none;color:inherit" href="assunto/{a}.html"><h3>{e(nome)}</h3><span class="meta">{len(sel)} {"decisão" if len(sel)==1 else "decisões"}</span></a>'
        body = f'''<header class="top band"><div class="wrap"><p class="crumbs"><a href="../index.html">Início</a> › <a href="../assuntos.html">Assuntos</a></p><h1>{e(nome)}</h1>
<p class="lead" style="color:#f3dbe3;margin:0">{len(sel)} {"decisão" if len(sel)==1 else "decisões"} dos Tribunais de Contas sobre este tema, da mais recente para a mais antiga.</p></div></header>
<main class="band"><div class="wrap"><div class="list">{''.join(card(d, '../') for d in sel)}</div>{ad_slot()}{curso_box('../')}</div></main>'''
        write(f'assunto/{a}.html', page(f'{nome} — decisões dos Tribunais de Contas sobre câmaras', f'Jurisprudência dos Tribunais de Contas sobre {nome.lower()} nas câmaras municipais.', body, '../', f'assunto/{a}'))
        pages.append(f'assunto/{a}')
    body = f'<header class="top band"><div class="wrap"><h1>Assuntos</h1><p class="lead" style="color:#f3dbe3;margin:0">Escolha um tema da rotina da câmara.</p></div></header><main class="band"><div class="wrap list">{items}</div></main>'
    write('assuntos.html', page('Assuntos — Radar das Câmaras', 'Decisões dos Tribunais de Contas sobre câmaras municipais organizadas por assunto.', body, '', 'assuntos'))
    pages.append('assuntos')

    # Tribunais
    items = ''
    for t, (slug, nome) in TRIBUNAIS.items():
        sel = [d for d in decs if d['tribunal'] == t]
        items += f'<a class="card" style="text-decoration:none;color:inherit" href="tribunal/{slug}.html"><h3>{e(t)}</h3><span>{e(nome)}</span><span class="meta">{len(sel)} decisões</span></a>'
        body = f'''<header class="top band"><div class="wrap"><p class="crumbs"><a href="../index.html">Início</a> › <a href="../tribunais.html">Tribunais</a></p><h1>{e(nome)}</h1>
<p class="lead" style="color:#f3dbe3;margin:0">{len(sel)} decisões sobre câmaras municipais.</p></div></header>
<main class="band"><div class="wrap"><div class="list">{''.join(card(d, '../') for d in sel)}</div>{ad_slot()}</div></main>'''
        write(f'tribunal/{slug}.html', page(f'{t}: decisões sobre câmaras municipais — Radar das Câmaras', f'Decisões do {nome} sobre câmaras municipais.', body, '../', f'tribunal/{slug}'))
        pages.append(f'tribunal/{slug}')
    body = f'<header class="top band"><div class="wrap"><h1>Tribunais</h1><p class="lead" style="color:#f3dbe3;margin:0">Tribunais já incluídos no Radar. Novos tribunais entram aos poucos.</p></div></header><main class="band"><div class="wrap list">{items}</div></main>'
    write('tribunais.html', page('Tribunais — Radar das Câmaras', 'Tribunais de Contas monitorados pelo Radar das Câmaras.', body, '', 'tribunais'))
    pages.append('tribunais')

    # Institucionais
    def inst(fname, title, h, content):
        b = f'<header class="top band"><div class="wrap"><h1>{h}</h1></div></header><main class="band"><div class="wrap prose">{content}</div></main>'
        write(fname + '.html', page(title, h, b, '', fname))
        pages.append(fname)
    inst('sobre', 'Sobre — Radar das Câmaras', 'Sobre o Radar das Câmaras', '''
<p>O Radar das Câmaras reúne, num só lugar, as decisões dos Tribunais de Contas que tratam da gestão das câmaras municipais: subsídio de vereadores, repasse do duodécimo, controle interno, pessoal, licitações, transparência e julgamento das contas do prefeito.</p>
<p>Cada decisão traz um resumo em linguagem direta, a ficha com número, órgão julgador, relator e data, e o link para o documento oficial do tribunal. O acervo é atualizado periodicamente a partir dos informativos de jurisprudência publicados pelos próprios tribunais.</p>
<h2>Como ler as etiquetas</h2>
<p><b>Específica de câmara</b>: a decisão trata diretamente de câmara municipal, vereadores ou Poder Legislativo municipal. <b>Aplicável à câmara</b>: decisão de alcance geral cujo entendimento também vale para as câmaras.</p>
<h2>Aviso</h2>
<p>O Radar das Câmaras é um projeto independente, sem vínculo com os Tribunais de Contas. Os resumos são elaborados de boa-fé, mas não substituem o inteiro teor das decisões nem constituem orientação jurídica para casos concretos. Antes de decidir, consulte a decisão original e a legislação do seu município.</p>''')
    temas = [
        ('Subsídio dos vereadores', 'Fixação, prazos, anterioridade, revisão geral e teto: o que dá multa e devolução.'),
        ('Duodécimo e limites do art. 29-A', 'Base de cálculo, inativos e pensionistas, repasse no meio do ano e devolução de saldo.'),
        ('Controle interno do Legislativo', 'Estrutura, independência, rotinas e o que o Tribunal espera da unidade de controle.'),
        ('Pessoal e cargos', 'Comissionados, funções de confiança, gratificações e limites da LRF.'),
        ('Licitações e contratações diretas', 'Dispensa, inexigibilidade e pesquisa de preços na Lei 14.133/2021, com os erros mais punidos.'),
        ('Julgamento das contas do prefeito', 'Rito, prazos, quórum e o envio da decisão ao Tribunal de Contas.'),
        ('Transparência', 'O que o portal da câmara precisa publicar para não ser apontado pelo Tribunal.'),
        ('Verbas indenizatórias', 'Auxílios, diárias e ressarcimentos: quando são válidos e como instituí-los.'),
    ]
    tl = ''.join(f'<div class="card"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in temas)
    b = f'''<header class="top band"><div class="wrap hero">
<div><h1>Cursos sob medida para a sua câmara</h1>
<p class="lead">Capacitação para vereadores, servidores, controladores e assessores, montada a partir das dúvidas reais da sua câmara e das decisões do Tribunal de Contas do seu estado.</p>
<a class="btn" href="contato.html">Solicitar uma proposta</a></div>
<div style="justify-self:center;text-align:center"><div aria-label="Foto de Carlos Átila Emerick Soares (a incluir)" style="width:220px;height:220px;border-radius:50%;background:#7a2346;border:4px solid #f3cdd9;display:grid;place-items:center;font:800 64px 'Libre Franklin',sans-serif;color:#fbeff3;margin:0 auto">CÁ</div>
<p style="margin:14px 0 0;color:#fff;font:700 18px 'Libre Franklin',sans-serif">Carlos Átila Emerick Soares</p><p style="margin:2px 0 0;color:#efd2dc;font:15px 'Libre Franklin',sans-serif">Advogado · OAB/ES 15.650</p></div></div></header>
<main><section class="band"><div class="wrap grid2"><div class="prose">
<h2>Por que um curso sob medida</h2>
<p>Cursos abertos falam de regras gerais. A sua câmara tem a Lei Orgânica, o Regimento, a estrutura de pessoal e o Tribunal de Contas dela. Um curso sob medida parte disso: o que a equipe faz no dia a dia, onde estão as dúvidas e o que o Tribunal do seu estado já decidiu sobre cada ponto.</p>
<p>O conteúdo nasce do acervo do Radar das Câmaras, que acompanha as decisões dos Tribunais de Contas sobre a gestão das câmaras. Cada tema é explicado com casos reais: o que foi aprovado, o que gerou multa e o que precisou ser devolvido.</p>
<h2>Dois formatos</h2>
<p><b>Para a sua câmara.</b> Turma fechada, presencial ou online, para vereadores, servidores, controle interno e assessoria. O programa é ajustado ao que a câmara precisa resolver agora: fixação de subsídios, estrutura do controle interno, preparação para o julgamento das contas, revisão de rotinas de compras.</p>
<p><b>Para a sua região.</b> Um encontro para várias câmaras vizinhas, organizado com associações ou consórcios de municípios. O custo é dividido entre as câmaras participantes, e a troca de experiências entre equipes que enfrentam os mesmos problemas enriquece o curso.</p>
<h2>Como funciona</h2>
<ol><li><b>Conversa inicial</b>: entendemos o público, as dúvidas e o momento da câmara.</li>
<li><b>Programa sob medida</b>: temas, carga horária e formato definidos com a câmara, com base nas decisões do Tribunal do seu estado.</li>
<li><b>Curso</b>: aulas práticas, com casos reais e espaço para as perguntas da equipe.</li>
<li><b>Material de apoio</b>: resumo das decisões citadas e roteiros práticos para consulta depois do curso.</li></ol>
<p>A contratação de treinamento e aperfeiçoamento de pessoal segue a Lei 14.133/2021; a proposta traz a documentação necessária para o processo da câmara.</p>
</div><aside><div class="box"><h3>Sobre o instrutor</h3>
<p style="font-size:16px">Carlos Átila Emerick Soares é advogado (OAB/ES 15.650) e servidor público há mais de 15 anos, com atuação no controle interno do Poder Legislativo municipal. É o criador do Radar das Câmaras, que reúne a jurisprudência dos Tribunais de Contas sobre a gestão das câmaras.</p></div>
<div style="height:16px"></div><div class="curso"><h3>Vamos conversar sobre a sua câmara?</h3><p style="margin:0 0 14px">Conte quem vai participar e quais temas mais preocupam a equipe. Você recebe uma proposta sem compromisso.</p><a class="btn" href="contato.html">Solicitar uma proposta</a></div></aside></div></section>
<section class="band soft"><div class="wrap"><h2>Temas mais pedidos</h2><p class="aviso" style="margin-top:-6px">Combine os temas de acordo com a necessidade da sua câmara.</p><div class="list">{tl}</div></div></section></main>'''
    write('cursos.html', page('Cursos sob medida para câmaras municipais — Radar das Câmaras',
        'Capacitação sob medida para câmaras municipais e regiões: subsídios, duodécimo, controle interno, pessoal e licitações com as decisões do Tribunal de Contas do seu estado.', b, '', 'cursos'))
    pages.append('cursos')

    inst('privacidade', 'Política de privacidade — Radar das Câmaras', 'Política de privacidade', f'''
<p>Atualizada em {dbr(datetime.date.today().isoformat())}.</p>
<h2>Dados coletados</h2><p>O site não exige cadastro. Podem ser coletados dados de navegação (páginas visitadas, tipo de navegador e dispositivo, endereço IP de forma anonimizada) por ferramentas de estatística e de publicidade.</p>
<h2>Cookies e publicidade</h2><p>Este site pode exibir anúncios do Google AdSense. O Google e seus parceiros usam cookies para exibir anúncios com base em visitas anteriores a este e a outros sites. Você pode desativar a publicidade personalizada nas Configurações de anúncios do Google (adssettings.google.com) e saber mais em policies.google.com/technologies/ads.</p>
<h2>Seus direitos (LGPD)</h2><p>Você pode solicitar informações sobre o tratamento de seus dados, correção ou eliminação, pelo canal indicado na página de contato. Os dados são tratados com base no legítimo interesse e no consentimento, nos termos da Lei 13.709/2018.</p>
<h2>Links externos</h2><p>As decisões apontam para os sites oficiais dos tribunais, que têm políticas próprias.</p>''')
    inst('contato', 'Contato — Radar das Câmaras', 'Contato', '''
<p>Sugestões de decisões, correções nos resumos ou interesse no curso: escreva para o e-mail de contato do Radar das Câmaras.</p>
<p class="box">E-mail de contato: será publicado aqui quando o domínio estiver ativo.</p>
<p class="aviso">O Radar das Câmaras não presta consultoria por este canal sobre casos concretos.</p>''')

    # SEO
    today = datetime.date.today().isoformat()
    sm = ''.join(f'<url><loc>{SITE_URL}/{p}</loc><lastmod>{today}</lastmod></url>' for p in pages)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    print(f'{len(pages)} páginas geradas em {OUT}')

def write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(content)

if __name__ == '__main__':
    build()
