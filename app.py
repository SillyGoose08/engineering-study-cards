import html, sqlite3, random
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import streamlit as st

DB=Path('flashcards.db')
st.set_page_config(page_title='Engineering Study Cards',page_icon='🧠',layout='wide',initial_sidebar_state='expanded')

st.markdown('''<style>
:root{--bg:#06101d;--panel:#0d1b2d;--panel2:#10233b;--border:#203854;--muted:#9aa8bd;--purple:#7657ff;--blue:#258cff;--green:#2bd47f;--red:#ff5a6f;--gold:#ffbf3f}
.stApp{background:radial-gradient(circle at 70% 0,rgba(98,65,255,.14),transparent 28%),linear-gradient(180deg,#07111f,#050d18);color:#f5f7ff}
.block-container{max-width:1480px;padding-top:1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0c1b2f,#091525);border-right:1px solid var(--border)}
[data-testid="stSidebar"] label{font-weight:650;color:#e3ebf8!important}
[data-testid="stSidebar"] .stRadio label{border:1px solid var(--border);border-radius:10px;padding:.45rem .55rem;margin:.15rem 0;background:#0a1727}
[data-testid="stSidebar"] .stRadio label:has(input:checked){border-color:#6d57ff;background:linear-gradient(90deg,rgba(109,87,255,.28),rgba(37,140,255,.12))}
[data-testid="stSelectbox"]>div>div{background:#081524!important;border-color:var(--border)!important;border-radius:10px!important}
.stButton>button{min-height:44px;border-radius:11px;border:1px solid var(--border);background:#0d1b2d;color:#fff;font-weight:750}
.stButton>button:hover{border-color:#745cff;transform:translateY(-1px)}
button[kind="primary"]{background:linear-gradient(90deg,#5368ff,#762cff)!important;border:none!important;box-shadow:0 8px 26px rgba(96,62,255,.25)}
.stTabs [data-baseweb="tab-list"]{gap:.45rem;border-bottom:1px solid var(--border)}
.stTabs [data-baseweb="tab"]{color:#aab7c9;font-weight:750;border-radius:8px 8px 0 0}
.stTabs [aria-selected="true"]{color:white!important;background:rgba(111,83,255,.12)}
.brand{display:flex;align-items:center;gap:11px;margin-bottom:10px}.brain{font-size:36px}.brand h2{margin:0;font-size:25px}.sub{color:var(--muted);font-size:12px}
.hero{position:relative;overflow:hidden;min-height:145px;border-radius:18px;padding:27px 31px;margin:12px 0 18px;border:1px solid #566dff;background:radial-gradient(circle at 78% 24%,#ff9ac8 0 5%,transparent 5.4%),linear-gradient(128deg,#243ac7,#6c38d6 52%,#ec6fbd);box-shadow:0 16px 45px rgba(22,29,95,.2)}
.hero:before{content:"";position:absolute;left:-3%;right:-3%;bottom:-38px;height:105px;background:linear-gradient(150deg,transparent 0 12%,#183a91 12% 25%,transparent 25% 31%,#153478 31% 47%,transparent 47% 54%,#153b8a 54% 69%,transparent 69% 75%,#0a2455 75%)}
.hero h1,.hero p{position:relative;z-index:2}.hero h1{margin:0;font-size:34px}.hero p{margin:.5rem 0;color:#f2f4ff}.hero .badge{position:absolute;z-index:3;right:22px;top:24px;background:rgba(12,22,62,.62);padding:12px 15px;border:1px solid rgba(255,255,255,.25);border-radius:12px;font-weight:800}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-bottom:18px}.mcard{background:linear-gradient(180deg,#10223a,#0a192b);border:1px solid var(--border);border-radius:15px;padding:16px 18px;min-height:112px}.mlabel{font-size:13px;font-weight:700;color:#dbe5f2}.mval{font-size:29px;font-weight:850;margin-top:9px}.mfoot{font-size:11px;color:var(--muted);margin-top:4px}
.flash{background:linear-gradient(145deg,#fff,#f1f6ff);color:#0b1730;border:1px solid #957eff;border-radius:20px;padding:28px 31px;min-height:300px;box-shadow:0 0 0 1px rgba(45,196,255,.3),0 22px 48px rgba(0,0,0,.2)}.pill{display:inline-block;padding:7px 12px;border-radius:99px;background:#e7e0ff;color:#563cd6;font-size:12px;font-weight:800;margin-right:7px}.pill.blue{background:#dceeff;color:#0c63bf}.count{float:right;color:#5c6c83;font-size:12px;font-weight:700}.question{font-size:28px;line-height:1.34;font-weight:850;margin-top:28px;max-width:780px}.rule{height:1px;background:#d9e0ec;margin:24px 0 18px}.hint{color:#65738b;font-style:italic;line-height:1.55;font-size:14px}.answer{border:1px solid rgba(43,212,127,.72);background:linear-gradient(90deg,rgba(7,63,52,.58),rgba(5,45,48,.58));border-radius:15px;padding:20px 22px;margin-top:17px}.answer strong{color:#3be18e;font-size:19px}.answer p{color:#cfe5df;margin:.4rem 0 0;font-size:13px}
.side{background:linear-gradient(180deg,#0f2036,#0a182a);border:1px solid var(--border);border-radius:15px;padding:16px 17px;margin-bottom:14px}.stitle{font-weight:850;margin-bottom:11px}.big{font-size:24px;font-weight:850;color:#9d90ff}.small{font-size:11px;color:var(--muted)}.qitem{padding:9px 0;border-bottom:1px solid rgba(45,67,94,.55)}.qname{font-size:12px;font-weight:750}.high{color:#ff6175}.med{color:#ffc247}.low{color:#2edc84}.prog{height:10px;border-radius:99px;background:#1b2c47;overflow:hidden;margin-top:10px}.prog>div{height:100%;background:linear-gradient(90deg,#5268ff,#9149ff)}.quote{margin-top:30px;border-left:3px solid #6b50ff;background:rgba(92,71,255,.06);padding:12px 13px;color:#aab7ca;font-style:italic;font-size:12px;line-height:1.6;border-radius:0 10px 10px 0}
[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:12px;overflow:hidden}
@media(max-width:1000px){.metrics{grid-template-columns:repeat(2,1fr)}.hero .badge{display:none}.question{font-size:23px}}
</style>''',unsafe_allow_html=True)

def now(): return datetime.now(timezone.utc).isoformat()
def conn():
    c=sqlite3.connect(DB,check_same_thread=False);c.row_factory=sqlite3.Row;return c

def init():
    c=conn();c.executescript('''CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,topic TEXT,card_type TEXT,front TEXT,back TEXT,hint TEXT,created_at TEXT);CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY AUTOINCREMENT,card_id INTEGER,result TEXT,confidence INTEGER,attempted_at TEXT);''');c.commit()
    cols=[r[1] for r in c.execute('PRAGMA table_info(cards)').fetchall()]
    if 'choices' not in cols: c.execute('ALTER TABLE cards ADD COLUMN choices TEXT');c.commit()
    if c.execute('SELECT COUNT(*) FROM cards').fetchone()[0]==0:
        cards=[
        ('Calc 3','Vector integrals','Recognition','What do you do when integrating a vector-valued function?','Integrate each component separately.','Treat i, j, and k components as separate ordinary integrals.'),
        ('Calc 3','Vector functions','Process',"Given r'(t) and an initial condition r(a), what is the workflow?",'Integrate each component, add constants, then use the initial condition to solve the constants.','Derivative given → integrate → constants → initial condition.'),
        ('Calc 3','Integration patterns','Recognition','You see ∫ t/(t²+1) dt. What method should you recognize?','u-substitution with u=t²+1, because du=2t dt.','Look for derivative-of-denominator over denominator.'),
        ('Calc 3','Integration patterns','Recognition','You see ∫ 1/(1+t²) dt. What antiderivative should you recognize?','arctan(t)+C.','This is a standard inverse trig pattern.'),
        ('Calc 3','Integration patterns','Recognition','You see √t inside an integral. What should you do first?','Rewrite √t as t^(1/2), then use the power rule.','Radicals are easier as exponents.'),
        ('Calc 3','Dot product','Recognition','What should “angle between two vectors” make you think?','Dot product: a·b = |a||b|cosθ.','Dot product produces a scalar and connects to cosθ.'),
        ('Calc 3','Cross product','Recognition','What should “vector perpendicular to two vectors” make you think?','Cross product.','Cross product produces a new vector perpendicular to both inputs.'),
        ('Calc 3','Planes','Process','How do you build a plane equation once you know a point and a normal vector?','Use a(x-x₀)+b(y-y₀)+c(z-z₀)=0.','The normal vector gives a,b,c.'),
        ('Calc 3','Line intersection','Process','How do you find the intersection point of two parametric lines?','Use separate parameters, set x/y/z equal, solve, then plug one parameter back into its line.','Different parameters are allowed for path intersection.'),
        ('Calc 3','Particle motion','Recognition','What is the key difference between path intersection and particle collision?','Collision requires the same point at the same time, so use the same time parameter.','Intersection allows different parameters; collision does not.')]
        c.executemany('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at) VALUES (?,?,?,?,?,?,?)',[(a,b,d,e,f,g,now()) for a,b,d,e,f,g in cards]);c.commit()
    mcqs=[('Common derivatives', 'd/dx(x^5) = ?', '5x^4', ['x^4', '5x^4', '5x^5', 'x^6/6'], 'Power rule: bring 5 down and subtract 1 from the exponent.'), ('Common derivatives', 'd/dx(1/x) = ?', '-1/x^2', ['1/x^2', '-1/x^2', 'ln|x|', '-x'], 'Rewrite 1/x as x^-1.'), ('Common derivatives', 'd/dx(sqrt(x)) = ?', '1/(2sqrt(x))', ['sqrt(x)/2', '1/(2sqrt(x))', '2sqrt(x)', 'x^(-2)'], 'Rewrite sqrt(x) as x^(1/2).'), ('Common derivatives', 'd/dx(ln x) = ?', '1/x', ['ln x', 'x', '1/x', 'e^x'], 'Standard natural-log derivative.'), ('Common derivatives', 'd/dx(e^x) = ?', 'e^x', ['xe^(x-1)', '1/e^x', 'e^x', 'x e^x'], 'e^x is its own derivative.'), ('Common derivatives', 'Which rule is central to d/dx[(x^2+1)^5]?', 'Chain rule', ['Product rule', 'Quotient rule', 'Chain rule', 'Integration by parts'], 'Differentiate the outside, then the inside.'), ('Common integrals', '∫ x^4 dx = ?', 'x^5/5 + C', ['4x^3 + C', 'x^5/5 + C', '5x^5 + C', 'x^4/4 + C'], 'Add 1 to the exponent, then divide by it.'), ('Common integrals', '∫ 1/x dx = ?', 'ln|x| + C', ['1/x^2 + C', 'x ln x + C', 'ln|x| + C', 'e^x + C'], 'This is the special logarithm integral.'), ('Common integrals', '∫ e^x dx = ?', 'e^x + C', ['xe^x + C', 'e^x + C', 'ln(e^x)+C', 'e^(x+1)+C'], 'e^x is its own antiderivative.'), ('Common integrals', '∫ 1/(1+x^2) dx = ?', 'arctan(x) + C', ['arcsin(x)+C', 'ln(1+x^2)+C', 'arctan(x) + C', 'tan(x)+C'], 'Recognize the inverse-tangent pattern.'), ('Common integrals', 'For [F(x)]_a^b, which calculation is correct?', 'F(b) - F(a)', ['F(a)-F(b)', 'F(b)+F(a)', 'F(b)-F(a)', 'F(a)F(b)'], 'Upper bound minus lower bound.'), ('Common integrals', 'What does +C represent?', 'An arbitrary constant', ['The upper bound', 'An arbitrary constant', 'A chain-rule factor', 'The x-intercept'], 'Differentiation loses constants.'), ('Exponentials', 'e^0 = ?', '1', ['0', '1', 'e', 'undefined'], 'Any nonzero base to the zero power is 1.'), ('Exponentials', 'e^(-1) is approximately:', '0.368', ['-2.718', '0', '0.368', '2.718'], 'e^-1 = 1/e.'), ('Exponentials', 'e^(-x) is equivalent to:', '1/e^x', ['-e^x', '1/e^x', 'e^x', 'x/e'], 'Negative exponent means reciprocal.'), ('Exponentials', 'e^a · e^b = ?', 'e^(a+b)', ['e^(ab)', 'e^(a+b)', 'e^(a-b)', '2e^(a+b)'], 'Same base: add exponents when multiplying.'), ('Exponentials', 'd/dx(e^(3x)) = ?', '3e^(3x)', ['e^(3x)', '3e^x', '3e^(3x)', 'e^(3x-1)'], 'Use the chain rule.'), ('Exponentials', '∫ e^(2x) dx = ?', '(1/2)e^(2x) + C', ['2e^(2x)+C', 'e^(2x)+C', '(1/2)e^(2x) + C', 'e^(x^2)+C'], 'Reverse the chain rule: divide by 2.'), ('Natural logs', 'ln(1) = ?', '0', ['1', '0', 'e', 'undefined'], 'Because e^0=1.'), ('Natural logs', 'ln(e) = ?', '1', ['0', '1', 'e', '-1'], 'Because e^1=e.'), ('Natural logs', 'ln(e^x) = ?', 'x', ['e^x', '1/x', 'x', 'ln x'], 'ln and e^x are inverse functions.'), ('Natural logs', 'ln(ab) = ?', 'ln a + ln b', ['ln a · ln b', 'ln a + ln b', 'ln a - ln b', 'a ln b'], 'Product rule for logarithms.'), ('Natural logs', 'ln(a/b) = ?', 'ln a - ln b', ['ln a + ln b', 'ln a / ln b', 'ln a - ln b', 'b ln a'], 'Quotient rule for logarithms.'), ('Natural logs', 'ln(a^k) = ?', 'k ln a', ['(ln a)^k', 'k + ln a', 'k ln a', 'ln(ka)'], 'The exponent moves in front.'), ('Natural logs', 'If ln x = 2, then x = ?', 'e^2', ['2e', 'ln 2', 'e^2', '1/e^2'], 'Exponentiate both sides with base e.'), ('Natural logs', 'd/dx[ln(g(x))] = ?', "g'(x)/g(x)", ['1/g(x)', "g(x)/g'(x)", "g'(x)/g(x)", "ln(g'(x))"], 'Chain rule for ln.'), ('Trig identities', 'Which is the Pythagorean identity?', 'sin^2(theta) + cos^2(theta) = 1', ['sin(theta)+cos(theta)=1', 'sin^2(theta) + cos^2(theta) = 1', 'tan^2(theta)+cos^2(theta)=1', 'sec(theta)+csc(theta)=1'], 'The foundational trig identity.'), ('Trig identities', 'tan(theta) = ?', 'sin(theta)/cos(theta)', ['cos(theta)/sin(theta)', 'sin(theta)/cos(theta)', '1/sin(theta)', '1/cos(theta)'], 'Tangent is sine over cosine.'), ('Trig identities', 'sec(theta) = ?', '1/cos(theta)', ['1/sin(theta)', '1/cos(theta)', 'sin(theta)/cos(theta)', 'cos(theta)/sin(theta)'], 'Secant is reciprocal cosine.'), ('Trig identities', '1 + tan^2(theta) = ?', 'sec^2(theta)', ['csc^2(theta)', 'sec^2(theta)', '1', 'cot^2(theta)'], 'Divide the Pythagorean identity by cos^2(theta).'), ('Trig identities', '1 + cot^2(theta) = ?', 'csc^2(theta)', ['sec^2(theta)', 'csc^2(theta)', 'tan^2(theta)', '1'], 'Divide the Pythagorean identity by sin^2(theta).'), ('Unit circle', 'At 0° (0 rad), (cos theta, sin theta) = ?', '(1, 0)', ['(0, 1)', '(1, 0)', '(-1, 0)', '(0, -1)'], 'Positive x-axis.'), ('Unit circle', 'At 90° (pi/2), (cos theta, sin theta) = ?', '(0, 1)', ['(1, 0)', '(0, 1)', '(-1, 0)', '(0, -1)'], 'Top of the unit circle.'), ('Unit circle', 'sin(pi/4) = ?', 'sqrt(2)/2', ['1/2', 'sqrt(2)/2', 'sqrt(3)/2', '1'], '45° has equal x and y magnitudes.'), ('Unit circle', 'cos(pi/3) = ?', '1/2', ['1/2', 'sqrt(2)/2', 'sqrt(3)/2', '0'], 'pi/3 = 60°.'), ('Unit circle', 'sin(pi/6) = ?', '1/2', ['sqrt(3)/2', 'sqrt(2)/2', '1/2', '1'], 'pi/6 = 30°.'), ('Unit circle', 'In Quadrant II, which signs are correct?', 'sin positive, cos negative', ['sin +, cos +', 'sin positive, cos negative', 'sin -, cos -', 'sin -, cos +'], 'Coordinates are (-,+).'), ('Unit circle', 'In Quadrant IV, which signs are correct?', 'sin negative, cos positive', ['sin negative, cos positive', 'sin +, cos -', 'sin -, cos -', 'sin +, cos +'], 'Coordinates are (+,-).'), ('Trig derivatives & integrals', 'd/dx(sin x) = ?', 'cos x', ['-cos x', 'cos x', 'sin x', '-sin x'], 'Standard trig derivative.'), ('Trig derivatives & integrals', 'd/dx(cos x) = ?', '-sin x', ['sin x', '-sin x', 'cos x', '-cos x'], 'Cosine differentiates to negative sine.'), ('Trig derivatives & integrals', 'd/dx(tan x) = ?', 'sec^2 x', ['csc^2 x', 'sec^2 x', 'sec x tan x', '-csc x cot x'], 'Standard trig derivative.'), ('Trig derivatives & integrals', 'd/dx(sec x) = ?', 'sec x tan x', ['sec^2 x', 'sec x tan x', '-csc x cot x', 'tan x'], 'Standard trig derivative.'), ('Trig derivatives & integrals', 'd/dx(csc x) = ?', '-csc x cot x', ['csc x cot x', '-csc x cot x', 'sec x tan x', '-csc^2 x'], 'Cosecant derivative carries a negative.'), ('Trig derivatives & integrals', 'd/dx(cot x) = ?', '-csc^2 x', ['csc^2 x', '-csc^2 x', 'sec^2 x', '-sec^2 x'], 'Cotangent derivative is negative cosecant squared.'), ('Trig derivatives & integrals', '∫ cos x dx = ?', 'sin x + C', ['-sin x+C', 'sin x + C', 'cos x+C', 'tan x+C'], 'Reverse d/dx(sin x)=cos x.'), ('Trig derivatives & integrals', '∫ sin x dx = ?', '-cos x + C', ['cos x+C', '-cos x + C', 'sin x+C', '-sin x+C'], 'Reverse d/dx(-cos x)=sin x.'), ('Trig derivatives & integrals', '∫ sec^2 x dx = ?', 'tan x + C', ['sec x+C', 'tan x + C', 'cot x+C', '-cot x+C'], 'Reverse d/dx(tan x)=sec^2 x.'), ('Trig derivatives & integrals', '∫ csc^2 x dx = ?', '-cot x + C', ['cot x+C', '-cot x + C', 'csc x+C', 'tan x+C'], 'Reverse d/dx(cot x)=-csc^2 x.'), ('Trig derivatives & integrals', '∫ sec x tan x dx = ?', 'sec x + C', ['tan x+C', 'sec x + C', '-csc x+C', 'sec^2 x+C'], 'Reverse d/dx(sec x)=sec x tan x.'), ('Trig derivatives & integrals', '∫ csc x cot x dx = ?', '-csc x + C', ['csc x+C', '-csc x + C', 'cot x+C', '-cot x+C'], 'Reverse d/dx(csc x)=-csc x cot x.')]
    for top,front,back,choices,hint in mcqs:
        if not c.execute('SELECT 1 FROM cards WHERE front=?',(front,)).fetchone():
            c.execute('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at,choices) VALUES (?,?,?,?,?,?,?,?)',('Math Foundations',top,'Multiple Choice',front,back,hint,now(),'|||'.join(choices)))
    c.commit()
    c.close()

def cards_df():
    c=conn();d=pd.read_sql_query('SELECT * FROM cards ORDER BY subject,topic,id',c);c.close();return d

def stats():
    c=conn();d=pd.read_sql_query('''SELECT c.*,COUNT(a.id) attempts,SUM(CASE WHEN a.result='Correct' THEN 1 ELSE 0 END) correct,SUM(CASE WHEN a.result='Wrong' THEN 1 ELSE 0 END) wrong,AVG(CASE WHEN a.id IS NOT NULL THEN a.confidence END) avg_confidence FROM cards c LEFT JOIN attempts a ON a.card_id=c.id GROUP BY c.id''',c);c.close()
    for x in ['attempts','correct','wrong']: d[x]=d[x].fillna(0).astype(int)
    d['accuracy']=d.apply(lambda r:100*r.correct/r.attempts if r.attempts else None,axis=1)
    d['weakness']=d.apply(lambda r:50 if r.attempts==0 else min(100,18+62*(r.wrong/max(r.attempts,1))+min(r.wrong*4,16)+max(0,3-(r.avg_confidence or 3))*3),axis=1)
    d['mastery']=d.apply(lambda r:0 if r.attempts==0 else max(0,min(100,100-r.weakness)),axis=1)
    return d

def record(cid,result,conf):
    c=conn();c.execute('INSERT INTO attempts(card_id,result,confidence,attempted_at) VALUES (?,?,?,?)',(int(cid),result,int(conf),now()));c.commit();c.close()

def pick(mode,subject,topic,exclude=None):
    d=stats();
    if subject!='All': d=d[d.subject==subject]
    if topic!='All': d=d[d.topic==topic]
    if exclude and len(d)>1: d=d[d.id!=exclude]
    if d.empty:return None
    if mode=='Weakest First':
        p=d.sort_values(['weakness','wrong','attempts'],ascending=[False,False,True]).head(min(12,len(d)));return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    if mode=='Missed Only':
        p=d[d.wrong>0];p=d if p.empty else p;return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    return d.sample(1).iloc[0]

def streak():
    c=conn();r=[x[0] for x in c.execute('SELECT result FROM attempts ORDER BY id DESC').fetchall()];c.close();n=0
    for x in r:
        if x=='Correct':n+=1
        else:break
    return n

def esc(x):return html.escape(str(x),quote=True)
def elapsed(s):
    t=datetime.fromisoformat(s);q=max(0,int((datetime.now(timezone.utc)-t).total_seconds()));return f'{q//60}:{q%60:02d}'

init()
for k,v in {'card_id':None,'show_answer':False,'show_hint':False,'sig':None,'session_start':now(),'session_seen':0,'target':12,'last_card':None,'mc_choice':None}.items():
    if k not in st.session_state:st.session_state[k]=v

with st.sidebar:
    st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
    st.markdown('### Study Controls')
    mode=st.radio('Study mode',['Weakest First','Missed Only','Random'])
    cd=cards_df();subjects=['All']+sorted(cd.subject.unique());subject=st.selectbox('Subject',subjects)
    fd=cd if subject=='All' else cd[cd.subject==subject];topics=['All']+sorted(fd.topic.unique());topic=st.selectbox('Topic',topics)
    if st.button('▶ Start / New Session',type='primary',use_container_width=True):
        st.session_state.session_start=now();st.session_state.session_seen=0;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.rerun()
    st.caption('Weakest First automatically prioritizes the cards you miss most often.')
    st.markdown('<div class="quote">“A little progress every day adds up to big results.”</div>',unsafe_allow_html=True)

sig=(mode,subject,topic)
if sig!=st.session_state.sig:st.session_state.sig=sig;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False

st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Engineering Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
t1,t2,t3,t4=st.tabs(['🏠 Study','▥ Progress','▱ Decks','⚙ Settings'])

with t1:
    st.markdown('<div class="hero"><div class="badge">🎯 Same Effort.<br>Bigger Results.</div><h1>Engineering Study Cards</h1><p>Adaptive flashcards that focus on what you need most.</p></div>',unsafe_allow_html=True)
    d=stats();sc=d.copy();
    if subject!='All':sc=sc[sc.subject==subject]
    if topic!='All':sc=sc[sc.topic==topic]
    a=int(sc.attempts.sum()) if len(sc) else 0;c=int(sc.correct.sum()) if len(sc) else 0;ac=100*c/a if a else 0;w=int((sc.weakness>=60).sum()) if len(sc) else 0;m=float(sc.mastery.mean()) if len(sc) else 0
    st.markdown(f'<div class="metrics"><div class="mcard"><div class="mlabel">📗 Total Attempts</div><div class="mval">{a}</div><div class="mfoot">Every answer improves your model</div></div><div class="mcard"><div class="mlabel">🎯 Accuracy</div><div class="mval">{ac:.0f}%</div><div class="mfoot">Correct across this filter</div></div><div class="mcard"><div class="mlabel">⚠️ Weak Cards</div><div class="mval">{w}</div><div class="mfoot">Priority score ≥ 60</div></div><div class="mcard"><div class="mlabel">📊 Average Mastery</div><div class="mval">{m:.0f}%</div><div class="mfoot">Adaptive mastery score</div></div></div>',unsafe_allow_html=True)
    if st.session_state.card_id is None:
        r=pick(mode,subject,topic,st.session_state.last_card)
        if r is not None:st.session_state.card_id=int(r.id)
    cur=stats();cur=cur[cur.id==st.session_state.card_id]
    if cur.empty:st.info('No cards match the current filters.')
    else:
        r=cur.iloc[0];left,right=st.columns([3.25,1],gap='large')
        with left:
            idx=min(st.session_state.session_seen+1,st.session_state.target);hint=esc(r.hint) if st.session_state.show_hint else 'Try to name the method or recognition cue before revealing the answer.'
            st.markdown(f'<div class="flash"><span class="count">Card {idx} of {st.session_state.target} ☆</span><span class="pill">{esc(r.subject)}</span><span class="pill blue">{esc(r.topic)}</span><div class="question">{esc(r.front)}</div><div class="rule"></div><div class="hint">💡 {hint}</div></div>',unsafe_allow_html=True)
            def advance(result,conf):
                record(r.id,result,conf);st.session_state.last_card=int(r.id);st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.session_seen+=1;st.rerun()
            is_mc=(str(r.card_type)=='Multiple Choice' and 'choices' in r.index and pd.notna(r['choices']) and str(r['choices']).strip())
            if is_mc:
                choices=str(r['choices']).split('|||')
                st.markdown('#### Choose the best answer')
                choice=st.radio('Answer choices',choices,index=None,key=f"mcq_{int(r.id)}",label_visibility='collapsed')
                x,y=st.columns(2)
                if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                if y.button('✓ Submit Answer',type='primary',use_container_width=True,disabled=choice is None):st.session_state.mc_choice=choice;st.session_state.show_answer=True;st.rerun()
                if st.session_state.show_answer and st.session_state.mc_choice is not None:
                    correct=(st.session_state.mc_choice==str(r.back)); icon='✅' if correct else '❌'; msg='Correct!' if correct else f'Not quite — you chose {esc(st.session_state.mc_choice)}.'
                    st.markdown(f'<div class="answer"><strong>{icon} {msg}</strong><p>Correct answer: <b>{esc(r.back)}</b><br>{esc(r.hint)}</p></div>',unsafe_allow_html=True)
                    a1,a2=st.columns(2)
                    if correct:
                        if a1.button('🔵 Got it',use_container_width=True):advance('Correct',3)
                        if a2.button('✅ Easy / automatic',use_container_width=True):advance('Correct',5)
                    else:
                        if a1.button('❌ Need to see this again',use_container_width=True):advance('Wrong',1)
                        if a2.button('🟡 I understand now',use_container_width=True):advance('Wrong',2)
            else:
                x,y=st.columns(2)
                if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                if not st.session_state.show_answer:
                    if y.button('✨ Reveal Answer',type='primary',use_container_width=True):st.session_state.show_answer=True;st.rerun()
                else:
                    st.markdown(f'<div class="answer"><strong>✅ {esc(r.back)}</strong><p>Rate how automatic this felt. Your rating changes how often this card returns.</p></div>',unsafe_allow_html=True)
                    q1,q2,q3,q4=st.columns(4)
                    if q1.button('❌ I missed it\nAgain',use_container_width=True):advance('Wrong',1)
                    if q2.button('🟡 Still learning\nHard',use_container_width=True):advance('Wrong',2)
                    if q3.button('🔵 I got it\nMedium',use_container_width=True):advance('Correct',3)
                    if q4.button('✅ Easy\nMove on',use_container_width=True):advance('Correct',5)
        with right:
            prog=min(100,100*st.session_state.session_seen/max(1,st.session_state.target));st.markdown(f'<div class="side"><div class="stitle">⏱ Current Session</div><div style="display:flex;justify-content:space-between"><div><div class="big">{elapsed(st.session_state.session_start)}</div><div class="small">Time</div></div><div><div class="big">{streak()} 🔥</div><div class="small">Streak</div></div></div></div>',unsafe_allow_html=True)
            qs=sc.sort_values('weakness',ascending=False).head(4);items=''
            for _,z in qs.iterrows():
                cl='high' if z.weakness>=70 else ('med' if z.weakness>=50 else 'low');pr='High Priority' if z.weakness>=70 else ('Medium Priority' if z.weakness>=50 else 'Low Priority');items+=f'<div class="qitem"><div class="qname">{esc(z.topic)}</div><div class="{cl}" style="font-size:10px;font-weight:800">{pr}</div></div>'
            st.markdown('<div class="side"><div class="stitle">Next Up</div>'+items+'</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="side"><div class="stitle">Session Progress</div><div class="big">{st.session_state.session_seen} / {st.session_state.target}</div><div class="prog"><div style="width:{prog:.0f}%"></div></div><div class="small" style="text-align:right;margin-top:5px">{prog:.0f}%</div></div>',unsafe_allow_html=True)

with t2:
    st.markdown('## Progress & Weakness Tracker');st.caption('Higher weakness means the card returns more aggressively.')
    d=stats();g=d.groupby(['subject','topic'],as_index=False).agg(attempts=('attempts','sum'),correct=('correct','sum'),wrong=('wrong','sum'),avg_weakness=('weakness','mean'),avg_mastery=('mastery','mean'));g['accuracy']=g.apply(lambda r:100*r.correct/r.attempts if r.attempts else 0,axis=1);g['Topic']=g.subject+' · '+g.topic
    a,b=st.columns(2);a.bar_chart(g.set_index('Topic')['avg_mastery'],horizontal=True);b.dataframe(g.sort_values('avg_weakness',ascending=False)[['subject','topic','attempts','wrong','accuracy','avg_weakness']],use_container_width=True,hide_index=True)
    st.markdown('### Cards needing the most work');st.dataframe(d.sort_values(['weakness','wrong'],ascending=False)[['subject','topic','front','attempts','correct','wrong','accuracy','weakness']].head(20),use_container_width=True,hide_index=True)

with t3:
    st.markdown('## Deck Manager')
    with st.form('add'):
        a,b,c=st.columns(3);subj=a.text_input('Subject',value='Calc 3');top=b.text_input('Topic');ctype=c.selectbox('Card type',['Recognition','Formula','Process','Concept','Practice']);front=st.text_area('Front / question');back=st.text_area('Back / answer');hint=st.text_input('Hint (optional)')
        if st.form_submit_button('Add card',type='primary'):
            if subj.strip() and top.strip() and front.strip() and back.strip():
                c0=conn();c0.execute('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at) VALUES (?,?,?,?,?,?,?)',(subj.strip(),top.strip(),ctype,front.strip(),back.strip(),hint.strip(),now()));c0.commit();c0.close();st.success('Card added.');st.rerun()
            else:st.error('Subject, topic, question, and answer are required.')
    st.dataframe(cards_df()[['subject','topic','card_type','front','back']],use_container_width=True,hide_index=True)

with t4:
    st.markdown('## Settings');st.session_state.target=st.slider('Cards per study session',5,40,int(st.session_state.target));st.info('Progress is currently stored in local SQLite. Streamlit Community Cloud can reset local files during rebuilds. A future version can move progress to durable cloud storage.')
