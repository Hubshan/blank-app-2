import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Normalization Challenge', page_icon='🎮', layout='wide')
DB=Path('normalization_game.db')

def db():
    con=sqlite3.connect(DB)
    con.execute('CREATE TABLE IF NOT EXISTS responses(id INTEGER PRIMARY KEY AUTOINCREMENT,player TEXT,level TEXT,question TEXT,answer TEXT,correct INTEGER,score INTEGER,created_at TEXT)')
    con.commit(); return con

def save_response(player,level,q,answer,correct,score):
    con=db(); con.execute('INSERT INTO responses(player,level,question,answer,correct,score,created_at) VALUES(?,?,?,?,?,?,?)',(player,level,q,answer,int(correct),score,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))); con.commit(); con.close()

def scores():
    con=db(); df=pd.read_sql_query('SELECT player, SUM(score) score, ROUND(100.0*SUM(correct)/COUNT(*),0) quiz_percent, MAX(created_at) date FROM responses GROUP BY player ORDER BY score DESC LIMIT 10',con); con.close(); return df

def responses():
    con=db(); df=pd.read_sql_query('SELECT player,level,question,answer,CASE WHEN correct=1 THEN "Yes" ELSE "No" END correct,score,created_at FROM responses ORDER BY id DESC LIMIT 200',con); con.close(); return df

game={
'1NF':('Which change correctly converts the table toward 1NF?',[['Student_ID','Student_Name','Courses'],['S01','Anu','DBMS, Python'],['S02','Bala','Java, Web']],['Keep the list in one cell.','Split each course into a separate row/value.','Create another Student_Name column.','Sort students alphabetically.'],1,'1NF requires atomic values.'),
'2NF':('Primary key is (Student_ID, Course_ID). Which dependency violates 2NF?',[['Student_ID','Course_ID','Student_Name','Grade'],['S01','C01','Anu','A'],['S01','C02','Anu','B+']],['Student_ID, Course_ID → Grade','Student_ID → Student_Name','Course_ID, Student_ID → Grade','Student_ID, Course_ID → Grade, Student_Name'],1,'Student_Name depends only on part of the composite key: partial dependency.'),
'3NF':('Student_ID → Dept_ID and Dept_ID → Dept_Name. Which attribute is transitively dependent?',[['Student_ID','Dept_ID','Dept_Name'],['S01','D01','Computer Science'],['S02','D01','Computer Science']],['Student_ID','Dept_ID','Dept_Name','None'],2,'Dept_Name depends on Dept_ID, which depends on Student_ID.'),
'BCNF':('Teacher → Subject, but Teacher is not a superkey. Does the relation satisfy BCNF?',[['Teacher','Subject','Room'],['T01','DBMS','R1'],['T01','Python','R2']],['Yes, because it is 3NF.','Yes, because Teacher is a determinant.','No, because Teacher is not a superkey.','No, because Room is numeric.'],2,'BCNF requires every determinant of a non-trivial FD to be a superkey.')}
quiz=[('What is the main rule of 1NF?',['Atomic values','No primary key','No foreign key','Only one row'],0),('Which normal form removes partial dependency?',['1NF','2NF','3NF','BCNF'],1),('3NF mainly removes:',['Repeating groups','Partial dependency','Transitive dependency','Primary keys'],2),('BCNF requires every determinant to be:',['Foreign key','Non-key attribute','Superkey','Numeric value'],2),('A comma-separated list in one cell most directly violates:',['1NF','2NF','3NF','BCNF'],0),('2NF requires a relation to already be in:',['1NF','3NF','BCNF','4NF'],0),('Which is stricter?',['3NF','BCNF','2NF','1NF'],1),('Student_ID → Dept_ID and Dept_ID → Dept_Name is:',['Partial dependency','Transitive dependency','Multivalued dependency','Candidate key'],1),('A partial dependency occurs when a non-key attribute depends on:',['Whole composite key','Part of a composite key','Foreign key only','No key'],1),('BCNF is based on the rule that every determinant is a:',['Tuple','Attribute','Superkey','Foreign key'],2)]

init=db(); init.close()
if 'player' not in st.session_state: st.session_state.player=''
if 'score' not in st.session_state: st.session_state.score=0
if 'step' not in st.session_state: st.session_state.step=0
if 'started' not in st.session_state: st.session_state.started=False

st.title('🎮 Normalization Challenge')
st.caption('Interactive learning game: 1NF → 2NF → 3NF → BCNF + MCQ Quiz')

with st.sidebar:
    st.header('👤 Player')
    name=st.text_input('Your name',value=st.session_state.player,max_chars=30)
    if st.button('Start / Restart Game',use_container_width=True):
        if name.strip():
            st.session_state.player=name.strip(); st.session_state.score=0; st.session_state.step=0; st.session_state.started=True; st.rerun()
        else: st.warning('Enter your name first.')
    st.metric('Current Score',st.session_state.score)
    high=scores(); st.metric('High Score',int(high.iloc[0].score) if not high.empty else 0)
    st.divider(); st.info('Scores and answers are stored in SQLite. For Streamlit Community Cloud, persistent storage is not guaranteed across app restarts.')

home,game_tab,board,resp=st.tabs(['🏠 Home','🎯 Game','🏆 High Scores','📝 Responses'])
with home:
    st.subheader('How to Play')
    st.write('Answer four normalization challenges and then complete the 10-question MCQ quiz.')
    c1,c2,c3,c4=st.columns(4)
    c1.info('**1NF**\n\nAtomic values')
    c2.info('**2NF**\n\nNo partial dependency')
    c3.info('**3NF**\n\nNo transitive dependency')
    c4.info('**BCNF**\n\nEvery determinant is a superkey')
    if not st.session_state.started: st.warning('Enter your name in the sidebar and click Start / Restart Game.')

with game_tab:
    if not st.session_state.started:
        st.warning('Start the game from the sidebar.')
    else:
        total=14
        step=st.session_state.step
        st.progress(min(step,total)/total)
        if step<4:
            level=list(game.keys())[step]; q,table,opts,ans,why=game[level]
            st.subheader(f'Level {step+1}: {level}')
            st.write(q); st.table(pd.DataFrame(table[1:],columns=table[0]))
            choice=st.radio('Choose one answer:',opts,key=f'level_{step}')
            if st.button('Submit Answer',key=f'submit_{step}',type='primary'):
                i=opts.index(choice); correct=i==ans; pts=10 if correct else 0; st.session_state.score+=pts
                save_response(st.session_state.player,level,q,choice,correct,pts)
                if correct: st.success(f'✅ Correct! +{pts} points. {why}')
                else: st.error(f'❌ Incorrect. Correct answer: {opts[ans]} — {why}')
                st.session_state.step+=1; st.rerun()
        elif step<14:
            qi=step-4; q,opts,ans=quiz[qi]
            st.subheader(f'🧠 MCQ {qi+1} of 10')
            st.write(q); choice=st.radio('Choose one:',opts,key=f'quiz_{qi}')
            if st.button('Submit Answer',key=f'qsubmit_{qi}',type='primary'):
                i=opts.index(choice); correct=i==ans; pts=5 if correct else 0; st.session_state.score+=pts
                save_response(st.session_state.player,'MCQ',q,choice,correct,pts)
                if correct: st.success(f'✅ Correct! +{pts} points.')
                else: st.error(f'❌ Incorrect. Correct answer: {opts[ans]}')
                st.session_state.step+=1; st.rerun()
        else:
            st.balloons(); st.success('🎉 Game Complete!')
            st.metric('Final Score',st.session_state.score)
            st.write('Visit **High Scores** to see the leaderboard.')
            if st.button('Play Again'): st.session_state.score=0; st.session_state.step=0; st.rerun()

with board:
    st.subheader('🏆 High Score Leaderboard')
    df=scores()
    if df.empty: st.info('No scores yet. Be the first player!')
    else:
        df.index=range(1,len(df)+1); st.dataframe(df.rename(columns={'player':'Player','score':'Score','quiz_percent':'Accuracy %','date':'Latest Attempt'}),use_container_width=True)

with resp:
    st.subheader('📝 Stored Responses')
    df=responses()
    if df.empty: st.info('No responses recorded yet.')
    else: st.dataframe(df.rename(columns={'player':'Player','level':'Level','question':'Question','answer':'Selected Answer','correct':'Correct?','score':'Points','created_at':'Time'}),use_container_width=True)
