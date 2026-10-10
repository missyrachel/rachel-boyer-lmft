"""Build the practice website from Decap-managed content. No client data is stored."""
import argparse,html,json,os,re,shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import markdown,bleach
import seo

ROOT=Path(__file__).resolve().parent
ALLOWED=['p','br','strong','em','a','ul','ol','li','blockquote','h2','h3','h4','hr','code','pre','img']
ATTRS={'a':['href','title'],'img':['src','alt','title']}
def esc(value):return html.escape(str(value),quote=True)
def load(path):return json.loads((ROOT/path).read_text())
def md(value):
 return bleach.clean(markdown.markdown(str(value),extensions=['sane_lists']),tags=ALLOWED,attributes=ATTRS,protocols=['https','http','mailto','tel'],strip=True)
def text(value):return bleach.clean(str(value),tags=[],strip=True)
def safe_url(value,schemes=('https',),local=False):
 value=str(value)
 parsed=urlsplit(value)
 if local and value.startswith('/') and not value.startswith('//') and not parsed.scheme and '..' not in parsed.path.split('/') and '\\' not in value:return value
 if parsed.scheme not in schemes or not parsed.netloc or parsed.username or parsed.password:raise ValueError('Invalid URL: '+value)
 return value
def fill(template,values):
 def replace(m):
  if m[1] not in values:raise ValueError('Unresolved template field: '+m[1])
  return values[m[1]]
 return re.sub(r'\{\{([a-zA-Z0-9_.]+)\}\}',replace,template)
def money(value):
 value=float(value)
 if not 0<=value<=100000:raise ValueError('Fee out of range')
 return '$'+format(value,',.2f').rstrip('0').rstrip('.')
def minutes(value):
 value=int(value)
 if not 1<=value<=1440:raise ValueError('Invalid session length')
 return str(value)
def attrs(values):
 return ''.join(' '+k+'="'+esc(' '.join(v) if isinstance(v,list) else v)+'"' for k,v in values.items())
def field(value,meta):
 body=md(value);tag=meta['tag'];at=attrs(meta['attrs'])
 if re.fullmatch(r'<p>.*</p>',body,flags=re.S) and body.count('<p>')==1:
  body=body[3:-4]
 elif tag=='p':tag='div'
 if meta['tag'].startswith('h'):
  body=bleach.clean(body,tags=['strong','em','a','br'],attributes={'a':['href','title']},strip=True)
 return '<'+tag+at+'>'+body+'</'+tag+'>'
def cards(articles):
 return ''.join('<article class="card reflection-card" data-search="'+esc(a['title']+' '+a['summary']+' '+a['category'])+'"><p class="eyebrow">'+esc(a['category'])+'</p><h3><a href="/'+a['slug']+'">'+esc(a['title'])+'</a></h3><p>'+esc(a['summary'])+'</p><a class="btn ghost" href="/'+a['slug']+'">Read reflection</a></article>' for a in articles)

def build(preview=False):
 settings=load('content/settings.json')
 repo=os.environ.get('CMS_REPOSITORY','').strip()
 repo_file=ROOT/'cms/repository.json'
 if not repo and repo_file.exists():repo=load('cms/repository.json').get('repository','')
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+',repo):
  if not preview:raise ValueError('GitHub not connected. Run python3 configure.py OWNER/REPOSITORY first, or set CMS_REPOSITORY in Netlify.')
  repo=''
 email=settings['email'].strip()
 if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+',email):raise ValueError('Invalid email')
 phone=re.sub(r'\D','',settings['phone'])
 if len(phone)==10:phone='1'+phone
 if not 10<=len(phone)<=15:raise ValueError('Invalid phone number')
 values={key:esc(value) for key,value in settings.items()}
 values.update(email_href=esc('mailto:'+email),phone_href='tel:+'+phone,booking_url=esc(safe_url(settings['booking_url'])),headshot=esc(safe_url(settings['headshot'],local=True)))
 fee_rows=[]
 for kind,label in [('individual','Individual therapy'),('couples','Couples / relationship therapy'),('breathwork','Neurodynamic breathwork')]:
  fee_rows.append(label+' sessions ('+minutes(settings[kind+'_minutes'])+' minutes): <strong>'+money(settings[kind+'_fee'])+'</strong>')
 values['fees_html']='<p>'+'<br>'.join(fee_rows)+'</p>'
 values['hours_html']='<p>Monday–Friday: <strong>'+esc(settings['weekday_hours'])+'</strong><br>Saturday: <strong>'+esc(settings['saturday_hours'])+'</strong><br>Sunday: <strong>'+esc(settings['sunday_hours'])+'</strong></p>'
 values['breathwork_price_html']='<p>A typical neurodynamic breathwork session is <strong>'+minutes(settings['breathwork_minutes'])+' minutes</strong> and includes preparation, the guided breathwork experience, and time for integration afterward. Investment for a '+minutes(settings['breathwork_minutes'])+'-minute breathwork session is <strong>'+money(settings['breathwork_fee'])+'</strong>.</p>'
 render_map=load('cms/render-map.json')
 for path in sorted((ROOT/'content/pages').glob('*.json')):
  for key,value in json.loads(path.read_text()).items():
   name=path.stem+'.'+key
   values[name]=field(value,render_map[name])
 articles=[]
 for path in sorted((ROOT/'content/articles').glob('*.json')):
  a=json.loads(path.read_text());slug=path.stem
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug) or slug in ['index','admin','reflections','404']:raise ValueError('Invalid or reserved article filename: '+slug)
  if not isinstance(a.get('published',False),bool):raise ValueError('Published must be a boolean')
  if not a.get('published',False):continue
  date.fromisoformat(a['date'][:10]);a['slug']=slug
  for key in ['title','summary','category','body']:
   if not isinstance(a.get(key),str) or not a[key].strip():raise ValueError('Missing article '+key)
  articles.append(a)
 articles.sort(key=lambda a:(a['date'],a['slug']),reverse=True)
 listing=cards(articles)
 values['reflections_html']='<section id="reflection" class="section section-alt"><div class="container"><p class="eyebrow">Reflections & resources</p><h2>A little space for reflection.</h2><p>Thoughts on connection, mindfulness, and living with greater self-compassion.</p><div class="cards-3">'+cards(articles[:3])+'</div><p><a class="btn ghost" href="/reflections/">Browse all reflections</a></p></div></section>'
 specialties=seo.read_specialties(ROOT)
 values['specialties_html']=seo.specialty_cards(specialties)
 # Clear only generated output, including removed/unpublished articles.
 out=ROOT/'dist'
 if out.exists():shutil.rmtree(out)
 shutil.copytree(ROOT/'static',out)
 (out/'index.html').write_text(fill((ROOT/'templates/home.html').read_text(),values))
 template=(ROOT/'templates/article.html').read_text()
 for a in articles:
  actions='<a class="btn ghost" href="/reflections/">All reflections</a><a class="btn ghost" href="/#contact">Contact Rachel</a>'
  if a.get('pdf'):
   pdf=safe_url(a['pdf'],local=True)
   actions+='<a class="btn ghost" href="'+esc(pdf)+'" download>'+esc(a.get('pdf_label') or 'Download reflection (PDF)')+'</a>'
  data={'article_title':esc(a['title']),'article_summary':esc(a['summary']),'article_canonical':'https://rachelboyerlmft.com/'+a['slug'],'article_body':md(a['body']),'article_actions':actions}
  (out/(a['slug']+'.html')).write_text(fill(template,data))
 header=re.search(r'<header\b.*?</header>',(out/'index.html').read_text(),re.S)[0]
 footer=re.search(r'<footer\b.*?</footer>',(out/'index.html').read_text(),re.S)[0]
 header=header.replace('href="#','href="/#');footer=footer.replace('href="#','href="/#')
 (out/'reflections').mkdir()
 (out/'reflections/index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reflections | Rachel Boyer, LMFT</title><meta name="description" content="Reflections on relationships, mindfulness, and self-compassion by Rachel Boyer, LMFT."><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/cms-site.css"></head><body>'+header+'<a class="skip-link" href="#main-content">Skip to content</a><main id="main-content" class="section"><div class="container"><p class="eyebrow">Reflections & resources</p><h1>A little space for reflection.</h1><label for="search-reflections">Find a reflection</label><input id="search-reflections" type="search" placeholder="Search by title, topic, or category"><p id="search-status" role="status" aria-live="polite"></p><div class="cards-3" id="reflection-list">'+listing+'</div><p id="no-results" hidden>No reflections match your search. Try another word.</p></div></main>'+footer+'<script src="/reflections.js" defer></script></body></html>')
 if repo:
  config=load('cms/schema.json');config['backend']={'name':'github','repo':repo,'branch':'main','site_domain':'rachelboyerlmft.com'}
  (out/'admin/config.yml').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
 else:
  (out/'admin/index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Editor setup pending</title></head><body><h1>Editor setup pending</h1><p>The website files are prepared. GitHub and Netlify authentication must be connected before the editor can save or publish.</p><a href="/">View prepared website</a></body></html>')
 (out/'404.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Rachel Boyer</title><link rel="stylesheet" href="/styles.css"></head><body><main class="container section"><h1>That page could not be found.</h1><p><a href="/">Return to Rachel’s website</a></p></main></body></html>')
 seo.finalize(ROOT,out,settings,specialties,articles,md,header,footer)
 print(f'Built {len(articles)} published reflection(s), {len(specialties)} specialty pages, editable sections, search metadata and sitemap. Editor '+('configured; login requires Netlify OAuth.' if repo else 'awaiting GitHub connection.'))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');args=parser.parse_args();build(args.preview)
