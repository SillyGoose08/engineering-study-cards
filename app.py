import streamlit as st
import sqlite3
import random
from datetime import datetime
from pathlib import Path
import pandas as pd

DB_PATH = Path('flashcards.db')

st.set_page_config(page_title='Engineering Study Cards', page_icon='🧠', layout='wide')

# ---------- Database ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        card_type TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        hint TEXT DEFAULT '',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        result TEXT NOT NULL,
        confidence INTEGER NOT NULL DEFAULT 3,
        attempted_at TEXT NOT NULL,
        FOREIGN KEY(card_id) REFERENCES cards(id)
    );
    ''')
    conn.commit()
    conn.close()


def seed_cards():
    conn = get_conn()
    cur = conn.cursor()
    n = cur.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
    if n == 0:
        cards = [
            ('Calc 3','Vector integrals','Recognition','What do you do when integrating a vector-valued function?','Integrate each component separately.','Treat i, j, and k components as separate ordinary integrals.'),
            ('Calc 3','Vector functions','Process','Given r\'(t) and an initial condition r(a), what is the workflow?','Integrate each component, add constants, then use the initial condition to solve the constants.','Derivative given → integrate → constants → initial condition.'),
            ('Calc 3','Integration patterns','Recognition','You see ∫ t/(t²+1) dt. What method should you recognize?','u-substitution with u=t²+1, because du=2t dt.','Look for derivative-of-denominator over denominator.'),
            ('Calc 3','Integration patterns','Recognition','You see ∫ 1/(1+t²) dt. What antiderivative should you recognize?','arctan(t)+C.','This is a standard inverse trig pattern.'),
            ('Calc 3','Integration patterns','Recognition','You see √t inside an integral. What should you do first?','Rewrite √t as t^(1/2), then use the power rule.','Radicals are often easier as exponents.'),
            ('Calc 3','Dot product','Recognition','What should “angle between two vectors” make you think?','Dot product: a·b = |a||b|cosθ.','Dot product produces a scalar and connects directly to cosθ.'),
            ('Calc 3','Cross product','Recognition','What should “vector perpendicular to two vectors” make you think?','Cross product.','Cross product produces a new vector perpendicular to both inputs.'),
            ('Calc 3','Planes','Process','How do you build a plane equation once you know a point and a normal vector?','Use a(x-x₀)+b(y-y₀)+c(z-z₀)=0.','The normal vector gives a,b,c.'),
            ('Calc 3','Line intersection','Process','How do you find the intersection point of two parametric lines?','Use separate parameters, set x/y/z coordinates equal, solve for the parameters, then plug one parameter back into its line.','Different parameters are allowed for path intersection.'),
            ('Calc 3','Particle motion','Recognition','What is the key difference between path intersection and particle collision?','Collision requires both particles to be at the same point at the same time, so use the same time parameter.','Intersection allows different parameters; collision does not.'),
        ]
        cur.executemany('INSERT INTO cards(subject, topic, card_type, front, back, hint, created_at) VALUES (?,?,?,?,?,?,?)',
                        [(a,b,c,d,e,f,datetime.utcnow().isoformat()) for a,b,c,d,e,f in cards])
        conn.commit()
    conn.close()


def cards_df():
    conn = get_conn()
    df = pd.read_sql_query('SELECT * FROM cards ORDER BY subject, topic, id', conn)
    conn.close()
    return df


def stats_df():
    conn = get_conn()
    q = '''
    SELECT c.id, c.subject, c.topic, c.card_type, c.front,
           COUNT(a.id) AS attempts,
           SUM(CASE WHEN a.result='Correct' THEN 1 ELSE 0 END) AS correct,
           SUM(CASE WHEN a.result='Wrong' THEN 1 ELSE 0 END) AS wrong,
           MAX(a.attempted_at) AS last_attempt
    FROM cards c
    LEFT JOIN attempts a ON a.card_id=c.id
    GROUP BY c.id
    '''
    df = pd.read_sql_query(q, conn)
    conn.close()
    if len(df):
        df['correct'] = df['correct'].fillna(0)
        df['wrong'] = df['wrong'].fillna(0)
        df['attempts'] = df['attempts'].fillna(0)
        df['accuracy'] = df.apply(lambda r: (r.correct/r.attempts*100) if r.attempts else None, axis=1)
        # Higher = more urgent. Unseen cards get moderate priority.
        df['weakness'] = df.apply(lambda r: 50 if r.attempts == 0 else min(100, 25 + 60*(r.wrong/max(r.attempts,1)) + min(r.wrong*4,15)), axis=1)
        df['mastery'] = df.apply(lambda r: 0 if r.attempts == 0 else max(0, min(100, 100-r.weakness)), axis=1)
    return df


def record_attempt(card_id, result, confidence):
    conn = get_conn()
    conn.execute('INSERT INTO attempts(card_id, result, confidence, attempted_at) VALUES (?,?,?,?)',
                 (int(card_id), result, int(confidence), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def choose_card(mode, subject, topic):
    df = stats_df()
    if subject != 'All':
        df = df[df.subject == subject]
    if topic != 'All':
        df = df[df.topic == topic]
    if df.empty:
        return None
    if mode == 'Weakest First':
        pool = df.sort_values(['weakness','wrong','attempts'], ascending=[False,False,True]).head(min(12,len(df)))
        weights = [max(float(x), 1) for x in pool['weakness']]
        return pool.sample(1, weights=weights).iloc[0]
    if mode == 'Missed Only':
        pool = df[df.wrong > 0]
        if pool.empty:
            pool = df
        return pool.sample(1, weights=[max(float(x),1) for x in pool['weakness']]).iloc[0]
    return df.sample(1).iloc[0]


init_db(); seed_cards()

# ---------- Session state ----------
for k, v in {
    'card_id': None,
    'show_answer': False,
    'last_mode': None,
    'last_subject': None,
    'last_topic': None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- Sidebar ----------
st.sidebar.title('Study Controls')
mode = st.sidebar.radio('Study mode', ['Weakest First','Missed Only','Random'], index=0)
all_cards = cards_df()
subjects = ['All'] + sorted(all_cards.subject.unique().tolist())
subject = st.sidebar.selectbox('Subject', subjects)
filtered = all_cards if subject == 'All' else all_cards[all_cards.subject == subject]
topics = ['All'] + sorted(filtered.topic.unique().tolist())
topic = st.sidebar.selectbox('Topic', topics)

st.sidebar.caption('Weakest First automatically prioritizes cards you miss most often.')

# refresh card on filter/mode change
sig = (mode, subject, topic)
if sig != (st.session_state.last_mode, st.session_state.last_subject, st.session_state.last_topic):
    st.session_state.card_id = None
    st.session_state.show_answer = False
    st.session_state.last_mode, st.session_state.last_subject, st.session_state.last_topic = sig

# ---------- Header ----------
st.title('🧠 Engineering Study Cards')
st.caption('Adaptive flashcards that learn what you keep missing and build a more focused study set around those weaknesses.')

tab_study, tab_tracker, tab_deck = st.tabs(['Study', 'Weakness Tracker', 'Deck Manager'])

with tab_study:
    stats = stats_df()
    if subject != 'All': stats = stats[stats.subject == subject]
    if topic != 'All': stats = stats[stats.topic == topic]

    c1,c2,c3,c4 = st.columns(4)
    attempts = int(stats.attempts.sum()) if len(stats) else 0
    correct = int(stats.correct.sum()) if len(stats) else 0
    acc = (100*correct/attempts) if attempts else 0
    weak_count = int((stats.weakness >= 60).sum()) if len(stats) else 0
    mastery = float(stats.mastery.mean()) if len(stats) else 0
    c1.metric('Attempts', attempts)
    c2.metric('Accuracy', f'{acc:.0f}%')
    c3.metric('Weak cards', weak_count)
    c4.metric('Average mastery', f'{mastery:.0f}%')

    if st.session_state.card_id is None:
        row = choose_card(mode, subject, topic)
        if row is not None:
            st.session_state.card_id = int(row.id)

    current = stats_df()
    current = current[current.id == st.session_state.card_id]
    if current.empty:
        st.info('No cards match the current filters.')
    else:
        row = current.iloc[0]
        st.markdown(f"### {row.subject} · {row.topic}")
        st.caption(f"{row.card_type} card · Weakness priority: {row.weakness:.0f}/100")

        st.markdown('---')
        st.markdown(f"## {row.front}")
        st.markdown('---')

        a,b = st.columns([1,4])
        if not st.session_state.show_answer:
            if a.button('Show answer', use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
            with b.expander('Need a hint?'):
                cid = int(row.id)
                hint = all_cards.loc[all_cards.id==cid, 'hint'].iloc[0]
                st.write(hint)
        else:
            cid = int(row.id)
            back = all_cards.loc[all_cards.id==cid, 'back'].iloc[0]
            st.success(back)
            confidence = st.slider('How confident were you?', 1, 5, 3, help='1 = guessed / 5 = immediate recognition')
            x1,x2 = st.columns(2)
            if x1.button('❌ I missed it', use_container_width=True):
                record_attempt(cid, 'Wrong', confidence)
                st.session_state.card_id = None
                st.session_state.show_answer = False
                st.rerun()
            if x2.button('✅ I got it', use_container_width=True):
                record_attempt(cid, 'Correct', confidence)
                st.session_state.card_id = None
                st.session_state.show_answer = False
                st.rerun()

with tab_tracker:
    stats = stats_df()
    st.subheader('Weakness Tracker')
    st.caption('The higher the weakness score, the more aggressively the app will recycle that card into future sessions.')

    if len(stats):
        topic_stats = stats.groupby(['subject','topic'], as_index=False).agg(
            cards=('id','count'), attempts=('attempts','sum'), correct=('correct','sum'), wrong=('wrong','sum'),
            avg_weakness=('weakness','mean'), avg_mastery=('mastery','mean'))
        topic_stats['accuracy'] = topic_stats.apply(lambda r: (100*r.correct/r.attempts) if r.attempts else 0, axis=1)

        left,right = st.columns(2)
        with left:
            st.markdown('#### Mastery by topic')
            chart = topic_stats.copy()
            chart['label'] = chart['subject'] + ' — ' + chart['topic']
            st.bar_chart(chart.set_index('label')[['avg_mastery']])
        with right:
            st.markdown('#### Weakest topics')
            show = topic_stats.sort_values('avg_weakness', ascending=False)[['subject','topic','attempts','wrong','accuracy','avg_weakness']]
            st.dataframe(show, use_container_width=True, hide_index=True)

        st.markdown('#### Cards needing the most work')
        weak = stats.sort_values(['weakness','wrong'], ascending=False)[['subject','topic','front','attempts','correct','wrong','accuracy','weakness']].head(20)
        st.dataframe(weak, use_container_width=True, hide_index=True)

        st.markdown('#### Refined study set')
        refined = stats[(stats.wrong > 0) | (stats.attempts == 0)].sort_values(['weakness','wrong'], ascending=False).head(12)
        if refined.empty:
            st.success('No weak cards yet — keep studying and the tracker will build this set automatically.')
        else:
            for _, r in refined.iterrows():
                acc_text = 'Unseen' if pd.isna(r.accuracy) else f'{r.accuracy:.0f}% accuracy'
                st.write(f"**{r.topic}:** {r.front}  ·  {acc_text}  ·  priority {r.weakness:.0f}/100")

with tab_deck:
    st.subheader('Deck Manager')
    st.caption('Add your own cards now; CSV/PDF import can be added in the next phase.')

    with st.form('add_card'):
        c1,c2,c3 = st.columns(3)
        subj = c1.text_input('Subject', value='Calc 3')
        top = c2.text_input('Topic')
        ctype = c3.selectbox('Card type', ['Recognition','Formula','Process','Concept','Practice'])
        front = st.text_area('Front / question')
        back = st.text_area('Back / answer')
        hint = st.text_input('Hint (optional)')
        submitted = st.form_submit_button('Add card')
        if submitted:
            if subj.strip() and top.strip() and front.strip() and back.strip():
                conn = get_conn()
                conn.execute('INSERT INTO cards(subject, topic, card_type, front, back, hint, created_at) VALUES (?,?,?,?,?,?,?)',
                             (subj.strip(), top.strip(), ctype, front.strip(), back.strip(), hint.strip(), datetime.utcnow().isoformat()))
                conn.commit(); conn.close()
                st.success('Card added.')
                st.rerun()
            else:
                st.error('Subject, topic, front, and back are required.')

    st.markdown('#### Current deck')
    st.dataframe(cards_df()[['subject','topic','card_type','front','back']], use_container_width=True, hide_index=True)
