import re,json,os,shutil,sys
S='/home/claude/ref/321soul'; O='/home/claude/321devotion'
for f in os.listdir(S):
    if f in ('data','.git','README.md'): continue
    p=S+'/'+f
    if os.path.isfile(p): shutil.copy(p,O+'/'+f)
VER='2026.1121.2200-qt1'
OLDV=json.load(open(S+'/version.json'))['v']
def rep_zh(s):
    for a,b in [('停下來吃一份心靈快餐','停下來與主相會'),('停下来吃一份心灵快餐','停下来与主相会'),
                ('繼續天天吃快餐','繼續天天靈修'),('继续天天吃快餐','继续天天灵修'),
                ('321心靈快餐','321QT'),('321心灵快餐','321QT'),
                ('心靈快餐','靈修會主'),('心灵快餐','灵修会主'),('心[靈灵]快餐','[靈灵]修[會会]主'),
                ('讀快餐時','讀靈修時'),('读快餐时','读灵修时'),('今日快餐','今日靈修'),('这篇快餐','这篇灵修'),('這篇快餐','這篇靈修'),
                ('快餐','靈修')]:
        s=s.replace(a,b)
    return s
def rep_en(s):
    for a,b in [('Good afternoon. Pause and enjoy a Soul Snack.','Good afternoon. Pause and meet with the Lord.'),
                ('321 Soul Snack','321QT'),('Soul Snack No.','Devotion No.'),('Soul Snacks','Devotions'),('Soul Snack','Devotion'),
                ('Today\'s Snack','Today\'s Devotion'),('Random snack','Random devotion'),('Starred snacks','Starred devotions'),
                ('snacks','devotions'),('snack','devotion'),('Snack','Devotion'),('truth-snack-backup-','321qt-backup-')]:
        s=s.replace(a,b)
    return s
def sub_all(s,lang):
    s=rep_zh(s)
    s=s.replace('soul321','qt321').replace("app: 'soul'","app: 'qt'")
    return s
# app.js
a=open(O+'/app.js',encoding='utf8').read()
a=sub_all(a,'zh')
a=a.replace("truth-snack-backup-","321qt-backup-")
a=a.replace(OLDV,VER)
# range chips
old="for (var s = 1; s < 9; s++) h += '<button class=\"chip' + (LST.seg === s ? ' on' : '') + '\" data-act=\"lseg\" data-v=\"' + s + '\">' + Math.max(s * 100 + 1, 160) + '–' + Math.min(s * 100 + 100, 825) + '</button>';"
assert old in a
new="var MAXN = IDX && IDX.length ? IDX[IDX.length - 1][0] : 795; for (var s = 0; s * 100 < MAXN; s++) h += '<button class=\"chip' + (LST.seg === s ? ' on' : '') + '\" data-act=\"lseg\" data-v=\"' + s + '\">' + (s * 100 + 1) + '–' + Math.min(s * 100 + 100, MAXN) + '</button>';"
a=a.replace(old,new)
a=a.replace("var YT_LIST = 'PLid55ck_AyA2YwqTBhkMrx0mDtUtlwo8B'","var YT_LIST = 'PLid55ck_AyA128dNw_385uXINWgG7YRpr'")
open(O+'/app.js','w',encoding='utf8').write(a)
for f in ['lang-zs.json']:
    s=open(O+'/'+f,encoding='utf8').read(); s=rep_zh(s); s=s.replace(OLDV,VER); open(O+'/'+f,'w',encoding='utf8').write(s)
s=open(O+'/lang-en.json',encoding='utf8').read(); s=rep_zh(s); s=rep_en(s); open(O+'/lang-en.json','w',encoding='utf8').write(s)
json.load(open(O+'/lang-zs.json',encoding='utf8')); json.load(open(O+'/lang-en.json',encoding='utf8'))
# index.html
h=open(O+'/index.html',encoding='utf8').read(); h=rep_zh(h)
h=h.replace('每日靈修會主：經文、信息','每日新約靈修：經文、解說').replace('國度321空中團契・每天一份靈修會主','國度321空中團契・新約靈修會主')
open(O+'/index.html','w',encoding='utf8').write(h)
# manifest
m=json.load(open(O+'/manifest.json',encoding='utf8'))
m['name']='321QT 新約靈修會主'; m['short_name']='321QT'; m['description']='國度321空中團契・新約靈修會主（每日靈修）'
json.dump(m,open(O+'/manifest.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
# sw.js
w=open(O+'/sw.js',encoding='utf8').read(); w=rep_zh(w).replace('soul321','qt321').replace(OLDV,VER)
w=w.replace("for (var i = 3; i < 17; i++) ks.push(i);","for (var i = 0; i < 16; i++) ks.push(i);")
open(O+'/sw.js','w',encoding='utf8').write(w)
json.dump({'v':VER},open(O+'/version.json','w'))
print('app built')
