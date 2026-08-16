# 🎯 Normalization Problem Challenge

A problem-focused Streamlit game for undergraduate Database Management Systems.

## Features

- 1NF, 2NF, 3NF and BCNF problem-solving challenges
- Dependency and decomposition questions
- Mixed case-analysis problems
- 10 MCQs
- In-game scorecard
- Final score, correct/wrong count and accuracy
- Performance summary by normal form
- Complete answer history
- Downloadable CSV scorecard
- No Google Sheets or external database required

## Streamlit Community Cloud

Repository: `Hubshan/blank-app-2`

Main file: `streamlit_app.py`

Branch: `main`

Deploy through Streamlit Community Cloud by creating a new app from this GitHub repository.

Streamlit deployment documentation: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app

## Important

This version stores the scorecard in Streamlit session state. It is available while the student's session is active, but it is **not a shared cross-device leaderboard**.

A truly shared classroom leaderboard requires a persistent backend/database.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
