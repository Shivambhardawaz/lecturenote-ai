"""
LectureNote AI — app.py
========================
A Streamlit application that converts lecture recordings into organized study material.

Workflow: Upload Lecture → Speech-to-Text → Generate Study Material → Review → Practice

Author: LectureNote AI
"""

import os
import json
import re
import time
import base64
import textwrap
import tempfile
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

SUPPORTED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4",
                          "audio/x-m4a", "audio/aac", "video/mp4"]
SUPPORTED_EXTENSIONS  = [".mp3", ".wav", ".m4a", ".mp4"]

MAX_FILE_SIZE_MB = 200

# ─────────────────────────────────────────────
# ACADEMIC DESIGN SYSTEM — CSS
# ─────────────────────────────────────────────

ACADEMIC_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap');

/* ── Design Tokens ── */
:root {
    --bg:              #F8F9FA;
    --surface:         #FFFFFF;
    --primary:         #1A2B3C;
    --accent:          #4A90E2;
    --accent-dark:     #0060AC;
    --text-body:       #191C1D;
    --text-muted:      #44474C;
    --border:          #E1E4E8;
    --border-focus:    #4A90E2;
    --success:         #2E7D32;
    --warning:         #E65100;
    --error-col:       #B71C1C;
    --tag-bg:          #EEF2F7;
    --radius:          8px;
    --radius-sm:       4px;
    --shadow:          0 2px 4px rgba(26,43,60,0.06);
    --shadow-hover:    0 4px 12px rgba(26,43,60,0.12);
    --font-head:       'Inter', system-ui, sans-serif;
    --font-body:       'Source Sans 3', Georgia, serif;
}

/* ── Global Reset & Strict Background Enforcement ── */
.stApp,
.main,
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"],
section.main {
    background-color: #F8F9FA !important;
}

html, body {
    font-family: var(--font-body);
    background-color: #F8F9FA !important;
    color: #191C1D !important;
}

/* ── Strip ALL Streamlit top padding / toolbar ── */
[data-testid="stHeader"]           { display: none !important; height: 0 !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
.stDeployButton                    { display: none !important; }
div[class*="viewerBadge"]          { display: none !important; }

/* Kill every layer of top padding Streamlit adds */
[data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stAppViewContainer"] > section.main { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
section.main                       { padding-top: 0 !important; margin-top: 0 !important; }
.main                              { padding-top: 0 !important; margin-top: 0 !important; }

/* ── Streamlit Main Layout ── */
.main .block-container,
[data-testid="stMainBlockContainer"] {
    padding-top:    0 !important;
    padding-left:   2.5rem;
    padding-right:  2.5rem;
    padding-bottom: 4rem;
    max-width: 1100px;
}

/* ── Header / Nav Bar ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 0 1.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
.app-logo {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}
.app-logo-title {
    font-family: var(--font-head);
    font-size: 1.35rem;
    font-weight: 700;
    color: #1A2B3C !important;
    letter-spacing: -0.02em;
}
.app-logo-dot {
    color: var(--accent);
}
.app-logo-subtitle {
    font-family: var(--font-body);
    font-size: 0.85rem;
    color: #44474C !important;
}

/* ── Hero Section ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-family: var(--font-head);
    font-size: 2.5rem;
    font-weight: 700;
    color: #1A2B3C !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.75rem;
}
.hero p {
    font-family: var(--font-body);
    font-size: 1.125rem;
    color: #44474C !important;
    max-width: 560px;
    margin: 0 auto 0.5rem;
    line-height: 1.6;
}

/* ── Section Labels / Badges ── */
.section-badge {
    display: inline-block;
    background: var(--tag-bg);
    color: var(--accent-dark);
    font-family: var(--font-head);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-sm);
    margin-bottom: 1rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow);
}
.card:hover {
    box-shadow: var(--shadow-hover);
}
.card-title {
    font-family: var(--font-head);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 0.5rem;
}
.card-text {
    font-family: var(--font-body);
    font-size: 0.975rem;
    color: var(--text-body);
    line-height: 1.6;
}

/* ── Upload Box ── */
.upload-container {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: var(--radius);
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.upload-container:hover {
    border-color: var(--accent);
}
.upload-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}
.upload-title {
    font-family: var(--font-head);
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 0.25rem;
}
.upload-subtitle {
    font-family: var(--font-body);
    font-size: 0.9rem;
    color: var(--text-muted);
}
.format-tags {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    flex-wrap: wrap;
}
.format-tag {
    background: var(--tag-bg);
    color: var(--accent-dark);
    font-family: var(--font-head);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: var(--radius-sm);
    letter-spacing: 0.04em;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* ── Key Points numbered list ── */
.key-point-item {
    display: flex;
    gap: 1.25rem;
    align-items: flex-start;
    padding: 1rem 1.5rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 0.75rem;
}
.key-point-num {
    font-family: var(--font-head);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
    min-width: 2.5rem;
    line-height: 1;
}
.key-point-text {
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--text-body);
    line-height: 1.55;
    padding-top: 0.1rem;
}

/* ── Definition cards ── */
.def-card {
    background: var(--surface);
    border-left: 3px solid var(--accent);
    border-radius: 0 var(--radius) var(--radius) 0;
    border-top: 1px solid var(--border);
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 1.1rem 1.5rem;
    margin-bottom: 0.75rem;
}
.def-term {
    font-family: var(--font-head);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.3rem;
}
.def-meaning {
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text-body);
    line-height: 1.55;
}

/* ── Flashcard ── */
.flashcard-outer {
    perspective: 1200px;
    margin: 0 auto 1.5rem;
    max-width: 700px;
}
.flashcard {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2.5rem 2.5rem;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow);
}
.flashcard-side-label {
    font-family: var(--font-head);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding: 0.2rem 0.7rem;
    border-radius: var(--radius-sm);
}
.flashcard-front-label {
    background: var(--tag-bg);
    color: var(--accent-dark);
}
.flashcard-back-label {
    background: #EEF7EE;
    color: var(--success);
}
.flashcard-content {
    font-family: var(--font-body);
    font-size: 1.15rem;
    color: var(--text-body);
    line-height: 1.6;
}
.flashcard-counter {
    font-family: var(--font-head);
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* ── Quiz ── */
.quiz-question {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
}
.quiz-question-num {
    font-family: var(--font-head);
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.quiz-question-text {
    font-family: var(--font-head);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 1rem;
    line-height: 1.4;
}
.quiz-score-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    text-align: center;
}
.quiz-score-big {
    font-family: var(--font-head);
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
}
.quiz-score-label {
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* ── Progress / Status ── */
.processing-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0;
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text-body);
}
.step-done  { color: var(--success); }
.step-active { color: var(--accent-dark); font-weight: 600; }
.step-pending { color: var(--text-muted); }

/* ── Transcript ── */
.transcript-body {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.25rem;
    font-family: var(--font-body);
    font-size: 1rem;
    line-height: 1.75;
    color: var(--text-body);
    max-height: 520px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* ── Metadata row ── */
.meta-row {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.75rem;
    flex-wrap: wrap;
}
.meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}
.meta-label {
    font-family: var(--font-head);
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.meta-value {
    font-family: var(--font-body);
    font-size: 0.95rem;
    color: var(--text-body);
    font-weight: 600;
}

/* ── Streamlit widget overrides ── */
/* Buttons */
.stButton > button {
    font-family: var(--font-head) !important;
    font-weight: 600 !important;
    border-radius: var(--radius) !important;
    letter-spacing: 0.02em !important;
}
/* Text inputs / text area */
.stTextInput input, .stTextArea textarea {
    font-family: var(--font-body) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 2px rgba(74,144,226,0.2) !important;
}
/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-head) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.25rem !important;
    color: var(--text-muted) !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--accent) !important;
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--primary) !important;
}
section[data-testid="stSidebar"] * {
    color: #B7C8DE !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

/* ── Alerts / info ── */
.stAlert {
    border-radius: var(--radius) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: var(--font-head) !important;
    font-weight: 600 !important;
    color: var(--primary) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Theme toggle button in header ── */
.theme-toggle-btn {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-family: var(--font-head);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.3rem 0.75rem;
    transition: border-color 0.15s, color 0.15s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}
.theme-toggle-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
}
</style>
"""

# ─────────────────────────────────────────────
# DARK MODE — CSS OVERRIDES
# ─────────────────────────────────────────────

DARK_CSS = """
<style>
/* ── Dark Mode — Deep Navy Academic Palette ── */
:root {
    --bg:              #0D1B2A;
    --surface:         #162333;
    --primary:         #E2EAF4;
    --accent:          #5B9FE8;
    --accent-dark:     #7DB6F0;
    --text-body:       #CDD7E6;
    --text-muted:      #8FA3BB;
    --border:          #253547;
    --border-focus:    #5B9FE8;
    --success:         #4CAF74;
    --warning:         #F0A030;
    --error-col:       #E06060;
    --tag-bg:          #1A2D42;
    --shadow:          0 2px 6px rgba(0,0,0,0.35);
    --shadow-hover:    0 4px 16px rgba(0,0,0,0.5);
}

html, body {
    background-color: #0D1B2A !important;
    color: #CDD7E6 !important;
}

/* ── Streamlit main bg in dark mode ── */
.stApp,
.main,
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"],
section.main {
    background-color: #0D1B2A !important;
}

/* ── Hero text dark overrides ── */
.hero h1 {
    color: #E2EAF4 !important;
}
.hero p {
    color: #8FA3BB !important;
}

/* ── Upload container dark overrides ── */
.upload-container {
    background: #162333 !important;
    border: 2px dashed #253547 !important;
}
.upload-container:hover {
    border-color: #5B9FE8 !important;
}
.upload-title {
    color: #E2EAF4 !important;
}
.upload-subtitle {
    color: #8FA3BB !important;
}

/* ── All Streamlit widget containers ── */
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
.element-container {
    background-color: transparent !important;
}

/* ── Text: only target actual text containers ── */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
.stText, [data-testid="stText"] {
    color: #CDD7E6 !important;
}
label, .stRadio label, .stCheckbox label {
    color: #CDD7E6 !important;
}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #162333 !important;
    color: #E2EAF4 !important;
    border-color: #253547 !important;
}
[data-baseweb="input"],
[data-baseweb="textarea"] {
    background-color: #162333 !important;
    border-color: #253547 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div,
.stFileUploader {
    background-color: #162333 !important;
    border-color: #253547 !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small {
    color: #8FA3BB !important;
}
/* The inner upload button */
[data-testid="stFileUploaderDropzone"] button {
    background-color: #1A2D42 !important;
    color: #7DB6F0 !important;
    border-color: #253547 !important;
}

/* ── Select boxes ── */
[data-baseweb="select"] > div,
[data-baseweb="popover"] > div {
    background-color: #162333 !important;
    color: #E2EAF4 !important;
    border-color: #253547 !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #162333 !important;
    color: #E2EAF4 !important;
    border-color: #253547 !important;
}
.stButton > button[kind="primary"],
[data-testid="baseButton-primary"] {
    background-color: #7DB6F0 !important;
    color: #0D1B2A !important;
    border: none !important;
}
.stButton > button:hover {
    border-color: #5B9FE8 !important;
    color: #5B9FE8 !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background-color: #162333 !important;
    color: #E2EAF4 !important;
    border-color: #253547 !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {
    color: #E2EAF4 !important;
    font-size: 0.95rem !important;
}
[data-testid="stRadio"] > div {
    gap: 0.4rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0D1B2A !important;
    border-bottom-color: #253547 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8FA3BB !important;
}
.stTabs [aria-selected="true"] {
    color: #E2EAF4 !important;
    border-bottom-color: #5B9FE8 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: #0D1B2A !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background-color: #5B9FE8 !important;
}
[data-testid="stProgressBar"] > div {
    background-color: #253547 !important;
}

/* ── Alerts / status boxes ── */
[data-testid="stAlert"] {
    background-color: #162333 !important;
    border-color: #253547 !important;
    color: #CDD7E6 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #162333 !important;
    color: #E2EAF4 !important;
    border-color: #253547 !important;
}
.streamlit-expanderContent {
    background-color: #162333 !important;
    border-color: #253547 !important;
}

/* ── Status widget ── */
[data-testid="stStatus"] {
    background-color: #162333 !important;
    border-color: #253547 !important;
    color: #CDD7E6 !important;
}
[data-testid="stStatus"] p, [data-testid="stStatus"] span {
    color: #CDD7E6 !important;
}

/* ── st.code blocks ── */
.stCode, [data-testid="stCodeBlock"] {
    background-color: #0A1420 !important;
    border-color: #253547 !important;
}
.stCode code, [data-testid="stCodeBlock"] code {
    color: #A8C8F0 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0A1520 !important;
}

/* ── Custom HTML component dark overrides ── */
.card {
    background: #162333 !important;
    border: 1px solid #253547 !important;
}
.card-title {
    color: #E2EAF4 !important;
}
.card-text {
    color: #CDD7E6 !important;
}
.def-card {
    background: #162333 !important;
    border-left: 3px solid #5B9FE8 !important;
    border-top: 1px solid #253547 !important;
    border-right: 1px solid #253547 !important;
    border-bottom: 1px solid #253547 !important;
}
.def-term {
    color: #E2EAF4 !important;
}
.def-meaning {
    color: #CDD7E6 !important;
}
.key-point-item {
    background: #162333 !important;
    border: 1px solid #253547 !important;
}
.key-point-num {
    color: #5B9FE8 !important;
}
.key-point-text {
    color: #CDD7E6 !important;
}
.flashcard {
    background: #162333 !important;
    border: 1px solid #253547 !important;
}
.flashcard-content {
    color: #E2EAF4 !important;
}
.quiz-question {
    background: #162333 !important;
    border: 1px solid #253547 !important;
}
.quiz-question-text {
    color: #E2EAF4 !important;
}
.quiz-score-box {
    background: #162333 !important;
    border: 1px solid #253547 !important;
}
.quiz-score-big {
    color: #E2EAF4 !important;
}
.transcript-body {
    background: #162333 !important;
    border: 1px solid #253547 !important;
    color: #CDD7E6 !important;
}
.format-tag {
    background: #1A2D42 !important;
    color: #7DB6F0 !important;
}
.section-badge {
    background: #1A2D42 !important;
    color: #7DB6F0 !important;
}
.flashcard-front-label {
    background: #1A2D42 !important;
    color: #7DB6F0 !important;
}
.flashcard-back-label {
    background: #0F2A1A !important;
    color: #4CAF74 !important;
}
</style>
"""

# ─────────────────────────────────────────────
# SAMPLE LECTURE DATA (Demo Mode)
# ─────────────────────────────────────────────

SAMPLE_TRANSCRIPT = """Introduction to Machine Learning — Lecture Transcript

Welcome everyone to today's lecture. We're going to be covering the fundamentals of Machine Learning, which forms the bedrock of modern artificial intelligence.

Machine learning is a subfield of artificial intelligence that enables computer systems to learn from data and improve their performance on tasks without being explicitly programmed for each task. The key idea here is that instead of writing fixed rules, we expose the system to examples and let it figure out the patterns by itself.

There are three main paradigms in machine learning. The first is Supervised Learning. In supervised learning, we train a model on a labeled dataset — meaning the training examples come with correct answers. The model learns a mapping from inputs to outputs. Classic examples include email spam detection, where emails are labeled as spam or not spam, and image classification, where images are labeled with the objects they contain.

The second paradigm is Unsupervised Learning. Here, we have data without any labels. The goal is to discover hidden structure or patterns in the data. Clustering algorithms like K-Means are a great example — they group data points into clusters based on similarity, without any predefined categories. Another technique is dimensionality reduction using methods like Principal Component Analysis, or PCA, which compresses high-dimensional data into fewer dimensions while preserving important variance.

The third paradigm is Reinforcement Learning. In this setting, an agent interacts with an environment and learns by receiving rewards or penalties. The agent aims to maximize cumulative reward over time. This is the approach behind breakthrough applications like AlphaGo, which mastered the game of Go, and modern robotics.

Now let's discuss some fundamental concepts. A feature is an individual measurable property or characteristic of the data. For example, in a housing price prediction model, features might include the number of bedrooms, the square footage, and the neighborhood. Choosing good features — a process called feature engineering — is critical to building effective models.

The model is the mathematical function that maps inputs to outputs. Common model families include linear regression, which fits a straight line through data points; decision trees, which split the data based on feature thresholds; neural networks, which are inspired by the human brain and consist of layers of interconnected nodes; and support vector machines, which find an optimal separating hyperplane between classes.

Overfitting is one of the most important concepts to understand. A model that overfits has learned the training data too well — it memorizes noise and specific patterns in the training set rather than generalizing to new data. To combat overfitting, we use techniques such as regularization, dropout in neural networks, and cross-validation to properly evaluate model performance.

The bias-variance tradeoff is closely related to overfitting. High bias means the model is too simple and underfits the data — it doesn't capture the underlying pattern. High variance means the model is too complex and overfits — it captures noise. Good machine learning practice involves finding the right balance between bias and variance.

The training process involves feeding data into the model, computing a loss function that measures how wrong the predictions are, and then using an optimization algorithm — typically gradient descent — to adjust the model's parameters to reduce the loss. This cycle repeats many times until the model converges.

To evaluate a model, we split our dataset into at least two parts: a training set and a test set. The model never sees the test set during training, so it provides an unbiased estimate of how the model will perform on real, unseen data. Common evaluation metrics include accuracy for classification, mean squared error for regression, and the F1 score when dealing with imbalanced classes.

Data preprocessing is another essential step. Real-world data is often messy — it may contain missing values, outliers, inconsistent formatting, and varying scales. Techniques like normalization and standardization put features on the same scale, which is important for many algorithms. Handling missing data through imputation ensures we don't lose valuable training examples.

In recent years, deep learning — a subfield of machine learning that uses neural networks with many layers — has revolutionized fields such as computer vision, natural language processing, and speech recognition. Convolutional neural networks excel at image tasks. Recurrent neural networks and transformers are designed for sequential data like text and speech.

To summarize today's lecture: machine learning allows systems to learn from data. We covered the three main paradigms — supervised, unsupervised, and reinforcement learning. We discussed critical concepts like features, models, overfitting, the bias-variance tradeoff, the training loop, and evaluation. We also touched on the importance of data preprocessing and the rise of deep learning. In the next lecture, we'll dive into a hands-on implementation using Python's scikit-learn library.

Thank you for your attention today.
"""

SAMPLE_STUDY_MATERIAL = {
    "summary": {
        "overview": "This lecture provides a comprehensive introduction to machine learning (ML), covering its definition, the three core learning paradigms, fundamental concepts including features, models, overfitting, the bias-variance tradeoff, the training process, and model evaluation. It also briefly introduces deep learning and its revolutionary impact.",
        "main_concepts": [
            "Machine Learning: A subfield of AI where systems learn from data without explicit programming.",
            "Supervised Learning: Training on labeled data to learn input-output mappings (e.g., spam detection, image classification).",
            "Unsupervised Learning: Discovering hidden patterns in unlabeled data (e.g., clustering with K-Means, PCA for dimensionality reduction).",
            "Reinforcement Learning: An agent learns by interacting with an environment and maximizing cumulative reward (e.g., AlphaGo, robotics).",
            "The Training Loop: Feed data → compute loss → optimize with gradient descent → repeat until convergence.",
        ],
        "detailed_notes": [
            "Features are individual measurable properties of data; feature engineering is critical for model performance.",
            "Common model families: linear regression, decision trees, neural networks, support vector machines (SVMs).",
            "Overfitting: model memorizes training noise instead of generalizing; combated via regularization, dropout, and cross-validation.",
            "Bias-Variance Tradeoff: High bias = underfitting (too simple). High variance = overfitting (too complex). Balance is key.",
            "Dataset is split into training set (for learning) and test set (for unbiased evaluation).",
            "Evaluation metrics: accuracy (classification), MSE (regression), F1-score (imbalanced classes).",
            "Data preprocessing: handling missing values, normalization, standardization — essential for algorithm performance.",
            "Deep Learning uses multi-layer neural networks; CNNs for images, RNNs/Transformers for sequential data.",
        ],
        "takeaways": [
            "ML enables computers to learn from data rather than following explicit rules.",
            "Know the three paradigms: Supervised, Unsupervised, and Reinforcement Learning.",
            "Overfitting is one of the biggest practical challenges — always evaluate on a held-out test set.",
            "The bias-variance tradeoff is fundamental to choosing and tuning models.",
            "Data quality and preprocessing are as important as model choice.",
            "Deep learning has transformed computer vision, NLP, and speech recognition.",
        ]
    },
    "key_points": [
        "Machine learning is a subfield of AI that enables systems to learn from data without explicit programming.",
        "Supervised Learning trains on labeled data to map inputs to correct outputs.",
        "Unsupervised Learning finds hidden patterns in data without predefined labels.",
        "Reinforcement Learning uses reward signals from an environment to train agents.",
        "Features are measurable properties of data; feature engineering significantly impacts model quality.",
        "Common model families include linear regression, decision trees, neural networks, and SVMs.",
        "Overfitting occurs when a model memorizes training data noise and fails to generalize.",
        "Regularization, dropout, and cross-validation are standard techniques to prevent overfitting.",
        "The bias-variance tradeoff requires balancing model simplicity and complexity.",
        "Gradient descent is the core optimization algorithm used in the training loop.",
        "Models are evaluated on a separate test set using metrics like accuracy, MSE, and F1-score.",
        "Data preprocessing — normalization, standardization, and imputation — is essential before training.",
        "Deep learning (multi-layer neural networks) has revolutionized vision, NLP, and speech tasks.",
    ],
    "definitions": [
        {"term": "Machine Learning", "definition": "A subfield of artificial intelligence where computer systems learn patterns from data and improve their performance on tasks without being explicitly programmed for each task."},
        {"term": "Supervised Learning", "definition": "A type of machine learning where the model is trained on a labeled dataset — each training example has a known correct answer — and learns to map inputs to outputs."},
        {"term": "Unsupervised Learning", "definition": "A machine learning paradigm where the model discovers hidden structure or patterns in data that has no predefined labels."},
        {"term": "Reinforcement Learning", "definition": "A learning paradigm where an agent learns by interacting with an environment, receiving rewards for correct actions and penalties for incorrect ones, aiming to maximize total reward."},
        {"term": "Feature", "definition": "An individual measurable property or characteristic used as input to a machine learning model (e.g., square footage in a housing price model)."},
        {"term": "Overfitting", "definition": "A problem where a model learns the training data too precisely — including its noise — and therefore performs poorly on new, unseen data."},
        {"term": "Bias-Variance Tradeoff", "definition": "The balance between a model's error from wrong assumptions (bias / underfitting) and its error from sensitivity to small data fluctuations (variance / overfitting)."},
        {"term": "Gradient Descent", "definition": "An iterative optimization algorithm that adjusts a model's parameters in the direction that reduces the loss function, used to train machine learning models."},
        {"term": "Loss Function", "definition": "A mathematical function that measures how wrong a model's predictions are compared to the actual values; the goal of training is to minimize this function."},
        {"term": "K-Means Clustering", "definition": "An unsupervised learning algorithm that groups data points into K clusters based on similarity by iteratively assigning points to the nearest cluster centroid."},
        {"term": "Principal Component Analysis (PCA)", "definition": "A dimensionality reduction technique that compresses high-dimensional data into fewer dimensions while preserving as much variance (information) as possible."},
        {"term": "Regularization", "definition": "A set of techniques (e.g., L1, L2 penalties) added to a model's training process to penalize complexity and reduce overfitting."},
        {"term": "Deep Learning", "definition": "A subfield of machine learning using neural networks with many layers (deep architectures) that have achieved state-of-the-art results in vision, NLP, and speech."},
        {"term": "Convolutional Neural Network (CNN)", "definition": "A type of deep neural network designed for processing structured grid data like images, using convolutional layers to automatically detect spatial features."},
    ],
    "quiz": [
        {
            "question": "What is machine learning?",
            "options": [
                "A method of programming computers with explicit rules for every task",
                "A subfield of AI where systems learn patterns from data without being explicitly programmed",
                "A type of database management system",
                "A hardware technology used in graphics processing"
            ],
            "answer": 1,
            "explanation": "Machine learning allows systems to learn from data and improve performance without explicit programming for each task — unlike traditional rule-based programming."
        },
        {
            "question": "Which machine learning paradigm requires labeled training data?",
            "options": [
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Supervised Learning",
                "Self-supervised Learning"
            ],
            "answer": 2,
            "explanation": "Supervised Learning trains on labeled datasets where each example has a known correct answer, enabling the model to learn input-output mappings."
        },
        {
            "question": "What is overfitting in machine learning?",
            "options": [
                "When a model is too simple to capture patterns in the data",
                "When a model memorizes training data noise and fails to generalize to new data",
                "When the training process takes too long",
                "When the dataset is too large for the model"
            ],
            "answer": 1,
            "explanation": "Overfitting occurs when a model learns the training data too precisely — including noise — causing poor performance on unseen data."
        },
        {
            "question": "Which algorithm is primarily used to optimize machine learning models during training?",
            "options": [
                "K-Means",
                "PCA",
                "Gradient Descent",
                "Backtracking Search"
            ],
            "answer": 2,
            "explanation": "Gradient descent iteratively adjusts model parameters in the direction that reduces the loss function, and is the core optimization algorithm used in training."
        },
        {
            "question": "What is the purpose of a test set in machine learning?",
            "options": [
                "To train the model faster",
                "To provide additional training data",
                "To provide an unbiased evaluation of the model's performance on unseen data",
                "To store hyperparameters for the model"
            ],
            "answer": 2,
            "explanation": "The test set is kept separate from training data and is used only for evaluation, providing an unbiased estimate of real-world model performance."
        },
        {
            "question": "Which of the following is an example of Unsupervised Learning?",
            "options": [
                "Email spam detection using labeled emails",
                "Training an agent to play chess using rewards",
                "Grouping customer data into segments using K-Means clustering",
                "Predicting house prices using labeled historical data"
            ],
            "answer": 2,
            "explanation": "K-Means clustering groups data points by similarity without predefined labels, making it an unsupervised learning technique."
        },
        {
            "question": "What does a high bias in a model indicate?",
            "options": [
                "The model is overfitting the training data",
                "The model is too complex",
                "The model is too simple and underfits the data",
                "The model has too many parameters"
            ],
            "answer": 2,
            "explanation": "High bias means the model makes overly simplistic assumptions and cannot capture the true underlying pattern in the data — a condition called underfitting."
        },
        {
            "question": "What is Principal Component Analysis (PCA) primarily used for?",
            "options": [
                "Supervised classification of images",
                "Dimensionality reduction by compressing data while preserving variance",
                "Training reinforcement learning agents",
                "Computing gradient descent"
            ],
            "answer": 1,
            "explanation": "PCA is a dimensionality reduction technique that transforms high-dimensional data into fewer dimensions while retaining as much variance (information) as possible."
        },
        {
            "question": "Which type of neural network is best suited for image classification tasks?",
            "options": [
                "Recurrent Neural Network (RNN)",
                "Feedforward Neural Network",
                "Convolutional Neural Network (CNN)",
                "Support Vector Machine"
            ],
            "answer": 2,
            "explanation": "CNNs use convolutional layers to detect spatial features in images, making them the go-to architecture for computer vision tasks."
        },
        {
            "question": "Why is data preprocessing important before training a machine learning model?",
            "options": [
                "It is not necessary; modern algorithms handle all data formats automatically",
                "Real-world data often contains missing values, outliers, and varying scales that can degrade model performance",
                "It reduces the number of features to exactly three",
                "It converts unsupervised problems into supervised ones"
            ],
            "answer": 1,
            "explanation": "Real-world data is messy. Preprocessing (normalization, imputation, standardization) ensures data quality and consistent scale, which is critical for most ML algorithms."
        }
    ],
    "flashcards": [
        {"front": "What is Machine Learning?", "back": "A subfield of AI where computer systems learn patterns from data and improve performance on tasks without being explicitly programmed for each task."},
        {"front": "Name the three main ML paradigms.", "back": "1. Supervised Learning (labeled data)\n2. Unsupervised Learning (unlabeled data)\n3. Reinforcement Learning (reward signals from environment)"},
        {"front": "What is Overfitting?", "back": "When a model memorizes the training data including its noise, and fails to generalize to new, unseen data. Combated with regularization, dropout, and cross-validation."},
        {"front": "Explain the Bias-Variance Tradeoff.", "back": "High Bias = too simple, underfits (misses patterns).\nHigh Variance = too complex, overfits (memorizes noise).\nGoal: Find the right balance between them."},
        {"front": "What is Gradient Descent?", "back": "An iterative optimization algorithm that adjusts model parameters in the direction that minimizes the loss function. It is the core algorithm used to train most ML models."},
        {"front": "What is a Feature in machine learning?", "back": "An individual measurable property or characteristic of the data used as input to the model (e.g., square footage, number of bedrooms for house price prediction)."},
        {"front": "What is K-Means Clustering?", "back": "An unsupervised learning algorithm that groups data points into K clusters by iteratively assigning each point to its nearest cluster centroid based on similarity."},
        {"front": "What is PCA (Principal Component Analysis)?", "back": "A dimensionality reduction technique that compresses high-dimensional data into fewer dimensions while preserving the maximum amount of variance (information)."},
        {"front": "Why do we use a separate test set?", "back": "The model never sees the test set during training, so it provides an unbiased estimate of how the model will perform on real, unseen data in the real world."},
        {"front": "What is Deep Learning?", "back": "A subfield of ML using neural networks with many layers. It has revolutionized computer vision (CNNs), NLP, and speech recognition (RNNs, Transformers)."},
        {"front": "What is a Loss Function?", "back": "A mathematical function measuring how wrong a model's predictions are relative to the true values. The training process minimizes this function."},
        {"front": "What is Regularization?", "back": "Techniques added to model training (e.g., L1/L2 penalties) that penalize model complexity, helping prevent overfitting and improving generalization."},
    ]
}

# ─────────────────────────────────────────────
# API KEY DETECTION
# ─────────────────────────────────────────────

def get_api_key():
    """Return the first available API key, or None."""
    # Check st.secrets (Streamlit Cloud)
    if hasattr(st, "secrets"):
        try:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
            if "AI_API_KEY" in st.secrets:
                return st.secrets["AI_API_KEY"]
            if "OPENAI_API_KEY" in st.secrets:
                return st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    return (
        os.getenv("GEMINI_API_KEY") or
        os.getenv("AI_API_KEY") or
        os.getenv("OPENAI_API_KEY") or
        None
    )

def get_api_provider():
    """Return the detected provider name."""
    if hasattr(st, "secrets"):
        try:
            if "GEMINI_API_KEY" in st.secrets or "AI_API_KEY" in st.secrets:
                return "gemini"
            if "OPENAI_API_KEY" in st.secrets:
                return "openai"
        except Exception:
            pass
    if os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None

# ─────────────────────────────────────────────
# SPEECH-TO-TEXT
# ─────────────────────────────────────────────

def transcribe_audio(uploaded_file):
    """
    Transcribe an audio/video file using the configured AI provider.
    Returns the transcript as a string, or raises an Exception on failure.
    """
    provider = get_api_provider()
    api_key  = get_api_key()

    if not api_key:
        raise ValueError("No API key configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file.")

    file_bytes = uploaded_file.read()

    if provider == "gemini":
        return _transcribe_with_gemini(file_bytes, uploaded_file.name, api_key)
    elif provider == "openai":
        return _transcribe_with_openai(file_bytes, uploaded_file.name, api_key)
    else:
        raise ValueError("No supported API key found.")


def _transcribe_with_gemini(file_bytes: bytes, filename: str, api_key: str) -> str:
    """Transcribe audio using Google Gemini."""
    # Determine MIME type from extension
    ext = os.path.splitext(filename)[1].lower()
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "video/mp4",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }
    mime_type = mime_map.get(ext, "audio/mpeg")

    # Encode to base64
    audio_b64 = base64.b64encode(file_bytes).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": audio_b64
                    }
                },
                {
                    "text": (
                        "Please transcribe this audio/video recording accurately. "
                        "Produce a clean, readable transcript with proper punctuation and paragraph breaks. "
                        "Do not include timestamps unless they are very helpful for understanding. "
                        "Return only the transcript text, no commentary."
                    )
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192
        }
    }

    response = requests.post(url, json=payload, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:400]}")

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response format: {e}")


def _transcribe_with_openai(file_bytes: bytes, filename: str, api_key: str) -> str:
    """Transcribe audio using OpenAI Whisper."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    files = {
        "file": (filename, file_bytes),
        "model": (None, "whisper-1"),
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(url, headers=headers, files=files, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text[:400]}")
    return response.json().get("text", "").strip()


# ─────────────────────────────────────────────
# AI STUDY MATERIAL GENERATION
# ─────────────────────────────────────────────

def _call_gemini(prompt: str, api_key: str, temperature: float = 0.3) -> str:
    """Generic Gemini text generation call."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096}
    }
    response = requests.post(url, json=payload, timeout=90)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:400]}")
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_openai(prompt: str, api_key: str, temperature: float = 0.3) -> str:
    """Generic OpenAI chat completion call."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 4096
    }
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text[:400]}")
    return response.json()["choices"][0]["message"]["content"].strip()


def _call_ai(prompt: str, temperature: float = 0.3) -> str:
    """Route to the configured AI provider."""
    provider = get_api_provider()
    api_key  = get_api_key()
    if not api_key:
        raise ValueError("No API key configured.")
    if provider == "gemini":
        return _call_gemini(prompt, api_key, temperature)
    elif provider == "openai":
        return _call_openai(prompt, api_key, temperature)
    raise ValueError("No AI provider configured.")


def _parse_json_from_response(text: str) -> any:
    """
    Extract and parse JSON from an AI response that may wrap it in markdown code fences.
    """
    # Try to strip markdown code fences
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```\s*$", "", clean.strip(), flags=re.MULTILINE)
    clean = clean.strip()
    return json.loads(clean)


def generate_summary(transcript: str) -> dict:
    """
    Generate structured study notes from the transcript.
    Returns a dict with keys: overview, main_concepts, detailed_notes, takeaways.
    """
    prompt = f"""You are an expert academic note-taker. Based ONLY on the following lecture transcript, generate structured study notes.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return your response as valid JSON with exactly this structure:
{{
  "overview": "<2-3 sentence concise summary of the lecture>",
  "main_concepts": ["<concept 1>", "<concept 2>", ...],
  "detailed_notes": ["<bullet point 1>", "<bullet point 2>", ...],
  "takeaways": ["<key takeaway 1>", "<key takeaway 2>", ...]
}}

Rules:
- Only use information from the transcript. Do not invent facts.
- main_concepts: 4-8 important concepts explained clearly.
- detailed_notes: 6-12 organized bullet points of important lecture content.
- takeaways: 4-8 most important points for exam revision.
- Return only valid JSON, no other text.
"""
    raw = _call_ai(prompt)
    return _parse_json_from_response(raw)


def generate_key_points(transcript: str) -> list:
    """
    Generate 5–15 key points from the transcript.
    Returns a list of strings.
    """
    prompt = f"""You are an academic summarizer. Based ONLY on the following lecture transcript, extract the most important key points a student should remember.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return your response as valid JSON — a simple array of strings:
["<key point 1>", "<key point 2>", ...]

Rules:
- Generate between 5 and 15 key points depending on lecture length and complexity.
- Only include points actually discussed in the transcript.
- Each point should be 1-2 complete sentences.
- Return only valid JSON, no other text.
"""
    raw = _call_ai(prompt)
    return _parse_json_from_response(raw)


def generate_definitions(transcript: str) -> list:
    """
    Extract important terms and definitions from the transcript.
    Returns a list of dicts with keys: term, definition.
    """
    prompt = f"""You are an academic glossary creator. Based ONLY on the following lecture transcript, extract all important technical terms and vocabulary that a student should understand.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return your response as valid JSON — an array of objects:
[
  {{"term": "<term>", "definition": "<clear, student-friendly definition>"}},
  ...
]

Rules:
- Only include terms that were actually discussed in the transcript.
- Write definitions in clear, student-friendly language.
- Generate between 5 and 20 definitions depending on the lecture content.
- Return only valid JSON, no other text.
"""
    raw = _call_ai(prompt)
    return _parse_json_from_response(raw)


def generate_quiz(transcript: str) -> list:
    """
    Generate 5–10 multiple-choice quiz questions from the transcript.
    Returns a list of dicts with keys: question, options (list of 4), answer (0-indexed int), explanation.
    """
    prompt = f"""You are an expert academic quiz creator. Based ONLY on the following lecture transcript, create a multiple-choice quiz to test student understanding.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return your response as valid JSON — an array of question objects:
[
  {{
    "question": "<the quiz question>",
    "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
    "answer": <index of correct option, 0-3>,
    "explanation": "<brief explanation of why this answer is correct>"
  }},
  ...
]

Rules:
- Generate between 5 and 10 questions.
- Questions must be based entirely on lecture content — no external information.
- All 4 options must be plausible. Avoid obviously wrong distractors.
- The "answer" field must be the integer index (0, 1, 2, or 3) of the correct option.
- Return only valid JSON, no other text.
"""
    raw = _call_ai(prompt)
    return _parse_json_from_response(raw)


def generate_flashcards(transcript: str) -> list:
    """
    Generate 8–15 flashcards from the transcript.
    Returns a list of dicts with keys: front, back.
    """
    prompt = f"""You are an expert study card creator. Based ONLY on the following lecture transcript, create flashcards to help a student memorize and review key concepts.

Transcript:
\"\"\"
{transcript}
\"\"\"

Return your response as valid JSON — an array of flashcard objects:
[
  {{"front": "<question or concept on the front>", "back": "<answer or explanation on the back>"}},
  ...
]

Rules:
- Generate between 8 and 15 flashcards.
- Only use content from the transcript.
- Front: a question, term, or concept prompt.
- Back: a clear, concise answer or explanation.
- Return only valid JSON, no other text.
"""
    raw = _call_ai(prompt)
    return _parse_json_from_response(raw)


# ─────────────────────────────────────────────
# DOWNLOAD CONTENT GENERATION
# ─────────────────────────────────────────────

def format_summary_txt(summary: dict, topic: str) -> str:
    lines = [f"LECTURENOTE AI — STUDY NOTES", f"Lecture: {topic}", "=" * 60, ""]
    lines += ["LECTURE OVERVIEW", "-" * 40, summary.get("overview", ""), ""]
    lines += ["MAIN CONCEPTS", "-" * 40]
    for c in summary.get("main_concepts", []):
        lines.append(f"  • {c}")
    lines += ["", "DETAILED NOTES", "-" * 40]
    for n in summary.get("detailed_notes", []):
        lines.append(f"  • {n}")
    lines += ["", "IMPORTANT TAKEAWAYS", "-" * 40]
    for t in summary.get("takeaways", []):
        lines.append(f"  • {t}")
    return "\n".join(lines)


def format_key_points_txt(key_points: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — KEY POINTS", f"Lecture: {topic}", "=" * 60, ""]
    for i, pt in enumerate(key_points, 1):
        lines.append(f"{i:02d}. {pt}")
        lines.append("")
    return "\n".join(lines)


def format_definitions_txt(definitions: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — DEFINITIONS & GLOSSARY", f"Lecture: {topic}", "=" * 60, ""]
    for d in definitions:
        lines.append(f"[{d['term']}]")
        lines.append(f"  {d['definition']}")
        lines.append("")
    return "\n".join(lines)


def format_quiz_txt(quiz: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — QUIZ", f"Lecture: {topic}", "=" * 60, ""]
    for i, q in enumerate(quiz, 1):
        lines.append(f"Q{i}. {q['question']}")
        for j, opt in enumerate(q['options']):
            marker = "✓" if j == q['answer'] else " "
            lines.append(f"  [{marker}] {chr(65+j)}) {opt}")
        lines.append(f"  Explanation: {q['explanation']}")
        lines.append("")
    return "\n".join(lines)


def format_flashcards_txt(flashcards: list, topic: str) -> str:
    lines = [f"LECTURENOTE AI — FLASHCARDS", f"Lecture: {topic}", "=" * 60, ""]
    for i, fc in enumerate(flashcards, 1):
        lines.append(f"Card {i}")
        lines.append(f"  FRONT: {fc['front']}")
        lines.append(f"  BACK:  {fc['back']}")
        lines.append("")
    return "\n".join(lines)


def format_full_pack_txt(topic, transcript, summary, key_points, definitions, quiz, flashcards) -> str:
    parts = [
        f"LECTURENOTE AI — COMPLETE STUDY PACK\nLecture: {topic}\n" + "=" * 60,
        format_summary_txt(summary, topic),
        format_key_points_txt(key_points, topic),
        format_definitions_txt(definitions, topic),
        format_quiz_txt(quiz, topic),
        format_flashcards_txt(flashcards, topic),
        f"TRANSCRIPT\n" + "-" * 40 + "\n" + transcript,
    ]
    return "\n\n" + ("\n\n" + "=" * 60 + "\n\n").join(parts)


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

def init_session_state():
    defaults = {
        "processing_done":    False,
        "transcript":         None,
        "summary":            None,
        "key_points":         None,
        "definitions":        None,
        "quiz":               None,
        "flashcards":         None,
        "lecture_topic":      "",
        # Quiz state
        "quiz_current_q":     0,
        "quiz_answers":       {},
        "quiz_submitted":     False,
        "quiz_score":         0,
        # Flashcard state
        "card_index":         0,
        "card_show_back":     False,
        # Navigation
        "current_page":       "home",
        # Sample mode flag
        "using_sample":       False,
        # UI Preferences
        "dark_mode":          False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_results():
    """Clear all generated results to allow re-processing."""
    keys_to_clear = [
        "processing_done", "transcript", "summary", "key_points",
        "definitions", "quiz", "flashcards",
        "quiz_current_q", "quiz_answers", "quiz_submitted", "quiz_score",
        "card_index", "card_show_back", "using_sample"
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    init_session_state()


# ─────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────

def render_header():
    dark_mode = st.session_state.get("dark_mode", False)
    toggle_icon  = "☀️" if dark_mode else "🌙"
    toggle_label = "Light" if dark_mode else "Dark"

    logo_col = "#E2EAF4" if dark_mode else "#1A2B3C"
    sub_col  = "#8FA3BB" if dark_mode else "#44474C"
    nav_act  = "#E2EAF4" if dark_mode else "#1A2B3C"
    nav_mut  = "#8FA3BB" if dark_mode else "#74777D"
    bdr_col  = "#253547" if dark_mode else "#E1E4E8"

    col_logo, col_toggle = st.columns([5, 1])

    with col_logo:
        # Logo + inline nav links all in one HTML row (no stacking on mobile)
        st.markdown(f"""
        <div style="padding: 1rem 0 0.6rem; border-bottom: 1px solid {bdr_col};
                    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
            <div style="display:flex; align-items:baseline; gap:0.5rem; flex-shrink:0;">
                <span style="font-family:var(--font-head);font-size:1.3rem;font-weight:700;
                             color:{logo_col};letter-spacing:-0.02em;white-space:nowrap;"
                >LectureNote<span style='color:var(--accent);'> AI</span></span>
                <span style="font-family:var(--font-body);font-size:0.8rem;color:{sub_col};white-space:nowrap;"
                >&nbsp;&middot;&nbsp; Your lecture. Organized for learning.</span>
            </div>
            <nav style="display:flex; align-items:center; gap:1.5rem; flex-wrap:nowrap;">
                <span style="font-family:var(--font-head);font-size:0.85rem;font-weight:600;color:{nav_act};">Home</span>
                <span style="font-family:var(--font-head);font-size:0.85rem;font-weight:500;color:{nav_mut};">My Lectures</span>
                <span style="font-family:var(--font-head);font-size:0.85rem;font-weight:500;color:{nav_mut};">About</span>
            </nav>
        </div>
        """, unsafe_allow_html=True)

    with col_toggle:
        # Vertically align button with the bottom border
        st.markdown("<div style='padding-top:0.85rem;'>", unsafe_allow_html=True)
        if st.button(f"{toggle_icon} {toggle_label}", key="header_theme_toggle",
                     help="Toggle dark / light mode", use_container_width=True):
            st.session_state.dark_mode = not dark_mode
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)


def render_api_key_notice():
    """Show a non-blocking notice if no API key is configured."""
    if not get_api_key():
        st.info(
            "💡 **No API key detected.** You can still explore the app using the built-in Sample Lecture. "
            "To process your own lectures, add a `GEMINI_API_KEY` or `OPENAI_API_KEY` to a `.env` file.",
            icon=None
        )


def render_home_page():
    """Render the upload / home page."""

    # Hero
    st.markdown("""
    <div class="hero">
        <h1>Turn lectures into clear study material.</h1>
        <p>Upload a lecture recording and transform it into organized notes, quizzes, and flashcards.</p>
    </div>
    """, unsafe_allow_html=True)

    render_api_key_notice()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="section-badge">Upload Lecture</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-container">
        <div class="upload-icon">🎙️</div>
        <div class="upload-title">Upload your lecture</div>
        <div class="upload-subtitle">Drag and drop your audio or video file here</div>
        <div class="format-tags">
            <span class="format-tag">MP3</span>
            <span class="format-tag">WAV</span>
            <span class="format-tag">M4A</span>
            <span class="format-tag">MP4</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose audio or video file",
        type=["mp3", "wav", "m4a", "mp4", "aac", "flac", "ogg"],
        label_visibility="collapsed",
        key="lecture_uploader"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Topic input
    st.markdown('<div class="card-title">Lecture Topic <span style="font-weight:400;color:var(--text-muted);font-size:0.85rem;">(optional)</span></div>', unsafe_allow_html=True)
    lecture_topic = st.text_input(
        "Lecture Topic",
        placeholder="e.g. Introduction to Machine Learning",
        label_visibility="collapsed",
        key="topic_input"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn, col_sample, col_spacer = st.columns([2, 2, 4])

    with col_btn:
        generate_clicked = st.button(
            "🎓  Generate Study Material",
            type="primary",
            use_container_width=True,
            key="btn_generate"
        )

    with col_sample:
        sample_clicked = st.button(
            "📄  Load Sample Lecture",
            use_container_width=True,
            key="btn_sample"
        )

    # ── Handle SAMPLE ──
    if sample_clicked:
        reset_results()
        with st.status("Loading sample lecture...", expanded=True) as status:
            st.write("✅ Loading built-in lecture recording...")
            time.sleep(0.3)
            st.write("✅ Using pre-processed transcript...")
            time.sleep(0.3)
            st.write("✅ Loading study notes, quiz, and flashcards...")
            time.sleep(0.4)

            st.session_state.transcript    = SAMPLE_TRANSCRIPT
            st.session_state.summary       = SAMPLE_STUDY_MATERIAL["summary"]
            st.session_state.key_points    = SAMPLE_STUDY_MATERIAL["key_points"]
            st.session_state.definitions   = SAMPLE_STUDY_MATERIAL["definitions"]
            st.session_state.quiz          = SAMPLE_STUDY_MATERIAL["quiz"]
            st.session_state.flashcards    = SAMPLE_STUDY_MATERIAL["flashcards"]
            st.session_state.lecture_topic = "Introduction to Machine Learning"
            st.session_state.processing_done = True
            st.session_state.using_sample  = True
            st.session_state.current_page  = "results"
            status.update(label="Sample lecture ready!", state="complete")

        st.rerun()

    # ── Handle GENERATE ──
    if generate_clicked:
        # Validation
        if uploaded_file is None:
            st.warning("📂 Please upload a lecture recording to continue.", icon=None)
            return

        # File size check
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"⚠️ File is too large ({file_size_mb:.1f} MB). Maximum supported size is {MAX_FILE_SIZE_MB} MB.")
            return

        if not get_api_key():
            st.error("🔑 No API key found. Please configure `GEMINI_API_KEY` or `OPENAI_API_KEY` in your `.env` file.")
            return

        topic = lecture_topic.strip() or uploaded_file.name

        reset_results()
        st.session_state.lecture_topic = topic

        # Processing pipeline
        try:
            with st.status("Processing your lecture...", expanded=True) as status:

                # Step 1: Upload confirmed
                st.write("✅ Lecture uploaded")
                time.sleep(0.3)

                # Step 2: Transcription
                st.write("⏳ Converting speech to text...")
                transcript = transcribe_audio(uploaded_file)
                if not transcript or len(transcript.strip()) < 50:
                    raise ValueError("Transcript appears to be empty or too short. Please try a different recording.")
                st.session_state.transcript = transcript
                st.write("✅ Speech-to-text complete")

                # Step 3: Organize content
                st.write("⏳ Organizing lecture content...")
                summary = generate_summary(transcript)
                st.session_state.summary = summary
                st.write("✅ Study notes generated")

                # Step 4: Key points & definitions
                st.write("⏳ Extracting key points and definitions...")
                key_points  = generate_key_points(transcript)
                definitions = generate_definitions(transcript)
                st.session_state.key_points  = key_points
                st.session_state.definitions = definitions
                st.write("✅ Key points and definitions ready")

                # Step 5: Quiz
                st.write("⏳ Creating quiz...")
                quiz = generate_quiz(transcript)
                st.session_state.quiz = quiz
                st.write("✅ Quiz created")

                # Step 6: Flashcards
                st.write("⏳ Creating flashcards...")
                flashcards = generate_flashcards(transcript)
                st.session_state.flashcards = flashcards
                st.write("✅ Flashcards ready")

                st.session_state.processing_done = True
                st.session_state.current_page = "results"
                status.update(label="Study material ready!", state="complete")

        except ValueError as e:
            st.error(f"⚠️ {e}")
        except requests.exceptions.Timeout:
            st.error("⏱️ The request timed out. Please try again with a shorter recording or check your connection.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Could not connect to the AI service. Please check your internet connection.")
        except json.JSONDecodeError:
            st.error("⚠️ Something went wrong while processing the AI response. Please try again.")
        except Exception as e:
            st.error(f"⚠️ Something went wrong while processing your lecture. Please try again.\n\nDetails: {str(e)[:200]}")
            return

        if st.session_state.processing_done:
            st.rerun()


# ─────────────────────────────────────────────
# RESULTS PAGE COMPONENTS
# ─────────────────────────────────────────────

def render_transcript_tab():
    topic     = st.session_state.lecture_topic
    transcript = st.session_state.transcript

    st.markdown('<div class="section-badge">Lecture Transcript</div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family:var(--font-head);color:var(--primary);font-size:1.4rem;margin-bottom:1rem;'>Lecture Transcript</h2>", unsafe_allow_html=True)
    st.markdown(f'<div class="transcript-body">{transcript}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️  Download Transcript",
            data=transcript,
            file_name=f"transcript_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_transcript"
        )
    with col2:
        # Copy-friendly expander (Streamlit compatible)
        with st.expander("📋  Copy Transcript"):
            st.code(transcript, language=None)


def render_study_notes_tab():
    topic   = st.session_state.lecture_topic
    summary = st.session_state.summary

    st.markdown('<div class="section-badge">Study Notes</div>', unsafe_allow_html=True)

    # Overview
    st.markdown("""<h3 style='font-family:var(--font-head);color:var(--primary);font-size:1.15rem;margin:1rem 0 0.5rem;'>📋 Lecture Overview</h3>""", unsafe_allow_html=True)
    st.markdown(f'<div class="card"><p class="card-text">{summary.get("overview","")}</p></div>', unsafe_allow_html=True)

    # Main Concepts
    st.markdown("""<h3 style='font-family:var(--font-head);color:var(--primary);font-size:1.15rem;margin:1.25rem 0 0.5rem;'>💡 Main Concepts</h3>""", unsafe_allow_html=True)
    concepts_html = "".join(f'<li style="margin-bottom:0.5rem;font-family:var(--font-body);font-size:0.975rem;color:var(--text-body);line-height:1.6;">{c}</li>' for c in summary.get("main_concepts", []))
    st.markdown(f'<div class="card"><ul style="margin:0;padding-left:1.25rem;">{concepts_html}</ul></div>', unsafe_allow_html=True)

    # Detailed Notes
    st.markdown("""<h3 style='font-family:var(--font-head);color:var(--primary);font-size:1.15rem;margin:1.25rem 0 0.5rem;'>📝 Detailed Notes</h3>""", unsafe_allow_html=True)
    notes_html = "".join(f'<li style="margin-bottom:0.6rem;font-family:var(--font-body);font-size:0.975rem;color:var(--text-body);line-height:1.6;">{n}</li>' for n in summary.get("detailed_notes", []))
    st.markdown(f'<div class="card"><ul style="margin:0;padding-left:1.25rem;">{notes_html}</ul></div>', unsafe_allow_html=True)

    # Important Takeaways
    st.markdown("""<h3 style='font-family:var(--font-head);color:var(--primary);font-size:1.15rem;margin:1.25rem 0 0.5rem;'>⭐ Important Takeaways</h3>""", unsafe_allow_html=True)
    takeaway_html = "".join(f'<li style="margin-bottom:0.6rem;font-family:var(--font-body);font-size:0.975rem;color:var(--text-body);line-height:1.6;">{t}</li>' for t in summary.get("takeaways", []))
    st.markdown(f'<div class="card" style="border-left:3px solid var(--accent);"><ul style="margin:0;padding-left:1.25rem;">{takeaway_html}</ul></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "⬇️  Download Study Notes",
        data=format_summary_txt(summary, topic),
        file_name=f"study_notes_{topic.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=False,
        key="dl_notes"
    )


def render_key_points_tab():
    topic      = st.session_state.lecture_topic
    key_points = st.session_state.key_points

    st.markdown('<div class="section-badge">Key Points</div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family:var(--font-head);color:var(--primary);font-size:1.4rem;margin-bottom:1.25rem;'>Key Points</h2>", unsafe_allow_html=True)

    for i, pt in enumerate(key_points, 1):
        num_str = f"{i:02d}"
        st.markdown(f"""
        <div class="key-point-item">
            <div class="key-point-num">{num_str}</div>
            <div class="key-point-text">{pt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "⬇️  Download Key Points",
        data=format_key_points_txt(key_points, topic),
        file_name=f"key_points_{topic.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=False,
        key="dl_keypoints"
    )


def render_definitions_tab():
    topic       = st.session_state.lecture_topic
    definitions = st.session_state.definitions

    st.markdown('<div class="section-badge">Glossary & Definitions</div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family:var(--font-head);color:var(--primary);font-size:1.4rem;margin-bottom:1.25rem;'>Definitions</h2>", unsafe_allow_html=True)

    for d in definitions:
        st.markdown(f"""
        <div class="def-card">
            <div class="def-term">{d.get('term','')}</div>
            <div class="def-meaning">{d.get('definition','')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "⬇️  Download Definitions",
        data=format_definitions_txt(definitions, topic),
        file_name=f"definitions_{topic.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=False,
        key="dl_definitions"
    )


def render_quiz_tab():
    topic = st.session_state.lecture_topic
    quiz  = st.session_state.quiz

    st.markdown('<div class="section-badge">Practice Quiz</div>', unsafe_allow_html=True)

    if not quiz:
        st.info("No quiz questions available.")
        return

    total_q = len(quiz)

    if st.session_state.quiz_submitted:
        # ── Results View ──
        score    = st.session_state.quiz_score
        pct      = int((score / total_q) * 100)
        emoji    = "🎉" if pct >= 70 else ("📚" if pct >= 50 else "💪")

        st.markdown(f"""
        <div class="quiz-score-box">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">{emoji}</div>
            <div class="quiz-score-big">{score} / {total_q}</div>
            <div class="quiz-score-label">Quiz Complete · {pct}% Correct</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Show all questions with correct/incorrect indicators
        for i, q in enumerate(quiz):
            user_ans = st.session_state.quiz_answers.get(i)
            correct  = q["answer"]
            is_right = user_ans == correct
            border_color = "#2E7D32" if is_right else "#B71C1C"
            icon         = "✅" if is_right else "❌"

            st.markdown(f"""
            <div class="quiz-question" style="border-left:3px solid {border_color};">
                <div class="quiz-question-num">Question {i+1} &nbsp; {icon}</div>
                <div class="quiz-question-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            if not is_right:
                u_text = q["options"][user_ans] if user_ans is not None else "No answer"
                c_text = q["options"][correct]
                with st.expander(f"📖 View Explanation — Q{i+1}"):
                    st.markdown(f"**Your answer:** {u_text}")
                    st.markdown(f"**Correct answer:** {c_text}")
                    st.markdown(f"**Explanation:** {q.get('explanation','')}")

        st.markdown("<br>", unsafe_allow_html=True)
        col_r, col_d, _ = st.columns([2, 2, 3])
        with col_r:
            if st.button("🔄  Retake Quiz", use_container_width=True, key="quiz_retake"):
                st.session_state.quiz_current_q = 0
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score     = 0
                st.rerun()
        with col_d:
            st.download_button(
                "⬇️  Download Quiz",
                data=format_quiz_txt(quiz, topic),
                file_name=f"quiz_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="dl_quiz"
            )
        return

    # ── Interactive Quiz View ──
    current_q = st.session_state.quiz_current_q
    q_data    = quiz[current_q]

    # Progress indicator
    progress_val = (current_q) / total_q
    st.progress(progress_val)
    st.markdown(f"<p style='font-family:var(--font-head);font-size:0.8rem;color:var(--text-muted);font-weight:600;'>Question {current_q+1} of {total_q}</p>", unsafe_allow_html=True)

    # Question card
    st.markdown(f"""
    <div class="quiz-question">
        <div class="quiz-question-num">Question {current_q+1}</div>
        <div class="quiz-question-text">{q_data['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Options (radio)
    options      = q_data["options"]
    prev_answer  = st.session_state.quiz_answers.get(current_q)
    radio_index  = prev_answer if prev_answer is not None else None

    selected = st.radio(
        "Select your answer:",
        options=options,
        index=radio_index,
        label_visibility="collapsed",
        key=f"quiz_radio_{current_q}"
    )

    if selected is not None:
        st.session_state.quiz_answers[current_q] = options.index(selected)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation
    col_prev, col_next, col_submit = st.columns([2, 2, 3])

    with col_prev:
        if current_q > 0:
            if st.button("← Previous", use_container_width=True, key="quiz_prev"):
                st.session_state.quiz_current_q -= 1
                st.rerun()

    with col_next:
        if current_q < total_q - 1:
            if st.button("Next →", use_container_width=True, key="quiz_next"):
                st.session_state.quiz_current_q += 1
                st.rerun()

    with col_submit:
        if current_q == total_q - 1 or len(st.session_state.quiz_answers) == total_q:
            if st.button("✔  Submit Quiz", type="primary", use_container_width=True, key="quiz_submit"):
                # Calculate score
                score = sum(
                    1 for i, q in enumerate(quiz)
                    if st.session_state.quiz_answers.get(i) == q["answer"]
                )
                st.session_state.quiz_score     = score
                st.session_state.quiz_submitted = True
                st.rerun()

    # Answered indicator
    answered = len(st.session_state.quiz_answers)
    st.markdown(f"<p style='font-family:var(--font-head);font-size:0.78rem;color:var(--text-muted);margin-top:1rem;'>{answered} of {total_q} questions answered</p>", unsafe_allow_html=True)


def render_flashcards_tab():
    topic      = st.session_state.lecture_topic
    flashcards = st.session_state.flashcards

    st.markdown('<div class="section-badge">Flashcards</div>', unsafe_allow_html=True)

    if not flashcards:
        st.info("No flashcards available.")
        return

    total_cards = len(flashcards)
    idx         = st.session_state.card_index
    show_back   = st.session_state.card_show_back
    card        = flashcards[idx]

    # Card display
    if show_back:
        label_html   = '<span class="flashcard-side-label flashcard-back-label">Answer</span>'
        content_html = card["back"].replace("\n", "<br>")
    else:
        label_html   = '<span class="flashcard-side-label flashcard-front-label">Question</span>'
        content_html = card["front"]

    st.markdown(f"""
    <div class="flashcard-outer">
        <div class="flashcard">
            {label_html}
            <div class="flashcard-content">{content_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Counter
    st.markdown(f'<p class="flashcard-counter" style="text-align:center;margin-bottom:1rem;">Card {idx+1} of {total_cards}</p>', unsafe_allow_html=True)

    # Progress bar
    st.progress((idx + 1) / total_cards)

    st.markdown("<br>", unsafe_allow_html=True)

    # Controls
    col_prev, col_flip, col_next = st.columns([2, 3, 2])

    with col_prev:
        if idx > 0:
            if st.button("← Previous", use_container_width=True, key="fc_prev"):
                st.session_state.card_index     = idx - 1
                st.session_state.card_show_back = False
                st.rerun()

    with col_flip:
        flip_label = "Hide Answer" if show_back else "Show Answer"
        if st.button(flip_label, type="primary", use_container_width=True, key="fc_flip"):
            st.session_state.card_show_back = not show_back
            st.rerun()

    with col_next:
        if idx < total_cards - 1:
            if st.button("Next →", use_container_width=True, key="fc_next"):
                st.session_state.card_index     = idx + 1
                st.session_state.card_show_back = False
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_restart, col_dl, _ = st.columns([2, 2, 3])
    with col_restart:
        if st.button("↩ Restart Cards", use_container_width=True, key="fc_restart"):
            st.session_state.card_index     = 0
            st.session_state.card_show_back = False
            st.rerun()
    with col_dl:
        st.download_button(
            "⬇️  Download Flashcards",
            data=format_flashcards_txt(flashcards, topic),
            file_name=f"flashcards_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_fc"
        )


def render_results_page():
    """Render the full results view with 6 tabs."""
    topic    = st.session_state.lecture_topic
    is_demo  = st.session_state.get("using_sample", False)

    # Back button
    if st.button("← New Lecture", key="btn_back"):
        reset_results()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Metadata row
    status_badge = (
        '<span style="background:#EEF7EE;color:#2E7D32;font-family:var(--font-head);'
        'font-size:0.72rem;font-weight:600;letter-spacing:0.06em;padding:0.2rem 0.6rem;'
        'border-radius:4px;">READY FOR REVISION</span>'
    )
    demo_note = ' &nbsp;<span style="font-family:var(--font-head);font-size:0.75rem;color:var(--text-muted);">(Sample Lecture)</span>' if is_demo else ""

    st.markdown(f"""
    <div class="meta-row">
        <div class="meta-item">
            <span class="meta-label">Lecture</span>
            <span class="meta-value">{topic}{demo_note}</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">Status</span>
            <span>{status_badge}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 style='font-family:var(--font-head);font-size:1.85rem;font-weight:700;color:var(--primary);letter-spacing:-0.02em;margin-bottom:1.5rem;'>Your Study Material</h1>", unsafe_allow_html=True)

    # Tabs
    tab_labels = ["📄 Transcript", "📝 Study Notes", "🔑 Key Points", "📖 Definitions", "✏️ Quiz", "🃏 Flashcards"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_transcript_tab()

    with tabs[1]:
        render_study_notes_tab()

    with tabs[2]:
        render_key_points_tab()

    with tabs[3]:
        render_definitions_tab()

    with tabs[4]:
        render_quiz_tab()

    with tabs[5]:
        render_flashcards_tab()

    # Download all
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-badge">Downloads</div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-family:var(--font-head);color:var(--primary);font-size:1.1rem;margin-bottom:1rem;'>Download All Study Material</h3>", unsafe_allow_html=True)

    full_pack = format_full_pack_txt(
        topic,
        st.session_state.transcript,
        st.session_state.summary,
        st.session_state.key_points,
        st.session_state.definitions,
        st.session_state.quiz,
        st.session_state.flashcards
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "⬇️  Full Study Pack",
            data=full_pack,
            file_name=f"study_pack_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_full"
        )
    with col2:
        st.download_button(
            "⬇️  Notes + Key Points",
            data=format_summary_txt(st.session_state.summary, topic) + "\n\n" +
                 format_key_points_txt(st.session_state.key_points, topic),
            file_name=f"notes_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_notes_kp"
        )
    with col3:
        st.download_button(
            "⬇️  Quiz + Flashcards",
            data=format_quiz_txt(st.session_state.quiz, topic) + "\n\n" +
                 format_flashcards_txt(st.session_state.flashcards, topic),
            file_name=f"practice_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_qz_fc"
        )


def render_about_page():
    st.markdown("""
    <div class="hero">
        <h1>About LectureNote AI</h1>
        <p>A study companion built for students who want to learn more effectively from their lectures.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">🎙️ Speech-to-Text</div>
            <div class="card-text">Automatically converts audio and video lecture recordings into a clean, readable transcript using AI-powered speech recognition.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-title">📝 Smart Study Notes</div>
            <div class="card-text">Generates structured notes including a lecture overview, main concepts, detailed bullet notes, and the most important revision takeaways.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-title">📖 Glossary & Definitions</div>
            <div class="card-text">Extracts every important technical term discussed in the lecture and provides a clear, student-friendly definition for each.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">✏️ Practice Quiz</div>
            <div class="card-text">Creates interactive multiple-choice quizzes generated entirely from the lecture content — complete with explanations for every answer.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-title">🃏 Flashcards</div>
            <div class="card-text">Generates interactive study flashcards with questions on the front and answers on the back to support spaced repetition learning.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div class="card-title">⬇️ Download Everything</div>
            <div class="card-text">Export your transcript, notes, key points, definitions, quiz, and flashcards as text files. Study anywhere, even offline.</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🎓 LectureNote AI")
        st.markdown("---")

        # Navigation
        pages = {"🏠 Home": "home", "📚 My Lectures": "home", "ℹ️ About": "about"}
        for label, page in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page}_{label}"):
                if page != st.session_state.current_page:
                    st.session_state.current_page = page
                    st.rerun()

        st.markdown("---")

        # ── Dark Mode Toggle ──
        dark_mode = st.session_state.get("dark_mode", False)
        toggle_label = "☀️  Light Mode" if dark_mode else "🌙  Dark Mode"
        if st.button(toggle_label, use_container_width=True, key="btn_dark_mode"):
            st.session_state.dark_mode = not dark_mode
            st.rerun()

        st.markdown("---")

        # API status
        api_key = get_api_key()
        provider = get_api_provider()

        if api_key:
            provider_name = "Google Gemini" if provider == "gemini" else "OpenAI"
            st.success(f"✅ API Key Active\n\n**{provider_name}**")
        else:
            st.warning("⚠️ No API Key\n\nAdd one to `.env` to process real lectures.")

        st.markdown("---")
        st.markdown("""
        <div style="font-family:var(--font-head);font-size:0.75rem;color:#B7C8DE;line-height:1.8;">
        <b style="color:#FFFFFF;">Supported Formats</b><br>
        MP3 · WAV · M4A · MP4<br><br>
        <b style="color:#FFFFFF;">Powered by</b><br>
        Streamlit · Google Gemini
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN APPLICATION ENTRY POINT
# ─────────────────────────────────────────────

def main():
    # ── Page Config ──
    st.set_page_config(
        page_title="LectureNote AI — Turn Lectures Into Study Material",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Inject academic CSS (always)
    st.markdown(ACADEMIC_CSS, unsafe_allow_html=True)

    # Inject dark mode CSS overrides if enabled
    if st.session_state.get("dark_mode", False):
        st.markdown(DARK_CSS, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Sidebar
    render_sidebar()

    # Main content
    render_header()

    # Page routing
    page = st.session_state.current_page

    if page == "about":
        render_about_page()
    elif page == "results" and st.session_state.processing_done:
        render_results_page()
    else:
        render_home_page()


if __name__ == "__main__":
    main()
