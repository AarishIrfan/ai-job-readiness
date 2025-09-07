import json
import math
from typing import List, Dict, Tuple, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import re
nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))

# ------------------------
# Load skills DB
# ------------------------
def load_skills(path="skills.json") -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SKILLS_DB = load_skills()

# ------------------------
# Basic text cleaning
# ------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+#+\-]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)

# ------------------------
# Extract skills from JD
# ------------------------
def extract_skills_from_text(text: str, skills_db: Dict[str, List[str]]=SKILLS_DB) -> List[str]:
    text_clean = clean_text(text)
    found = set()
    for _, skills in skills_db.items():
        for skill in skills:
            skl = skill.lower()
            if skl in text_clean:
                found.add(skill)
    return sorted(list(found))

# ------------------------
# Unified Role + JD flow
# ------------------------
def get_required_skills(input_data: Union[str, Dict], skills_db=SKILLS_DB) -> List[str]:
    """
    input_data can be:
      - role name (str, must exist in skills_db)
      - job description text (str)
      - dict with { "role": "Python Developer", "jd": "..." }
    """
    if isinstance(input_data, str):
        if input_data in skills_db:  # role direct
            return skills_db[input_data]
        else:  # assume JD text
            return extract_skills_from_text(input_data, skills_db)
    elif isinstance(input_data, dict):
        role_skills = []
        jd_skills = []
        if "role" in input_data and input_data["role"] in skills_db:
            role_skills = skills_db[input_data["role"]]
        if "jd" in input_data:
            jd_skills = extract_skills_from_text(input_data["jd"], skills_db)
        return sorted(set(role_skills + jd_skills))
    else:
        return []

# ------------------------
# Readiness calculation
# ------------------------
def calculate_readiness(user_skills: List[str], role_skills: List[str], weights: Dict[str, float]=None) -> float:
    user_set = set([s.strip().lower() for s in user_skills])
    role_set = set([s.strip().lower() for s in role_skills])
    if not role_set:
        return 0.0
    matched = user_set.intersection(role_set)
    readiness = (len(matched) / len(role_set)) * 100
    return round(readiness, 2)

# ------------------------
# Category progress
# ------------------------
def category_progress(user_skills: List[str], role_skills: List[str]) -> Dict[str, float]:
    progress = {}
    user_set = set([s.strip().lower() for s in user_skills])
    for s in role_skills:
        progress[s] = 100.0 if s.strip().lower() in user_set else 0.0
    return progress

# ------------------------
# Recommend learning resources
# ------------------------
RESOURCE_DB = {
    "Python": "https://www.python.org/about/gettingstarted/",
    "Docker": "https://docs.docker.com/get-started/",
    "Kubernetes": "https://kubernetes.io/docs/tutorials/",
    "Selenium": "https://www.selenium.dev/documentation/",
    "Playwright": "https://playwright.dev/docs/intro",
    "SQL": "https://www.w3schools.com/sql/",
    "CI/CD": "https://www.atlassian.com/continuous-delivery/ci-vs-cd",
    "API Testing": "https://www.postman.com/",
    "Pandas": "https://pandas.pydata.org/docs/getting_started/index.html",
    "TensorFlow": "https://www.tensorflow.org/tutorials"
}

def recommend_learning(user_skills: List[str], role_skills: List[str], top_n=5) -> List[Tuple[str,str]]:
    user_set = set([s.strip().lower() for s in user_skills])
    missing = [s for s in role_skills if s.strip().lower() not in user_set]
    recs = []
    for m in missing:
        url = RESOURCE_DB.get(m, "https://www.google.com/search?q=learn+" + m.replace(" ", "+"))
        recs.append((m, url))
        if len(recs) >= top_n:
            break
    return recs

# ------------------------
# Role recommender
# ------------------------
def recommend_roles_from_user(user_skills: List[str], skills_db=SKILLS_DB, top_n=3) -> List[Tuple[str, float]]:
    roles = list(skills_db.keys())
    corpus = [" ".join(skills_db[r]).lower() for r in roles]
    user_text = " ".join(user_skills).lower()
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus + [user_text])
    sims = cosine_similarity(X[-1], X[:-1])[0]
    ranked = sorted([(roles[i], float(sims[i])) for i in range(len(roles))], key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

# ------------------------
# Utility
# ------------------------
def all_skills(skills_db=SKILLS_DB) -> List[str]:
    s = set()
    for skills in skills_db.values():
        for sk in skills:
            s.add(sk)
    return sorted(list(s))

# ------------------------
# Local test
# ------------------------
if __name__ == "__main__":
    # Example 1: JD text only
    jd = "We are looking for Python, Docker and CI/CD experience and familiarity with APIs and SQL."
    skills_from_jd = get_required_skills(jd)
    print("From JD:", skills_from_jd)

    # Example 2: Role only
    skills_from_role = get_required_skills("Python Developer")
    print("From Role:", skills_from_role)

    # Example 3: Both JD + Role
    skills_from_both = get_required_skills({
        "role": "Python Developer",
        "jd": jd
    })
    print("From Both:", skills_from_both)

    # Readiness check
    print("Readiness:", calculate_readiness(["Python","SQL"], skills_from_both))

    # Role recommendation
    print("Recommend roles:", recommend_roles_from_user(["Python", "APIs", "SQL"]))
