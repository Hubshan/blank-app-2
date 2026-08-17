import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Normalization Kahoot", page_icon="🎯", layout="wide")

# Google Sheets connection
@st.cache_resource
def get_book():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            return None
        info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])
    except Exception:
        return None

def worksheet(title, headers):
    book = get_book()
    if book is None: return None
    try: ws = book.worksheet(title)
    except Exception: ws = book.add_worksheet(title=title, rows=2000, cols=len(headers))
    try:
        if not ws.get_all_values(): ws.append_row(headers)
    except Exception: pass
    return ws

def save_score(player, score, correct, total, accuracy):
    ws = worksheet("Scores", ["Time","Player","Score","Correct","Total","Accuracy"])
    if ws is None: return False
    try:
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),player,score,correct,total,accuracy])
        return True
    except Exception: return False

def save_response(row):
    ws = worksheet("Responses", ["Time","Player","Level","Type","Question","Selected Answer","Result","Points"])
    if ws is None: return False
    try: ws.append_row(row); return True
    except Exception: return False

def get_scores():
    ws = worksheet("Scores", ["Time","Player","Score","Correct","Total","Accuracy"])
    if ws is None: return pd.DataFrame()
    try:
        data = ws.get_all_records()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(data)
        for c in ["Score","Correct","Total","Accuracy"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        return df.sort_values(["Score","Accuracy"], ascending=[False,False]).reset_index(drop=True)
    except Exception: return pd.DataFrame()

PROBLEMS = [
("1NF","Find the Violation","Student(SID, Name, Courses) has S01, Anu, 'DBMS, Python, Java'. What should be changed?",["Keep the list","Create one row per course","Remove SID","Remove Name"],1,"1NF requires atomic values."),
("1NF","Problem Solving","Order 101 stores Product_ID as 'P01, P02, P03' in one cell. What is the best first action?",["Create one row per product","Delete Product_ID","Make Product_ID a foreign key","Duplicate Order_ID"],0,"Repeating values must be separated into atomic values."),
("2NF","Dependency Detective","Enrollment(Student_ID, Course_ID, Student_Name, Course_Name, Grade) has key (Student_ID, Course_ID). Which dependency violates 2NF?",["Student_ID, Course_ID → Grade","Student_ID → Student_Name","Student_ID, Course_ID → Course_Name","Course_ID → Grade"],1,"Student_Name depends on only part of the composite key."),
("2NF","Choose the Decomposition","Which design removes Student_Name's partial dependency?",["Student(Student_ID, Student_Name) + Enrollment(Student_ID, Course_ID, Grade)","Student(Student_ID, Grade) + Course(Course_ID, Student_Name)","Keep the original table","Delete Student_Name"],0,"Move attributes dependent only on Student_ID into Student."),
("3NF","Find the Transitive Dependency","Student_ID → Dept_ID and Dept_ID → Dept_Name. Which dependency creates the 3NF issue?",["Student_ID → Dept_ID","Student_ID → Dept_Name","Dept_ID → Dept_Name","Student_ID → Student_ID"],2,"Dept_Name depends on non-key Dept_ID, creating a transitive dependency."),
("3NF","Choose the Decomposition","Employee(Emp_ID, Emp_Name, Dept_ID, Dept_Name). Dept_ID → Dept_Name. Which design is correct?",["Employee(Emp_ID, Emp_Name, Dept_ID) + Department(Dept_ID, Dept_Name)","Employee(Emp_ID, Dept_Name) only","Delete Dept_ID","Duplicate Dept_Name"],0,"Department details should be stored with Dept_ID as their determinant."),
("BCNF","BCNF Judge","R(Student, Course, Teacher) has Teacher → Course, but Teacher is not a superkey. What is the result?",["BCNF satisfied","BCNF violated","1NF violated","No functional dependency exists"],1,"BCNF requires every determinant of a non-trivial FD to be a superkey."),
("BCNF","Choose the Decomposition","R(A,B,C) has A → B and B → C. A is a key; B is not. What decomposition fixes the BCNF violation?",["Keep R","R1(B,C) and R2(A,B)","Delete B","Make C the key"],1,"B → C violates BCNF because B is not a superkey."),
("Mixed","Order the Fix","A table has repeating values, a partial dependency and a transitive dependency. What is the correct sequence?",["3NF → 1NF → 2NF → BCNF","1NF → 2NF → 3NF → BCNF","BCNF → 3NF → 2NF → 1NF","2NF → BCNF → 1NF → 3NF"],1,"Normalization progresses from 1NF to 2NF to 3NF and then BCNF."),
("Mixed","Case Analysis","A relation is already in 2NF and a non-key attribute depends on another non-key attribute. What should you investigate?",["Atomicity","Partial dependency","Transitive dependency","Repeating group"],2,"A non-key to non-key dependency is the classic 3NF/transitive-dependency problem."),
]
MCQS=[
("What does 1NF require?",["Atomic values","No keys","Only foreign keys","No rows"],0),
("Which normal form removes partial dependency?",["1NF","2NF","3NF","BCNF"],1),
("Which normal form removes transitive dependency?",["1NF","2NF","3NF","BCNF"],2),
("BCNF requires every determinant to be a:",["Foreign key","Superkey","Non-key","Tuple"],1),
("A comma-separated list in one cell violates:",["1NF","2NF","3NF","BCNF"],0),
]

for k,v in {"started":False,"player":"","index":0,"score":0,"attempts":[],"finished":False,"mode":"All Problems","saved":False}.items():
    if k not in st.session_state: st.session_state[k]=v

def reset():
    for k,v in {"started":False,"player":"","index":0,"score":0,"attempts":[],"finished":False,"mode":"All Problems","saved":False}.items(): st.session_state[k]=v

st.markdown("""<style>.hero{padding:22px;border-radius:18px;background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:white;margin-bottom:18px}.box{padding:18px;border-left:6px solid #7c3aed;border-radius:12px;background:#faf7ff}</style><div class='hero'><h1>🎯 Normalization Kahoot</h1><p>Problem-first game: 1NF → 2NF → 3NF → BCNF</p></div>""",unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Game")
    if not st.session_state.started:
        name=st.text_input("Student / Player Name")
        mode=st.selectbox("Problem Set",["All Problems","1NF","2NF","3NF","BCNF","Mixed"])
        if st.button("🚀 Start Game",type="primary",use_container_width=True):
            if name.strip():
                st.session_state.player=name.strip();st.session_state.mode=mode;st.session_state.started=True;st.session_state.index=0;st.session_state.score=0;st.session_state.attempts=[];st.session_state.saved=False;st.rerun()
            else: st.warning("Enter your name first.")
    else:
        st.success(st.session_state.player);st.metric("Score",st.session_state.score)
        if st.button("🔄 Restart",use_container_width=True): reset();st.rerun()
    st.divider()
    if get_book() is not None: st.success("☁️ Google Sheets connected")
    else: st.warning("Google Sheets not connected")

if not st.session_state.started:
    st.subheader("🏆 Live Online Leaderboard")
    board=get_scores()
    if not board.empty:
        board=board.head(10).copy();board.insert(0,"Rank",range(1,len(board)+1))
        board["Rank"]=board["Rank"].map(lambda x:"🥇" if x==1 else "🥈" if x==2 else "🥉" if x==3 else str(x))
        st.dataframe(board.rename(columns={"Player":"Student","Accuracy":"Accuracy %"}),use_container_width=True,hide_index=True)
    else: st.info("No scores yet. Be the first Normalization Master!")
    st.info("Enter your name in the sidebar to start.");st.stop()

problems=PROBLEMS if st.session_state.mode=="All Problems" else [p for p in PROBLEMS if p[0]==st.session_state.mode]
total=len(problems)+len(MCQS);i=st.session_state.index

if i<len(problems):
    level,ptype,question,options,answer,explanation=problems[i]
    st.progress(i/total);st.caption(f"Problem {i+1} of {len(problems)} • {level} • {ptype}")
    st.markdown(f"<div class='box'><b>{ptype}</b><br><br>{question}</div>",unsafe_allow_html=True)
    choice=st.radio("Choose the best solution:",options,index=None,key=f"p{i}")
    if st.button("✅ Submit",type="primary",use_container_width=True):
        if choice is None: st.warning("Select an answer.")
        else:
            correct=options.index(choice)==answer;points=10 if correct else 0;now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.score+=points;st.session_state.attempts.append({"Time":now,"Player":st.session_state.player,"Level":level,"Type":ptype,"Question":question,"Selected Answer":choice,"Result":"Correct" if correct else "Wrong","Points":points})
            save_response([now,st.session_state.player,level,ptype,question,choice,"Correct" if correct else "Wrong",points])
            st.success(f"✅ Correct! +{points}") if correct else st.error(f"❌ Incorrect. Correct answer: {options[answer]}")
            st.info(explanation);st.session_state.index+=1;st.rerun()

elif i<total:
    qidx=i-len(problems);question,options,answer=MCQS[qidx]
    st.progress(i/total);st.caption(f"Final MCQ {qidx+1} of {len(MCQS)}")
    st.markdown(f"<div class='box'><b>MCQ Challenge</b><br><br>{question}</div>",unsafe_allow_html=True)
    choice=st.radio("Choose one:",options,index=None,key=f"m{qidx}")
    if st.button("✅ Submit MCQ",type="primary",use_container_width=True):
        if choice is None: st.warning("Select an answer.")
        else:
            correct=options.index(choice)==answer;points=5 if correct else 0;now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.score+=points;st.session_state.attempts.append({"Time":now,"Player":st.session_state.player,"Level":"MCQ","Type":"MCQ","Question":question,"Selected Answer":choice,"Result":"Correct" if correct else "Wrong","Points":points})
            save_response([now,st.session_state.player,"MCQ","MCQ",question,choice,"Correct" if correct else "Wrong",points])
            st.success(f"✅ Correct! +{points}") if correct else st.error(f"❌ Incorrect. Correct answer: {options[answer]}")
            st.session_state.index+=1;st.rerun()

else:
    df=pd.DataFrame(st.session_state.attempts);total_answers=len(df);correct=int((df["Result"]=="Correct").sum()) if total_answers else 0;accuracy=round(correct/total_answers*100) if total_answers else 0
    if not st.session_state.saved: save_score(st.session_state.player,st.session_state.score,correct,total_answers,accuracy);st.session_state.saved=True
    st.balloons();st.success("🎉 Challenge Completed!");st.header(f"🏆 Scorecard — {st.session_state.player}")
    a,b,c,d=st.columns(4);a.metric("Final Score",st.session_state.score);b.metric("Correct",correct);c.metric("Wrong",total_answers-correct);d.metric("Accuracy",f"{accuracy}%")
    st.subheader("🌐 LIVE SHARED LEADERBOARD")
    board=get_scores()
    if not board.empty:
        board.insert(0,"Rank",range(1,len(board)+1));board["Rank"]=board["Rank"].map(lambda x:"🥇" if x==1 else "🥈" if x==2 else "🥉" if x==3 else str(x))
        st.dataframe(board.rename(columns={"Player":"Student","Accuracy":"Accuracy %"}),use_container_width=True,hide_index=True)
        positions=board.index[board["Player"]==st.session_state.player].tolist()
        if positions: st.info(f"🎯 Your current leaderboard position is **#{positions[0]+1}**.")
    else: st.warning("Leaderboard unavailable. Configure Streamlit Secrets and share the Sheet with the service account.")
    st.subheader("📊 My Performance")
    summary=df.groupby("Level").agg(Problems=("Level","size"),Correct=("Result",lambda s:(s=="Correct").sum()),Points=("Points","sum")).reset_index();summary["Accuracy"]=(summary["Correct"]/summary["Problems"]*100).round(0).astype(int);st.dataframe(summary,use_container_width=True,hide_index=True)
    st.subheader("📝 My Answer History");st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download My Scorecard",df.to_csv(index=False).encode(),f"{st.session_state.player}_normalization_scorecard.csv","text/csv",use_container_width=True)
    if st.button("🔄 Play Again",type="primary",use_container_width=True): reset();st.rerun()

st.divider();x,y,z=st.columns(3);x.metric("👤 Player",st.session_state.player);y.metric("🏆 Score",st.session_state.score);z.metric("🧩 Progress",f"{min(st.session_state.index,total)}/{total}")
