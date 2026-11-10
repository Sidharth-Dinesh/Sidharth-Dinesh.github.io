#!/usr/bin/env python3
"""Generate a small static academic website. Python standard library only."""
from pathlib import Path
from urllib.parse import urlsplit
import html,json,os,subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/site.json').read_text())

TIMEZONE=ZoneInfo('America/Phoenix')
def last_updated():
    """Use an explicit build timestamp, the latest Git commit, or local build time."""
    value=os.environ.get('SITE_LAST_UPDATED','').strip()
    if not value:
        try:
            value=subprocess.check_output(
                ['git','log','-1','--format=%cI'],cwd=ROOT,
                stderr=subprocess.DEVNULL,text=True,timeout=5).strip()
        except (OSError,subprocess.SubprocessError):
            value=''
    if value:
        try:
            stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
            if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=TIMEZONE)
            return stamp.astimezone(TIMEZONE).date()
        except ValueError:
            pass
    return datetime.now(TIMEZONE).date()
UPDATED=last_updated()
UPDATED_LABEL=f'{UPDATED:%b} {UPDATED.day}, {UPDATED.year}'
COPYRIGHT_YEAR=datetime.now(TIMEZONE).year

NAV=[('About','index.html','about'),('Research','research/index.html','research'),('Publications','publications/index.html','publications'),('Projects','projects/index.html','projects'),('Experience','experience/index.html','experience'),('Gallery','gallery/index.html','gallery'),('CV','cv/index.html','cv')]
def esc(value):return html.escape(str(value),quote=True)
def local(path,prefix):
    if urlsplit(path).scheme or path.startswith('#'):return path
    return prefix+path.lstrip('/')
def link(path,text,prefix,cls=''):
    return f'<a href="{esc(local(path,prefix))}"'+(f' class="{cls}"' if cls else '')+f'>{text}</a>'
def media(item,prefix,small=False,label='Project visual'):
    src=item.get('src','')
    if not src:
        return f'<figure class="media-placeholder" role="img" aria-label="{esc(label)}: placeholder"><span class="media-label">{esc(label)}</span><small>Image or video to follow</small></figure>'
    caption=f'<figcaption>{esc(item["caption"])}</figcaption>' if item.get('caption') else ''
    if item.get('type')=='animation':
        if small:src=item.get('preview_src',src)
        poster=local(item['poster'],prefix)
        animated=local(src,prefix)
        return f'<figure class="media animation"><picture><source media="(prefers-reduced-motion: reduce)" srcset="{esc(poster)}"><img src="{esc(animated)}" alt="{esc(item.get("alt",label))}" data-animation-src="{esc(animated)}" data-still-src="{esc(poster)}" loading="lazy" decoding="async"></picture><button class="animation-toggle" type="button" aria-pressed="false" hidden>Pause animation</button>{caption}</figure>'
    if item.get('type')=='video':
        poster=f' poster="{esc(local(item["poster"],prefix))}"' if item.get('poster') else ''
        track=f'<track kind="captions" src="{esc(local(item["captions"],prefix))}" srclang="en" label="English" default>' if item.get('captions') else ''
        transcript=link(item['transcript'],'Read transcript',prefix) if item.get('transcript') else ''
        return f'<figure class="media"><video controls playsinline preload="metadata" aria-label="{esc(item.get("alt",label))}"{poster}><source src="{esc(local(src,prefix))}" type="video/mp4">{track}'+link(src,'Download video',prefix)+f'</video>{caption}{transcript}</figure>'
    return f'<figure class="media"><img src="{esc(local(src,prefix))}" alt="{esc(item.get("alt",label))}" loading="lazy" decoding="async">{caption}</figure>'
def research_figures(item,prefix):
    figures=item.get('figures') or ([item['media']] if item.get('media') else [])
    return '<div class="research-grid">'+''.join(media(f,prefix,label='Research figure') for f in figures)+'</div>'
def actions(items,prefix):
    return '<div class="links">'+''.join(link(url,esc(text),prefix) for text,url in items if url)+'</div>'
def education():
    return '<dl class="education-list">'+''.join(f'<div class="education-row"><dt>{esc(e["institution"])}</dt><dd>{esc(e["degree"])}{('<br>'+esc(e['rank'])) if e.get('rank') else ''}</dd><dd class="date">{esc(e["period"])}<br>GPA: {esc(e["gpa"])}</dd></div>' for e in DATA['education'])+'</dl>'
def publication(prefix,compact=False):
    p=DATA['publication'];tag='h3' if compact else 'h2'
    authors=', '.join('<strong>'+esc(a)+'</strong>' if a==DATA['name'] else esc(a) for a in p['authors'])
    summary='' if compact else '<p>This paper studies how to assign video-processing work across edge servers using an optimization-based load-balancing method.</p>'
    return f'<article class="publication"><p class="meta">{p["year"]} · Journal article</p><{tag}>'+link(p['doi'],esc(p['title']),prefix)+f'</{tag}><p class="authors">{authors}</p><p class="venue"><em>{esc(p["journal"])}</em>, {p["volume"]}({p["issue"]}), {p["article"]}.</p>'+summary+(research_figures(p,prefix) if not compact and p.get('media') else '')+actions([('DOI / publisher',p['doi']),('Paper PDF',p['pdf']),('Research repository',p.get('repository',''))],prefix)+'</article>'
def project_rows(prefix,selected=False):
    rows=[]
    for p in DATA['projects']:
        if selected and not p.get('featured'):continue
        visual=media(p['media'],prefix,True,'Project visual')
        # Avoid placing interactive video controls inside a link.
        if p['media'].get('type')=='animation':
            opening=f'<a class="media-link" href="{esc(local(p["url"],prefix))}" aria-label="View project: {esc(p["title"])}">'
            visual=visual.replace('<picture>',opening+'<picture>',1).replace('</picture>','</picture></a>',1)
        elif p['media'].get('type')!='video':
            visual=link(p['url'],visual,prefix,'media-link').replace('<a ', '<a aria-label="View project: '+esc(p['title'])+'" ', 1)
        rows.append(f'<article class="project-row">{visual}<div><h2>'+link(p['url'],esc(p['title']),prefix)+f'</h2><p>{esc(p["summary"])}</p><p class="meta">{esc(" · ".join(p["tags"]))}</p>'+actions([('Repository',p['links']['code'])],prefix)+'</div></article>')
    return '<div class="project-list">'+''.join(rows)+'</div>'
def shell(title,body,key,path,description=None):
    depth=len(Path(path).parts)-1;prefix='../'*depth
    nav=''.join(f'<li><a href="{esc(prefix+url)}"'+(' aria-current="page"' if key==k else '')+'>'+text+'</a></li>' for text,url,k in NAV)
    full_title=DATA['name'] if key=='about' else title+' | '+DATA['name']
    content=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full_title)}</title><meta name="description" content="{esc(description or DATA['description'])}">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="{prefix}index.html">{esc(DATA['name'])}</a>
<button class="menu-toggle" type="button" data-menu-toggle aria-controls="site-navigation" aria-expanded="false">Menu</button>
<nav class="site-nav" id="site-navigation" aria-label="Main navigation"><ul>{nav}</ul></nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><span>&copy; {COPYRIGHT_YEAR} {esc(DATA['name'])}</span><span>Last updated: <time datetime="{UPDATED.isoformat()}">{UPDATED_LABEL}</time></span><span><a href="mailto:{esc(DATA['email'])}">{esc(DATA['email'])}</a></span></footer>
</body></html>'''
    target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content+'\n')
    return prefix
# About: deliberately short, with detailed work living on separate pages.
body=f'''<section class="intro" aria-labelledby="about-name"><div><h1 id="about-name">{esc(DATA['name'])}</h1><p class="affiliation">{esc(DATA['role'])}<br>{esc(DATA['school'])}<br>{esc(DATA['affiliation'])}</p></div><img class="portrait" src="assets/portrait.webp" alt="Portrait of Sidharth Dinesh" width="162" height="162" fetchpriority="high"><div class="intro-body"><p>I am a Systems Analyst at Arizona State University’s W. P. Carey School of Business, where I work on undergraduate-advising software, database integrations, and data applications for faculty and staff. My background combines computer science with electronics and edge computing.</p><p>I am interested in <strong>spatial and spatiotemporal data systems</strong>, particularly how we process and explore geographic data to understand movement, cities, and environmental change. My interests include spatial analysis, interactive mapping, and the systems that make large geographic datasets useful.</p>'''
body+=actions([('Email','mailto:'+DATA['email']),('GitHub',DATA['links']['github']),('LinkedIn',DATA['links']['linkedin']),('CV (PDF)','files/CV_Sidharth_Dinesh.pdf')],'')+'</div></section>'
body+='<h2>Research interests</h2><ul class="research-list">'+''.join('<li><strong>'+esc(x['title'])+'.</strong> '+esc(x['text'])+'</li>' for x in DATA['interests'])+'</ul><p>'+link('research/index.html','More about my research background →','')+'</p>'
body+='<p>My spatial projects include '+link('projects/spatial-hotspots/index.html','spatiotemporal hotspot detection in NYC taxi data','')+' and '+link('projects/dinosaur-visualization/index.html','an interactive geographic map and timeline','')+'.</p>'
body+='<h2>Education</h2>'+education()
body+='<div class="section-heading"><h2>Publication</h2>'+link('publications/index.html','Publication details →','')+'</div>'+publication('',True)
shell('About',body,'about','index.html')
# Research
prefix='../';t=DATA['thesis']
body='<h1>Research</h1><p class="lead">Spatial data systems, geographic analysis, and urban and environmental applications.</p>'
body+='<div class="prose"><p>My interests are in spatial data systems, geographic analysis, and interactive mapping. I am drawn to work that uses location and time to understand movement, cities, and environmental change, including applications in mobility, pollution, climate, and disaster response.</p><h2>Spatial projects</h2><p>My hotspot project analyzed NYC taxi pickups using spatial joins and Getis–Ord statistics in Spark. My mapping project linked the locations of 309 dinosaur records to an interactive timeline. These projects introduced me to spatial data processing and geographic visualization.</p><p>My earlier research focused on distributing video-processing work across edge servers. I now work on university databases and production applications, bringing together my interests in data processing and systems development.</p>'
body+=f'<h2>Research background</h2><h3>{esc(t["title"])}</h3><p class="meta">Undergraduate thesis research · VNIT Nagpur · {esc(t["period"])}</p><p><strong>Advisor:</strong> {esc(t["advisor"])}</p><p>With {esc(t["coauthor"])}, I co-developed the Dynamic Decision-Making Engine (DDME). It shifts video-processing tasks from busy edge servers to servers with spare capacity. Here, edge computing means processing data close to where it is collected.</p><p>The thesis evaluates processing delays and workload distribution against an existing offloading method.</p></div>'
body+='<ul>'+''.join('<li>'+esc(x)+'</li>' for x in t['bullets'])+'</ul>'+research_figures(t,prefix)
body+='<div class="prose"><h2>Related publication</h2><p>I coauthored a journal article on optimization-based load balancing for edge computing. Its ISROLBS-ECE method is distinct from the DDME framework in my thesis.</p><p>'+link('publications/index.html','Read the publication →',prefix)+'</p><h2>Related projects</h2></div>'+project_rows(prefix,True)
shell('Research',body,'research','research/index.html')
# Publications
p=DATA['publication']
bib='''@article{deshpande2023edge,
  author = {Deshpande, Prasanna and Dinesh, Sidharth and
            Umredkar, Apurva and Kothari, Ashwin G.},
  title = {Improved search and rescue optimization based load balancing
           scheme of CCTV footage on edge computing environment},
  journal = {Concurrency and Computation: Practice and Experience},
  year = {2023},
  volume = {35},
  number = {5},
  pages = {e7556},
  doi = {10.1002/cpe.7556}
}'''
body='<h1>Publications</h1><p class="lead">My journal publication on load balancing for edge computing.</p>'+publication(prefix)
body+='<details><summary>BibTeX citation</summary><pre><code id="paper-citation">'+esc(bib)+'</code></pre><p><button class="copy-citation" type="button" data-copy-citation="paper-citation">Copy citation</button><span class="copy-status" role="status" aria-live="polite"></span></p></details>'
shell('Publications',body,'publications','publications/index.html')
# Projects
body='<h1>Projects</h1><p class="lead">Projects in spatial analysis, interactive mapping, cloud computing, and data mining.</p>'+project_rows(prefix)
shell('Projects',body,'projects','projects/index.html')
for p in DATA['projects']:
    prefix='../../'
    body='<p class="breadcrumb">'+link('projects/index.html','← All projects',prefix)+'</p><header class="project-header"><h1>'+esc(p['title'])+'</h1><p class="lead">'+esc(p['summary'])+'</p><p class="meta"><strong>Tools:</strong> '+esc(', '.join(p['tags']))+'</p></header>'
    body+=media(p['media'],prefix,label='Project image or video')
    body+='<div class="prose"><h2>Overview</h2><p>'+esc(p['problem'])+'</p><h2>Approach</h2><ul>'+''.join('<li>'+esc(a)+'</li>' for a in p['approach'])+'</ul><h2>Implementation</h2><p>'+esc(p['scope'])+'</p><h2>Reflections</h2><p>'+esc(p['takeaway'])+'</p>'
    body+=actions([('Repository',p['links']['code']),('Live demo',p['links']['demo']),('Project report',p['links']['report']),('Video demo (MP4)',p['links'].get('video',''))],prefix)+'</div>'
    shell(p['title'],body,'projects',p['url'],p['summary'])
# Experience: presentations first, followed by professional work and teaching.
prefix='../'
body='<h1>Experience</h1><p class="lead">My presentations, work experience, and teaching.</p><h2>Presentations and recognition</h2>'
for talk in DATA['talks']:
    body+='<section class="entry presentation"><h3>'+esc(talk['title'])+'</h3><p class="meta">'+esc(talk['venue'])+(' · '+esc(talk['date']) if talk['date'] else '')+'</p><p>'+esc(talk['description'])+'</p>'
    if talk.get('media'):
        body+='<div class="talk-media">'+''.join(media(m,prefix,label='Presentation photo or slide') for m in talk['media'])+'</div>'
    body+=actions([('Slides (PDF)',talk.get('slides','')),('Watch recording at ASU',talk.get('recording',''))],prefix)
    if talk.get('recording'):
        body+='<details class="recording"><summary>Watch the session here</summary><iframe class="recording-player" src="'+esc(talk['recording'])+'" title="'+esc(talk['title'])+' — ASU recording" loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></details>'
    body+='</section>'
body+='<section class="entry recognition"><h3>Sun Awards</h3><p>'+esc(DATA['recognition'])+'</p></section>'
body+='<h2>Professional experience</h2><div class="experience-list">'
for w in DATA['experience']:
    body+=f'<section class="entry" id="{esc(w["id"])}"><h2>{esc(w["title"])}</h2><p class="organization"><strong>{esc(w["role"])}</strong><br>{esc(w["organization"])}</p><p class="meta">{esc(w["period"])}</p><p>{esc(w["summary"])}</p>'+('<ul>'+''.join('<li>'+esc(a)+'</li>' for a in w['details'])+'</ul>' if w['details'] else '')
    if w.get('show_media') and w.get('media',{}).get('src'):body+=media(w['media'],prefix,label='Work image or video')
    body+='</section>'
body+='</div><h2>Teaching and mentoring</h2><section class="entry"><h3>LEAD MAT 117 Tutor</h3><p class="meta">Academic Support Network, Arizona State University · Aug–Nov 2023</p><p>I tutored mathematics students and helped them work through practice problems using ALEKS.</p></section><section class="entry"><h3>Student Mentor</h3><p class="meta">Visvesvaraya National Institute of Technology, Nagpur · Jul 2020–May 2022</p><p>I mentored 15 first-year students on academics, campus life, and adapting to online learning during COVID-19.</p></section>'
shell('Experience',body,'experience','experience/index.html')
# Gallery retained as requested, with neutral empty slots.
body='<h1>Gallery</h1><p class="lead">Photos from graduation and life at ASU.</p><div class="gallery">'
for item in (DATA['gallery'] or [{},{},{},{}]):body+=media(item,prefix,label='Photo or video')
body+='</div>'
shell('Gallery',body,'gallery','gallery/index.html')
# Web CV
body='<h1>Curriculum vitae</h1><p class="pdf-link">'+link('files/CV_Sidharth_Dinesh.pdf','Download CV (PDF)',prefix,'download')+'</p><h2>Education</h2>'+education()
body+=f'<h2>Research experience</h2><section class="entry"><h3>Undergraduate thesis research</h3><p>{esc(t["institution"])}</p><p class="meta">{esc(t["period"])} · Advisor: {esc(t["advisor"])}</p><p><em>{esc(t["title"])}</em></p><ul>{''.join('<li>'+esc(x)+'</li>' for x in t['bullets'])}</ul>'+'</section><h2>Publication</h2>'+publication(prefix,True)
body+='<h2>Selected projects</h2>'
for p in DATA['projects']:
    body+='<section class="entry"><h3>'+link(p['url'],esc(p['title']),prefix)+'</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in p['approach'])+'</ul>'+actions([('Repository',p['links']['code'])],prefix)+'</section>'
body+='<h2>Professional experience</h2>'
for w in DATA['cv_employment']:
    body+=f'<section class="entry"><h3>{esc(w["role"])}</h3><p>{esc(w["organization"])}</p><p class="meta">{esc(w["period"])}</p><ul>'+''.join('<li>'+esc(x)+'</li>' for x in w['bullets'])+'</ul></section>'
body+='<h2>Teaching and mentoring</h2><p>LEAD MAT 117 Tutor, Arizona State University · Aug–Nov 2023</p><p>Student Mentor, VNIT Nagpur · Jul 2020–May 2022</p><p>Mentored 15 first-year students on academics, campus life, and online learning during COVID-19.</p><p>'+link('experience/index.html','Full experience and presentations →',prefix)+'</p><h2>Presentations and recognition</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in DATA['presentation_bullets'])+'</ul><h2>Technical skills</h2><dl class="skill-list">'+''.join('<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>' for k,v in DATA['skills'].items())+'</dl>'
shell('CV',body,'cv','cv/index.html')
shell('Page not found','<h1>Page not found</h1><p>The page may have moved. Please use the navigation above or return to the '+link('index.html','home page','')+'.</p>','none','404.html')
print('Generated 12 HTML pages.')
