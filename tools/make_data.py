import json,re,os,sys
sys.path.insert(0,'/home/claude/build')
Z=json.load(open('/home/claude/ref/321ot/tools/zhmap.json',encoding='utf8'))
def t2s(s): return ''.join(Z['t2s'].get(c,c) for c in s)
OUT='/home/claude/321devotion'
os.makedirs(OUT+'/data',exist_ok=True)
L=json.load(open('lessons_zh.json',encoding='utf8'))
BKS={'馬太福音':('马太福音','Matthew','matthew'),'馬可福音':('马可福音','Mark','mark'),'路加福音':('路加福音','Luke','luke'),'約翰福音':('约翰福音','John','john'),'使徒行傳':('使徒行传','Acts','acts')}
# WEB
WEB={}
base='/tmp/web/node_modules/world-english-bible/json/'
for zh,(zs,en,fn) in BKS.items():
    d=json.load(open(base+fn+'.json',encoding='utf8')); ch={}
    for x in d:
        if x.get('type') in ('paragraph text','line text') and 'verseNumber' in x:
            c=str(x['chapterNumber']); v=str(x['verseNumber'])
            ch.setdefault(c,{}); ch[c][v]=(ch[c].get(v,'')+' '+x['value'].strip()).strip() if v in ch[c] else x['value'].strip()
    WEB[en]=ch
json.dump(WEB,open('web_nt.json','w'),ensure_ascii=False)
def endash(s): return s.replace('～','–')
def mk(n,d):
    d=dict(d); d.pop('_bk',None); d['ref']=endash(d['ref']); return d
def conv(o,f):
    if isinstance(o,str): return f(o)
    if isinstance(o,list): return [conv(x,f) for x in o]
    if isinstance(o,dict): return {k:conv(v,f) for k,v in o.items()}
    return o
def en_ref(ref):
    m=re.match(r'^(\S+) (.+)$',ref); return BKS[m.group(1)][1]+' '+m.group(2)
def web_verses(ref):
    m=re.match(r'^(\S+) (\d+):(\d+)(?:[–～](?:(\d+):)?(\d+))?$',ref)
    bk=BKS[m.group(1)][1]; c1=int(m.group(2)); v1=int(m.group(3))
    if m.group(5): c2=int(m.group(4) or c1); v2=int(m.group(5))
    else: c2,v2=c1,v1
    out=[]
    for c in range(c1,c2+1):
        vs=WEB[bk].get(str(c),{})
        a=v1 if c==c1 else 1; b=v2 if c==c2 else max(map(int,vs)) if vs else 0
        for v in range(a,b+1):
            if str(v) in vs: out.append([c,v,vs[str(v)]])
    return out
ns=sorted(int(k) for k in L)
zh={};zs={};en={}
miss=[]
for n in ns:
    d=mk(n,L[str(n)]); zh[n]=d; zs[n]=conv(d,t2s)
    e=json.loads(json.dumps(d,ensure_ascii=False))
    bk=d['th']; e['th']=BKS[bk][1]; e['ref']=en_ref(d['ref']); e['t']='Devotion %d'%n
    wv=web_verses(d['ref']); 
    if wv: e['v']=wv
    else: miss.append(n)
    e['pend']=1
    en[n]=e
print('web verses missing for',miss[:10],len(miss))
def first(d): return (d['v'][0][2] if d['v'] else '')[:60]
def idxrow(d,keep_t=True): return [d['n'],d['t'],d['ref'],first(d),d['th'],d['sq']]
for name,dd in (('zh',zh),('zs',zs),('en',en)):
    json.dump([idxrow(dd[n]) for n in ns],open(f'{OUT}/data/idx-{name}.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    chunks={}
    for n in ns: chunks.setdefault((n-1)//50,[]).append(dd[n])
    for k,arr in chunks.items():
        json.dump(arr,open(f'{OUT}/data/{name}-{k:02d}.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print('chunks',sorted(chunks))
json.dump(ns,open('built_ns.json','w'))
json.dump([n for n in ns],open(OUT+'/pending_en.json','w'))
