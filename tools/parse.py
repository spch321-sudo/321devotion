import json,re,collections,sys
Z=json.load(open('/home/claude/ref/321ot/tools/zhmap.json',encoding='utf8'))
def t2s(s): return ''.join(Z['t2s'].get(c,c) for c in s)
def s2t(s):
    out=[]
    for i,c in enumerate(s):
        nx=s[i+1] if i+1<len(s) else ''; pv=s[i-1] if i else ''
        out.append(Z['bi'].get(c+nx) or Z['bp'].get(pv+c) or Z['s2t'].get(c,c))
    return ''.join(out)
files=json.load(open('/home/claude/all_drive.json',encoding='utf8'))
by=collections.defaultdict(list)
for f in files:
    m=re.search(r'(?:會主|会主)\s*(\d+)',f['title'])
    if not m: continue
    by[int(m.group(1))].append(f)
def prio(f):
    t=f['title']
    if t.endswith('.txt'): return 0
    if '繁' in t: return 1
    return 2
CN={'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
def cn(s):
    if s.isdigit(): return int(s)
    if '百' in s:
        a,b=s.split('百'); return (CN[a] if a else 1)*100+(cn(b) if b else 0)
    if '十' in s:
        a,b=s.split('十'); return (CN[a] if a else 1)*10+(CN[b] if b else 0)
    return CN[s]
BK={'太':'馬太福音','可':'馬可福音','路':'路加福音','約':'約翰福音','约':'約翰福音','徒':'使徒行傳'}
def pref(s):
    s=s.replace('：',':').replace('_',':').replace('—','-').replace('–','-').replace('～','-').replace('~','-').replace('至','-').replace('﹣','-')
    return s
def parse_ref(raw):
    """raw like 約5:44 / 太21:28～32 / 太 1：1-17 / 太五1-12 / 路22:30至23:11"""
    s=pref(raw).strip()
    m=re.match(r'^([太可路約约徒])\s*(\d+|[一二三四五六七八九十百]+)\s*:?\s*(.*)$',s)
    if not m: return None
    bk=BK[m.group(1)]; ch=cn(m.group(2)); rest=m.group(3).strip(' .txt')
    rest=rest.replace(' ','')
    m2=re.match(r'^(\d+)(?:-(\d+)(?::(\d+))?)?(?:-(\d+))?',rest)
    if not m2: return None
    v1=int(m2.group(1)); a=m2.group(2); b=m2.group(3); c=m2.group(4)
    ch2=ch; v2=v1
    if a and b: ch2=int(a); v2=int(b)
    elif a: v2=int(a)
    return bk,ch,v1,ch2,v2
def fmt_ref(bk,ch,v1,ch2,v2):
    if ch==ch2: return f'{bk} {ch}:{v1}' + (f'～{v2}' if v2!=v1 else '')
    return f'{bk} {ch}:{v1}～{ch2}:{v2}'
GREET=re.compile(r'^親愛的家人們平安')
VERSE=re.compile(r'^\s*(?:(\d+)[:：])?(\d+)\s*(.+)$')
def parse(n,title,text):
    text=text.replace('\r','')
    lines=[l.rstrip() for l in text.split('\n')]
    L=[l.strip() for l in lines]
    # header
    hdr=None
    for i,l in enumerate(L):
        if l: hdr=i; break
    head=L[hdr] if hdr is not None else ''
    # ref from filename after number
    fm=re.search(r'(?:會主|会主)\s*\d+\s*[-—－]?\s*(.*?)(?:（.*?）)?(?:\s*txt)?\.(?:txt|docx)$',title)
    raw=fm.group(1) if fm else ''
    r=parse_ref(raw) if raw else None
    if not r:
        hm=re.search(r'[-—]\s*([太可路約约徒][^\s]*)',head); 
        if hm: r=parse_ref(hm.group(1))
    # greet fallback
    gi=next((i for i,l in enumerate(L) if GREET.match(l)),None)
    if not r and gi is not None:
        m=re.search(r'(馬太福音|馬可福音|路加福音|約翰福音|使徒行傳)第([一二三四五六七八九十百\d]+)章(?:第)?(\d+)(?:至(\d+)節|節)?',L[gi])
        if m:
            bk=m.group(1); ch=cn(m.group(2)); v1=int(m.group(3)); v2=int(m.group(4) or v1); r=(bk,ch,v1,ch,v2)
    if not r: return None,'noref'
    bk,ch,v1,ch2,v2=r
    # sections
    start=(gi+1) if gi is not None else (hdr+1)
    i=start; verses=[]; curch=ch; lastv=None
    # skip blanks
    while i<len(L) and not L[i]: i+=1
    if i<len(L) and re.match(r'^(馬太福音|馬可福音|路加福音|約翰福音|使徒行傳)\s*\d+[:：]\d+',L[i]):
        i+=1
        while i<len(L) and not L[i]: i+=1
    if i<len(L) and not VERSE.match(L[i]):
        j=i+1
        while j<len(L) and not L[j]: j+=1
        mm=VERSE.match(L[j]) if j<len(L) else None
        if mm and mm.group(1) and int(mm.group(2))==v1+1 and len(L[i])<400:
            verses.append([ch,v1,L[i]]); lastv=v1; i=j
    while i<len(L):
        l=L[i]
        if not l: 
            # allow blank between verses
            j=i
            while j<len(L) and not L[j]: j+=1
            if j<len(L) and VERSE.match(L[j]) and verses: i=j; continue
            break
        m=VERSE.match(l)
        if m and not m.group(1):
            vv=int(m.group(2)); hasws=bool(re.match(r'^\s*\d+\s',l))
            if not (hasws or vv==(lastv if lastv is not None else v1-1)+1): m=None
        if not m: 
            if verses and not VERSE.match(l) and verses[-1][2] and not re.match(r'^[一二三四五六七八九十]+、',l) and len(l)<200 and i+1<len(L) and VERSE.match(L[i+1] if L[i+1] else 'x'):
                verses[-1][2]+=l; i+=1; continue
            break
        c,v,tx=m.group(1),int(m.group(2)),m.group(3)
        if len(tx)<2 and not re.search('[一-鿿]',tx): break
        if c: curch=int(c)
        elif lastv is not None and v<lastv and ch2>curch: curch+=1
        lastv=v
        verses.append([curch,v,tx.strip()]); i+=1
    # remaining
    rest=L[i:]
    # find sections
    def idx(pred):
        for k,l in enumerate(rest):
            if pred(l): return k
        return None
    ip=idx(lambda l: re.match(r'^讓我們一起禱告|^讓我們(?:一同|一起)?禱告|^禱告[:：]?$',l))
    iq=idx(lambda l: l.startswith('默想題目') or l.startswith('默想：'))
    bless=idx(lambda l: '感謝聖靈引導' in l[:8])
    end_body=min([k for k in (ip,iq,bless) if k is not None] or [len(rest)])
    body_lines=rest[:end_body]
    paras=[];cur=[]
    def flush():
        nonlocal cur
        if cur:
            out=''
            for ln in cur:
                if out and not re.search(r'[，。！？；：、」）』…—─]$',out): out+='；' if not ln.startswith(('「','（')) else ''
                out+=ln
            paras.append(out); cur=[]
    for l in body_lines:
        if not l: flush(); continue
        if re.match(r'^(?:[•·‧\-\*]|\d+[\.、\)）])\s*',l) or re.match(r'^[一二三四五六七八九十]+、',l):
            flush(); paras.append(l); continue
        cur.append(l)
    flush()
    dc=''
    if bless is not None: dc=rest[bless]
    pr=''
    if ip is not None:
        e=iq if (iq is not None and iq>ip) else len(rest)
        pl=[l for l in rest[ip+1:e] if l]
        if bless is not None and bless>ip: pl=[l for l in pl if '感謝聖靈引導' not in l[:8]]
        pr=''.join(pl)
    q=[]
    if iq is not None:
        ql=[l for l in rest[iq:] if l]
        first=ql[0]; first=re.sub(r'^默想題目[:：]?\s*','',first)
        ql=([first] if first else [])+ql[1:]
        for l in ql:
            l=re.sub(r'^\d+[\.、\)）]\s*','',l); l=re.sub(r'^\d+(?=[\u4e00-\u9fff])','',l)
            q.append(l)
        # merge: if few lines and each ends w/o ？ merge
        q=[x for x in q if x]
    if not verses and paras and re.match(r'^[「“『"]',paras[0]) and (len(paras[0])>20):
        verses=[[ch,v1,s2t(paras[0].strip('“”"'))]]; paras=paras[1:]
    ref=fmt_ref(bk,ch,v1,ch2,v2)
    return dict(n=n,t='靈修會主 %d'%n,ref=ref,v=verses,b=paras,a=[],q=q,pr=pr,dc=dc,ah='',th=bk,sq='',_bk=bk),None
if __name__=='__main__':
    src=json.load(open('/home/claude/src_text.json',encoding='utf8'))
