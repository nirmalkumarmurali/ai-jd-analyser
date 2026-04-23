# coding: utf-8
import sys
import os

# Ensure the project root is on sys.path when running via `streamlit run app/main.py`
_project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

import streamlit as st
import plotly.graph_objects as go

from utils.jd_parser import parse_jd
from utils.cv_parser import parse_cv
from utils.matcher import match
from utils.insights import generate_suggestions


# --- Page config ---
st.set_page_config(
    page_title="AI JD Analyser",
    page_icon=":page_facing_up:",
    layout="wide",
)

st.title("AI Job Description Analyser")
st.caption("Paste a job description, upload your CV, and get an instant match score + AI-powered suggestions.")


# --- Inputs ---
col_left, col_right = st.columns(2)

with col_left:
    jd_text = st.text_area(
        "Job Description",
        height=300,
        placeholder="Paste the full job description here...",
    )

with col_right:
    cv_file = st.file_uploader("Upload your CV (PDF)", type=["pdf"])


# --- Run pipeline ---
if st.button("Analyse", type="primary", use_container_width=True):
    if not jd_text.strip():
        st.error("Please paste a job description.")
        st.stop()
    if cv_file is None:
        st.error("Please upload your CV as a PDF.")
        st.stop()

    with st.spinner("Parsing and analysing..."):
        jd_parsed = parse_jd(jd_text)
        cv_parsed = parse_cv(cv_file)
        gap = match(jd_parsed, cv_parsed)

    with st.spinner("Generating AI suggestions..."):
        try:
            suggestions_text = generate_suggestions(gap)
        except EnvironmentError as e:
            suggestions_text = f"Could not generate suggestions: {e}"

    # --- Results layout ---
    st.divider()

    # Match score
    score = gap["match_score"]
    score_colour = "#2ecc71" if score >= 70 else "#e67e22" if score >= 40 else "#e74c3c"
    st.markdown(
        f"<h1 style='text-align:center; color:{score_colour};'>{score}% Match</h1>",
        unsafe_allow_html=True,
    )

    st.divider()

    col_match, col_miss = st.columns(2)

    with col_match:
        st.subheader("Matched Skills")
        if gap["matched_skills"]:
            for skill in gap["matched_skills"]:
                st.markdown(
                    f"<span style='background:#d5f5e3; color:#1e8449; padding:3px 10px; "
                    f"border-radius:12px; margin:3px; display:inline-block;'>+ {skill}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No skills matched.")

    with col_miss:
        st.subheader("Missing Skills")
        if gap["missing_skills"]:
            for skill in gap["missing_skills"]:
                st.markdown(
                    f"<span style='background:#fadbd8; color:#922b21; padding:3px 10px; "
                    f"border-radius:12px; margin:3px; display:inline-block;'>x {skill}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.success("No skills are missing - great match!")

    st.divider()

    # AI suggestions
    st.subheader("AI-Powered Suggestions")
    lines = [line.strip() for line in suggestions_text.splitlines() if line.strip()]
    for line in lines:
        if line and line[0].isdigit():
            st.markdown(f"- {line}")
        else:
            st.markdown(line)

    st.divider()

    # Keyword bar chart
    st.subheader("JD Keyword Frequency")
    all_skills = jd_parsed["skills_found"]
    if all_skills:
        matched_set = set(gap["matched_skills"])
        colours = ["#2ecc71" if s in matched_set else "#e74c3c" for s in all_skills]

        fig = go.Figure(
            go.Bar(
                x=all_skills,
                y=[1] * len(all_skills),
                marker_color=colours,
                text=all_skills,
                textposition="outside",
            )
        )
        fig.update_layout(
            yaxis_visible=False,
            xaxis_title="Skills required by JD",
            showlegend=False,
            height=350,
            margin=dict(t=20, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Green = present in your CV   |   Red = missing from your CV")
    else:
        st.info("No recognised skills found in the JD.")
