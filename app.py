import html, sqlite3, random, re
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

/* Interactive practice builders */
.interactive-panel{background:linear-gradient(180deg,#0d1f34,#081725);border:1px solid #294665;border-radius:16px;padding:18px 20px;margin:12px 0 14px}.interactive-title{font-size:18px;font-weight:850;color:#eef5ff;margin-bottom:5px}.interactive-sub{font-size:12px;color:var(--muted);margin-bottom:14px}.formula-builder{background:#f7f9fd;color:#10203c;border:1px solid #d5deec;border-radius:14px;padding:16px 18px;margin:10px 0 14px;text-align:center}.formula-builder .katex{font-size:1.35em}.vector-chip{display:inline-block;background:#e7e0ff;color:#563cd6;border-radius:10px;padding:7px 10px;margin:3px 5px 3px 0;font-weight:800}.interactive-feedback{border-radius:13px;padding:13px 15px;margin:12px 0}.interactive-feedback.ok{border:1px solid #2bd47f;background:rgba(43,212,127,.08)}.interactive-feedback.no{border:1px solid #ff5a6f;background:rgba(255,90,111,.08)}
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
    if 'review_stage' not in acols: c.execute('ALTER TABLE attempts ADD COLUMN review_stage INTEGER DEFAULT 0');c.commit()
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
    # Interactive practice base cards are inserted even for existing databases.
    # Their parameters are randomized each time they are served, so one base card
    # represents many practice variations while still feeding the same concept tracker.
    interactive_cards=[
        ('Calc 3','Dot product','Interactive','INTERACTIVE_DOT','Dot product','Compute the scalar by multiplying matching components and adding.'),
        ('Calc 3','Cross product','Interactive','INTERACTIVE_CROSS','Cross product','Use the determinant / component formula and watch the j-sign.'),
        ('Math Foundations','Product rule','Interactive','INTERACTIVE_PRODUCT_RULE','Product rule',"Build (fg)' = f'g + fg'."),
        ('Math Foundations','Quotient rule','Interactive','INTERACTIVE_QUOTIENT_RULE','Quotient rule',"For f/g: low·d(high) − high·d(low), over low²."),
        ('Math Foundations','Power rule','Interactive','INTERACTIVE_POWER_RULE','Power rule','Bring the exponent down, then subtract 1 from the exponent.'),
        ('Math Foundations','Chain rule','Interactive','INTERACTIVE_CHAIN_RULE','Chain rule','Differentiate the outer function, keep the inner, then multiply by the inner derivative.'),
    ]
    for subj,top,ctype,front,back,hint in interactive_cards:
        if not c.execute('SELECT 1 FROM cards WHERE front=?',(front,)).fetchone():
            c.execute('INSERT INTO cards(subject,topic,card_type,front,back,hint,created_at,choices) VALUES (?,?,?,?,?,?,?,NULL)',(subj,top,ctype,front,back,hint,now()))
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

def record(cid,result,conf,answer_mode='Flashcards',review_stage=0):
    c=conn();c.execute('INSERT INTO attempts(card_id,result,confidence,attempted_at,answer_mode,review_stage) VALUES (?,?,?,?,?,?)',(int(cid),result,int(conf),now(),answer_mode,int(review_stage)));c.commit();c.close()

def get_best_quiz_streak():
    c=conn();r=c.execute("SELECT value FROM records WHERE key='best_quiz_streak'").fetchone();c.close();return int(r[0]) if r else 0

def save_best_quiz_streak(n):
    c=conn();c.execute("INSERT INTO records(key,value) VALUES ('best_quiz_streak',?) ON CONFLICT(key) DO UPDATE SET value=MAX(value,excluded.value)",(int(n),));c.commit();c.close()

def is_fillable(r):
    ans=str(r.back).strip()
    if len(ans)>34:return False
    bad=['because ','integrate ','use ','requires ','cross product:','dot product:','separate ','collision ','arbitrary constant']
    return not any(x in ans.lower() for x in bad)

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

def eligible_cards(subject,topic,answer_style='Flashcards'):
    d=stats()
    if subject!='All': d=d[d.subject==subject]
    if topic!='All': d=d[d.topic==topic]
    if answer_style=='Multiple Choice': d=d[d.choices.notna() & (d.choices.astype(str).str.strip()!='')]
    elif answer_style=='Fill in Blank': d=d[d.apply(is_fillable,axis=1)]
    elif answer_style=='Mixed Quiz': d=d[(d.choices.notna() & (d.choices.astype(str).str.strip()!='')) | d.apply(is_fillable,axis=1)]
    elif answer_style=='Interactive Practice': d=d[d.card_type.astype(str).eq('Interactive')]
    return d

def pick(mode,subject,topic,answer_style='Flashcards',exclude=None,exclude_topic=None):
    d=eligible_cards(subject,topic,answer_style)
    if exclude and len(d)>1: d=d[d.id!=exclude]
    if exclude_topic and len(d)>1:
        alt=d[d.topic!=exclude_topic]
        if not alt.empty:d=alt
    if d.empty:return None
    if mode=='Weakest First':
        p=d.sort_values(['weakness','wrong','attempts'],ascending=[False,False,True]).head(min(12,len(d)))
        return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    if mode=='Missed Only':
        p=d[d.wrong>0];p=d if p.empty else p
        return p.sample(1,weights=[max(float(x),1) for x in p.weakness]).iloc[0]
    return d.sample(1).iloc[0]

def concept_variant(card_id,subject,topic,answer_style):
    d=eligible_cards(subject,topic,answer_style)
    d=d[d.id!=int(card_id)]
    if d.empty:return int(card_id)
    d=d.sort_values(['attempts','weakness'],ascending=[True,False]).head(min(6,len(d)))
    return int(d.sample(1).iloc[0].id)

def concept_progress():
    c=conn()
    q=pd.read_sql_query("SELECT c.subject,c.topic,a.card_id,a.result,COALESCE(a.review_stage,0) review_stage FROM attempts a JOIN cards c ON c.id=a.card_id",c)
    c.close()
    if q.empty:return pd.DataFrame(columns=['subject','topic','attempts','correct','spaced_successes','variations','concept_mastered'])
    rows=[]
    for (subj,top),g in q.groupby(['subject','topic']):
        correct=g[g.result=='Correct']
        rows.append({'subject':subj,'topic':top,'attempts':len(g),'correct':len(correct),
                     'spaced_successes':int(((g.result=='Correct') & (g.review_stage>0)).sum()),
                     'variations':int(correct.card_id.nunique())})
    out=pd.DataFrame(rows)
    out['concept_mastered']=(out.spaced_successes>=3)&(out.variations>=2)
    return out

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
    # Normalize common Unicode math glyphs used in the deck before building LaTeX.
    s=(s.replace('²','^2').replace('³','^3').replace('⁴','^4')
         .replace('⁵','^5').replace('⁶','^6').replace('⁻','-'))
    # coordinate pairs / ordered pairs
    if re.fullmatch(r'\([^()]+,[^()]+\)',s):
        a,b=[x.strip() for x in s[1:-1].split(',',1)]
        return rf"\left({expr_latex(a)},\,{expr_latex(b)}\right)"
    # top-level fraction
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
    """Return (kind, value): kind is 'latex' for display math or 'md' for mixed prose."""
    import re
    q=str(raw).strip()
    # derivative questions
    m=re.fullmatch(r'd/dx\((.+)\)\s*=\s*\?',q)
    if m:return 'latex',rf"\frac{{d}}{{dx}}\left({expr_latex(m.group(1))}\right)=\ ?"
    m=re.fullmatch(r'd/dx\[(.+)\]\s*=\s*\?',q)
    if m:return 'latex',rf"\frac{{d}}{{dx}}\left[{expr_latex(m.group(1))}\right]=\ ?"
    # integrals
    m=re.fullmatch(r'∫\s*(.+)\s+d([A-Za-z])\s*=\s*\?',q)
    if m:return 'latex',rf"\int {expr_latex(m.group(1))}\,d{m.group(2)}=\ ?"
    # simple equation questions
    if q.endswith('= ?') and not q.startswith(('Which','For','At','In')):
        lhs=q[:-3].strip()
        return 'latex',rf"{expr_latex(lhs)}=\ ?"
    # Mixed prose with an embedded integral, e.g.
    # "You see ∫ 1/(1+t²) dt. What antiderivative should you recognize?"
    # Keep the sentence as prose but render the mathematical expression with KaTeX.
    m=re.search(r'∫\s*(.+?)\s+d([A-Za-z])(?=[.?!,]|\s|$)',q)
    if m:
        integrand=m.group(1).strip()
        var=m.group(2)
        latex_integral=rf'\displaystyle \int {expr_latex(integrand)}\,d{var}'
        q=q[:m.start()]+f'${latex_integral}$'+q[m.end():]

    # Other mixed-prose replacements.
    q=q.replace('d/dx[(x^2+1)^5]',r'$\frac{d}{dx}\left[(x^2+1)^5\right]$')
    q=q.replace('[F(x)]_a^b',r'$\left[F(x)\right]_a^b$')
    q=q.replace('e^(-1)',r'$e^{-1}$').replace('e^(-x)',r'$e^{-x}$')
    q=q.replace('0° (0 rad)',r'$0^\circ\;(0\text{ rad})$')
    q=q.replace('90° (pi/2)',r'$90^\circ\;(\pi/2)$')
    q=q.replace('(cos theta, sin theta)',r'$(\cos\theta,\sin\theta)$')
    q=re.sub(r'(?<![$\w])ln\s+([A-Za-z])',lambda m: rf'$\ln({m.group(1)})$',q)
    return 'md',q

def option_markup(raw):
    s=str(raw).strip()
    # prose answers should stay prose
    prose_markers=['rule','constant','upper bound','x-intercept','positive','negative','undefined','automatic']
    if any(x in s.lower() for x in prose_markers) and not any(ch in s for ch in '^/=()'):
        return esc(s)
    return f'${expr_latex(s)}$'
def make_interactive_payload(r):
    """Create one randomized, reproducible-on-rerun practice variation."""
    top=str(r.topic)
    if top=='Dot product':
        a=[random.randint(-5,5) for _ in range(3)]
        b=[random.randint(-5,5) for _ in range(3)]
        while a==[0,0,0]: a=[random.randint(-5,5) for _ in range(3)]
        while b==[0,0,0]: b=[random.randint(-5,5) for _ in range(3)]
        return {'kind':'dot','a':a,'b':b,'answer':sum(x*y for x,y in zip(a,b))}
    if top=='Cross product':
        a=[random.randint(-4,4) for _ in range(3)]
        b=[random.randint(-4,4) for _ in range(3)]
        while a==[0,0,0] or b==[0,0,0] or a==b:
            a=[random.randint(-4,4) for _ in range(3)];b=[random.randint(-4,4) for _ in range(3)]
        ans=[a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
        return {'kind':'cross','a':a,'b':b,'answer':ans}
    if top=='Product rule':
        return {'kind':'product','answer':["f'","g","f","g'"]}
    if top=='Quotient rule':
        return {'kind':'quotient','answer':['g',"f'",'f',"g'",'g']}
    if top=='Power rule':
        n=random.randint(2,9)
        return {'kind':'power','n':n,'answer':[n,n-1]}
    if top=='Chain rule':
        a=random.choice([2,3,4,5]);b=random.randint(1,6);n=random.randint(2,6)
        return {'kind':'chain','a':a,'b':b,'n':n,'answer':[n*a,n-1]}
    return {'kind':'unknown'}

def interactive_payload(r):
    cid=int(r.id)
    if st.session_state.get('interactive_payload_card')!=cid or not st.session_state.get('interactive_payload'):
        st.session_state.interactive_payload=make_interactive_payload(r)
        st.session_state.interactive_payload_card=cid
        st.session_state.interactive_result=None
    return st.session_state.interactive_payload

def vector_latex(v):
    return r'\langle '+',\,'.join(str(int(x)) for x in v)+r'\rangle'

def elapsed(s):
    t=datetime.fromisoformat(s);q=max(0,int((datetime.now(timezone.utc)-t).total_seconds()));return f'{q//60}:{q%60:02d}'

init()
for k,v in {'card_id':None,'show_answer':False,'show_hint':False,'sig':None,'session_start':now(),'session_seen':0,'target':12,'last_card':None,'last_topic':None,'mc_choice':None,'answer_style':'Flashcards','session_correct':0,'session_quiz_answered':0,'perfect_streak':0,'fill_value':'','review_queue':[],'current_review_stage':0,'adaptive_note':'','interactive_payload':None,'interactive_payload_card':None,'interactive_result':None}.items():
    if k not in st.session_state:st.session_state[k]=v

with st.sidebar:
    st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
    st.markdown('### Study Controls')
    answer_styles=['Flashcards','Multiple Choice','Fill in Blank','Mixed Quiz','Interactive Practice'];answer_style=st.radio('Answer style',answer_styles,index=answer_styles.index(st.session_state.answer_style) if st.session_state.answer_style in answer_styles else 0,help='Perfect streaks count objectively graded Multiple Choice, Fill in Blank, and Interactive Practice answers.')
    st.session_state.answer_style=answer_style
    mode=st.radio('Card order',['Weakest First','Missed Only','Random'])
    cd=cards_df();subjects=['All']+sorted(cd.subject.unique());subject=st.selectbox('Subject',subjects)
    fd=cd if subject=='All' else cd[cd.subject==subject];topics=['All']+sorted(fd.topic.unique());topic=st.selectbox('Topic',topics)
    if st.button('▶ Start a New Session',type='primary',use_container_width=True):
        st.session_state.session_start=now();st.session_state.session_seen=0;st.session_state.session_correct=0;st.session_state.session_quiz_answered=0;st.session_state.perfect_streak=0;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.fill_value='';st.session_state.review_queue=[];st.session_state.current_review_stage=0;st.session_state.last_topic=None;st.session_state.adaptive_note='';st.session_state.interactive_payload=None;st.session_state.interactive_payload_card=None;st.session_state.interactive_result=None;st.rerun()
    st.caption('Adaptive spacing is on: misses return after a short delay, then a concept variation returns later. Topics are interleaved when possible.')
    st.markdown(f'<div class="record-card"><div class="record-sub">🏆 PERFECT STREAK RECORD</div><div class="record-num">{get_best_quiz_streak()}</div><div class="record-sub">objective answers correct in a row</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="quote">“A little progress every day adds up to big results.”</div>',unsafe_allow_html=True)

sig=(mode,subject,topic,answer_style)
if sig!=st.session_state.sig:st.session_state.sig=sig;st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False

st.markdown('<div class="brand"><div class="brain">🧠</div><div><h2>Engineering Study Cards</h2><div class="sub">Study smarter. Master faster.</div></div></div>',unsafe_allow_html=True)
t1,t2,t3,t4=st.tabs(['🏠 Study','▥ Progress','▱ Decks','⚙ Settings'])

with t1:
    st.markdown('<div class="hero"><div class="badge">🎯 Same Effort.<br>Bigger Results.</div><h1>Engineering Study Cards</h1><p>Adaptive flashcards that focus on what you need most.</p></div>',unsafe_allow_html=True)
    d=stats();sc=d.copy()
    if subject!='All':sc=sc[sc.subject==subject]
    if topic!='All':sc=sc[sc.topic==topic]
    a=int(sc.attempts.sum()) if len(sc) else 0;c=int(sc.correct.sum()) if len(sc) else 0;ac=100*c/a if a else 0;w=int((sc.weakness>=60).sum()) if len(sc) else 0;m=float(sc.mastery.mean()) if len(sc) else 0
    st.markdown(f'<div class="metrics"><div class="mcard"><div class="mlabel">📗 Total Attempts</div><div class="mval">{a}</div><div class="mfoot">Every answer improves your model</div></div><div class="mcard"><div class="mlabel">🎯 Accuracy</div><div class="mval">{ac:.0f}%</div><div class="mfoot">Correct across this filter</div></div><div class="mcard"><div class="mlabel">⚠️ Weak Cards</div><div class="mval">{w}</div><div class="mfoot">Priority score ≥ 60</div></div><div class="mcard"><div class="mlabel">🏆 Best Perfect Streak</div><div class="mval perfect">{get_best_quiz_streak()}</div><div class="mfoot">MCQ + fill-in + interactive</div></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="session-banner"><div class="session-stat"><strong>{answer_style}</strong><span>Current answer style</span></div><div class="session-stat"><strong>{st.session_state.session_correct}/{st.session_state.session_quiz_answered}</strong><span>Quiz score this session</span></div><div class="session-stat"><strong class="perfect">{st.session_state.perfect_streak} 🔥</strong><span>Current perfect streak</span></div><div class="session-stat"><strong>{len(st.session_state.review_queue)}</strong><span>Spaced reviews queued</span></div></div>',unsafe_allow_html=True)

    if st.session_state.card_id is None:
        due=[x for x in st.session_state.review_queue if int(x.get('due',9999))<=st.session_state.session_seen]
        if due:
            item=sorted(due,key=lambda x:(x.get('due',9999),-x.get('stage',0)))[0]
            st.session_state.review_queue.remove(item)
            st.session_state.card_id=int(item['card_id']);st.session_state.current_review_stage=int(item.get('stage',1))
            st.session_state.adaptive_note='Scheduled review — retrieve it from memory before checking the answer.'
        else:
            r=pick(mode,subject,topic,answer_style,st.session_state.last_card,st.session_state.last_topic)
            if r is not None:
                st.session_state.card_id=int(r.id);st.session_state.current_review_stage=0;st.session_state.adaptive_note=''
    cur=stats();cur=cur[cur.id==st.session_state.card_id]
    if cur.empty:
        st.info('No cards match this combination. Try another subject/topic or answer style.')
    else:
        r=cur.iloc[0];left,right=st.columns([3.25,1],gap='large')
        with left:
            idx=min(st.session_state.session_seen+1,st.session_state.target)
            hint=esc(r.hint) if st.session_state.show_hint else 'Try to identify the rule or pattern before answering.'
            qkind,qvalue=question_markup(r.front)
            if st.session_state.adaptive_note:
                st.info('🧠 '+st.session_state.adaptive_note)

            def objective_result(correct):
                st.session_state.session_quiz_answered += 1
                if correct:
                    st.session_state.session_correct += 1
                    st.session_state.perfect_streak += 1
                    save_best_quiz_streak(st.session_state.perfect_streak)
                else:
                    st.session_state.perfect_streak = 0

            def advance(result,conf,ans_mode):
                stage=int(st.session_state.current_review_stage or 0)
                record(r.id,result,conf,ans_mode,stage)
                next_step=st.session_state.session_seen+1
                if result=='Wrong':
                    delay=random.randint(3,5)
                    st.session_state.review_queue.append({'card_id':int(r.id),'due':next_step+delay,'stage':max(1,stage+1)})
                elif result=='Correct' and stage>0 and stage<3:
                    vid=concept_variant(r.id,r.subject,r.topic,answer_style)
                    delay=random.randint(8,12)
                    st.session_state.review_queue.append({'card_id':int(vid),'due':next_step+delay,'stage':stage+1})
                st.session_state.last_card=int(r.id);st.session_state.last_topic=str(r.topic);st.session_state.card_id=None;st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.fill_value='';st.session_state.current_review_stage=0;st.session_state.adaptive_note='';st.session_state.interactive_payload=None;st.session_state.interactive_payload_card=None;st.session_state.interactive_result=None;st.session_state.session_seen+=1;st.rerun()

            def skip_to_needs_work():
                # A skip is evidence that recall is not yet secure. Record it as a miss for
                # weakness/adaptive scheduling, but do not count it as a submitted quiz answer.
                stage=int(st.session_state.current_review_stage or 0)
                record(r.id,'Wrong',1,'Skipped',stage)
                st.session_state.perfect_streak=0
                next_step=st.session_state.session_seen+1
                st.session_state.review_queue.append({'card_id':int(r.id),'due':next_step+random.randint(3,5),'stage':max(1,stage+1)})
                st.session_state.last_card=int(r.id);st.session_state.last_topic=str(r.topic);st.session_state.card_id=None
                st.session_state.show_answer=False;st.session_state.show_hint=False;st.session_state.mc_choice=None;st.session_state.fill_value=''
                st.session_state.current_review_stage=0;st.session_state.adaptive_note='';st.session_state.interactive_payload=None
                st.session_state.interactive_payload_card=None;st.session_state.interactive_result=None;st.session_state.session_seen+=1
                st.rerun()

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

            elif answer_style=='Interactive Practice':
                payload=interactive_payload(r)
                kind=payload.get('kind')
                with st.container(key='flashcard'):
                    st.markdown(f'<span class="count">Card {idx} of {st.session_state.target} ☆</span><span class="pill">{esc(r.subject)}</span><span class="pill blue">{esc(r.topic)}</span>',unsafe_allow_html=True)
                    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
                    if kind=='dot':
                        st.markdown('### Compute the dot product')
                        st.latex(rf"\mathbf a={vector_latex(payload['a'])}\qquad \mathbf b={vector_latex(payload['b'])}")
                        st.latex(r"\mathbf a\cdot\mathbf b=\ ?")
                    elif kind=='cross':
                        st.markdown('### Build the cross product from the determinant')
                        a,b=payload['a'],payload['b']
                        st.latex(rf"\mathbf a\times\mathbf b=\begin{{vmatrix}}\mathbf i&\mathbf j&\mathbf k\\{a[0]}&{a[1]}&{a[2]}\\{b[0]}&{b[1]}&{b[2]}\end{{vmatrix}}")
                        st.caption('Cover the column for each component. Remember the sign pattern:  + i,  − j,  + k.')
                        st.latex(rf"\mathbf i\left[({a[1]})({b[2]})-({a[2]})({b[1]})\right]-\mathbf j\left[({a[0]})({b[2]})-({a[2]})({b[0]})\right]+\mathbf k\left[({a[0]})({b[1]})-({a[1]})({b[0]})\right]")
                        st.latex(r"\mathbf a\times\mathbf b=\langle\ ?,\ ?,\ ?\ \rangle")
                    elif kind=='product':
                        st.markdown('### Build the product rule')
                        st.latex(r"\frac{d}{dx}[f(x)g(x)]")
                        st.caption('Choose what belongs in each slot. The preview updates as you build it.')
                    elif kind=='quotient':
                        st.markdown('### Build the quotient rule')
                        st.latex(r"\frac{d}{dx}\left[\frac{f(x)}{g(x)}\right]")
                        st.caption('Build the numerator first, then choose the denominator base.')
                    elif kind=='power':
                        st.markdown('### Complete the power rule')
                        st.latex(rf"\frac{{d}}{{dx}}x^{{{payload['n']}}}=\boxed{{\ ?\ }}x^{{\boxed{{\ ?\ }}}}")
                    elif kind=='chain':
                        st.markdown('### Complete the chain-rule derivative')
                        st.latex(rf"\frac{{d}}{{dx}}\left({payload['a']}x+{payload['b']}\right)^{{{payload['n']}}}=\boxed{{\ ?\ }}\left({payload['a']}x+{payload['b']}\right)^{{\boxed{{\ ?\ }}}}")
                    st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
                    st.markdown(f'<div class="hint">💡 {hint}</div>',unsafe_allow_html=True)

                correct_now=None
                response_desc=''
                if kind=='dot':
                    val=st.number_input('Dot product (scalar)',step=1,value=None,placeholder='Enter the scalar result')
                    if st.button('✓ Check Interactive Answer',type='primary',use_container_width=True,disabled=val is None):
                        correct_now=(int(val)==int(payload['answer']));response_desc=str(int(val));objective_result(correct_now);st.session_state.interactive_result={'correct':correct_now,'response':response_desc};st.session_state.show_answer=True;st.rerun()
                elif kind=='cross':
                    a,b=payload['a'],payload['b']
                    c1,c2,c3=st.columns(3)
                    with c1:
                        st.latex(rf"i:\ ({a[1]})({b[2]})-({a[2]})({b[1]})")
                        vi=st.number_input('i component',step=1,value=None,key=f'cross_i_{r.id}')
                    with c2:
                        st.latex(rf"j:\ -\left[({a[0]})({b[2]})-({a[2]})({b[0]})\right]")
                        vj=st.number_input('j component',step=1,value=None,key=f'cross_j_{r.id}')
                    with c3:
                        st.latex(rf"k:\ ({a[0]})({b[1]})-({a[1]})({b[0]})")
                        vk=st.number_input('k component',step=1,value=None,key=f'cross_k_{r.id}')
                    if st.button('✓ Check Interactive Answer',type='primary',use_container_width=True,disabled=any(v is None for v in [vi,vj,vk])):
                        vals=[int(vi),int(vj),int(vk)];correct_now=(vals==payload['answer']);response_desc=str(vals);objective_result(correct_now);st.session_state.interactive_result={'correct':correct_now,'response':response_desc};st.session_state.show_answer=True;st.rerun()
                elif kind=='product':
                    opts=['—','f',"f'",'g',"g'"]
                    c1,c2,c3,c4=st.columns(4);s1=c1.selectbox('Slot 1',opts,key=f'pr1_{r.id}');s2=c2.selectbox('Slot 2',opts,key=f'pr2_{r.id}');s3=c3.selectbox('Slot 3',opts,key=f'pr3_{r.id}');s4=c4.selectbox('Slot 4',opts,key=f'pr4_{r.id}')
                    preview=[s if s!='—' else r'\square' for s in [s1,s2,s3,s4]];st.latex(rf"({preview[0]})({preview[1]})+({preview[2]})({preview[3]})")
                    ready=all(x!='—' for x in [s1,s2,s3,s4])
                    if st.button('✓ Check Rule Builder',type='primary',use_container_width=True,disabled=not ready):
                        vals=[s1,s2,s3,s4];correct_now=(vals==payload['answer']);response_desc=' '.join(vals);objective_result(correct_now);st.session_state.interactive_result={'correct':correct_now,'response':response_desc};st.session_state.show_answer=True;st.rerun()
                elif kind=='quotient':
                    opts=['—','f',"f'",'g',"g'"]
                    c1,c2,c3,c4=st.columns(4);s1=c1.selectbox('Numerator 1',opts,key=f'qr1_{r.id}');s2=c2.selectbox('Numerator 2',opts,key=f'qr2_{r.id}');s3=c3.selectbox('Numerator 3',opts,key=f'qr3_{r.id}');s4=c4.selectbox('Numerator 4',opts,key=f'qr4_{r.id}')
                    den=st.selectbox('Denominator base (squared)',opts,key=f'qr5_{r.id}')
                    pv=[s if s!='—' else r'\square' for s in [s1,s2,s3,s4,den]];st.latex(rf"\frac{{({pv[0]})({pv[1]})-({pv[2]})({pv[3]})}}{{({pv[4]})^2}}")
                    ready=all(x!='—' for x in [s1,s2,s3,s4,den])
                    if st.button('✓ Check Rule Builder',type='primary',use_container_width=True,disabled=not ready):
                        vals=[s1,s2,s3,s4,den];correct_now=(vals==payload['answer']);response_desc=' '.join(vals);objective_result(correct_now);st.session_state.interactive_result={'correct':correct_now,'response':response_desc};st.session_state.show_answer=True;st.rerun()
                elif kind in {'power','chain'}:
                    a1,a2=st.columns(2);coef=a1.number_input('Coefficient',step=1,value=None);exp=a2.number_input('New exponent',step=1,value=None)
                    if st.button('✓ Check Interactive Answer',type='primary',use_container_width=True,disabled=coef is None or exp is None):
                        vals=[int(coef),int(exp)];correct_now=(vals==payload['answer']);response_desc=str(vals);objective_result(correct_now);st.session_state.interactive_result={'correct':correct_now,'response':response_desc};st.session_state.show_answer=True;st.rerun()

                if not st.session_state.show_answer:
                    if st.button('⏭ Skip — Mark Needs Work',use_container_width=True,help='Records this card as needing work and schedules it for a spaced review.'):
                        skip_to_needs_work()

                if st.session_state.show_answer and st.session_state.interactive_result:
                    rr=st.session_state.interactive_result;ok=bool(rr['correct']);cls='ok' if ok else 'no';msg='✅ Correct!' if ok else '❌ Not quite'
                    st.markdown(f'<div class="interactive-feedback {cls}"><strong>{msg}</strong><div class="small">Your response: {esc(rr.get("response",""))}</div></div>',unsafe_allow_html=True)
                    st.markdown('**Correct construction:**')
                    if kind=='dot': st.latex(rf"\mathbf a\cdot\mathbf b={payload['answer']}")
                    elif kind=='cross': st.latex(rf"\mathbf a\times\mathbf b={vector_latex(payload['answer'])}")
                    elif kind=='product': st.latex(r"(fg)'=f'g+fg'")
                    elif kind=='quotient': st.latex(r"\left(\frac{f}{g}\right)'=\frac{gf'-fg'}{g^2}")
                    elif kind=='power': st.latex(rf"\frac{{d}}{{dx}}x^{{{payload['n']}}}={payload['answer'][0]}x^{{{payload['answer'][1]}}}")
                    elif kind=='chain': st.latex(rf"\frac{{d}}{{dx}}({payload['a']}x+{payload['b']})^{{{payload['n']}}}={payload['answer'][0]}({payload['a']}x+{payload['b']})^{{{payload['answer'][1]}}}")
                    if st.button('Next Question →',type='primary',use_container_width=True):advance('Correct' if ok else 'Wrong',5 if ok else 1,'Interactive Practice')

            else:
                # Choose objective rendering. Mixed Quiz uses MCQ when choices exist, otherwise fill-in.
                has_mc=(pd.notna(r.get('choices',None)) and str(r.get('choices','')).strip())
                render_mc = answer_style=='Multiple Choice' or (answer_style=='Mixed Quiz' and has_mc)
                if answer_style=='Fill in Blank':render_mc=False
                with st.container(key='flashcard'):
                    st.markdown(f'<span class="count">Card {idx} of {st.session_state.target} ☆</span><span class="pill">{esc(r.subject)}</span><span class="pill blue">{esc(r.topic)}</span>',unsafe_allow_html=True)
                    st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True)
                    if qkind=='latex': st.latex(qvalue)
                    else: st.markdown(f'### {qvalue}')
                    st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
                    st.markdown(f'<div class="hint">💡 {hint}</div>',unsafe_allow_html=True)

                if render_mc and has_mc:
                    choices=str(r['choices']).split('|||');letters=['A','B','C','D'][:len(choices)]
                    st.markdown('#### Choose the best answer')
                    cols=st.columns(2)
                    for i,ch in enumerate(choices):
                        with cols[i%2]: st.markdown(f'**{letters[i]}.** &nbsp; {option_markup(ch)}')
                    selected_letter=st.radio('Select A, B, C, or D',letters,index=None,key=f"mcq_{int(r.id)}",horizontal=True,label_visibility='collapsed')
                    choice=choices[letters.index(selected_letter)] if selected_letter in letters else None
                    x,y=st.columns(2)
                    if x.button('💡 Hide Hint' if st.session_state.show_hint else '💡 Show Hint',use_container_width=True):st.session_state.show_hint=not st.session_state.show_hint;st.rerun()
                    if y.button('✓ Submit Answer',type='primary',use_container_width=True,disabled=choice is None):
                        correct=(choice==str(r.back));objective_result(correct);st.session_state.mc_choice=choice;st.session_state.show_answer=True;st.rerun()
                    if st.session_state.show_answer and st.session_state.mc_choice is not None:
                        correct=(st.session_state.mc_choice==str(r.back));cls='correct-glow' if correct else 'wrong-glow';icon='✅ Correct!' if correct else '❌ Not quite'
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
    st.markdown('### Concept mastery')
    cp=concept_progress()
    if cp.empty: st.caption('Concept mastery appears after you begin answering cards.')
    else:
        cp['status']=cp['concept_mastered'].map({True:'✅ Mastered',False:'🔁 Building'})
        st.caption('A concept is promoted after at least 3 successful delayed reviews across at least 2 different question variations.')
        st.dataframe(cp.sort_values(['concept_mastered','spaced_successes','variations'],ascending=[True,True,True])[['subject','topic','spaced_successes','variations','status']],use_container_width=True,hide_index=True)

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
    st.markdown('## Settings');st.session_state.target=st.slider('Cards per study session',5,40,int(st.session_state.target));st.info('Adaptive retrieval is enabled: a miss returns after 3–5 other questions; a successful delayed review schedules a concept variation 8–12 questions later. Topics are interleaved when possible. Perfect streaks count objectively graded Multiple Choice, Fill in Blank, and Interactive Practice answers. Progress is currently stored in local SQLite; Streamlit Community Cloud can reset local files during rebuilds.')
