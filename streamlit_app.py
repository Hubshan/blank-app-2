import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title='Normalization Challenge', page_icon='🎮', layout='wide')

DB_PATH = Path('normalization_game.db')


def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT, level TEXT, question TEXT,
            selected_answer TEXT, correct INTEGER, created_at TEXT
        )''')