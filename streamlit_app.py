import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Normalization Problem Challenge", page_icon="🎯", layout="wide")

# ---------- Problem Bank ----------
PROBLEMS = [
    {
        "level": "1NF", "type": "Find the Violation",
        "question": "A Student table contains Student_ID, Student_Name and Courses. For S01, Courses = 'DBMS, Python, Java'. What is the best normalization action?",
        "options": ["Keep the list because all courses belong to the same student.", "Create separate rows so each course is stored as an atomic value.", "Create a second Student_ID column.", "Remove Student_Name."],
        "answer": 1, "explanation": "1NF requires atomic values. The courses list should be separated into individual values/rows.", "points": 10,
    },
    {
        "level": "1NF", "type": "Problem Solving",
        "question": "Order_ID 101 stores Product_ID as 'P01, P02, P03' in one cell. What should you do first?",
        "options": ["Create one row for each Product_ID for the order.", "Make Product_ID a foreign key.", "Remove Product_ID.", "Add another Order_ID column."],
        "answer": 0, "explanation": "Repeating values inside one cell violate atomicity. Store one Product_ID per row.", "points": 10,
    },
    {
        "level": "2NF", "type": "Dependency Detective",
        "question": "Enrollment(Student_ID, Course_ID, Student_Name, Course_Name, Grade) has composite key (Student_ID, Course_ID). Which dependency violates 2NF?",
        "options": ["Student_ID, Course_ID → Grade", "Student_ID → Student_Name", "Student_ID, Course_ID → Course_Name", "Student_ID, Course_ID → Grade, Course_Name"],
        "answer": 1, "explanation": "Student_Name depends only on Student_ID, which is part of the composite key. This is partial dependency.", "points": 10,
    },
    {
        "level": "2NF", "type": "Choose the Decomposition",
        "question": "A relation uses (Student_ID, Course_ID) as its key and stores Student_Name and Grade. Which decomposition is best for 2NF?",
        "options": ["Student(Student_ID, Student_Name) and Enrollment(Student_ID, Course_ID, Grade)", "Student(Student_ID, Grade) and Course(Course_ID, Student_Name)", "Enrollment(Student_Name, Course_Name, Grade)", "Keep the original relation unchanged."],
        "answer": 0, "explanation": "Student_Name depends only on Student_ID, so move it to a Student relation.", "points": 10,
    },
    {
        "level": "3NF", "type": "Find the Transitive Dependency",
        "question": "Student(Student_ID, Student_Name, Dept_ID, Dept_Name) has Student_ID → Dept_ID and Dept_ID → Dept_Name. Which dependency causes the 3NF problem?",
        "options": ["Student_ID → Student_Name", "Student_ID → Dept_ID", "Dept_ID → Dept_Name", "Student_Name → Dept_Name"],
        "answer": 2, "explanation": "Dept_Name depends on Dept_ID, while Dept_ID depends on Student_ID. This creates a transitive dependency.", "points": 10,
    },
    {
        "level": "3NF", "type": "Choose the Decomposition",
        "question": "Employee(Emp_ID, Emp_Name, Dept_ID, Dept_Name) has Emp_ID as the key and Dept_ID → Dept_Name. Which design removes the transitive dependency?",
        "options": ["Employee(Emp_ID, Emp_Name, Dept_ID) and Department(Dept_ID, Dept_Name)", "Employee(Emp_ID, Dept_Name) and Department(Emp_ID, Dept_ID)", "Employee(Emp_Name, Dept_Name) only", "Duplicate Dept_Name into another column."],
        "answer": 0, "explanation": "Department facts belong in Department, where Dept_ID determines Dept_Name directly.", "points": 10,
    },
    {
        "level": "BCNF", "type": "BCNF Judge",
        "question": "R(Student, Course, Teacher) has Student, Course → Teacher and Teacher → Course. Teacher is not a superkey. Does R satisfy BCNF?",
        "options": ["Yes, because the relation is in 3NF.", "Yes, because Teacher is a determinant.", "No, because Teacher is not a superkey.", "No, because Course is not numeric."],
        "answer": 2, "explanation": "BCNF requires every determinant of a non-trivial functional dependency to be a superkey.", "points": 10,
    },
    {
        "level": "BCNF", "type": "Choose the Decomposition",
        "question": "R(A, B, C) has A → B and B → C. A is a key but B is not a superkey. What is the appropriate BCNF decomposition?",
        "options": ["Keep R unchanged.", "R1(B, C) and R2(A, B)", "Delete B.", "Make C the primary key."],
        "answer": 1, "explanation": "B → C violates BCNF because B is not a superkey. Decompose using that dependency.", "points": 10,
    },
    {
        "level": "Mixed", "type": "Order the Fix",
        "question": "A table has repeating values, a partial dependency and a transitive dependency. What is the correct sequence?",
        "options": ["3NF → 1NF → 2NF → BCNF", "1NF → 2NF → 3NF → BCNF", "BCNF → 3NF → 2NF → 1NF", "2NF → BCNF → 1NF → 3NF"],
        "answer": 1, "explanation": "Normalization is normally applied progressively from 1NF to 2NF, then 3NF and BCNF.", "points": 10,
    },
    {
        "level": "Mixed", "type": "Case Analysis",
        "question": "A relation is already in 2NF. A non-key attribute depends on another non-key attribute. What problem should you solve next?",
        "options": ["Atomicity", "Partial dependency", "Transitive dependency", "Missing primary key"],
        "answer": 2, "explanation": "A non-key attribute depending on another non-key attribute is a transitive dependency, the main 3NF problem.", "points": 10,
    },
    {
        "level": "Mixed", "type": "Exam Trap",
        "question": "Can a relation satisfy 3NF but still violate BCNF?",
        "options": ["Yes, because BCNF is stricter than 3NF.", "No, because 3NF and BCNF are identical.", "Yes, but only when there is no key.", "No, BCNF applies only to 1NF."],
        "answer": 0, "explanation": "BCNF is stricter than 3NF, so a relation can satisfy 3NF and still violate BCNF.", "points": 10,
    },
]

MCQS = [
    ("What is the main rule of 1NF?", ["Atomic values", "No primary key", "No foreign key", "Only one row"], 0),
    ("Which normal form removes partial dependency?", ["1NF", "2NF", "3NF", "BCNF"], 1),
    ("3NF mainly removes:", ["Repeating groups", "Partial dependency", "Transitive dependency", "Primary keys"], 2),
    ("BCNF requires every determinant to be:", ["Foreign key", "Non-key attribute", "Superkey", "Numeric value"], 2),
    ("A comma-separated list in one cell most directly violates:", ["1NF", "2NF", "3NF", "BCNF"], 0),
    ("2NF requires a relation to already be in:", ["1NF", "3NF", "BCNF", "4NF"], 0),
    ("Which is stricter?", ["3NF", "BCNF", "2NF", "1NF"], 1),
    ("Student_ID → Dept_ID and Dept_ID → Dept_Name is:", ["Partial dependency", "Transitive dependency", "Multivalued dependency", "Candidate key"], 1),
    ("A partial dependency occurs when a non-key attribute depends on:", ["Whole composite key", "Part of a composite key", "Foreign key only", "No key"], 1),
    ("BCNF is based on the rule that every determinant is a:", ["Tuple", "Attribute", "Superkey", "Foreign key"], 2),
]

# ---------- Session State ----------
for key, value in {
    "started": False,
    "player": "",
    "problem_index": 0,
    "score": 0,
    "attempts": [],
    "finished": False,
    "mode": "All Problems",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def selected_problems():
    if st.session_state.mode == "All Problems":
        return PROBLEMS
    return [p for p in PROBLEMS if p["level"] == st.session_state.mode]


def record_attempt(problem, selected, correct, points):
    st.session_state.attempts.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player": st.session_state.player,
        "Level": problem["level"],
        "Type": problem["type"],
        "Problem": problem["question"],
        "Selected Answer": selected,
        "Result": "Correct" if correct else "Wrong",
        "Points": points,
    })


def reset_game():
    st.session_state.started = False
    st.session_state.player = ""
    st.session_state.problem_index = 0
    st.session_state.score = 0
    st.session_state.attempts = []
    st.session_state.finished = False


st.markdown("""
<style>
.hero{padding:1.3rem 1.5rem;border-radius:18px;color:white;background:linear-gradient(135deg,#1d4ed8,#7c3aed);margin-bottom:1rem}
.problem-box{padding:1rem 1.2rem;border-left:6px solid #7c3aed;border-radius:10px;background:#faf7ff}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='hero'><h1>🎯 Normalization Problem Challenge</h1><p>Solve problems on 1NF, 2NF, 3NF and BCNF. Think about keys, dependencies and decomposition.</p></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Game Setup")
    if not st.session_state.started:
        name = st.text_input("Student / Player Name", max_chars=40)
        mode = st.selectbox("Problem Set", ["All Problems", "1NF", "2NF", "3NF", "BCNF", "Mixed"])
        if st.button("🚀 Start Game", type="primary", use_container_width=True):
            if not name.strip():
                st.warning("Please enter your name.")
            else:
                st.session_state.player = name.strip()
                st.session_state.mode = mode
                st.session_state.started = True
                st.session_state.problem_index = 0
                st.session_state.score = 0
                st.session_state.attempts = []
                st.session_state.finished = False
                st.rerun()
    else:
        st.success(f"Playing: {st.session_state.player}")
        st.metric("Current Score", st.session_state.score)
        if st.button("🔄 Restart", use_container_width=True):
            reset_game()
            st.rerun()
    st.divider()
    st.caption("No Google Sheets or external database is required.")

if not st.session_state.started:
    a, b, c, d = st.columns(4)
    a.info("**1NF**\n\nAtomic values")
    b.info("**2NF**\n\nNo partial dependency")
    c.info("**3NF**\n\nNo transitive dependency")
    d.info("**BCNF**\n\nEvery determinant is a superkey")
    st.subheader("🎯 Problem-first learning")
    st.write("Students find violations, identify dependencies, choose decompositions and solve mixed cases.")
    st.info("Enter a student name and click Start Game in the sidebar.")
    st.stop()

problems = selected_problems()
# First all selected problems, then 10 MCQs.
total = len(problems) + len(MCQS)
idx = st.session_state.problem_index

if idx < len(problems):
    problem = problems[idx]
    st.progress(idx / total)
    st.caption(f"Problem {idx+1} of {len(problems)} • {problem['level']} • {problem['type']}")
    st.markdown(f"<div class='problem-box'><b>{problem['type']}</b><br><br>{problem['question']}</div>", unsafe_allow_html=True)
    choice = st.radio("Choose the best solution:", problem["options"], index=None, key=f"p_{idx}")
    if st.button("✅ Submit Problem", type="primary", use_container_width=True):
        if choice is None:
            st.warning("Select an answer first.")
        else:
            correct = problem["options"].index(choice) == problem["answer"]
            points = problem["points"] if correct else 0
            if correct:
                st.session_state.score += points
                st.success(f"✅ Correct! +{points} points.")
            else:
                st.error(f"❌ Incorrect. Correct answer: {problem['options'][problem['answer']]}")
            st.info(problem["explanation"])
            record_attempt(problem, choice, correct, points)
            st.session_state.problem_index += 1
            st.rerun()
elif idx < total:
    qi = idx - len(problems)
    question, options, answer = MCQS[qi]
    st.progress(idx / total)
    st.caption(f"MCQ {qi+1} of {len(MCQS)}")
    st.markdown(f"<div class='problem-box'><b>MCQ</b><br><br>{question}</div>", unsafe_allow_html=True)
    choice = st.radio("Choose one:", options, index=None, key=f"m_{qi}")
    if st.button("✅ Submit MCQ", type="primary", use_container_width=True):
        if choice is None:
            st.warning("Select an answer first.")
        else:
            correct = options.index(choice) == answer
            points = 5 if correct else 0
            if correct:
                st.session_state.score += points
                st.success(f"✅ Correct! +{points} points.")
            else:
                st.error(f"❌ Incorrect. Correct answer: {options[answer]}")
            record_attempt({"level":"MCQ","type":"MCQ","question":question}, choice, correct, points)
            st.session_state.problem_index += 1
            st.rerun()
else:
    st.session_state.finished = True

if st.session_state.finished:
    df = pd.DataFrame(st.session_state.attempts)
    total_answers = len(df)
    correct = int((df["Result"] == "Correct").sum()) if total_answers else 0
    wrong = total_answers - correct
    accuracy = round(correct / total_answers * 100) if total_answers else 0

    st.balloons()
    st.success("🎉 Game Complete!")
    st.header(f"🏆 Scorecard — {st.session_state.player}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Final Score", st.session_state.score)
    m2.metric("Correct", correct)
    m3.metric("Wrong", wrong)
    m4.metric("Accuracy", f"{accuracy}%")

    if accuracy >= 90:
        st.subheader("🏆 Normalization Master")
    elif accuracy >= 75:
        st.subheader("🌟 Excellent Problem Solver")
    elif accuracy >= 60:
        st.subheader("👍 Good Progress")
    else:
        st.subheader("💪 Keep Practising")

    st.subheader("📊 Performance by Normal Form")
    summary = (
        df.groupby("Level")
        .agg(Problems=("Level", "size"), Correct=("Result", lambda s: (s == "Correct").sum()), Points=("Points", "sum"))
        .reset_index()
    )
    summary["Accuracy"] = (summary["Correct"] / summary["Problems"] * 100).round(0).astype(int)
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.subheader("📝 Answer History")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download My Scorecard (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{st.session_state.player}_normalization_scorecard.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()
    st.info("This scorecard is stored in the current Streamlit session. It is not a shared cross-device leaderboard.")
    if st.button("🎮 Play Again", type="primary", use_container_width=True):
        reset_game()
        st.rerun()

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("👤 Player", st.session_state.player)
c2.metric("🏆 Score", st.session_state.score)
c3.metric("🧩 Solved", min(st.session_state.problem_index, total))
