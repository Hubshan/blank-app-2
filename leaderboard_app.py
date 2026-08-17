import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title='Normalization Challenge', page_icon='🎯', layout='wide')

@st.cache_resource
def get_db():
    url = st.secrets.get('SUPABASE_URL')
    key = st.secrets.get('SUPABASE_KEY')
    if not url or not key: return None
    try: return create_client(url, key)
    except Exception: return None

db=get_db()

PROBLEMS=[
('1NF','Atomicity','A Student table stores Courses = "DBMS, Python, Java" in one cell. What is the best fix?',['Keep the list','Create one row per course','Create another Student_ID','Delete Courses'],1,'1NF requires one atomic value per cell.'),
('1NF','Problem Solving','Order 101 stores Product_ID as "P01, P02, P03" in one cell. What should be done first?',['Create one row for each product','Make Product_ID a foreign key','Delete Product_ID','Duplicate Order_ID'],0,'Repeating values must be separated into individual rows.'),
('2NF','Partial Dependency','Enrollment(Student_ID, Course_ID, Student_Name, Grade) has composite key (Student_ID, Course_ID). Which FD violates 2NF?',['Student_ID,Course_ID → Grade','Student_ID → Student_Name','Student_ID,Course_ID → Student_Name','Grade → Student_ID'],1,'Student_Name depends only on part of the composite key.'),
('2NF','Decomposition','Which decomposition removes Student_Name partial dependency from Enrollment(Student_ID, Course_ID, Student_Name, Grade)?',['Student(Student_ID,Student_Name) and Enrollment(Student_ID,Course_ID,Grade)','Student(Student_ID,Grade) and Course(Course_ID,Student_Name)','Enrollment(Student_Name,Grade)','No decomposition'],0,'Move Student_Name to a relation where Student_ID is the key.'),
('3NF','Transitive Dependency','Student_ID → Dept_ID and Dept_ID → Dept_Name. Which FD causes the 3NF issue?',['Student_ID → Student_Name','Student_ID → Dept_ID','Dept_ID → Dept_Name','Student_Name → Dept_Name'],2,'Dept_Name is transitively dependent on Student_ID through Dept_ID.'),
('3NF','Decomposition','Employee(Emp_ID, Emp_Name, Dept_ID, Dept_Name) with Dept_ID → Dept_Name should be decomposed into:',['Employee(Emp_ID,Emp_Name,Dept_ID) + Department(Dept_ID,Dept_Name)','Employee(Emp_ID,Dept_Name) + Department(Emp_ID,Dept_ID)','Employee(Emp_Name,Dept_Name)','No change'],0,'Department facts should depend directly on Dept_ID in Department.'),
('BCNF','Determinant Check','R(Student,Course,Teacher) has Teacher → Course, but Teacher is not a superkey. Is R in BCNF?',['Yes','No, because Teacher is not a superkey','Yes, because it is 3NF','Only if Course is numeric'],1,'BCNF requires every determinant of a non-trivial FD to be a superkey.'),
('BCNF','Decomposition','R(A,B,C) has A → B and B → C; A is a key and B is not a superkey. What is the BCNF decomposition?',['Keep R','R1(B,C) and R2(A,B)','Delete B','Make C the key'],1,'B → C violates BCNF, so decompose on B → C.'),
('Mixed','Order of Work','A table has repeating values, a partial dependency and a transitive dependency. What order should be used?',['3NF→1NF→2NF→BCNF','1NF→2NF→3NF→BCNF','BCNF→3NF→2NF→1NF','2NF→BCNF→1NF→3NF'],1,'Normalization is applied progressively from 1NF to BCNF.'),
('Mixed','Concept Check','A relation is in 2NF and a non-key attribute depends on another non-key attribute. What should be addressed next?',['1NF','2NF again','3NF','BCNF directly'],2,'A non-key to non-key dependency is a transitive dependency, addressed by 3NF.')]
MCQS=[('1NF mainly requires:',['Atomic values','No foreign keys','No primary key','One row only'],0),('Partial dependency is mainly removed by:',['1NF','2NF','3NF','BCNF'],1),('Transitive dependency is mainly removed by:',['1NF','2NF','3NF','BCNF'],2),('BCNF requires every determinant to be a:',['Foreign key','Non-key attribute','Superkey','Tuple'],2),('A comma-separated list in one cell most directly violates:',['1NF','2NF','3NF','BCNF'],0),('2NF assumes the relation is already in:',['1NF','3NF','BCNF','4NF'],0),('Which is stricter?',['3NF','BCNF','2NF','1NF'],1),('Student_ID → Dept_ID and Dept_ID → Dept_Name is:',['Partial dependency','Transitive dependency','Multivalued dependency','Candidate key'],1),('A determinant is the left side of a:',['Tuple','Functional dependency','Foreign key','Primary key only'],1),('A relation can be in 3NF but not BCNF:',['Yes','No','Only without a key','Only in 1NF'],0)]

for k,v in {'started':False,'player':'','idx':0,'score':0,'attempts':[],'mode':'All Problems','saved':False}.items():
    st.session_state.setdefault(k,v)
def get_problems(): return PROBLEMS if st.session_state.mode=='All Problems' else [p for p in PROBLEMS if p[0]==st.session_state.mode]
def save_attempt(level,ptype,q,answer,correct,points):
    if db:
        try: db.table('normalization_attempts').insert({'player':st.session_state.player,'level':level,'problem_type':ptype,'question':q,'selected_answer':answer,'correct':correct,'points':points}).execute()
        except Exception: pass
def save_score():
    if not db or st.session_state.saved:return
    total=len(st.session_state.attempts);correct=sum(x['correct'] for x in st.session_state.attempts);acc=round(correct/total*100) if total else 0
    try: db.table('normalization_scores').insert({'player':st.session_state.player,'score':st.session_state.score,'correct':correct,'total':total,'accuracy':acc}).execute();st.session_state.saved=True
    except Exception: pass
def leaderboard():
    if not db:return pd.DataFrame()
    try:
        r=db.table('normalization_scores').select('player,score,correct,total,accuracy,created_at').order('score',desc=True).order('created_at',desc=False).limit(20).execute();return pd.DataFrame(r.data or [])
    except Exception:return pd.DataFrame()
def reset():
    for k,v in {'started':False,'player':'','idx':0,'score':0,'attempts':[],'mode':'All Problems','saved':False}.items():st.session_state[k]=v

st.markdown("<style>.hero{padding:20px;border-radius:18px;color:white;background:linear-gradient(135deg,#1d4ed8,#7c3aed);margin-bottom:1rem}.problem{padding:18px;border-left:6px solid #7c3aed;border-radius:10px;background:#faf7ff}</style>",unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>🎯 Normalization Problem Challenge</h1><p>Problem-first game for 1NF, 2NF, 3NF and BCNF with a shared online leaderboard.</p></div>",unsafe_allow_html=True)
with st.sidebar:
    st.header('🎮 Game Setup')
    if not st.session_state.started:
        name=st.text_input('Student / Player Name',max_chars=40);mode=st.selectbox('Problem Set',['All Problems','1NF','2NF','3NF','BCNF','Mixed'])
        if st.button('🚀 Start Game',type='primary',use_container_width=True):
            if not name.strip():st.warning('Please enter your name.')
            else:st.session_state.player=name.strip();st.session_state.mode=mode;st.session_state.started=True;st.session_state.idx=0;st.session_state.score=0;st.session_state.attempts=[];st.session_state.saved=False;st.rerun()
    else:
        st.success(f"Playing: {st.session_state.player}");st.metric('Current Score',st.session_state.score)
        if st.button('🔄 Restart',use_container_width=True):reset();st.rerun()
    st.divider();st.success('☁️ Shared leaderboard connected') if db else st.warning('☁️ Configure Supabase Secrets')

if not st.session_state.started:
    st.subheader('🏆 Shared Online Scorecard');board=leaderboard()
    if not board.empty:
        board.insert(0,'Rank',range(1,len(board)+1));board['created_at']=pd.to_datetime(board['created_at'],errors='coerce').dt.strftime('%d-%m-%Y %H:%M');st.dataframe(board.rename(columns={'player':'Player','score':'Score','correct':'Correct','total':'Total','accuracy':'Accuracy %','created_at':'Time'}),use_container_width=True,hide_index=True)
    else:st.info('No scores yet. Be the first player!')
    st.write('Students using the same deployed app see the same online leaderboard.');st.stop()

ps=get_problems();total=len(ps)+len(MCQS);i=st.session_state.idx
if i<len(ps):
    level,ptype,q,opts,ans,why=ps[i];st.progress(i/total);st.caption(f'Problem {i+1} of {len(ps)} • {level} • {ptype}');st.markdown(f"<div class='problem'><b>{ptype}</b><br><br>{q}</div>",unsafe_allow_html=True);answer=st.radio('Choose the best solution:',opts,index=None,key=f'p{i}')
    if st.button('✅ Submit Problem',type='primary',use_container_width=True):
        if answer is None:st.warning('Select an answer first.')
        else:
            correct=opts.index(answer)==ans;points=10 if correct else 0;st.session_state.score+=points;st.session_state.attempts.append({'level':level,'type':ptype,'question':q,'selected':answer,'correct':correct,'points':points});save_attempt(level,ptype,q,answer,correct,points);st.success(f'✅ Correct! +{points} points.') if correct else st.error(f'❌ Incorrect. Correct answer: {opts[ans]}');st.info(why);st.session_state.idx+=1;st.rerun()
elif i<total:
    qi=i-len(ps);q,opts,ans=MCQS[qi];st.progress(i/total);st.caption(f'MCQ {qi+1} of {len(MCQS)}');st.markdown(f"<div class='problem'><b>MCQ</b><br><br>{q}</div>",unsafe_allow_html=True);answer=st.radio('Choose one:',opts,index=None,key=f'm{qi}')
    if st.button('✅ Submit MCQ',type='primary',use_container_width=True):
        if answer is None:st.warning('Select an answer first.')
        else:
            correct=opts.index(answer)==ans;points=5 if correct else 0;st.session_state.score+=points;st.session_state.attempts.append({'level':'MCQ','type':'MCQ','question':q,'selected':answer,'correct':correct,'points':points});save_attempt('MCQ','MCQ',q,answer,correct,points);st.success(f'✅ Correct! +{points} points.') if correct else st.error(f'❌ Incorrect. Correct answer: {opts[ans]}');st.session_state.idx+=1;st.rerun()
else:
    save_score();df=pd.DataFrame(st.session_state.attempts);total_a=len(df);correct=int(df['correct'].sum());accuracy=round(correct/total_a*100) if total_a else 0;st.balloons();st.success('🎉 Game Complete!');st.header(f'🏆 Scorecard — {st.session_state.player}');a,b,c,d=st.columns(4);a.metric('Final Score',st.session_state.score);b.metric('Correct',correct);c.metric('Wrong',total_a-correct);d.metric('Accuracy',f'{accuracy}%');st.subheader('🌐 Shared Online Leaderboard');board=leaderboard()
    if not board.empty:
        board.insert(0,'Rank',range(1,len(board)+1));board['created_at']=pd.to_datetime(board['created_at'],errors='coerce').dt.strftime('%d-%m-%Y %H:%M');st.dataframe(board.rename(columns={'player':'Player','score':'Score','correct':'Correct','total':'Total','accuracy':'Accuracy %','created_at':'Time'}),use_container_width=True,hide_index=True)
    else:st.warning('Leaderboard unavailable. Configure Supabase Secrets.');st.subheader('📝 My Answer History');st.dataframe(df,use_container_width=True,hide_index=True);st.download_button('⬇️ Download My Scorecard',df.to_csv(index=False).encode('utf-8'),f'{st.session_state.player}_scorecard.csv','text/csv',use_container_width=True)
    if st.button('🎮 Play Again',type='primary',use_container_width=True):reset();st.rerun()
