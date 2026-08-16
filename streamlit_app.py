import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Normalization Problem Challenge", page_icon="🎯", layout="wide")

# Google Sheets: credentials are read only from Streamlit Secrets.
def get_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if "gcp_service_account" not in st.secrets or "spreadsheet_id" not in st.secrets:
            return None
        info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        return gspread.authorize(Credentials.from_service_account_info(info, scopes=scopes))
    except Exception:
        return None

def ws(name):
    client = get_client()
    if client is None: return None
    try:
        book = client.open_by_key(st.secrets["spreadsheet_id"])
        try: return book.worksheet(name)
        except Exception: return book.add_worksheet(title=name, rows=1000, cols=12)
    except Exception: return None

def append_row(sheet, row):
    w = ws(sheet)
    if w is None: return False
    try:
        w.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception: return False

def read_sheet(sheet):
    w = ws(sheet)
    if w is None: return pd.DataFrame()
    try: return pd.DataFrame(w.get_all_records())
    except Exception: return pd.DataFrame()

for k,v in {"started":False,"player":"","score":0,"i":0,"responses":[],"finished":False,"mode":"All Problems"}.items():
    if k not in st.session_state: st.session_state[k]=v

P=[
("1NF","Find the Violation","A Student table stores Courses = 'DBMS, Python, Java' in one cell. What should you do?",["Keep the list.","Create separate rows so each course is atomic.","Duplicate Student_ID.","Remove Student_Name."],1,"1NF requires one atomic value per cell."),
("1NF","Problem Solving","Order 101 stores Product_ID = 'P01, P02, P03' in one cell. What is the first fix?",["Create one row per product.","Make Product_ID a foreign key.","Remove Product_ID.","Create another Order_ID."],0,"Repeating values must be represented as separate rows/records."),
("2NF","Dependency Detective","Enrollment(Student_ID, Course_ID, Student_Name, Course_Name, Grade) has key (Student_ID, Course_ID). Which dependency violates 2NF?",["Student_ID, Course_ID → Grade","Student_ID → Student_Name","Student_ID, Course_ID → Course_Name","Student_ID, Course_ID → Grade, Course_Name"],1,"Student_Name depends on only part of the composite key: partial dependency."),
("2NF","Choose the Decomposition","A table has key (Student_ID, Course_ID) and Student_Name. Which decomposition removes the partial dependency?",["Student(Student_ID, Student_Name) + Enrollment(Student_ID, Course_ID, Grade)","Student(Student_ID, Grade) + Course(Course_ID, Student_Name)","Enrollment(Student_Name, Course_Name, Grade)","Keep the table unchanged."],0,"Move attributes that depend only on Student_ID into Student."),
("3NF","Find the Transitive Dependency","Student_ID → Dept_ID and Dept_ID → Dept_Name. Which attribute is transitively dependent on Student_ID?",["Student_ID","Dept_ID","Dept_Name","None"],2,"Dept_Name depends on Dept_ID, which itself depends on Student_ID."),
("3NF","Choose the Design","Employee(Emp_ID, Emp_Name, Dept_ID, Dept_Name), with Dept_ID → Dept_Name. Which design is best?",["Employee(Emp_ID, Emp_Name, Dept_ID) + Department(Dept_ID, Dept_Name)","Employee(Emp_ID, Dept_Name) + Department(Emp_ID, Dept_ID)","Employee(Emp_Name, Dept_Name)","Duplicate Dept_Name."],0,"Department facts should depend on Department's key, not transitively through Employee."),
("BCNF","BCNF Judge","R(Student, Course, Teacher) has Teacher → Course, but Teacher is not a superkey. Does R satisfy BCNF?",["Yes, it is 3NF.","Yes, Teacher is a determinant.","No, Teacher is not a superkey.","No, because Room is numeric."],2,"BCNF requires every determinant of a non-trivial FD to be a superkey."),
("BCNF","Choose the Decomposition","R(A,B,C) has A → B and B → C. A is a key, but B is not. What is the BCNF decomposition?",["Keep R unchanged.","R1(B,C) and R2(A,B).","Delete B.","Make C the key."],1,"B → C violates BCNF because B is not a superkey; decompose using that dependency."),
("Mixed","Order the Fix","A table has repeating values, a partial dependency and a transitive dependency. What is the correct order?",["3NF → 1NF → 2NF → BCNF","1NF → 2NF → 3NF → BCNF","BCNF → 3NF → 2NF → 1NF","2NF → BCNF → 1NF → 3NF"],1,"Normalize progressively: atomicity, full-key dependency, no transitive dependency, then BCNF."),
("Mixed","Case Analysis","A relation is already in 2NF. A non-key attribute depends on another non-key attribute. What should you investigate?",["Atomicity","Partial dependency","Transitive dependency","Only foreign keys"],2,"A non-key → non-key dependency is a transitive dependency, addressed by 3NF."),
("Mixed","Exam Trap","Can a relation satisfy 3NF but violate BCNF?",["Yes, because BCNF is stricter.","No, they are identical.","Yes, only if there are no keys.","No, BCNF only applies to 1NF."],0,"BCNF is stricter than 3NF; some 3NF relations do not satisfy BCNF."),
("Mixed","Final Boss","You find repeating values, then a partial dependency, then a transitive dependency. What principle should guide the solution?",["Remove the highest normal form first.","Fix the current violation before moving to the next normal form.","Remove foreign keys first.","Denormalize immediately."],1,"Fix each violation in sequence rather than jumping directly to a higher form."),
]

if "quiz" not in st.session_state:
    st.session_state.quiz=[
    ("What is the main rule of 1NF?",["Atomic values","No primary key","No foreign key","Only one row"],0),
    ("Which normal form removes partial dependency?",["1NF","2NF","3NF","BCNF"],1),
    ("3NF mainly removes:",["Repeating groups","Partial dependency","Transitive dependency","Primary keys"],2),
    ("BCNF requires every determinant to be:",["Foreign key","Non-key attribute","Superkey","Numeric value"],2),
    ("A comma-separated list in one cell most directly violates:",["1NF","2NF","3NF","BCNF"],0),
    ("2NF requires a relation to already be in:",["1NF","3NF","BCNF","4NF"],0),
    ("Which is stricter?",["3NF","BCNF","2NF","1NF"],1),
    ("Student_ID → Dept_ID and Dept_ID → Dept_Name is:",["Partial dependency","Transitive dependency","Multivalued dependency","Candidate key"],1),
    ("A partial dependency occurs when a non-key attribute depends on:",["Whole composite key","Part of a composite key","Foreign key only","No key"],1),
    ("BCNF is based on the rule that every determinant is a:",["Tuple","Attribute","Superkey","Foreign key"],2),]

st.markdown("<style>.block-container{max-width:1200px}.hero{padding:1.3rem;border-radius:18px;background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:white}.problem{padding:1rem;border-left:6px solid #7c3aed;background:#faf7ff;border-radius:10px}</style>",unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>🎯 Normalization Problem Challenge</h1><p>Problem-first learning: find violations, analyze dependencies, choose decompositions and justify BCNF.</p></div>",unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Player")
    if not st.session_state.started:
        name=st.text_input("Student / Player Name")
        st.session_state.mode=st.selectbox("Problem Set",["All Problems","1NF","2NF","3NF","BCNF","Mixed"])
        if st.button("🚀 Start Game",use_container_width=True):
            if name.strip():
                st.session_state.player=name.strip();st.session_state.started=True;st.session_state.score=0;st.session_state.i=0;st.session_state.responses=[];st.session_state.finished=False;st.rerun()
            else: st.warning("Enter your name first.")
    else:
        st.success(f"Playing: {st.session_state.player}");st.metric("Score",st.session_state.score)
        if st.button("🔄 Restart",use_container_width=True): st.session_state.started=False;st.rerun()
    st.divider();st.subheader("☁️ Google Sheets")
    if get_client(): st.success("Connected")
    else: st.warning("Not configured")
    st.caption("Add Google credentials through Streamlit Secrets. Never put the service-account key in GitHub.")

home,game,leader,responses=st.tabs(["🏠 Home","🎯 Problems","🏆 Live Leaderboard","📝 Responses"])

with home:
    st.subheader("This game is problem-focused")
    a,b,c,d=st.columns(4)
    a.info("**1NF**\n\nFix repeating / non-atomic values")
    b.info("**2NF**\n\nFind partial dependencies")
    c.info("**3NF**\n\nRemove transitive dependencies")
    d.info("**BCNF**\n\nJudge determinants and decompose")
    st.write("Students solve **12 normalization problems** followed by **10 MCQs**. Every submitted answer can be written to Google Sheets.")

with game:
    if not st.session_state.started:
        st.warning("Start the game from the sidebar.")
    else:
        selected=[p for p in P if st.session_state.mode=="All Problems" or p[0]==st.session_state.mode]
        total=len(selected)+10
        i=st.session_state.i
        st.progress(min(i,total)/total)
        if i<len(selected):
            level,ptype,q,opts,ans,why=selected[i]
            st.caption(f"Problem {i+1} of {len(selected)} • {level} • {ptype}")
            st.markdown(f"<div class='problem'><b>{ptype}</b><br><br>{q}</div>",unsafe_allow_html=True)
            choice=st.radio("Choose the best solution:",opts,key=f"p_{st.session_state.mode}_{i}")
            if st.button("✅ Submit Problem",type="primary",use_container_width=True):
                idx=opts.index(choice);correct=idx==ans;points=10 if correct else 0
                if correct: st.session_state.score+=points;st.success(f"Correct! +{points} points.")
                else: st.error(f"Incorrect. Correct answer: {opts[ans]}")
                st.info(why)
                row=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.player,str(i+1),level,ptype,q,choice,"Correct" if correct else "Wrong",str(points)]
                st.session_state.responses.append(row);append_row("Responses",row)
                st.session_state.i+=1;st.rerun()
        elif i<total:
            qi=i-len(selected);q,opts,ans=st.session_state.quiz[qi]
            st.caption(f"MCQ {qi+1} of 10")
            st.markdown(f"<div class='problem'><b>MCQ</b><br><br>{q}</div>",unsafe_allow_html=True)
            choice=st.radio("Choose one:",opts,key=f"m_{st.session_state.mode}_{qi}")
            if st.button("✅ Submit MCQ",type="primary",use_container_width=True):
                idx=opts.index(choice);correct=idx==ans;points=5 if correct else 0
                if correct: st.session_state.score+=points;st.success(f"Correct! +{points} points.")
                else: st.error(f"Incorrect. Correct answer: {opts[ans]}")
                row=[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.player,str(qi+1),"MCQ","MCQ",q,choice,"Correct" if correct else "Wrong",str(points)]
                st.session_state.responses.append(row);append_row("Responses",row)
                st.session_state.i+=1
                if st.session_state.i>=total:
                    correct_count=sum(1 for r in st.session_state.responses if r[7]=="Correct")
                    pct=round(correct_count/len(st.session_state.responses)*100)
                    append_row("Scores",[datetime.now().strftime("%Y-%m-%d %H:%M:%S"),st.session_state.player,str(st.session_state.score),str(correct_count),str(len(st.session_state.responses)),str(pct)])
                    st.session_state.finished=True
                st.rerun()
        else:
            st.balloons();st.success("🎉 Game Complete!")
            correct_count=sum(1 for r in st.session_state.responses if r[7]=="Correct");pct=round(correct_count/len(st.session_state.responses)*100) if st.session_state.responses else 0
            x,y,z=st.columns(3);x.metric("Final Score",st.session_state.score);y.metric("Correct",f"{correct_count}/{len(st.session_state.responses)}");z.metric("Accuracy",f"{pct}%")
            st.info("Open Live Leaderboard to see the shared Google Sheets results.")
            if st.button("Play Again"): st.session_state.started=False;st.rerun()

with leader:
    st.subheader("🏆 Live High Score Leaderboard")
    df=read_sheet("Scores")
    if df.empty: st.info("No shared scores yet, or Google Sheets is not configured.")
    else:
        if "Score" in df.columns: df["Score_num"]=pd.to_numeric(df["Score"],errors="coerce");df=df.sort_values("Score_num",ascending=False).drop(columns=["Score_num"])
        st.dataframe(df.head(20),use_container_width=True,hide_index=True)

with responses:
    st.subheader("📝 Student Responses")
    df=read_sheet("Responses")
    if df.empty: st.info("No shared responses yet, or Google Sheets is not configured.")
    else: st.dataframe(df.tail(200).iloc[::-1],use_container_width=True,hide_index=True)
