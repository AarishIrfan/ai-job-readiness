import streamlit as st
import pandas as pd
import json
from tracker import (
    load_skills,
    calculate_readiness,
    category_progress,
    recommend_learning,
    extract_skills_from_text,
    recommend_roles_from_user,
    all_skills
)

# -------------------------
# Streamlit App Config
# -------------------------
st.set_page_config(page_title="AI Job Readiness", layout="wide")

# Load skills database
SKILLS_DB = load_skills("skills.json")

st.title("AI-Powered Job Readiness Platform 🚀")
st.markdown(
    "Upload a job description or select a role, rate your skills, and get a readiness score + learning recommendations."
)

# -------------------------
# Sidebar - User Profile
# -------------------------
st.sidebar.header("Your Profile")
name = st.sidebar.text_input("Name", value="")

role_choice = st.sidebar.selectbox("Choose role to evaluate", options=list(SKILLS_DB.keys()))
st.sidebar.write("Or paste a job description to extract required skills:")

job_desc = st.sidebar.text_area("Paste job description (optional)", height=150)

st.sidebar.header("Your skills (tick or type)")
skills_list = all_skills(SKILLS_DB)
user_selected = st.sidebar.multiselect("Select skills you have", options=skills_list)

# Auto-extract skills
if st.sidebar.button("Auto-extract skills from job description"):
    if not job_desc.strip():
        st.sidebar.warning("Paste a job description first.")
    else:
        ext = extract_skills_from_text(job_desc)
        st.sidebar.success(f"Extracted skills: {', '.join(ext)}")
        st.session_state["extracted_skills"] = ext

# -------------------------
# Required Skills (Union Merge)
# -------------------------
role_skills = SKILLS_DB[role_choice]
jd_skills = st.session_state.get("extracted_skills", extract_skills_from_text(job_desc)) if job_desc.strip() else []

# Union merge (no duplicates)
required_skills = sorted(list(set(role_skills) | set(jd_skills)))

# -------------------------
# Evaluation
# -------------------------
st.header("Evaluation")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Required Skills (Role + JD)")
    st.write(", ".join(required_skills) if required_skills else "No skills detected yet.")

    st.subheader("Rate your skill levels (0-5)")
    ratings = {}
    for s in required_skills:
        val = st.slider(s, 0, 5, 0, key=f"r_{s}")
        ratings[s] = val

with col2:
    st.subheader("Your Selected Skills")
    st.write(", ".join(user_selected) if user_selected else "No skills selected yet.")

    st.subheader("Quick Predictions")
    rec_roles = recommend_roles_from_user(user_selected)
    st.write("Top matching roles based on your selected skills:")
    for r, score in rec_roles:
        st.write(f"- {r}  —  similarity {round(score,3)}")

# -------------------------
# Compute Readiness
# -------------------------
if st.button("Compute Readiness"):
    user_skill_list = [s for s, v in ratings.items() if v >= 3] + user_selected
    user_skill_list = sorted(list(set(user_skill_list)))

    readiness = calculate_readiness(user_skill_list, required_skills)
    st.metric(label="Readiness %", value=f"{readiness}%")

    st.write("Category progress (per required skill):")
    cp = category_progress(user_skill_list, required_skills)
    df = pd.DataFrame({"skill": list(cp.keys()), "progress": list(cp.values())})
    st.dataframe(df)

    st.subheader("Recommended Learning for Missing Skills:")
    recs = recommend_learning(user_skill_list, required_skills, top_n=8)
    for skill, url in recs:
        st.markdown(f"- **{skill}** → [Learn here]({url})")

    st.subheader("Export Results")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV", data=csv, file_name="readiness_results.csv", mime="text/csv"
    )

st.markdown("---")
st.caption("Built with Streamlit • Tracker engine is in tracker.py")
