import html, sqlite3, random, re
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

DB=Path('flashcards.db')


def natural_sort_key(value):
    """Sort labels with embedded numbers in human curriculum order.

    Examples: Ch 2 comes before Ch 10, and 12.4 comes before 12.10.
    """
    import re
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r"(\d+)", str(value))]


def render_shape_graph(shape_key):
    fig=plt.figure(figsize=(6.2,4.6))
    if shape_key=='circle':
        ax=fig.add_subplot(111);t=np.linspace(0,2*np.pi,400);ax.plot(3*np.cos(t),3*np.sin(t),linewidth=2.6);ax.axhline(0,linewidth=.8,alpha=.45);ax.axvline(0,linewidth=.8,alpha=.45);ax.set_aspect('equal',adjustable='box');ax.set_xlim(-4,4);ax.set_ylim(-4,4);ax.set_xlabel('x');ax.set_ylabel('y');ax.grid(alpha=.18)
    else:
        ax=fig.add_subplot(111,projection='3d')
        if shape_key=='sphere':
            u=np.linspace(0,2*np.pi,64);v=np.linspace(0,np.pi,36);x=2*np.outer(np.cos(u),np.sin(v));y=2*np.outer(np.sin(u),np.sin(v));z=2*np.outer(np.ones_like(u),np.cos(v));ax.plot_surface(x,y,z,alpha=.58,linewidth=0);lim=2.6
        elif shape_key=='ellipsoid':
            u=np.linspace(0,2*np.pi,64);v=np.linspace(0,np.pi,36);x=3*np.outer(np.cos(u),np.sin(v));y=2*np.outer(np.sin(u),np.sin(v));z=np.outer(np.ones_like(u),np.cos(v));ax.plot_surface(x,y,z,alpha=.58,linewidth=0);lim=3.5
        elif shape_key=='helix':
            t=np.linspace(-2*np.pi,2*np.pi,500);ax.plot(np.cos(t),np.sin(t),t/np.pi,linewidth=3);lim=2.4
        elif shape_key=='twisted_cubic':
            t=np.linspace(-1.5,1.5,500);ax.plot(t,t**2,t**3,linewidth=3);lim=3.8
        ax.set_xlabel('x');ax.set_ylabel('y');ax.set_zlabel('z');ax.set_box_aspect((1,1,1));ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_zlim(-lim,lim);ax.view_init(elev=22,azim=-58)
    fig.tight_layout();st.pyplot(fig,use_container_width=False);plt.close(fig)

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
.st-key-flashcard{background:linear-gradient(145deg,#fff,#f1f6ff);color:#0b1730;border:1px solid #957eff;border-radius:20px;padding:26px 30px 22px;min-height:300px;box-shadow:0 0 0 1px rgba(45,196,255,.3),0 22px 48px rgba(0,0,0,.2);margin-bottom:14px}
.st-key-flashcard [data-testid="stMarkdownContainer"]{color:#0b1730}
.st-key-flashcard .katex{font-size:1.45em}
.st-key-flashcard .katex-display{margin:1.2rem 0;text-align:left}
.choice-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:10px 0 6px}.choice-box{background:#f7f9fd;border:1px solid #d5deec;border-radius:12px;padding:12px 14px;color:#14213d;min-height:54px;font-size:15px}.choice-letter{display:inline-block;color:#6948df;font-weight:900;margin-right:7px}
@media(max-width:760px){.choice-grid{grid-template-columns:1fr}}
@media(max-width:1000px){.metrics{grid-template-columns:repeat(2,1fr)}.hero .badge{display:none}.question{font-size:23px}}

/* Quiz / flip-card upgrade */
.mode-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:2px 0 16px}.mode-chip{border:1px solid var(--border);background:#0b1b2f;border-radius:12px;padding:10px 12px;text-align:center;color:#cdd8e8;font-size:12px;font-weight:800}.record-card{background:linear-gradient(135deg,#27143e,#14213d);border:1px solid #7c5cff;border-radius:15px;padding:15px 17px}.record-num{font-size:30px;font-weight:900;color:#ffd768}.record-sub{font-size:11px;color:#aebbd0}.session-banner{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:8px 0 16px}.session-stat{background:#0d1c30;border:1px solid var(--border);border-radius:13px;padding:12px 14px}.session-stat strong{display:block;font-size:22px}.session-stat span{font-size:10px;color:var(--muted)}
.flip-shell{perspective:1200px}.flip-face{animation:flipIn .42s ease both;transform-style:preserve-3d}.flip-face.back{animation:flipBack .48s ease both}@keyframes flipIn{from{transform:rotateY(-88deg);opacity:.25}to{transform:rotateY(0);opacity:1}}@keyframes flipBack{from{transform:rotateY(88deg);opacity:.25}to{transform:rotateY(0);opacity:1}}@media(prefers-reduced-motion:reduce){.flip-face,.flip-face.back{animation:none}}
.quiz-answer{background:linear-gradient(180deg,#0d1f34,#0a1727);border:1px solid var(--border);border-radius:14px;padding:16px;margin:10px 0}.correct-glow{border-color:#2bd47f;box-shadow:0 0 0 1px rgba(43,212,127,.15)}.wrong-glow{border-color:#ff5a6f;box-shadow:0 0 0 1px rgba(255,90,111,.15)}
.fill-help{font-size:12px;color:var(--muted);margin:-4px 0 8px}.perfect{color:#ffd768!important}.objective-note{background:rgba(118,87,255,.08);border:1px solid rgba(118,87,255,.35);padding:10px 12px;border-radius:10px;color:#c9d2e4;font-size:12px}
@media(max-width:900px){.session-banner,.mode-strip{grid-template-columns:repeat(2,1fr)}}
</style>''',unsafe_allow_html=True)

def now(): return datetime.now(timezone.utc).isoformat()
def conn():
    c=sqlite3.connect(DB,check_same_thread=False);c.row_factory=sqlite3.Row;return c

def init():
    c=conn();c.executescript('''CREATE TABLE IF NOT EXISTS cards(id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT,topic TEXT,card_type TEXT,front TEXT,back TEXT,hint TEXT,created_at TEXT);CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY AUTOINCREMENT,card_id INTEGER,result TEXT,confidence INTEGER,attempted_at TEXT,answer_mode TEXT);CREATE TABLE IF NOT EXISTS records(key TEXT PRIMARY KEY,value INTEGER DEFAULT 0);''');c.commit()
    cols=[r[1] for r in c.execute('PRAGMA table_info(cards)').fetchall()]
    if 'choices' not in cols: c.execute('ALTER TABLE cards ADD COLUMN choices TEXT');c.commit()
    acols=[r[1] for r in c.execute('PRAGMA table_info(attempts)').fetchall()]
    if 'answer_mode' not in acols: c.execute('ALTER TABLE attempts ADD COLUMN answer_mode TEXT');c.commit()
    c.execute("INSERT OR IGNORE INTO records(key,value) VALUES ('best_quiz_streak',0)");c.commit()
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
    # Comprehensive chapter 12–17 curriculum. Seed on every launch with
    # duplicate protection so existing users receive new material without losing progress.
    curriculum_cards=[('Calc 3 — Ch 12', '12.1 3D Coordinates', 'Recognition', 'In 3D, what equation represents a sphere centered at (a,b,c) with radius r?', '(x-a)^2+(y-b)^2+(z-c)^2=r^2', 'Sphere = distance from center held constant.', None), ('Calc 3 — Ch 12', '12.1 3D Coordinates', 'Multiple Choice', 'Which equation describes a sphere centered at the origin with radius 4?', 'x^2+y^2+z^2=16', 'Radius squared appears on the right.', ['x^2+y^2+z^2=4', 'x^2+y^2+z^2=16', 'x+y+z=4', 'x^2+y^2=16']), ('Calc 3 — Ch 12', '12.2 Vectors', 'Recognition', 'Given points A and B, how do you form vector AB?', 'B-A', 'Terminal point minus initial point.', None), ('Calc 3 — Ch 12', '12.2 Vectors', 'Multiple Choice', 'What operation gives the magnitude of v=<a,b,c>?', 'sqrt(a^2+b^2+c^2)', 'Use the 3D Pythagorean formula.', ['a+b+c', 'a^2+b^2+c^2', 'sqrt(a^2+b^2+c^2)', '|a+b+c|']), ('Calc 3 — Ch 12', '12.2 Vectors', 'Recognition', 'How do you create a unit vector in the direction of v?', 'v/|v|', 'Divide the vector by its magnitude.', None), ('Calc 3 — Ch 12', '12.3 Dot Product', 'Recognition', 'A problem asks for the angle between two vectors. What operation should you think of first?', 'Dot product', 'Angle → dot product → cosine formula.', None), ('Calc 3 — Ch 12', '12.3 Dot Product', 'Recognition', 'How do you test whether two nonzero vectors are perpendicular?', 'Dot product equals 0', 'Orthogonal vectors have zero dot product.', None), ('Calc 3 — Ch 12', '12.3 Dot Product', 'Multiple Choice', 'What does a dot product produce?', 'A scalar', 'Dot → number.', ['A vector', 'A scalar', 'A plane', 'A matrix']), ('Calc 3 — Ch 12', '12.3 Dot Product', 'Recognition', 'What formula connects the dot product to the angle theta?', 'a dot b=|a||b|cos(theta)', 'This is the main angle formula for vectors.', None), ('Calc 3 — Ch 12', '12.3 Dot Product', 'Recognition', 'A problem asks for the projection of a onto b. Which operation is central?', 'Dot product', 'Projection measures the component along another vector.', None), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Recognition', 'A problem asks for a vector perpendicular to two vectors. What operation should you use?', 'Cross product', 'Perpendicular to TWO vectors → cross product.', None), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Multiple Choice', 'What does a cross product produce?', 'A vector', 'Cross → new perpendicular vector.', ['A scalar', 'A vector', 'An angle only', 'A derivative']), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Recognition', 'How do you find the area of a parallelogram spanned by a and b?', '|a cross b|', 'Magnitude of the cross product gives parallelogram area.', None), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Recognition', 'How do you find the area of a triangle formed by vectors a and b?', '1/2|a cross b|', 'Triangle is half the corresponding parallelogram.', None), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Recognition', 'What is the scalar triple product used to find geometrically?', 'Volume', '|a·(b×c)| gives parallelepiped volume.', None), ('Calc 3 — Ch 12', '12.4 Cross Product', 'Multiple Choice', 'If a cross b = 0 for nonzero vectors, what does that tell you?', 'They are parallel', 'Zero cross magnitude means sin(theta)=0.', ['They are perpendicular', 'They are parallel', 'They have equal magnitude', 'Their dot product is zero']), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'You are given two points and asked for a line. What should you find first?', 'Direction vector by subtracting the points', 'Two points → subtract → direction vector.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'What is the vector form of a line through r0 with direction v?', 'r=r0+tv', 'Point + parameter times direction.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'To find whether two paths intersect, may the two lines use different parameters?', 'Yes', 'Path intersection allows separate parameters such as s and t.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'To check whether two particles collide, what must be the same?', 'Time parameter', 'Collision means same position at the same time.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'A plane problem gives two direction vectors in the plane. How do you get a normal vector?', 'Cross product', 'Cross the in-plane directions.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'What is the point-normal form of a plane?', 'a(x-x0)+b(y-y0)+c(z-z0)=0', '<a,b,c> is the normal vector.', None), ('Calc 3 — Ch 12', '12.5 Lines and Planes', 'Recognition', 'How do you test whether two planes are parallel?', 'Their normal vectors are parallel', 'Plane orientation is controlled by its normal.', None), ('Calc 3 — Ch 12', '12.6 Quadric Surfaces', 'Recognition', 'Equal positive coefficients on x^2, y^2, z^2 describe what basic closed surface?', 'Sphere', 'Equal squared scaling gives equal radii.', None), ('Calc 3 — Ch 12', '12.6 Quadric Surfaces', 'Recognition', 'Positive but unequal coefficients on x^2, y^2, z^2 equal to 1 usually describe what?', 'Ellipsoid', 'A stretched/squished sphere.', None), ('Calc 3 — Ch 12', '12.6 Quadric Surfaces', 'Recognition', 'If one variable is missing from a surface equation, what geometric behavior should you expect?', 'The curve extends parallel to the missing variable axis', 'Missing variable → extrusion in that direction.', None), ('Calc 3 — Ch 13', '13.1 Vector Functions', 'Recognition', 'What is a vector-valued function r(t)?', 'A function whose output is a vector', 'Typically r(t)=<x(t),y(t),z(t)>.', None), ('Calc 3 — Ch 13', '13.1 Vector Functions', 'Recognition', 'How do you evaluate a limit of a vector function?', 'Take the limit of each component', 'Vector limits are componentwise.', None), ('Calc 3 — Ch 13', '13.1 Vector Functions', 'Recognition', 'How do you determine where two space curves intersect?', 'Set their component equations equal using separate parameters', 'Same point does not require same parameter value.', None), ('Calc 3 — Ch 13', '13.2 Derivatives and Integrals', 'Recognition', 'How do you differentiate a vector-valued function?', 'Differentiate each component', 'Treat components independently.', None), ('Calc 3 — Ch 13', '13.2 Derivatives and Integrals', 'Recognition', 'How do you integrate a vector-valued function?', 'Integrate each component separately', 'Each component is an ordinary integral.', None), ('Calc 3 — Ch 13', '13.2 Derivatives and Integrals', 'Recognition', 'Given r prime(t) and r(t0), what is the workflow?', 'Integrate components, add constants, use the initial condition', 'Initial position determines integration constants.', None), ('Calc 3 — Ch 13', '13.3 Arc Length and Curvature', 'Recognition', 'What quantity do you integrate to find arc length of r(t)?', '|r prime(t)|', 'Arc length is integral of speed.', None), ('Calc 3 — Ch 13', '13.3 Arc Length and Curvature', 'Recognition', 'How is the unit tangent vector T defined?', 'r prime(t)/|r prime(t)|', 'Normalize the velocity/tangent vector.', None), ('Calc 3 — Ch 13', '13.3 Arc Length and Curvature', 'Recognition', 'What does curvature measure?', 'How rapidly a curve changes direction', 'Large curvature means tighter bending.', None), ('Calc 3 — Ch 13', '13.3 Arc Length and Curvature', 'Recognition', 'How is the principal unit normal N obtained from T?', 'T prime/|T prime|', 'Differentiate T and normalize.', None), ('Calc 3 — Ch 13', '13.4 Motion in Space', 'Recognition', 'For position r(t), what is velocity?', 'r prime(t)', 'Velocity is the derivative of position.', None), ('Calc 3 — Ch 13', '13.4 Motion in Space', 'Recognition', 'For position r(t), what is acceleration?', 'r double prime(t)', 'Acceleration is the derivative of velocity.', None), ('Calc 3 — Ch 13', '13.4 Motion in Space', 'Recognition', 'What is speed for a particle with velocity v(t)?', '|v(t)|', 'Speed is the magnitude of velocity.', None), ('Calc 3 — Ch 13', '13.4 Motion in Space', 'Recognition', 'In projectile motion without air resistance, which acceleration component is constant?', 'Vertical acceleration', 'Gravity acts vertically downward.', None), ('Calc 3 — Ch 14', '14.1 Multivariable Functions', 'Recognition', 'What does z=f(x,y) represent geometrically?', 'A surface in 3D', 'Two inputs and one output create a surface.', None), ('Calc 3 — Ch 14', '14.1 Multivariable Functions', 'Recognition', 'What is a level curve of f(x,y)?', 'f(x,y)=k', 'Hold the output constant.', None), ('Calc 3 — Ch 14', '14.2 Limits and Continuity', 'Recognition', 'To show a multivariable limit does not exist, what strategy is often useful?', 'Approach along two paths and get different limits', 'Different path values disprove a unique limit.', None), ('Calc 3 — Ch 14', '14.2 Limits and Continuity', 'Recognition', 'For continuity at a point, what must equal the function value?', 'The limit', 'Continuity requires limit = function value.', None), ('Calc 3 — Ch 14', '14.3 Partial Derivatives', 'Recognition', 'When taking partial derivative fx, what do you do with y?', 'Treat y as a constant', 'Differentiate only with respect to x.', None), ('Calc 3 — Ch 14', '14.3 Partial Derivatives', 'Recognition', 'When taking partial derivative fy, what do you do with x?', 'Treat x as a constant', 'Differentiate only with respect to y.', None), ('Calc 3 — Ch 14', '14.3 Partial Derivatives', 'Recognition', 'What does fxy mean?', 'Differentiate first with respect to x, then y', 'Read derivative subscripts in the order differentiation is performed in this notation convention.', None), ('Calc 3 — Ch 14', '14.4 Tangent Planes', 'Recognition', 'What data do you need for the tangent plane to z=f(x,y) at (a,b)?', 'f(a,b), fx(a,b), and fy(a,b)', 'These determine the point and two slopes.', None), ('Calc 3 — Ch 14', '14.4 Tangent Planes', 'Recognition', 'What is linearization used for?', 'Approximate a function near a point', 'The tangent plane is a local approximation.', None), ('Calc 3 — Ch 14', '14.5 Chain Rule', 'Recognition', 'If z=f(x,y) and x,y both depend on t, what rule should you recognize for dz/dt?', 'Multivariable chain rule', 'Follow every dependency path from t to z.', None), ('Calc 3 — Ch 14', '14.5 Chain Rule', 'Recognition', 'Implicit differentiation with several variables often relies on what derivative idea?', 'Chain rule', 'Dependent variables generate derivative factors.', None), ('Calc 3 — Ch 14', '14.6 Gradient and Directional Derivatives', 'Recognition', 'What is the gradient of f(x,y)?', '<fx,fy>', 'The gradient collects first partial derivatives.', None), ('Calc 3 — Ch 14', '14.6 Gradient and Directional Derivatives', 'Recognition', 'In what direction does the gradient point?', 'Direction of maximum increase', 'Gradient points steepest uphill.', None), ('Calc 3 — Ch 14', '14.6 Gradient and Directional Derivatives', 'Recognition', 'How do you compute the directional derivative in unit direction u?', 'Gradient dot u', 'Directional derivative is a dot product.', None), ('Calc 3 — Ch 14', '14.6 Gradient and Directional Derivatives', 'Recognition', 'The gradient is perpendicular to what geometric objects?', 'Level curves and level surfaces', 'Gradient is normal to constant-value sets.', None), ('Calc 3 — Ch 14', '14.7 Maximum and Minimum', 'Recognition', 'For an interior critical point of f(x,y), what equations do you solve first?', 'fx=0 and fy=0', 'Critical points occur where the gradient vanishes or derivatives fail.', None), ('Calc 3 — Ch 14', '14.7 Maximum and Minimum', 'Recognition', 'What test classifies many two-variable critical points?', 'Second derivative test', 'Use D=fxx*fyy-(fxy)^2.', None), ('Calc 3 — Ch 14', '14.8 Lagrange Multipliers', 'Recognition', 'Optimization subject to a constraint g(x,y)=c should trigger what method?', 'Lagrange multipliers', 'Constraint + extrema → ∇f=lambda∇g.', None), ('Calc 3 — Ch 14', '14.8 Lagrange Multipliers', 'Recognition', 'What vector equation is central to Lagrange multipliers?', 'grad f=lambda grad g', 'At constrained extrema the gradients are parallel.', None), ('Calc 3 — Ch 15', '15.1 Double Integrals', 'Recognition', 'What does a double integral of f(x,y) over a region accumulate?', 'A quantity over area', 'Think many small f dA contributions.', None), ('Calc 3 — Ch 15', '15.1 Double Integrals', 'Recognition', 'For a rectangular region, how are double integrals commonly evaluated?', 'As iterated integrals', 'Integrate one variable, then the other.', None), ('Calc 3 — Ch 15', '15.2 General Regions', 'Recognition', 'When changing the order of integration, what should you do first?', 'Sketch the region', 'The geometry determines the new bounds.', None), ('Calc 3 — Ch 15', '15.2 General Regions', 'Recognition', 'For a Type I region, which variable typically has function bounds?', 'y', 'Type I: a<=x<=b and g1(x)<=y<=g2(x).', None), ('Calc 3 — Ch 15', '15.3 Polar Coordinates', 'Recognition', 'A circular region or x^2+y^2 expression should make you consider what coordinates?', 'Polar coordinates', 'Circles simplify with r and theta.', None), ('Calc 3 — Ch 15', '15.3 Polar Coordinates', 'Recognition', 'What is dA in polar coordinates?', 'r dr dtheta', 'Do not forget the Jacobian factor r.', None), ('Calc 3 — Ch 15', '15.3 Polar Coordinates', 'Recognition', 'What does x^2+y^2 become in polar coordinates?', 'r^2', 'Core polar identity.', None), ('Calc 3 — Ch 15', '15.4 Applications', 'Recognition', 'How do you find mass of a lamina with density rho(x,y)?', 'Double integral of rho dA', 'Density integrated over area gives mass.', None), ('Calc 3 — Ch 15', '15.4 Applications', 'Recognition', 'What do moments of mass help you compute?', 'Center of mass', 'Moments determine balance location.', None), ('Calc 3 — Ch 15', '15.5 Surface Area', 'Recognition', 'Surface area of z=f(x,y) uses what factor under the double integral?', 'sqrt(1+fx^2+fy^2)', 'This accounts for surface tilt.', None), ('Calc 3 — Ch 15', '15.6 Triple Integrals', 'Recognition', 'What does a triple integral integrate over?', 'Volume', 'Use dV over a 3D region.', None), ('Calc 3 — Ch 15', '15.7 Cylindrical Coordinates', 'Recognition', 'A 3D region with circular symmetry around the z-axis should suggest what coordinates?', 'Cylindrical coordinates', 'Polar in xy plus z.', None), ('Calc 3 — Ch 15', '15.7 Cylindrical Coordinates', 'Recognition', 'What is dV in cylindrical coordinates?', 'r dz dr dtheta', 'Cylindrical Jacobian contributes r.', None), ('Calc 3 — Ch 15', '15.8 Spherical Coordinates', 'Recognition', 'A sphere-centered region should suggest what coordinate system?', 'Spherical coordinates', 'Spheres simplify with rho, phi, theta.', None), ('Calc 3 — Ch 15', '15.8 Spherical Coordinates', 'Recognition', 'What is dV in spherical coordinates?', 'rho^2 sin(phi) d rho d phi d theta', 'Remember the spherical Jacobian.', None), ('Calc 3 — Ch 15', '15.9 Change of Variables', 'Recognition', 'What factor appears when changing variables in a multiple integral?', 'Absolute value of the Jacobian determinant', 'The Jacobian rescales area or volume.', None), ('Calc 3 — Ch 16', '16.1 Vector Fields', 'Recognition', 'What is a vector field?', 'A function assigning a vector to each point', 'Examples include velocity and force fields.', None), ('Calc 3 — Ch 16', '16.1 Vector Fields', 'Recognition', 'For a scalar function f, what vector field is naturally associated with it?', 'Gradient field', '∇f is a vector field.', None), ('Calc 3 — Ch 16', '16.2 Line Integrals', 'Recognition', 'What does a line integral integrate over?', 'A curve', 'The domain of accumulation is a path.', None), ('Calc 3 — Ch 16', '16.2 Line Integrals', 'Recognition', 'Work done by a force field F along a curve C uses which integral?', 'Integral F dot dr', 'Work is a vector line integral.', None), ('Calc 3 — Ch 16', '16.3 Fundamental Theorem', 'Recognition', 'If F is conservative, how can a line integral from A to B be evaluated quickly?', 'Potential at B minus potential at A', 'Use F=grad f and compute f(B)-f(A).', None), ('Calc 3 — Ch 16', '16.3 Fundamental Theorem', 'Recognition', 'What does path independence suggest about a vector field?', 'It is conservative', 'Under suitable domain conditions.', None), ('Calc 3 — Ch 16', '16.3 Fundamental Theorem', 'Recognition', 'For F=<P,Q> on a suitable simply connected domain, what test suggests F is conservative?', 'Py=Qx', 'Matching cross partials is the 2D test.', None), ('Calc 3 — Ch 16', '16.4 Greens Theorem', 'Recognition', 'A closed planar curve and a line integral around its boundary should make you consider what theorem?', 'Greens theorem', 'Green converts boundary line integrals to double integrals.', None), ('Calc 3 — Ch 16', '16.5 Curl and Divergence', 'Recognition', 'What does divergence measure conceptually?', 'Net outward source or sink strength', 'Positive divergence behaves like a source.', None), ('Calc 3 — Ch 16', '16.5 Curl and Divergence', 'Recognition', 'What does curl measure conceptually?', 'Local rotation', 'Curl measures rotational tendency.', None), ('Calc 3 — Ch 16', '16.6 Parametric Surfaces', 'Recognition', 'How is a parametric surface commonly represented?', 'r(u,v)', 'Two parameters sweep out a surface.', None), ('Calc 3 — Ch 16', '16.6 Parametric Surfaces', 'Recognition', 'How do you get a normal direction to a parametric surface r(u,v)?', 'r_u cross r_v', 'Cross the tangent vectors.', None), ('Calc 3 — Ch 16', '16.7 Surface Integrals', 'Recognition', 'Flux through a surface fundamentally uses which vector operation?', 'Dot product', 'Flux measures field component through the normal.', None), ('Calc 3 — Ch 16', '16.8 Stokes Theorem', 'Recognition', 'A line integral around a 3D boundary curve can often be converted to a surface integral using what theorem?', 'Stokes theorem', 'Stokes relates circulation to curl through a surface.', None), ('Calc 3 — Ch 16', '16.9 Divergence Theorem', 'Recognition', 'Flux through a closed surface can often be converted to a triple integral using what theorem?', 'Divergence theorem', 'Closed-surface flux ↔ volume integral of divergence.', None), ('Calc 3 — Ch 16', '16.9 Divergence Theorem', 'Recognition', 'What is the key visual clue for the Divergence Theorem?', 'Closed surface', 'The surface must enclose a volume.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'What makes an ODE second order?', 'The highest derivative is second derivative', 'Order is determined by the highest derivative present.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'For ay double prime+by prime+cy=0 with constant coefficients, what should you form?', 'Characteristic equation ar^2+br+c=0', 'Replace derivatives by powers of r.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'Two distinct real characteristic roots r1,r2 give what solution form?', 'c1 e^(r1 t)+c2 e^(r2 t)', 'Distinct real roots produce two exponentials.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'A repeated characteristic root r gives what solution form?', '(c1+c2 t)e^(rt)', 'The second independent solution gains a factor t.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'Complex roots alpha plus/minus beta i give what real solution form?', 'e^(alpha t)(c1 cos(beta t)+c2 sin(beta t))', 'Complex roots become sine/cosine with exponential envelope.', None), ('Differential Equations — Ch 17', '17.1 Second-Order Linear', 'Recognition', 'How many initial conditions are normally needed for a second-order IVP?', '2', 'A second-order equation has two arbitrary constants.', None), ('Differential Equations — Ch 17', '17.2 Nonhomogeneous', 'Recognition', 'For L[y]=g(t), how is the general solution organized?', 'y=yc+yp', 'Complementary solution plus particular solution.', None), ('Differential Equations — Ch 17', '17.2 Nonhomogeneous', 'Recognition', 'Polynomial, exponential, sine, or cosine forcing with constant coefficients should suggest what method?', 'Undetermined coefficients', 'Use when the forcing has a suitable standard form.', None), ('Differential Equations — Ch 17', '17.2 Nonhomogeneous', 'Recognition', 'When your trial particular solution duplicates part of yc, what do you do?', 'Multiply the trial by t enough times', 'Resonance requires a modified trial.', None), ('Differential Equations — Ch 17', '17.2 Nonhomogeneous', 'Recognition', 'A nonhomogeneous linear equation with awkward forcing may suggest what general method?', 'Variation of parameters', 'More general than undetermined coefficients.', None), ('Differential Equations — Ch 17', '17.3 Applications', 'Recognition', 'What physical system is modeled by m x double prime+c x prime+kx=F(t)?', 'Mass-spring-damper system', 'm=mass, c=damping, k=spring stiffness.', None), ('Differential Equations — Ch 17', '17.3 Applications', 'Recognition', 'In m x double prime+c x prime+kx=0, what does c represent?', 'Damping coefficient', 'It controls velocity-proportional resistance.', None), ('Differential Equations — Ch 17', '17.3 Applications', 'Recognition', 'What does F(t) represent in a forced vibration model?', 'External forcing', 'It drives the system from outside.', None), ('Differential Equations — Ch 17', '17.3 Applications', 'Recognition', 'No damping means which coefficient is zero?', 'c=0', 'Remove the x prime damping term.', None), ('Differential Equations — Ch 17', '17.3 Applications', 'Recognition', 'What phenomenon occurs when forcing frequency aligns with natural frequency in an undamped system?', 'Resonance', 'The response amplitude can grow strongly.', None), ('Differential Equations — Ch 17', '17.4 Series Solutions', 'Recognition', 'When ordinary closed-form methods fail near a point, what method may be used for a linear ODE?', 'Power series solution', 'Assume y=sum a_n x^n and determine coefficients.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You see an integral containing a function and its derivative, such as ∫x cos(x^2) dx. What method should you try?', 'u-substitution', 'Look for an inside function and its derivative.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You see a product like ∫x e^x dx. What integration method should you consider?', 'Integration by parts', 'Product of unlike function types often signals IBP.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You see ∫1/(1+x^2) dx. What antiderivative pattern should you recognize?', 'arctan(x)+C', 'Inverse tangent derivative pattern.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You need a number measuring alignment or angle between vectors. Dot or cross?', 'Dot product', 'Dot produces a scalar and connects to cosine.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You need a new vector perpendicular to two given vectors. Dot or cross?', 'Cross product', 'Cross produces a perpendicular vector.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You see a circular double-integral region. What coordinate change should you consider?', 'Polar coordinates', 'Circular xy geometry → polar.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You see a spherical triple-integral region. What coordinate change should you consider?', 'Spherical coordinates', 'Spherical geometry → spherical coordinates.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You need constrained extrema of f subject to g=c. What method?', 'Lagrange multipliers', 'Constraint optimization → Lagrange.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You need the steepest-increase direction of a scalar field. What object?', 'Gradient', 'Gradient points in maximum-increase direction.', None), ('Method Recognition — Calculus', 'Recognition Drills', 'Recognition', 'You have a conservative field and endpoints only. What shortcut?', 'Fundamental theorem for line integrals', 'Use the potential difference.', None)]

    # Complete Calc I / II curriculum (Chapters 1-11).
    # Each chapter deliberately mixes recognition, setup/method, and calculation prompts.
    early_calc_cards = [
        # CHAPTER 1 — FUNCTIONS & MODELS
        ('Calc 1 — Ch 1','1.1-1.3 Functions','Recognition','What does f(a) mean?','The output of f when the input is a','Input a into the function.',None),
        ('Calc 1 — Ch 1','1.1-1.3 Functions','Recognition','How do you find the domain of a function?','Find all input values for which the expression is defined','Watch for zero denominators, even roots of negatives, and invalid logarithm inputs.',None),
        ('Calc 1 — Ch 1','1.1-1.3 Functions','Multiple Choice','For an even function, which identity is true?','f(-x)=f(x)','Even functions are symmetric about the y-axis.',['f(-x)=f(x)','f(-x)=-f(x)','f(x)=0','f(x+1)=f(x)']),
        ('Calc 1 — Ch 1','1.4 Transformations','Recognition','What does f(x-h)+k do to the graph of f(x)?','Shift right h and up k','Inside changes horizontal position; outside changes vertical position.',None),
        ('Calc 1 — Ch 1','1.5 Exponential Functions','Recognition','What key property identifies an exponential function?','The variable is in the exponent','Example: a^x.',None),
        ('Calc 1 — Ch 1','1.6 Inverse Functions','Recognition','How can you test graphically whether a function has an inverse?','Horizontal line test','One-to-one functions pass the horizontal line test.',None),
        ('Calc 1 — Ch 1','1.6 Inverse Functions','Recognition','What relationship connects a function and its inverse?','f(f^-1(x))=x','The inverse undoes the original function.',None),
        ('Calc 1 — Ch 1','1.6 Logarithms','Multiple Choice','Which identity is correct?','ln(ab)=ln(a)+ln(b)','Products become sums under logarithms.',['ln(ab)=ln(a)+ln(b)','ln(a+b)=ln(a)+ln(b)','ln(a/b)=ln(a)ln(b)','ln(a^b)=b+ln(a)']),

        # CHAPTER 2 — LIMITS & DERIVATIVES
        ('Calc 1 — Ch 2','2.1-2.3 Limits','Recognition','What is a limit asking you to determine?','The value a function approaches as x approaches a point','A limit concerns nearby behavior, not necessarily the function value.',None),
        ('Calc 1 — Ch 2','2.1-2.3 Limits','Recognition','Direct substitution gives 0/0 in a limit. What does that mean?','The form is indeterminate and needs more work','Try algebraic simplification, factoring, rationalizing, or another limit technique.',None),
        ('Calc 1 — Ch 2','2.1-2.3 Limits','Recognition','When a rational limit gives 0/0 and the expression factors, what should you try first?','Factor and cancel the common factor','Simplify before evaluating again.',None),
        ('Calc 1 — Ch 2','2.4 Continuity','Recognition','What three conditions are required for continuity at x=a?','f(a) exists, lim f(x) exists, and lim f(x)=f(a)','All three must hold.',None),
        ('Calc 1 — Ch 2','2.5 Limits at Infinity','Recognition','For a rational function with equal numerator and denominator degrees, what determines the horizontal asymptote?','Ratio of leading coefficients','Highest-degree terms dominate.',None),
        ('Calc 1 — Ch 2','2.6 Derivatives','Recognition','Conceptually, what does f prime(a) represent?','Instantaneous rate of change or tangent-line slope','Derivative = local rate/slope.',None),
        ('Calc 1 — Ch 2','2.6 Derivatives','Recognition','What limit defines f prime(a)?','lim h->0 [f(a+h)-f(a)]/h','This is the difference quotient.',None),
        ('Calc 1 — Ch 2','2.7 Derivative as Function','Multiple Choice','If position is s(t), what is velocity?','s prime(t)','Velocity is the derivative of position.',['s(t)^2','s prime(t)','integral of s(t)','1/s(t)']),

        # CHAPTER 3 — DIFFERENTIATION RULES
        ('Calc 1 — Ch 3','3.1 Basic Rules','Recognition','What is d/dx(x^n)?','n*x^(n-1)','Power rule.',None),
        ('Calc 1 — Ch 3','3.1 Basic Rules','Multiple Choice','What is d/dx(e^x)?','e^x','The natural exponential is its own derivative.',['x e^(x-1)','e^x','ln(x)','1/e^x']),
        ('Calc 1 — Ch 3','3.2 Product and Quotient Rules','Recognition','You need the derivative of two functions multiplied together. What rule?','Product rule','(fg) prime = f prime g + f g prime.',None),
        ('Calc 1 — Ch 3','3.2 Product and Quotient Rules','Recognition','You need the derivative of one function divided by another. What rule?','Quotient rule','Low d-high minus high d-low over low squared.',None),
        ('Calc 1 — Ch 3','3.3 Trig Derivatives','Recognition','What is d/dx(sin x)?','cos x','Core trig derivative.',None),
        ('Calc 1 — Ch 3','3.3 Trig Derivatives','Recognition','What is d/dx(cos x)?','-sin x','Core trig derivative.',None),
        ('Calc 1 — Ch 3','3.4 Chain Rule','Recognition','You see a function inside another function, such as sin(x^2). What rule should you think of?','Chain rule','Differentiate outside, keep inside, multiply by derivative of inside.',None),
        ('Calc 1 — Ch 3','3.5 Implicit Differentiation','Recognition','x and y are mixed in an equation and y is not isolated. What method should you consider?','Implicit differentiation','Differentiate both sides with respect to x and remember y terms produce y prime.',None),
        ('Calc 1 — Ch 3','3.6 Logarithmic Derivatives','Recognition','What is d/dx(ln x)?','1/x','Natural-log derivative.',None),
        ('Calc 1 — Ch 3','3.9 Related Rates','Recognition','Several quantities change with time and you are asked for one rate from another. What problem type is this?','Related rates','Write a relationship, differentiate with respect to time, then substitute known values.',None),

        # CHAPTER 4 — APPLICATIONS OF DIFFERENTIATION
        ('Calc 1 — Ch 4','4.1 Extrema','Recognition','At an interior local maximum or minimum where f is differentiable, what is usually true?','f prime(x)=0','Such points are critical points.',None),
        ('Calc 1 — Ch 4','4.1 Extrema','Recognition','How do you find critical numbers?','Find where f prime(x)=0 or f prime(x) does not exist','Restrict to values in the domain of f.',None),
        ('Calc 1 — Ch 4','4.3 Derivative Tests','Recognition','If f prime changes from positive to negative at c, what occurs at c?','Local maximum','Increasing then decreasing.',None),
        ('Calc 1 — Ch 4','4.3 Derivative Tests','Recognition','If f prime changes from negative to positive at c, what occurs at c?','Local minimum','Decreasing then increasing.',None),
        ('Calc 1 — Ch 4','4.4 Concavity','Recognition','What does f double prime(x)>0 tell you?','The graph is concave up','Positive second derivative means slopes are increasing.',None),
        ('Calc 1 — Ch 4','4.4 Concavity','Recognition','What is an inflection point?','A point where concavity changes','A zero of f double prime alone is not enough; concavity must change.',None),
        ('Calc 1 — Ch 4','4.7 Optimization','Recognition','A problem asks for the largest or smallest possible physical quantity. What process should you think of?','Optimization','Build an objective function, reduce variables using constraints, find extrema.',None),
        ('Calc 1 — Ch 4','4.9 Antiderivatives','Recognition','What is an antiderivative of f?','A function F such that F prime=f','Differentiation and antidifferentiation reverse each other.',None),

        # CHAPTER 5 — INTEGRALS
        ('Calc 1 — Ch 5','5.1 Area and Distance','Recognition','What does a definite integral represent geometrically when f is nonnegative?','Area under the curve','More generally it gives signed/net area.',None),
        ('Calc 1 — Ch 5','5.2 Definite Integral','Recognition','What does a Riemann sum approximate?','A definite integral','It adds many function-value times width contributions.',None),
        ('Calc 1 — Ch 5','5.3 Fundamental Theorem','Recognition','What does the Fundamental Theorem of Calculus connect?','Derivatives and definite integrals','It links accumulation and rates of change.',None),
        ('Calc 1 — Ch 5','5.3 Fundamental Theorem','Recognition','What is d/dx of integral from a to x of f(t) dt?','f(x)','FTC Part 1.',None),
        ('Calc 1 — Ch 5','5.3 Fundamental Theorem','Recognition','How do you evaluate integral from a to b of f(x) dx using an antiderivative F?','F(b)-F(a)','FTC Part 2.',None),
        ('Calc 1 — Ch 5','5.4 Indefinite Integrals','Recognition','Why is +C required on an indefinite integral?','Antiderivatives differ by an arbitrary constant','The derivative of any constant is zero.',None),
        ('Calc 1 — Ch 5','5.5 Substitution','Recognition','You see a composite expression and its derivative factor inside an integral. What method should you try?','u-substitution','Reverse the chain rule.',None),
        ('Calc 1 — Ch 5','5.5 Substitution','Recognition','For integral x*cos(x^2) dx, what is a natural u choice?','u=x^2','Its derivative supplies the x dx factor.',None),

        # CHAPTER 6 — APPLICATIONS OF INTEGRATION
        ('Calc 1 — Ch 6','6.1 Area Between Curves','Recognition','How do you set up area between y=f(x) and y=g(x) using vertical slices?','integral of top minus bottom','Area must be nonnegative.',None),
        ('Calc 1 — Ch 6','6.1 Area Between Curves','Recognition','Using horizontal slices, what replaces top minus bottom?','Right minus left','Integrate with respect to y.',None),
        ('Calc 1 — Ch 6','6.2 Volumes','Recognition','Cross sections perpendicular to the axis are solid disks. What volume method?','Disk method','V=integral pi R^2.',None),
        ('Calc 1 — Ch 6','6.2 Volumes','Recognition','Cross sections have an outer and inner radius. What volume method?','Washer method','V=integral pi(R^2-r^2).',None),
        ('Calc 1 — Ch 6','6.3 Cylindrical Shells','Recognition','A rotated region is easier to describe with slices parallel to the axis of rotation. What method should you consider?','Shell method','V=integral 2*pi*(radius)*(height).',None),
        ('Calc 1 — Ch 6','6.4 Work','Recognition','What basic integration pattern models work by a variable force?','integral F(x) dx','Add force times small displacement.',None),
        ('Calc 1 — Ch 6','6.5 Average Value','Recognition','What is the average value of f on [a,b]?','1/(b-a) times integral from a to b of f(x) dx','Integral divided by interval length.',None),
        ('Calc 1 — Ch 6','6.1-6.5 Applications','Recognition','Before setting up an application integral, what should you identify first?','The quantity represented by one thin slice','Build the integral from a differential piece.',None),

        # CHAPTER 7 — TECHNIQUES OF INTEGRATION
        ('Calc 2 — Ch 7','7.1 Integration by Parts','Recognition','You see a product such as x*e^x or x*sin x. What integration method should you consider?','Integration by parts','Products of unlike function types often signal IBP.',None),
        ('Calc 2 — Ch 7','7.1 Integration by Parts','Recognition','What is the integration-by-parts formula?','integral u dv=u*v-integral v du','Choose u to simplify when differentiated.',None),
        ('Calc 2 — Ch 7','7.2 Trig Integrals','Recognition','For integral sin^m(x) cos^n(x) dx with an odd sine power, what common strategy works?','Save one sin x and convert the rest using sin^2 x=1-cos^2 x','Then use u=cos x.',None),
        ('Calc 2 — Ch 7','7.3 Trig Substitution','Recognition','You see sqrt(a^2-x^2). What trig substitution pattern should you recognize?','x=a sin(theta)','Then a^2-x^2 becomes a^2 cos^2(theta).',None),
        ('Calc 2 — Ch 7','7.3 Trig Substitution','Recognition','You see sqrt(a^2+x^2). What trig substitution pattern should you recognize?','x=a tan(theta)','Use 1+tan^2=sec^2.',None),
        ('Calc 2 — Ch 7','7.4 Partial Fractions','Recognition','A rational function has a factorable denominator and numerator degree is smaller. What method should you consider?','Partial fractions','Decompose into simpler rational pieces.',None),
        ('Calc 2 — Ch 7','7.4 Partial Fractions','Recognition','If numerator degree is at least denominator degree, what should you do before partial fractions?','Polynomial long division','Make the rational function proper first.',None),
        ('Calc 2 — Ch 7','7.8 Improper Integrals','Recognition','An integral has an infinite bound or an infinite discontinuity. What kind of integral is it?','Improper integral','Rewrite it as a limit.',None),
        ('Calc 2 — Ch 7','7.8 Improper Integrals','Recognition','What determines whether an improper integral converges?','Whether its defining limit is finite','If the limit is infinite or fails to exist, it diverges.',None),

        # CHAPTER 8 — FURTHER APPLICATIONS OF INTEGRATION
        ('Calc 2 — Ch 8','8.1 Arc Length','Recognition','What is the arc-length formula for y=f(x) from a to b?','integral sqrt(1+(f prime(x))^2) dx','Arc length comes from tiny Pythagorean segments.',None),
        ('Calc 2 — Ch 8','8.2 Surface Area','Recognition','For rotating y=f(x) about the x-axis, what factor appears in the surface-area integral?','2*pi*y*sqrt(1+(y prime)^2)','Circumference times slant-length element.',None),
        ('Calc 2 — Ch 8','8.3 Applications','Recognition','A variable physical quantity is distributed along a line or region. What calculus idea is usually used to total it?','Integration','Density times a small element is accumulated.',None),
        ('Calc 2 — Ch 8','8.3 Hydrostatic Force','Recognition','What determines fluid pressure at depth h?','rho*g*h','Pressure increases linearly with depth.',None),
        ('Calc 2 — Ch 8','8.3 Hydrostatic Force','Recognition','How is hydrostatic force on a submerged plate built?','Integrate pressure times strip area','Use a representative horizontal strip.',None),
        ('Calc 2 — Ch 8','8.1-8.3 Applications','Recognition','For an unfamiliar integration application, what is the best first question?','What does one small slice contribute?','Model dQ first, then integrate.',None),

        # CHAPTER 9 — DIFFERENTIAL EQUATIONS
        ('Calc 2 — Ch 9','9.1 Modeling with DEs','Recognition','What is a differential equation?','An equation involving an unknown function and one or more derivatives','The derivative describes how the unknown changes.',None),
        ('Calc 2 — Ch 9','9.2 Direction Fields','Recognition','What does a direction field show?','The slope prescribed by a differential equation at many points','Solution curves follow the small slope segments.',None),
        ('Calc 2 — Ch 9','9.3 Separable Equations','Recognition','If dy/dx can be written as g(x)h(y), what method should you consider?','Separation of variables','Move y terms with dy and x terms with dx, then integrate.',None),
        ('Calc 2 — Ch 9','9.3 Separable Equations','Recognition','After integrating a separable DE, what often remains to finish an IVP?','Use the initial condition to solve for C','The initial condition selects one solution.',None),
        ('Calc 2 — Ch 9','9.4 Exponential Growth and Decay','Recognition','A quantity changes at a rate proportional to itself. What model should you recognize?','dy/dt=k*y','Its solutions are exponential.',None),
        ('Calc 2 — Ch 9','9.5 Linear Equations','Recognition','What standard form identifies a first-order linear differential equation?','y prime+P(x)y=Q(x)','y and y prime appear only to the first power and are not multiplied together.',None),
        ('Calc 2 — Ch 9','9.5 Linear Equations','Recognition','For y prime+P(x)y=Q(x), what method should you think of?','Integrating factor','mu=e^(integral P(x) dx).',None),
        ('Calc 2 — Ch 9','9.5 Linear Equations','Recognition','What makes y prime+y^2=x nonlinear?','The dependent variable is squared','Linear DEs cannot contain nonlinear powers/functions of y.',None),

        # CHAPTER 10 — PARAMETRIC & POLAR
        ('Calc 2 — Ch 10','10.1 Parametric Curves','Recognition','In parametric equations x=f(t), y=g(t), what does t do?','It traces the point along the curve','Both coordinates depend on the same parameter.',None),
        ('Calc 2 — Ch 10','10.2 Parametric Calculus','Recognition','How do you compute dy/dx for x=f(t), y=g(t)?','(dy/dt)/(dx/dt)','Divide the component rates, provided dx/dt is nonzero.',None),
        ('Calc 2 — Ch 10','10.2 Parametric Calculus','Recognition','What quantity is integrated for arc length of a parametric plane curve?','sqrt((dx/dt)^2+(dy/dt)^2)','This is speed.',None),
        ('Calc 2 — Ch 10','10.3 Polar Coordinates','Recognition','What conversion takes polar coordinates to Cartesian coordinates?','x=r*cos(theta), y=r*sin(theta)','Polar gives distance and angle.',None),
        ('Calc 2 — Ch 10','10.3 Polar Coordinates','Recognition','What Cartesian identity follows from x=r cos(theta), y=r sin(theta)?','r^2=x^2+y^2','Square and add.',None),
        ('Calc 2 — Ch 10','10.4 Polar Curves','Recognition','When sketching r=f(theta), what should you track?','How radius r changes as theta changes','Negative r plots in the opposite direction.',None),
        ('Calc 2 — Ch 10','10.4 Polar Area','Recognition','What is the basic polar-area formula?','1/2 integral r^2 d(theta)','Polar sectors contribute one-half r squared d-theta.',None),
        ('Calc 2 — Ch 10','10.4 Polar Curves','Multiple Choice','Which polar equation describes a circle centered at the origin with radius 3?','r=3','Constant radius gives a centered circle.',['r=3','theta=3','r=3theta','r=cos(theta)']),

        # CHAPTER 11 — SEQUENCES & SERIES
        ('Calc 2 — Ch 11','11.1 Sequences','Recognition','What does it mean for a sequence a_n to converge to L?','a_n approaches L as n approaches infinity','Sequence convergence is a limit.',None),
        ('Calc 2 — Ch 11','11.2 Series','Recognition','What must be true of a_n if sum a_n converges?','a_n approaches 0','If terms do not approach zero, the series diverges.',None),
        ('Calc 2 — Ch 11','11.2 Geometric Series','Recognition','What condition makes sum a*r^n converge?','|r|<1','Then the infinite sum is a/(1-r) with the appropriate starting index.',None),
        ('Calc 2 — Ch 11','11.3 Integral Test','Recognition','A positive decreasing series resembles a function that is easy to integrate. What test may fit?','Integral test','Compare sum f(n) with integral f(x) dx.',None),
        ('Calc 2 — Ch 11','11.4 Comparison Tests','Recognition','Two positive-term series have similar size and one benchmark is known. What family of tests should you consider?','Comparison test','Use direct or limit comparison.',None),
        ('Calc 2 — Ch 11','11.5 Alternating Series','Recognition','What two conditions give convergence by the Alternating Series Test?','Terms decrease in magnitude and approach 0','Alternation alone is not enough.',None),
        ('Calc 2 — Ch 11','11.6 Ratio and Root Tests','Recognition','Factorials or exponentials dominate the terms of a series. What test is often efficient?','Ratio test','Ratios simplify factorials and powers well.',None),
        ('Calc 2 — Ch 11','11.8 Power Series','Recognition','What must you check after the ratio test gives an interval for a power series?','Test both endpoints separately','Endpoints can behave differently.',None),
        ('Calc 2 — Ch 11','11.9 Taylor Series','Recognition','What is a Taylor series designed to do?','Represent a function locally as an infinite polynomial','Coefficients come from derivatives at the center.',None),
        ('Calc 2 — Ch 11','11.10 Maclaurin Series','Recognition','What is a Maclaurin series?','A Taylor series centered at 0','Maclaurin is the special case a=0.',None),
        ('Calc 2 — Ch 11','11.10 Maclaurin Series','Recognition','What is the Maclaurin series for e^x?','sum from n=0 to infinity of x^n/n!','One of the core series to recognize.',None),
        ('Calc 2 — Ch 11','11.10 Maclaurin Series','Recognition','What is the first question to ask when choosing a convergence test?','What structural pattern does the series have?','Look for geometric, p-series, alternating, factorial/exponential, or comparison patterns before calculating.',None),
    ]
    curriculum_cards = early_calc_cards + curriculum_cards
    graph_match_cards=[
        ('Calc 3 — Ch 12','12.1 3D Coordinates','Graph Match','GRAPH_MATCH|circle','x^2+y^2=9','Circle: only x and y are needed.',['x^2+y^2=9','x^2+y^2+z^2=9','x^2/9 + y^2/4 + z^2 = 1','r(t)=<cos(t),sin(t),t>']),
        ('Calc 3 — Ch 12','12.1 3D Coordinates','Graph Match','GRAPH_MATCH|sphere','x^2+y^2+z^2=4','Sphere: x, y, and z are squared with equal scaling.',['x^2+y^2=4','x^2+y^2+z^2=4','x^2/9 + y^2/4 + z^2 = 1','r(t)=<t,t^2,t^3>']),
        ('Calc 3 — Ch 12','12.6 Quadric Surfaces','Graph Match','GRAPH_MATCH|ellipsoid','x^2/9 + y^2/4 + z^2 = 1','Unequal denominators create unequal semi-axis lengths.',['x^2+y^2+z^2=1','x^2/9 + y^2/4 + z^2 = 1','x^2+y^2=9','r(t)=<cos(t),sin(t),t>']),
        ('Calc 3 — Ch 13','13.1 Vector Functions','Graph Match','GRAPH_MATCH|helix','r(t)=<cos(t),sin(t),t/pi>','Circular x-y motion plus changing z creates a helix.',['r(t)=<cos(t),sin(t),t/pi>','r(t)=<t,t^2,t^3>','x^2+y^2+z^2=4','x^2+y^2=9']),
        ('Calc 3 — Ch 13','13.1 Vector Functions','Graph Match','GRAPH_MATCH|twisted_cubic','r(t)=<t,t^2,t^3>','Coordinate powers 1, 2, and 3 create the twisted cubic.',['r(t)=<t,t^2,t^3>','r(t)=<cos(t),sin(t),t/pi>','x^2/9 + y^2/4 + z^2 = 1','x^2+y^2+z^2=4']),
    ]
    curriculum_cards.extend(graph_match_cards)

    for subject,top,ctype,front,back,hint,choices in curriculum_cards:
        if not c.execute('SELECT 1 FROM cards WHERE subject=? AND front=?',(subject,front)).fetchone():
            packed='|||'.join(choices) if choices else None
            c.execute('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at,choices) VALUES (?,?,?,?,?,?,?,?)',(subject,top,ctype,front,back,hint,now(),packed))
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

def record(cid,result,conf,answer_mode='Flashcards'):
    c=conn();c.execute('INSERT INTO attempts(card_id,result,confidence,attempted_at,answer_mode) VALUES (?,?,?,?,?)',(int(cid),result,int(conf),now(),answer_mode));c.commit();c.close()

def get_best_quiz_streak():
    c=conn();r=c.execute("SELECT value FROM records WHERE key='best_quiz_streak'").fetchone();c.close();return int(r[0]) if r else 0

def save_best_quiz_streak(n):
    c=conn();c.execute("INSERT INTO records(key,value) VALUES ('best_quiz_streak',?) ON CONFLICT(key) DO UPDATE SET value=MAX(value,excluded.value)",(int(n),));c.commit();c.close()

def is_short_fill(r):
    """Use fill-in only for genuinely short recall answers (roughly 1–4 typed characters)."""
    ans=str(r.back).strip()
    compact=re.sub(r'\s+','',ans)
    if not compact or len(compact)>4:return False
    # Keep short symbolic/numeric answers as recall prompts; avoid short prose words.
    if re.search(r'[A-Za-z]{3,}',compact) and not re.search(r'[=+\-*/^0-9]',compact):
        return False
    return True

def is_fillable(r):
    return is_short_fill(r)

def normalize_answer(x):
    import re
    x=str(x).strip().casefold()

    # Natural-language aliases first, while spaces still exist.
    phrase_aliases={
        'inverse tangent':'atan',
        'inverse tan':'atan',
        'tan inverse':'atan',
        'arc tangent':'atan',
        'arc tan':'atan',
        'natural logarithm':'ln',
        'natural log':'ln',
        'plus c':'+c',
    }
    for src,dst in phrase_aliases.items(): x=x.replace(src,dst)

    # Be forgiving about normal typing differences without changing the concept.
    x=x.replace('π','pi').replace('−','-').replace('×','*').replace('·','*')
    x=x.replace('\\','').replace('{','(').replace('}',')')
    x=x.replace('arctan','atan').replace('tan^-1','atan').replace('tan^(-1)','atan')
    x=x.replace('tan⁻¹','atan')
    x=x.replace('e^(-1)','e^-1')
    x=x.replace('ln|x|','ln(abs(x))').replace('|x|','abs(x)')

    # Text answers should not fail because of capitalization, punctuation,
    # or a hyphen typed between words (cross-product vs Cross product.).
    x=re.sub(r'[.!?,;:]+$', '', x)
    x=re.sub(r'(?<=[a-z])-(?=[a-z])', '', x)
    x=re.sub(r'\s+', '', x)
    x=x.replace('*','')

    # Standardize common function spellings and trivial wrappers.
    x=re.sub(r'atan\((?:x|t|theta)\)', 'atan', x)
    x=re.sub(r'ln\((?:x|t)\)', 'ln', x)
    x=re.sub(r'(?<![a-z])1/e(?![a-z])', 'e^-1', x)
    return x

def answers_match(user,expected):
    a,b=normalize_answer(user),normalize_answer(expected)
    if a==b:return True

    # Concept-aware aliases for the foundation deck.  These are mathematically
    # equivalent ways students commonly type the same answer.
    equivalent_groups=[
        {'atan+c','atan'},                       # inverse tan / arctan recognition
        {'e^-1','1/e'},                          # reciprocal exponential notation
        {'sqrt(2)/2','1/sqrt(2)'},               # 45-degree unit-circle value
        {'sqrt(3)/3','1/sqrt(3)'},               # common rationalized trig value
    ]
    for group in equivalent_groups:
        if a in group and b in group:return True

    # Allow the variable to be omitted when the function itself is the tested
    # recognition target: atan(t)+C, atan(x)+C, and "inverse tan + C".
    if b.startswith('atan') and b.endswith('+c') and a in {'atan','atan+c'}:
        return True
    if a.startswith('atan') and a.endswith('+c') and b in {'atan','atan+c'}:
        return True

    # Numeric equivalence, including decimals such as 0.5 vs 1/2 when both
    # sides are directly parseable numbers.
    try:
        return abs(float(a)-float(b)) <= max(1e-4,abs(float(b))*0.01)
    except:
        return False

EXAM_SECTIONS={
    'Calc 3 — Exam 1': ['12.1','12.2','12.3','12.4','12.5','12.6','13.1'],
    'Calc 3 — Exam 2': ['13.2','13.3','13.4','14.1','14.2','14.3','14.4','14.5','14.6','14.7','14.8'],
    'Calc 3 — Exam 3': ['15.1','15.2','15.3','15.4','15.6','15.7','15.8','16.1','16.2','16.3','16.4'],
    'Calc 3 — Final Exam': ['12.1','12.2','12.3','12.4','12.5','12.6','13.1','13.2','13.3','13.4','14.1','14.2','14.3','14.4','14.5','14.6','14.7','14.8','15.1','15.2','15.3','15.4','15.6','15.7','15.8','16.1','16.2','16.3','16.4','16.5'],
}

def apply_exam_filter(d,exam):
    if exam=='All Material': return d
    secs=EXAM_SECTIONS.get(exam)
    if not secs: return d
    # The UNM exam filter intentionally removes textbook sections not assigned
    # for that exam, even if those cards remain available under All Material.
    mask=d['subject'].astype(str).str.startswith('Calc 3') & d['topic'].astype(str).apply(lambda x:any(x.startswith(sec) for sec in secs))
    return d[mask]

def pick(mode,exam,subject,topic,answer_style='Flashcards',exclude=None,seen_ids=None):
    d=apply_exam_filter(stats(),exam)
    if subject!='All': d=d[d.subject==subject]
    if topic!='All': d=d[d.topic==topic]
    if answer_style=='Fill in Blank': d=d[d.apply(is_short_fill,axis=1)]
    elif answer_style in ('Multiple Choice','Mixed Quiz'):
        d=d.copy()

    # Do not repeat a card during the same session while unseen cards remain.
    # Once every eligible card has been seen, a new cycle is allowed.
    full_pool=d.copy()
    seen_ids=set(seen_ids or [])
    if seen_ids:
        unseen=d[~d.id.isin(seen_ids)]
        if not unseen.empty:
            d=unseen

    # Never show the exact same card twice in a row when another card exists.
    if exclude is not None and len(d)>1:
        d=d[d.id!=exclude]

    if d.empty:
        d=full_pool
        if exclude is not None and len(d)>1:
            d=d[d.id!=exclude]
    if d.empty:return None

    if mode=='Weakest First':
        # Prioritize weak cards, but choose from a broader unseen pool so the
        # session has variety instead of bouncing among only a few cards.
        p=d.sort_values(['weakness','wrong','attempts'],ascending=[False,False,True]).head(min(20,len(d)))
        return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    if mode=='Missed Only':
        p=d[d.wrong>0]
        p=d if p.empty else p
        return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    return d.sample(1).iloc[0]

def streak():
    c=conn();r=[x[0] for x in c.execute('SELECT result FROM attempts ORDER BY id DESC').fetchall()];c.close();n=0
    for x in r:
        if x=='Correct':n+=1
        else:break
    return n

def esc(x):return html.escape(str(x),quote=True)

def _strip_outer_parens(x):
    x=x.strip()
    if len(x)>=2 and x[0]=='(' and x[-1]==')':
        depth=0;ok=True
        for i,ch in enumerate(x):
            if ch=='(': depth+=1
            elif ch==')': depth-=1
            if depth==0 and i<len(x)-1: ok=False;break
        if ok:return x[1:-1]
    return x

def expr_latex(raw):
    """Convert the compact notation stored in the deck into readable LaTeX."""
    import re
    s=str(raw).strip()

    # Canonical graph/equation forms. These bypass the generic fraction parser
    # so multi-term equations always render exactly as intended.
    canon=re.sub(r'\s+','',s)
    canonical_forms={
        'x^2+y^2=9': r'x^{2}+y^{2}=9',
        'x^2+y^2=4': r'x^{2}+y^{2}=4',
        'x^2+y^2+z^2=1': r'x^{2}+y^{2}+z^{2}=1',
        'x^2+y^2+z^2=4': r'x^{2}+y^{2}+z^{2}=4',
        'x^2+y^2+z^2=9': r'x^{2}+y^{2}+z^{2}=9',
        'x^2/9 + y^2/4 + z^2 = 1': r'\frac{x^{2}}{9}+\frac{y^{2}}{4}+z^{2}=1',
        'x^2/9+y^2/4+z^2/1=1': r'\frac{x^{2}}{9}+\frac{y^{2}}{4}+\frac{z^{2}}{1}=1',
        'x^2/4+y^2/9+z^2=1': r'\frac{x^{2}}{4}+\frac{y^{2}}{9}+z^{2}=1',
        'r(t)=<cos(t),sin(t),t>': r'\mathbf r(t)=\langle \cos t,\sin t,t\rangle',
        'r(t)=<cos(t),sin(t),t/pi>': r'\mathbf r(t)=\langle \cos t,\sin t,\frac{t}{\pi}\rangle',
        'r(t)=<t,t^2,t^3>': r'\mathbf r(t)=\langle t,t^{2},t^{3}\rangle',
    }
    if canon in canonical_forms:
        return canonical_forms[canon]
    # coordinate pairs / ordered pairs
    if re.fullmatch(r'\([^()]+,[^()]+\)',s):
        a,b=[x.strip() for x in s[1:-1].split(',',1)]
        return rf"\left({expr_latex(a)},\,{expr_latex(b)}\right)"
    # Equations/sums must be split before looking for a single fraction.
    # Example: x^2/9+y^2/4+z^2=1 should become three terms, not one nested fraction.
    depth=0
    eq_pos=None
    for i,ch in enumerate(s):
        if ch=='(': depth+=1
        elif ch==')': depth-=1
        elif ch=='=' and depth==0:
            eq_pos=i; break
    if eq_pos is not None:
        return rf"{expr_latex(s[:eq_pos])}={expr_latex(s[eq_pos+1:])}"

    depth=0
    plus_positions=[]
    for i,ch in enumerate(s):
        if ch=='(': depth+=1
        elif ch==')': depth-=1
        elif ch=='+' and depth==0:
            plus_positions.append(i)
    if plus_positions:
        parts=[]; start=0
        for pos in plus_positions:
            parts.append(s[start:pos]); start=pos+1
        parts.append(s[start:])
        return '+'.join(expr_latex(p.strip()) for p in parts)

    # A true single top-level fraction.
    depth=0
    for i,ch in enumerate(s):
        if ch=='(': depth+=1
        elif ch==')': depth-=1
        elif ch=='/' and depth==0:
            left,right=s[:i].strip(),s[i+1:].strip()
            return rf"\frac{{{expr_latex(left)}}}{{{expr_latex(_strip_outer_parens(right))}}}"
    # common leading fractional coefficient such as (1/2)e^(2x)
    m=re.match(r'^\(([^()/]+)/([^()/]+)\)(.+)$',s)
    if m:
        return rf"\frac{{{expr_latex(m.group(1))}}}{{{expr_latex(m.group(2))}}}{expr_latex(m.group(3))}"
    # recursively format function calls
    funcs={'sqrt':'\\sqrt','ln':'\\ln','sin':'\\sin','cos':'\\cos','tan':'\\tan','sec':'\\sec','csc':'\\csc','cot':'\\cot','arctan':'\\arctan','arcsin':'\\arcsin'}
    for name,cmd in funcs.items():
        pat=re.compile(rf'{name}\(([^()]*)\)')
        while pat.search(s):
            s=pat.sub(lambda m: (rf'{cmd}{{{expr_latex(m.group(1))}}}' if name=='sqrt' else rf'{cmd}\left({expr_latex(m.group(1))}\right)'),s)
    s=s.replace('theta',r'\theta').replace('pi',r'\pi')
    # e^(...) and generic parenthesized exponents
    s=re.sub(r'e\^\(([^()]*)\)',lambda m: rf'e^{{{expr_latex(m.group(1))}}}',s)
    s=re.sub(r'([A-Za-z0-9\\]+)\^\(([^()]*)\)',lambda m: rf'{m.group(1)}^{{{expr_latex(m.group(2))}}}',s)
    s=re.sub(r'\^(-?\d+)',r'^{\1}',s)
    s=re.sub(r'\^([A-Za-z])',r'^{\1}',s)
    s=s.replace('·',r'\cdot ')
    # readable function notation and constants
    s=s.replace(' + C','+C').replace('+ C','+C').replace(' - C','-C')
    return s

def question_markup(raw):
    """Render math cleanly inside prose without exposing raw x^2-style notation."""
    import re
    q=str(raw).strip()

    # Pure derivative questions
    m=re.fullmatch(r'd/dx\((.+)\)\s*=\s*\?',q)
    if m:return 'latex',rf"\frac{{d}}{{dx}}\left({expr_latex(m.group(1))}\right)=\ ?"
    m=re.fullmatch(r'd/dx\[(.+)\]\s*=\s*\?',q)
    if m:return 'latex',rf"\frac{{d}}{{dx}}\left[{expr_latex(m.group(1))}\right]=\ ?"

    # Pure integral questions
    m=re.fullmatch(r'∫\s*(.+)\s+d([A-Za-z])\s*=\s*\?',q)
    if m:return 'latex',rf"\int {expr_latex(m.group(1))}\,d{m.group(2)}=\ ?"

    # Simple equation questions
    if q.endswith('= ?') and not q.startswith(('Which','For','At','In')):
        lhs=q[:-3].strip()
        return 'latex',rf"{expr_latex(lhs)}=\ ?"

    # Natural-language integral prompt:
    # "For integral x*cos(x^2) dx, what is a natural u choice?"
    m=re.search(r'\bintegral\s+(.+?)\s+d([A-Za-z])(?=,|\?|$)',q,re.I)
    if m:
        integrand=m.group(1).strip()
        var=m.group(2)
        q=q[:m.start()] + rf"integral $\int {expr_latex(integrand)}\,d{var}$" + q[m.end():]

    # Known mixed-prose forms
    q=q.replace('d/dx[(x^2+1)^5]',r'$\frac{d}{dx}\left[(x^2+1)^5\right]$')
    q=q.replace('[F(x)]_a^b',r'$\left[F(x)\right]_a^b$')
    q=q.replace('e^(-1)',r'$e^{-1}$').replace('e^(-x)',r'$e^{-x}$')
    q=q.replace('0° (0 rad)',r'$0^\circ\;(0\text{ rad})$')
    q=q.replace('90° (pi/2)',r'$90^\circ\;(\pi/2)$')
    q=q.replace('(cos theta, sin theta)',r'$(\cos\theta,\sin\theta)$')

    # Named symbols
    q=re.sub(r'(?<![A-Za-z\\$])theta(?![A-Za-z$])',lambda m:r'$\theta$',q,flags=re.I)
    q=re.sub(r'(?<![A-Za-z\\$])pi(?![A-Za-z$])',lambda m:r'$\pi$',q,flags=re.I)

    # Convert compact powers in prose, e.g. x^2 -> $x^{2}$.
    parts=re.split(r'(\$[^$]*\$)',q)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(
            r'(?<![A-Za-z0-9_])([A-Za-z])\^(-?\d+)(?![A-Za-z0-9_])',
            lambda m: rf'${m.group(1)}^{{{m.group(2)}}}$',
            parts[i]
        )
    return 'md',''.join(parts)

def option_markup(raw):
    """Keep prose readable and format only the mathematical parts."""
    import re
    s=str(raw).strip()
    # Normalize stored LaTeX delimiters so they never leak literally into the UI.
    if len(s) >= 2 and s.startswith('$') and s.endswith('$'):
        s=s[1:-1].strip()

    # Explicitly prose-like answers should stay as prose.
    prose_like = bool(re.search(r'\s', s)) and not (
        s.startswith(('r(t)=','f(x)=','g(x)='))
        or re.fullmatch(r'[\sA-Za-z0-9_+\-*/^=<>|().,]+',s) and '=' in s and len(s.split()) <= 4
    )

    if not prose_like:
        # Pure/small symbolic answer
        mathish=(
            any(ch in s for ch in ['=', '^', '/', '<', '>', '√', '∫', '·'])
            or any(tok in s.lower() for tok in ['sqrt', 'pi', 'theta', 'sin(', 'cos(', 'tan(', 'ln(', 'e^', 'r(t)', 'f(x)', 'g(x)'])
        )
        if mathish:
            return f'${expr_latex(s)}$'
        return esc(s)

    # Prose: preserve word spacing and only convert obvious math snippets.
    out=esc(s)

    # u = ... expressions
    out=re.sub(r'\bu\s*=\s*([A-Za-z0-9_+\-*/^().]+)',
               lambda m: rf'$u={expr_latex(m.group(1))}$', out)

    # du = ... expressions
    out=re.sub(r'\bdu\s*=\s*([A-Za-z0-9_+\-*/^().]+)\s*d([A-Za-z])',
               lambda m: rf'$du={expr_latex(m.group(1))}\,d{m.group(2)}$', out)

    # Common dot-product formula embedded in prose
    out=re.sub(
        r'([A-Za-z])·([A-Za-z])\s*=\s*\|([A-Za-z])\|\|([A-Za-z])\|cos(?:theta|θ)',
        lambda m: rf'${m.group(1)}\cdot {m.group(2)}=|{m.group(3)}||{m.group(4)}|\cos\theta$',
        out, flags=re.I
    )

    # Named symbols inside prose answer choices.
    out=re.sub(r'(?<![A-Za-z\\$])theta(?![A-Za-z$])',
               lambda m:r'$\theta$', out, flags=re.I)
    out=re.sub(r'(?<![A-Za-z\\$])pi(?![A-Za-z$])',
               lambda m:r'$\pi$', out, flags=re.I)

    # Compact powers in prose
    parts=re.split(r'(\$[^$]*\$)',out)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(
            r'(?<![A-Za-z0-9_])([A-Za-z])\^(-?\d+)(?![A-Za-z0-9_])',
            lambda m: rf'${m.group(1)}^{{{m.group(2)}}}$',
            parts[i]
        )
    return ''.join(parts)

def objective_choices(r, exam, subject, topic):
    """Return sensible, stable MC options. Prefer curated concept families over random deck answers."""
    stored=r.get('choices',None)
    if pd.notna(stored) and str(stored).strip():
        return str(stored).split('|||')

    correct=str(r.back).strip()
    ckey=normalize_answer(correct)
    low=correct.lower().strip()
    qlow=str(r.front).lower()

    # Curated concept families. These produce plausible distractors instead of unrelated answers.
    families = [
        # Quadric / 3D shape recognition
        ['Sphere','Ellipsoid','Elliptic paraboloid','Hyperboloid of one sheet'],
        ['Sphere','Ellipsoid','Cylinder','Cone'],
        ['Circle','Sphere','Ellipsoid','Cylinder'],
        # Vector-output recognition
        ['A scalar','A vector','An angle','A point'],
        ['Dot product','Cross product','Scalar triple product','Projection'],
        ['Parallel','Perpendicular','Skew','Intersecting'],
        ['They are parallel','They are perpendicular','They have equal magnitude','Their dot product is zero'],
        # Lines / planes
        ['Point + direction vector','Point + normal vector','Two points only','A scalar equation only'],
        ['Intersecting','Parallel','Skew','Coincident'],
        # Calculus method recognition
        ['u-substitution','Integration by parts','Partial fractions','Trigonometric substitution'],
        ['Product rule','Quotient rule','Chain rule','Power rule'],
        ['Derivative','Integral','Limit','Series'],
        # Multivariable / vector calculus
        ['Gradient','Divergence','Curl','Laplacian'],
        ["Green's theorem","Stokes' theorem","Divergence theorem","Fundamental theorem for line integrals"],
        ['Polar coordinates','Cylindrical coordinates','Spherical coordinates','Cartesian coordinates'],
        # DE recognition
        ['Separation of variables','Integrating factor','Characteristic equation','Undetermined coefficients'],
        ['Stable','Unstable','Semistable','Not an equilibrium'],
    ]

    # Match by correct answer first.
    for fam in families:
        norm=[normalize_answer(x) for x in fam]
        if ckey in norm:
            opts=list(fam)
            random.shuffle(opts)
            return opts

    # Question-specific concept cues.
    if 'unequal coefficients' in qlow and any(v in qlow for v in ['x', 'y', 'z']):
        opts=['Sphere','Ellipsoid','Cylinder','Cone']
        random.shuffle(opts); return opts
    if 'cross product' in qlow and 'produce' in qlow:
        opts=['A vector','A scalar','An angle','A derivative']
        random.shuffle(opts); return opts
    if 'dot product' in qlow and ('produce' in qlow or 'result' in qlow):
        opts=['A scalar','A vector','A plane','A curve']
        random.shuffle(opts); return opts
    if 'critical number' in qlow:
        opts=[
            "Find where f'(x)=0 or f'(x) does not exist",
            "Find where f(x)=0",
            "Find where f''(x)=0 only",
            "Find where f(x) is undefined"
        ]
        random.shuffle(opts); return opts
    if 'intersection point of two parametric lines' in qlow:
        opts=[
            'Set corresponding coordinates equal, solve the parameters, then substitute back',
            'Take the dot product of the two direction vectors',
            'Take the cross product of the two position vectors',
            'Differentiate both line equations and set the derivatives equal'
        ]
        random.shuffle(opts); return opts
    if 'point-normal form of a plane' in qlow:
        opts=[
            'a(x-x0)+b(y-y0)+c(z-z0)=0',
            'r=r0+tv',
            'ax+by+cz=d',
            'n dot r=0'
        ]
        random.shuffle(opts); return opts
    if 'vector form of a line' in qlow:
        opts=[
            'r=r0+tv',
            'a(x-x0)+b(y-y0)+c(z-z0)=0',
            'ax+by+cz=d',
            'r(t)=<x0,y0,z0>'
        ]
        random.shuffle(opts); return opts
    if 'two planes are parallel' in qlow:
        opts=[
            'Their normal vectors are parallel',
            'Their normal vectors are perpendicular',
            'Their direction vectors have zero cross product',
            'They intersect at exactly one point'
        ]
        random.shuffle(opts); return opts
    if 'normal vector' in qlow and 'plane' in qlow and 'two direction vectors' in qlow:
        opts=[
            'Cross product',
            'Dot product',
            'Vector addition',
            'Scalar projection'
        ]
        random.shuffle(opts); return opts
    if 'polar coordinates' in qlow and 'x^2+y^2' in qlow.replace(' ',''):
        opts=['r^2','r','theta^2','x^2-y^2']
        random.shuffle(opts); return opts

    # Fallback: choose answers from the same topic, but only those with similar "answer shape".
    d=apply_exam_filter(stats(),exam)
    same_topic=d[(d.topic==r.topic) & (d.id!=r.id)]

    def answer_kind(s):
        s=str(s).strip()
        sl=s.lower()
        if re.search(r'[=^/<>]|sqrt|sin|cos|tan|ln|\d',s,re.I): return 'math'
        words=re.findall(r"[A-Za-z]+",s)
        if len(words)<=3: return 'short_prose'
        return 'long_prose'

    kind=answer_kind(correct)
    candidates=[]
    for ans in same_topic.back.astype(str).tolist():
        if normalize_answer(ans)==ckey: continue
        if answer_kind(ans)==kind:
            candidates.append(ans)

    # If we still do not have enough plausible same-topic distractors,
    # use generic distractors that match the response type rather than unrelated course material.
    topic_text=(str(r.topic)+' '+str(r.subject)+' '+qlow).lower()
    if 'lines and planes' in topic_text:
        generic_by_kind={
            'math':['r=r0+tv','ax+by+cz=d','a(x-x0)+b(y-y0)+c(z-z0)=0','n dot r=0'],
            'short_prose':['Direction vector','Normal vector','Cross product','Dot product'],
            'long_prose':['Their normal vectors are parallel','Their normal vectors are perpendicular',
                          'Set corresponding coordinates equal and solve','Use a cross product to find a normal vector']
        }
    elif 'quadric' in topic_text or '3d coordinates' in topic_text:
        generic_by_kind={
            'math':['x^2+y^2+z^2=1','x^2/4+y^2/9+z^2=1','x^2+y^2=1','z=x^2+y^2'],
            'short_prose':['Sphere','Ellipsoid','Cylinder','Cone'],
            'long_prose':['A sphere centered at the origin','An ellipsoid with unequal semi-axes',
                          'A cylinder extending along one axis','A paraboloid opening along one axis']
        }
    elif 'dot product' in topic_text or 'cross product' in topic_text or 'vectors' in topic_text:
        generic_by_kind={
            'math':['a dot b','a cross b','|a cross b|','a dot b=0'],
            'short_prose':['Dot product','Cross product','A scalar','A vector'],
            'long_prose':['The vectors are parallel','The vectors are perpendicular',
                          'Take the dot product first','Take the cross product first']
        }
    else:
        generic_by_kind={
            'math':['None of these','Cannot be determined','Equivalent expression','Different formula'],
            'short_prose':['None of these','Cannot be determined','Different method','Different quantity'],
            'long_prose':['None of these','Cannot be determined from the given information',
                          'Use a different method','The statement is not generally true']
        }

    seen={ckey}
    distractors=[]
    for ans in candidates + generic_by_kind[kind]:
        key=normalize_answer(ans)
        if not key or key in seen: continue
        distractors.append(ans); seen.add(key)
        if len(distractors)>=3: break

    choices=[correct]+distractors[:3]
    emergency=['None of these','Cannot be determined','Use a different method','Equivalent form not shown']
    for filler in emergency:
        if len(choices)>=4: break
        key=normalize_answer(filler)
        if key not in seen:
            choices.append(filler); seen.add(key)
    random.shuffle(choices)
    return choices

def elapsed(s):
    t=datetime.fromisoformat(s);q=max(0,int((datetime.now(timezone.utc)-t).total_seconds()));return f'{q//60}:{q%60:02d}'

init()
for k,v in {'card_id':None,'show_answer':False,'show_hint':False,'sig':None,'session_start':now(),'session_seen':0,'session_seen_ids':[],'target':12,'last_card':None,'mc_choice':None,'mc_options':None,'mc_options_card':None,'answer_style':'Flashcards','session_correct':0,'session_quiz_answered':0,'perfect_streak':0,'fill_value':''}.items():
    if k not in st.session_state:st.session_state[k]=v

with st.sidebar:
    st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
    st.markdown('### Study Controls')
    answer_style_options=['Flashcards','Multiple Choice','Fill in Blank','Mixed Quiz']
    saved_answer_style=st.session_state.get('answer_style','Flashcards')
    if saved_answer_style not in answer_style_options:
        saved_answer_style='Flashcards'
        st.session_state.answer_style=saved_answer_style
    answer_style=st.radio('Answer style',answer_style_options,index=answer_style_options.index(saved_answer_style),help='Perfect streaks count only objective quiz answers: Multiple Choice and Fill in Blank.')
    st.session_state.answer_style=answer_style
    mode=st.radio('Card order',['Weakest First','Missed Only','Random'])
    exam=st.selectbox('Study for', ['All Material','Calc 3 — Exam 1','Calc 3 — Exam 2','Calc 3 — Exam 3','Calc 3 — Final Exam'], help='Uses the UNM MATH 2531 exam coverage so you can study only the sections assigned to each exam.')
    cd=apply_exam_filter(cards_df(),exam)
    subjects=['All']+sorted(cd.subject.unique(), key=natural_sort_key);subject=st.selectbox('Subject',subjects)
    fd=cd if subject=='All' else cd[cd.subject==subject];topics=['All']+sorted(fd.topic.unique(), key=natural_sort_key);topic=st.selectbox('Topic',topics)
    if st.button('▶ Start a New Session',type='primary',use_container_width=True):
        st.session_state.session_start=now();st.session_state.session_seen=0;st.session_state.session_seen_ids=[];st.session_state.session_correct=0;st.session_state.session_quiz_answered=0;st.session_state.perfect_streak=0;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.mc_options=None;st.session_state.mc_options_card=None;st.session_state.fill_value='';st.rerun()
    st.caption('Weakest First automatically prioritizes the cards you miss most often.')
    st.markdown(f'<div class="record-card"><div class="record-sub">🏆 PERFECT STREAK RECORD</div><div class="record-num">{get_best_quiz_streak()}</div><div class="record-sub">objective answers correct in a row</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="quote">“A little progress every day adds up to big results.”</div>',unsafe_allow_html=True)

sig=(mode,exam,subject,topic,answer_style)
if sig!=st.session_state.sig:st.session_state.sig=sig;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.session_seen_ids=[]

st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Engineering Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
t1,t2,t3,t4=st.tabs(['🏠 Study','▥ Progress','▱ Decks','⚙ Settings'])

with t1:
    st.markdown('<div class="hero"><div class="badge">🎯 Same Effort.<br>Bigger Results.</div><h1>Engineering Study Cards</h1><p>Adaptive flashcards that focus on what you need most.</p></div>',unsafe_allow_html=True)
    d=apply_exam_filter(stats(),exam);sc=d.copy()
    if subject!='All':sc=sc[sc.subject==subject]
    if topic!='All':sc=sc[sc.topic==topic]
    a=int(sc.attempts.sum()) if len(sc) else 0;c=int(sc.correct.sum()) if len(sc) else 0;ac=100*c/a if a else 0;w=int((sc.weakness>=60).sum()) if len(sc) else 0;m=float(sc.mastery.mean()) if len(sc) else 0
    st.markdown(f'<div class="metrics"><div class="mcard"><div class="mlabel">📗 Total Attempts</div><div class="mval">{a}</div><div class="mfoot">Every answer improves your model</div></div><div class="mcard"><div class="mlabel">🎯 Accuracy</div><div class="mval">{ac:.0f}%</div><div class="mfoot">Correct across this filter</div></div><div class="mcard"><div class="mlabel">⚠️ Weak Cards</div><div class="mval">{w}</div><div class="mfoot">Priority score ≥ 60</div></div><div class="mcard"><div class="mlabel">🏆 Best Perfect Streak</div><div class="mval perfect">{get_best_quiz_streak()}</div><div class="mfoot">MCQ + fill-in answers</div></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="session-banner"><div class="session-stat"><strong>{exam}</strong><span>Study target</span></div><div class="session-stat"><strong>{answer_style}</strong><span>Current answer style</span></div><div class="session-stat"><strong>{st.session_state.session_correct}/{st.session_state.session_quiz_answered}</strong><span>Quiz score this session</span></div><div class="session-stat"><strong class="perfect">{st.session_state.perfect_streak} 🔥</strong><span>Current perfect streak</span></div><div class="session-stat"><strong>{elapsed(st.session_state.session_start)}</strong><span>Session time</span></div></div>',unsafe_allow_html=True)

    if st.session_state.card_id is None:
        r=pick(mode,exam,subject,topic,answer_style,st.session_state.last_card,st.session_state.session_seen_ids)
        if r is not None:st.session_state.card_id=int(r.id)
    cur=stats();cur=cur[cur.id==st.session_state.card_id]
    if cur.empty:
        st.info('No cards match this combination. Try another subject/topic or answer style.')
    else:
        r=cur.iloc[0];left,right=st.columns([3.25,1],gap='large')
        with left:
            idx=min(st.session_state.session_seen+1,st.session_state.target)
            hint=esc(r.hint) if st.session_state.show_hint else 'Try to identify the rule or pattern before answering.'
            qkind,qvalue=question_markup(r.front)

            def objective_result(correct):
                st.session_state.session_quiz_answered += 1
                if correct:
                    st.session_state.session_correct += 1
                    st.session_state.perfect_streak += 1
                    save_best_quiz_streak(st.session_state.perfect_streak)
                else:
                    st.session_state.perfect_streak = 0

            def advance(result,conf,ans_mode):
                record(r.id,result,conf,ans_mode)
                st.session_state.last_card=int(r.id);st.session_state.session_seen_ids=list(dict.fromkeys(st.session_state.session_seen_ids+[int(r.id)]));st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.mc_options=None;st.session_state.mc_options_card=None;st.session_state.fill_value='';st.session_state.session_seen+=1;st.rerun()

            # FLASHCARD MODE — self-rated, no objective streak scoring.
            if answer_style=='Flashcards':
                face='back' if st.session_state.show_answer else ''
                with st.container(key='flashcard'):
                    st.markdown(f'<div class="flip-shell"><div class="flip-face {face}"><span class="count">Card {idx} of {st.session_state.target} ☆</span><span class="pill">{esc(r.subject)}</span><span class="pill blue">{esc(r.topic)}</span></div></div>',unsafe_allow_html=True)
                    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
                    if not st.session_state.show_answer:
                        if qkind=='latex': st.latex(qvalue)
                        else: st.markdown(f'### {qvalue}')
                        st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
                        st.markdown(f'<div class="hint">💡 {hint}</div>',unsafe_allow_html=True)
                    else:
                        st.markdown('#### Answer')
                        if any(ch in str(r.back) for ch in '^/()'):
                            st.latex(expr_latex(r.back))
                        else:
                            st.markdown(f'### {esc(r.back)}')
                        st.caption(str(r.hint))
                x,y=st.columns(2)
                if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                if not st.session_state.show_answer:
                    if y.button('🔄 Flip Card',type='primary',use_container_width=True):st.session_state.show_answer=True;st.rerun()
                else:
                    if y.button('↩ Flip Back',use_container_width=True):st.session_state.show_answer=False;st.rerun()
                    q1,q2,q3,q4=st.columns(4)
                    if q1.button('❌ Missed',use_container_width=True):advance('Wrong',1,'Flashcards')
                    if q2.button('🟡 Hard',use_container_width=True):advance('Wrong',2,'Flashcards')
                    if q3.button('🔵 Got it',use_container_width=True):advance('Correct',3,'Flashcards')
                    if q4.button('✅ Easy',use_container_width=True):advance('Correct',5,'Flashcards')
                st.markdown('<div class="objective-note">Flashcard ratings improve the weakness tracker, but do not affect your Perfect Streak record.</div>',unsafe_allow_html=True)

            else:
                # Objective design: primarily multiple choice. In Mixed Quiz, only very
                # short recall answers (about 1–4 characters) become fill-in-the-blank.
                has_mc=(pd.notna(r.get('choices',None)) and str(r.get('choices','')).strip())
                if answer_style=='Multiple Choice':
                    render_mc=True
                elif answer_style=='Fill in Blank':
                    render_mc=False
                else:  # Mixed Quiz
                    render_mc=not is_short_fill(r)
                with st.container(key='flashcard'):
                    st.markdown(f'<span class="count">Card {idx} of {st.session_state.target} ☆</span><span class="pill">{esc(r.subject)}</span><span class="pill blue">{esc(r.topic)}</span>',unsafe_allow_html=True)
                    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
                    is_graph_match=str(r.front).startswith('GRAPH_MATCH|')
                    if is_graph_match:
                        st.markdown('### Match the equation to the graph')
                        render_shape_graph(str(r.front).split('|',1)[1])
                    elif qkind=='latex': st.latex(qvalue)
                    else: st.markdown(f'### {qvalue}')
                    st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
                    st.markdown(f'<div class="hint">💡 {hint}</div>',unsafe_allow_html=True)

                if render_mc:
                    if st.session_state.mc_options_card != int(r.id) or not st.session_state.mc_options:
                        st.session_state.mc_options=objective_choices(r,exam,subject,topic)
                        st.session_state.mc_options_card=int(r.id)
                    choices=list(st.session_state.mc_options)
                    letters=['A','B','C','D'][:len(choices)]
                    st.markdown('#### Choose the best answer')
                    for i,ch in enumerate(choices):
                        st.markdown(f"**{letters[i]}.** &nbsp;&nbsp; {option_markup(ch)}")
                    selected_letter=st.radio('Select A, B, C, or D',letters,index=None,key=f"mcq_{int(r.id)}",horizontal=True,label_visibility='collapsed')
                    choice=choices[letters.index(selected_letter)] if selected_letter in letters else None
                    x,y=st.columns(2)
                    if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                    if y.button('✓ Submit Answer',type='primary',use_container_width=True,disabled=choice is None):
                        correct=answers_match(choice,r.back);objective_result(correct);st.session_state.mc_choice=choice;st.session_state.show_answer=True;st.rerun()
                    if st.session_state.show_answer and st.session_state.mc_choice is not None:
                        correct=answers_match(st.session_state.mc_choice,r.back);cls='correct-glow' if correct else 'wrong-glow';icon='✅ Correct!' if correct else '❌ Not quite'
                        st.markdown(f'<div class="quiz-answer {cls}"><strong>{icon}</strong></div>',unsafe_allow_html=True)
                        st.markdown('**Correct answer:**')
                        if any(ch in str(r.back) for ch in '^/()'):
                            st.latex(expr_latex(r.back))
                        else:
                            st.markdown(f'### {esc(r.back)}')
                        if st.button('Next Question →',type='primary',use_container_width=True):advance('Correct' if correct else 'Wrong',5 if correct else 1,'Multiple Choice')
                else:
                    st.markdown('#### Type your answer')
                    st.caption('Simple equivalent formatting is accepted. Example: `5x^4`, `1/e`, `sqrt(2)/2`.')
                    typed=st.text_input('Answer',key=f"fill_{int(r.id)}",placeholder='Type the answer here…',label_visibility='collapsed')
                    x,y=st.columns(2)
                    if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                    if y.button('✓ Check Answer',type='primary',use_container_width=True,disabled=not typed.strip()):
                        correct=answers_match(typed,r.back);objective_result(correct);st.session_state.fill_value=typed;st.session_state.show_answer=True;st.rerun()
                    if st.session_state.show_answer and st.session_state.fill_value:
                        correct=answers_match(st.session_state.fill_value,r.back);cls='correct-glow' if correct else 'wrong-glow';icon='✅ Correct!' if correct else '❌ Not quite'
                        st.markdown(f'<div class="quiz-answer {cls}"><strong>{icon}</strong><div class="small">Your answer: {esc(st.session_state.fill_value)}</div></div>',unsafe_allow_html=True)
                        st.markdown('**Correct answer:**')
                        if any(ch in str(r.back) for ch in '^/()'):
                            st.latex(expr_latex(r.back))
                        else:
                            st.markdown(f'### {esc(r.back)}')
                        if st.button('Next Question →',type='primary',use_container_width=True):advance('Correct' if correct else 'Wrong',5 if correct else 1,'Fill in Blank')
        with right:
            shown_seen=min(st.session_state.session_seen,st.session_state.target)
            prog=min(100,100*shown_seen/max(1,st.session_state.target))
            st.markdown(f'<div class="side"><div class="stitle">⏱ Current Session</div><div style="display:flex;justify-content:space-between"><div><div class="big">{elapsed(st.session_state.session_start)}</div><div class="small">Time</div></div><div><div class="big perfect">{st.session_state.perfect_streak} 🔥</div><div class="small">Perfect streak</div></div></div></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="side"><div class="stitle">🏆 Record</div><div class="big perfect">{get_best_quiz_streak()}</div><div class="small">Best objective streak</div></div>',unsafe_allow_html=True)
            qs=sc.sort_values('weakness',ascending=False).head(4);items=''
            for _,z in qs.iterrows():
                cl='high' if z.weakness>=70 else ('med' if z.weakness>=50 else 'low');pr='High Priority' if z.weakness>=70 else ('Medium Priority' if z.weakness>=50 else 'Low Priority');items+=f'<div class="qitem"><div class="qname">{esc(z.topic)}</div><div class="{cl}" style="font-size:10px;font-weight:800">{pr}</div></div>'
            st.markdown('<div class="side"><div class="stitle">Next Up</div>'+items+'</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="side"><div class="stitle">Session Progress</div><div class="big">{shown_seen} / {st.session_state.target}</div><div class="prog"><div style="width:{prog:.0f}%"></div></div><div class="small" style="text-align:right;margin-top:5px">{prog:.0f}%</div></div>',unsafe_allow_html=True)

with t2:
    st.markdown('## Progress & Weakness Tracker');st.caption('Higher weakness means the card returns more aggressively.')
    d=stats();g=d.groupby(['subject','topic'],as_index=False).agg(attempts=('attempts','sum'),correct=('correct','sum'),wrong=('wrong','sum'),avg_weakness=('weakness','mean'),avg_mastery=('mastery','mean'));g['accuracy']=g.apply(lambda r:100*r.correct/r.attempts if r.attempts else 0,axis=1);g['Topic']=g.subject+' · '+g.topic
    a,b=st.columns(2);a.bar_chart(g.set_index('Topic')['avg_mastery'],horizontal=True);b.dataframe(g.sort_values('avg_weakness',ascending=False)[['subject','topic','attempts','wrong','accuracy','avg_weakness']],use_container_width=True,hide_index=True)
    st.markdown('### Cards needing the most work');st.dataframe(d.sort_values(['weakness','wrong'],ascending=False)[['subject','topic','front','attempts','correct','wrong','accuracy','weakness']].head(20),use_container_width=True,hide_index=True)

with t3:
    st.markdown('## Deck Manager')
    with st.form('add'):
        a,b,c=st.columns(3);subj=a.text_input('Subject',value='Calc 3');top=b.text_input('Topic');ctype=c.selectbox('Card type',['Flashcard','Multiple Choice','Fill in Blank','Recognition','Formula','Process','Concept','Practice']);front=st.text_area('Front / question');back=st.text_area('Back / answer');hint=st.text_input('Hint (optional)');choices=st.text_input('Multiple-choice options (optional, separate with |)')
        if st.form_submit_button('Add card',type='primary'):
            if subj.strip() and top.strip() and front.strip() and back.strip():
                c0=conn();c0.execute('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at,choices) VALUES (?,?,?,?,?,?,?,?)',(subj.strip(),top.strip(),ctype,front.strip(),back.strip(),hint.strip(),now(),'|||'.join([x.strip() for x in choices.split('|') if x.strip()]) if choices.strip() else None));c0.commit();c0.close();st.success('Card added.');st.rerun()
            else:st.error('Subject, topic, question, and answer are required.')
    st.dataframe(cards_df()[['subject','topic','card_type','front','back']],use_container_width=True,hide_index=True)

with t4:
    st.markdown('## Settings');st.session_state.target=st.slider('Cards per study session',5,40,int(st.session_state.target));st.info('Perfect streaks only count objectively graded Multiple Choice and Fill in Blank answers. Flashcard self-ratings still train the weakness model, but never affect the streak record. Progress is currently stored in local SQLite; Streamlit Community Cloud can reset local files during rebuilds.')
