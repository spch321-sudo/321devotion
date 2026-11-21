import json,re,sys
sys.path.insert(0,'/home/claude/build')
from parse import parse_ref,fmt_ref,s2t
acts=json.load(open('/home/claude/acts_drive.json',encoding='utf8'))
VERSE=re.compile(r'^(?:(\d+)[:：])?(\d+)\s+(.+)$')
def clean(l): return l.replace('\\*','*').replace('\\.','.').replace('\\-','-').strip()
out={}; bad=[]
for f in acts:
    t=f['title']; m=re.search(r'主(\d+)-徒',t)
    if not m: continue
    n=int(m.group(1))
    L=[clean(l) for l in f['contentSnippet'].split('\n')]
    # ref
    hm=re.search(r'使徒行傳\s*(\d+):(\d+)(?:～(?:(\d+):)?(\d+))?',L[0])
    if not hm: 
        for l in L[:8]:
            hm=re.search(r'經文：使徒行傳\s*(\d+):(\d+)(?:～(?:(\d+):)?(\d+))?',l)
            if hm: break
    if not hm: bad.append((n,'noref')); continue
    c1=int(hm.group(1)); v1=int(hm.group(2)); c2=int(hm.group(3) or c1); v2=int(hm.group(4) or v1)
    ref=fmt_ref('使徒行傳',c1,v1,c2,v2)
    # find sections
    def idx(pred,start=0):
        for k in range(start,len(L)):
            if pred(L[k]): return k
        return None
    ig=idx(lambda l: l.startswith('經文：'))
    i=ig+1 if ig is not None else 2
    verses=[]; cur=c1; last=None
    while i<len(L):
        l=L[i]
        if not l:
            j=i
            while j<len(L) and not L[j]: j+=1
            if j<len(L) and VERSE.match(L[j]) and verses and len(L[j])<600 and not L[j].startswith(('321',)): i=j; continue
            break
        mm=VERSE.match(l)
        if not mm: break
        c,v,tx=mm.group(1),int(mm.group(2)),mm.group(3)
        if c: cur=int(c)
        elif last is not None and v<last and c2>cur: cur+=1
        last=v; verses.append([cur,v,tx]); i+=1
    ia=idx(lambda l: l=='生命的回應',i)
    ip=idx(lambda l: l in ('同心禱告','禱告','一起禱告') or l.endswith('禱告') and len(l)<8,ia or i)
    iq=idx(lambda l: l.startswith('默想題目'),ip or i)
    if None in (ia,ip,iq): bad.append((n,'sections',ia,ip,iq)); continue
    # body
    paras=[];cur_l=[]
    def flush():
        global cur_l
        if cur_l: paras.append(''.join(cur_l)); cur_l=[]
    for l in L[i:ia]:
        if not l: flush(); continue
        if l.startswith('* '): flush(); paras.append('• '+l[2:]); continue
        cur_l.append(l)
    flush()
    a=[]
    for l in L[ia+1:ip]:
        if l.startswith('* '):
            tx=l[2:]; k=tx.find('：')
            a.append([tx[:k],tx[k+1:]] if 0<k<30 else ['',tx])
    pr='\n'.join(l for l in L[ip+1:iq] if l)
    q=[re.sub(r'^\d+\.\s*','',l) for l in L[iq+1:] if l]
    out[n]=dict(n=n,t='靈修會主 %d'%n,ref=ref.replace('～','～'),v=verses,b=paras,a=a,q=q,pr=pr,dc='',ah='生命的回應',th='使徒行傳',sq='',_bk='使徒行傳')
print(len(out),bad[:10])
vb=[(n,d['ref'],len(d['v'])) for n,d in out.items() if not d['v']]; print('noverse',vb[:10])
print(sum(1 for d in out.values() if len(d['a'])!=5),'a!=5', sum(1 for d in out.values() if len(d['q'])!=2),'q!=2')
L0=json.load(open('lessons_zh.json',encoding='utf8'))
for n,d in out.items(): L0[str(n)]=d
json.dump(L0,open('lessons_zh.json','w'),ensure_ascii=False)
print('total',len(L0)); print(json.dumps(out[696],ensure_ascii=False)[:700])
