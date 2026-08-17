import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Normalization Winners Game", page_icon="🏆", layout="wide")

# ---------------- Google Sheets ----------------
@st.cache_resource
def sheets_book():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            return None
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])
    except Exception:
        return None

HEADERS_S = ["Time","Player","Score","Correct","Total","Accuracy","Result"]
HEADERS_R = ["Time","Player","Level","Question Type","Question","Selected Answer","Result","Points"]

def ws(name, headers):
    book=sheets_book()
    if book is None: return None
    try: sh=book.worksheet(name)
    except Exception: sh=book.add_worksheet(title=name, rows=3000, cols=len(headers))
    try:
        if not sh.get_all_values(): sh.append_row(headers)
    except Exception: pass
    return sh

def save_result():
    total=len(st.session_state.attempts)
    correct=sum(x["Result"]=="Correct" for x in st.session_state.attempts)
    acc=round(correct/total*100) if total else 0
    result="Winner" if st.session_state.score >= 100 and acc >= 70 else "Participant"
    sh=ws("Scores",HEADERS_S)
    if sh:
        sh.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.player,st.session_state.score,correct,total,acc,result])
    return correct,acc,result

def save_response(a):
    sh=ws("Responses",HEADERS_R)
    if sh: sh.append_row(a)

def leaderboard():
    sh=ws("Scores",HEADERS_S)
    if not sh: return pd.DataFrame()
    try:
        rows=sh.get_all_records()
        if not rows: return pd.DataFrame()
        df=pd.DataFrame(rows)
        for c in ["Score","Correct","Total","Accuracy"]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0).astype(int)
        # Highest score first; accuracy is tie-breaker.
        return df.sort_values(["Score","Accuracy","Correct"],ascending=False).reset_index(drop=True)
    except Exception: return pd.DataFrame()

# ---------------- Normalization problem bank ----------------
PROBLEMS=[
("1NF","Atomicity","Student(SID,Name,Courses) stores Courses='DBMS, Python, Java'. What is the best fix?",["Keep the list","Create one row per course","Remove SID","Remove Name"],1,"1NF requires each cell to contain an atomic value."),
("1NF","Repeating Values","Order 101 stores Product_ID='P01,P02,P03' in one cell. What should be done?",["One row per product","Delete Product_ID","Make it a primary key","Duplicate Order_ID"],0,"Separate repeating values into atomic rows."),
("2NF","Partial Dependency","Enrollment(Student_ID,Course_ID,Student_Name,Course_Name,Grade) has key (Student_ID,Course_ID). Which dependency violates 2NF?",["Student_ID,Course_ID -> Grade","Student_ID -> Student_Name","Student_ID,Course_ID -> Course_Name","Course_ID -> Grade"],1,"Student_Name depends on only part of the composite key."),
("2NF","Decomposition","Which decomposition removes the partial dependency Student_ID -> Student_Name?",["Student(Student_ID,Student_Name) + Enrollment(Student_ID,Course_ID,Grade)","Student(Student_ID,Grade) + Course(Course_ID,Student_Name)","Keep original","Delete Student_Name"],0,"Move student details to Student."),
("3NF","Transitive Dependency","Student_ID -> Dept_ID and Dept_ID -> Dept_Name. What causes the 3NF violation?",["Student_ID -> Dept_ID","Dept_ID -> Dept_Name","Student_ID -> Student_ID","No dependency"],1,"Dept_Name depends transitively on Student_ID through Dept_ID."),
("3NF","Decomposition","Employee(Emp_ID,Emp_Name,Dept_ID,Dept_Name), with Dept_ID -> Dept_Name. Best design?",["Employee(Emp_ID,Emp_Name,Dept_ID) + Department(Dept_ID,Dept_Name)","Employee(Emp_ID,Dept_Name)","Delete Dept_ID","Duplicate Dept_Name"],0,"Separate department facts from employee facts."),
("BCNF","Determinant Test","R(Student,Course,Teacher) has Teacher -> Course, but Teacher is not a superkey. Is BCNF satisfied?",["Yes","No","Only if 3NF fails","Cannot determine"],1,"BCNF requires every determinant to be a superkey."),
("BCNF","Decomposition","R(A,B,C) has A -> B and B -> C. A is a key but B is not. Which decomposition fixes BCNF?",["Keep R","R1(B,C) + R2(A,B)","Delete B","Make C the key"],1,"B -> C violates BCNF because B is not a superkey."),
("Mixed","Normalization Sequence","A table has repeating values, a partial dependency and a transitive dependency. Correct sequence?",["3NF -> 2NF -> 1NF -> BCNF","1NF -> 2NF -> 3NF -> BCNF","BCNF -> 3NF -> 2NF -> 1NF","2NF -> BCNF -> 1NF -> 3NF"],1,"Normalization proceeds from 1NF through 2NF and 3NF to BCNF."),
("Mixed","Case Analysis","A relation is in 2NF and a non-key attribute depends on another non-key attribute. What should you investigate?",["Atomicity","Partial dependency","Transitive dependency","Repeating group"],2,"This is the classic transitive dependency addressed by 3NF."),
]

MCQS=[
("1NF mainly requires:",["Atomic values","No primary key","No foreign key","One row only"],0),
("2NF removes:",["Atomicity","Partial dependency","Transitive dependency","All foreign keys"],1),
("3NF removes:",["Repeating groups","Partial dependency","Transitive dependency","Primary keys"],2),
("BCNF requires every determinant to be:",["Foreign key","Superkey","Non-key","Tuple"],1),
("Can a relation be in 3NF but not BCNF?",["Yes","No","Only without a key","Only in 1NF"],0),
]

# ---------------- State ----------------
for k,v in {"started":False,"player":"","mode":"All Problems","i":0,"score":0,"attempts":[],"saved":False}.items():
    if k not in st.session_state: st.session_state[k]=v

def reset():
    for k,v in {"started":False,"player":"","mode":"All Problems","i":0,"score":0,"attempts":[],"saved":False}.items(): st.session_state[k]=v

# ---------------- UI ----------------
st.markdown("""<style>.hero{padding:22px;border-radius:18px;background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:white}.qbox{padding:18px;border-left:6px solid #7c3aed;border-radius:12px;background:#faf7ff}</style><div class='hero'><h1>🏆 Normalization Winners Game</h1><p>Find the winners, identify the learners who need practice, and master 1NF → 2NF → 3NF → BCNF.</p></div>""",unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Game Setup")
    if not st.session_state.started:
        name=st.text_input("Student / Player Name")
        mode=st.selectbox("Round",["All Problems","1NF","2NF","3NF","BCNF","Mixed"])
        if st.button("🚀 Start Game",type="primary",use_container_width=True):
            if name.strip():
                st.session_state.player=name.strip();st.session_state.mode=mode;st.session_state.started=True;st.session_state.i=0;st.session_state.score=0;st.session_state.attempts=[];st.session_state.saved=False;st.rerun()
            else: st.warning("Enter your name.")
    else:
        st.success(f"Playing: {st.session_state.player}")
        st.metric("Score",st.session_state.score)
        if st.button("🔄 Restart",use_container_width=True): reset();st.rerun()
    st.divider()
    st.success("☁️ Google Sheets connected") if sheets_book() else st.warning("☁️ Configure Google Sheets in Streamlit Secrets")

if not st.session_state.started:
    st.subheader("🏆 Winners Board")
    board=leaderboard()
    if board.empty: st.info("No results yet. Start the game and become the first winner!")
    else:
        board=board.head(10).copy();board.insert(0,"Rank",range(1,len(board)+1));board["Rank"]=board["Rank"].map(lambda n:"🥇" if n==1 else "🥈" if n==2 else "🥉" if n==3 else str(n))
        st.dataframe(board.rename(columns={"Player":"Student","Accuracy":"Accuracy %","Result":"Status"}),use_container_width=True,hide_index=True)
    st.info("The teacher can open the Google Sheet to see every score and every response.")
    st.stop()

problems=PROBLEMS if st.session_state.mode=="All Problems" else [p for p in PROBLEMS if p[0]==st.session_state.mode]
total=len(problems)+len(MCQS);i=st.session_state.i

if i<len(problems):
    level,typ,q,opts,ans,why=problems[i];st.progress(i/total);st.caption(f"Problem {i+1} of {len(problems)} • {level} • {typ}")
    st.markdown(f"<div class='qbox'><b>{typ}</b><br><br>{q}</div>",unsafe_allow_html=True)
    choice=st.radio("Select the best answer:",opts,index=None,key=f"p{i}")
    if st.button("✅ Submit Answer",type="primary",use_container_width=True):
        if choice is None: st.warning("Select an answer first.")
        else:
            correct=opts.index(choice)==ans;points=10 if correct else 0;now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.score+=points
            rec={"Time":now,"Player":st.session_state.player,"Level":level,"Type":typ,"Question":q,"Selected Answer":choice,"Result":"Correct" if correct else "Wrong","Points":points};st.session_state.attempts.append(rec)
            save_response([now,st.session_state.player,level,typ,q,choice,"Correct" if correct else "Wrong",points])
            st.success(f"Correct! +{points} points") if correct else st.error(f"Wrong. Correct answer: {opts[ans]}")
            st.info(why);st.session_state.i+=1;st.rerun()
elif i<total:
    j=i-len(problems);q,opts,ans=MCQS[j];st.progress(i/total);st.caption(f"Final MCQ {j+1} of {len(MCQS)}")
    st.markdown(f"<div class='qbox'><b>Final Challenge</b><br><br>{q}</div>",unsafe_allow_html=True);choice=st.radio("Choose one:",opts,index=None,key=f"m{j}")
    if st.button("✅ Submit MCQ",type="primary",use_container_width=True):
        if choice is None: st.warning("Select an answer first.")
        else:
            correct=opts.index(choice)==ans;points=5 if correct else 0;now=datetime.now().strftime("%Y-%m-%d %H:%M:%S");st.session_state.score+=points
            st.session_state.attempts.append({"Time":now,"Player":st.session_state.player,"Level":"MCQ","Type":"MCQ","Question":q,"Selected Answer":choice,"Result":"Correct" if correct else "Wrong","Points":points});save_response([now,st.session_state.player,"MCQ","MCQ",q,choice,"Correct" if correct else "Wrong",points]);st.success(f"Correct! +{points}") if correct else st.error(f"Wrong. Correct answer: {opts[ans]}");st.session_state.i+=1;st.rerun()
else:
    if not st.session_state.saved:
        correct,acc,result=save_result();st.session_state.saved=True
    df=pd.DataFrame(st.session_state.attempts);correct=int((df.Result=="Correct").sum());total_a=len(df);acc=round(correct/total_a*100) if total_a else 0
    st.balloons();st.success("🎉 Game Completed!")
    st.header(f"🏆 {st.session_state.player}'s Scorecard")
    a,b,c,d=st.columns(4);a.metric("Score",st.session_state.score);b.metric("Correct",correct);c.metric("Wrong",total_a-correct);d.metric("Accuracy",f"{acc}%")
    if st.session_state.score>=100 and acc>=70: st.success("🏆 WINNER — Excellent Normalization Master!")
    elif acc>=50: st.warning("🌟 PARTICIPANT — Good attempt. Practise the missed forms.")
    else: st.error("📚 NEEDS PRACTICE — Review dependencies and normalization rules.")
    st.subheader("🌐 LIVE WINNERS LEADERBOARD")
    board=leaderboard()
    if not board.empty:
        board.insert(0,"Rank",range(1,len(board)+1));board["Rank"]=board.Rank.map(lambda n:"🥇" if n==1 else "🥈" if n==2 else "🥉" if n==3 else str(n));st.dataframe(board.rename(columns={"Player":"Student","Accuracy":"Accuracy %","Result":"Status"}),use_container_width=True,hide_index=True)
        mine=board[board.Player==st.session_state.player]
        if not mine.empty: st.info(f"🎯 Your current rank: **#{mine.index[0]+1}**")
    st.subheader("📊 Your Answer Details");st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download My Scorecard",df.to_csv(index=False).encode(),f"{st.session_state.player}_normalization_scorecard.csv","text/csv",use_container_width=True)
    if st.button("🔄 Play Again",type="primary",use_container_width=True): reset();st.rerun()
