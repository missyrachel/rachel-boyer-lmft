"""Generate crawlable specialty pages and search metadata at build time."""
import html,json,re
from pathlib import Path

ORIGIN='https://rachelboyerlmft.com'
def esc(value):return html.escape(str(value),quote=True)
def read_specialties(root):
 pages=[]
 for path in sorted((root/'content/specialties').glob('*.json')):
  slug=path.stem
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise ValueError('Invalid specialty slug')
  page=json.loads(path.read_text())
  for key in ['title','label','description','heading','body']:
   if not isinstance(page.get(key),str) or not page[key].strip():raise ValueError('Missing specialty '+key)
  page['slug']=slug;pages.append(page)
 return pages

def specialty_cards(pages):
 cards=''.join('<article class="card reflection-card"><h3><a href="/'+p['slug']+'">'+esc(p['label'])+'</a></h3><p>'+esc(p['description'])+'</p><a class="btn ghost" href="/'+p['slug']+'">Explore '+esc(p['label'])+'</a></article>' for p in pages)
 return '<section class="section" id="specialties"><div class="container"><p class="eyebrow">Find support that fits</p><h2>Online therapy for your concerns and goals</h2><p>Explore how we might work together. You do not need to choose a category before reaching out.</p><div class="cards-3">'+cards+'</div></div></section>'

def finalize(root,out,settings,pages,articles,md,header,footer):
 booking=esc(settings['booking_url']);email=esc('mailto:'+settings['email'])
 schedule='<section class="section section-alt"><div class="container"><h2>Take the next step</h2><p>Individual therapy: check your insurance eligibility and booking options through Headway. For private-pay therapy or couples sessions, contact me directly. Coverage and out-of-pocket costs depend on your plan.</p><div class="hero-actions"><a class="btn primary" href="'+booking+'">Check insurance &amp; book</a><a class="btn ghost" href="'+email+'">Inquire about private-pay therapy</a></div><p><a href="/#fees">View current fees and hours</a> · <a href="/#expect">What to expect</a></p><p>Sessions are by secure video; therapy clients must be physically in California. Please keep initial email inquiries free of sensitive clinical information.</p></div></section>'
 for p in pages:
  related=''.join('<li><a href="/'+q['slug']+'">'+esc(q['label'])+'</a></li>' for q in pages if q['slug']!=p['slug'])
  body='<main id="main-content"><section class="section"><div class="container specialty-content"><p class="eyebrow">'+esc(p['title'])+'</p><h1>'+esc(p['heading'])+'</h1><p class="specialty-byline">Rachel Boyer, LMFT · Online therapy throughout California</p>'+md(p['body'])+'</div></section>'+schedule+'<section class="section"><div class="container"><h2>Explore related support</h2><ul class="related-links">'+related+'</ul></div></section></main>'
  document='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(p['title'])+' | Rachel Boyer, LMFT</title><meta name="description" content="'+esc(p['description'])+'"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/cms-site.css"></head><body><a class="skip-link" href="#main-content">Skip to content</a>'+header+body+footer+'</body></html>'
  (out/(p['slug']+'.html')).write_text(document)
 article_map={a['slug']:a for a in articles}
 urls=[]
 person={'@type':'Person','@id':ORIGIN+'/#rachel','name':'Rachel Boyer','jobTitle':'Licensed Marriage and Family Therapist','url':ORIGIN+'/','image':ORIGIN+settings['headshot'] if settings['headshot'].startswith('/') else settings['headshot'],'email':settings['email'],'telephone':settings['phone']}
 for path in sorted(out.rglob('*.html')):
  rel=path.relative_to(out).as_posix()
  if rel.startswith('admin/') or rel=='404.html' or re.fullmatch(r'google[a-f0-9]+\.html',rel):continue
  route='/' if rel=='index.html' else '/reflections/' if rel=='reflections/index.html' else '/'+rel.removesuffix('.html')
  canonical=ORIGIN+route;urls.append(canonical)
  document=path.read_text()
  title=html.unescape(re.search(r'<title>(.*?)</title>',document,re.S)[1])
  desc=re.search(r'<meta\b(?=[^>]*\bname=["\']description["\'])(?=[^>]*\bcontent=["\']([^"\']*)["\'])[^>]*>',document,re.S)
  description=html.unescape(desc[1]) if desc else title
  document=re.sub(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>','',document)
  webpage={'@type':'WebPage','@id':canonical+'#page','url':canonical,'name':title,'description':description,'inLanguage':'en-US','isPartOf':{'@id':ORIGIN+'/#website'},'about':{'@id':ORIGIN+'/#rachel'}}
  graph=[person,{'@type':'WebSite','@id':ORIGIN+'/#website','url':ORIGIN+'/','name':'Rachel Boyer, LMFT','inLanguage':'en-US'},webpage]
  slug=route.strip('/')
  if slug in article_map:
   a=article_map[slug]
   graph.append({'@type':'BlogPosting','headline':a['title'],'description':a['summary'],'datePublished':a['date'][:10],'author':{'@id':ORIGIN+'/#rachel'},'mainEntityOfPage':{'@id':canonical+'#page'}})
  schema=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')
  metadata='<link rel="canonical" href="'+esc(canonical)+'"><meta name="theme-color" content="#eee8f3"><meta property="og:type" content="'+('article' if slug in article_map else 'website')+'"><meta property="og:site_name" content="Rachel Boyer, LMFT"><meta property="og:title" content="'+esc(title)+'"><meta property="og:description" content="'+esc(description)+'"><meta property="og:url" content="'+esc(canonical)+'"><meta property="og:image" content="'+esc(person['image'])+'"><meta property="og:image:alt" content="Rachel Boyer, LMFT"><meta name="twitter:card" content="summary"><script type="application/ld+json">'+schema+'</script>'
  document=document.replace('</head>',metadata+'</head>',1)
  if rel=='reflections/index.html':document=document.replace('<main class="section">','<main class="section" id="main-content">')
  path.write_text(document)
 (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+esc(url)+'</loc></url>\n' for url in urls)+'</urlset>\n')
 (out/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
