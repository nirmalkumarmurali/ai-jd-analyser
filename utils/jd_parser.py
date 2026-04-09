import re
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Master skill list — technical + tools
SKILL_KEYWORDS = [
    # Data & Analytics
    "python", "sql", "r", "scala", "julia",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "tableau", "power bi", "looker", "qlik", "excel",
    "statistics", "machine learning", "deep learning", "nlp",
    "data analysis", "data visualization", "data wrangling",
    "feature engineering", "model evaluation", "a/b testing",

    # ML Libraries
    "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost",
    "lightgbm", "catboost", "mlflow", "hugging face",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "bigquery",
    "snowflake", "redshift", "databricks", "spark", "hadoop",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git",
    "github", "airflow", "dbt", "fastapi", "flask", "streamlit",

    # Soft skills
    "communication", "teamwork", "problem solving",
    "critical thinking", "leadership", "presentation",
]

def clean_text(text):
    """Lowercase and remove special characters."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/+#.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_skills(text):
    """Extract matching skills from text."""
    cleaned = clean_text(text)
    found_skills = []
    for skill in SKILL_KEYWORDS:
        if skill.lower() in cleaned:
            found_skills.append(skill)
    return list(set(found_skills))

def extract_experience_level(text):
    """Detect seniority level from JD text."""
    text_lower = text.lower()
    if any(word in text_lower for word in ["senior", "lead", "principal", "staff"]):
        return "Senior"
    elif any(word in text_lower for word in ["junior", "entry", "graduate", "intern"]):
        return "Junior"
    elif any(word in text_lower for word in ["mid", "intermediate", "2+ years", "3+ years"]):
        return "Mid-level"
    else:
        return "Not specified"

def extract_job_title(text):
    """Extract job title — first non-empty line usually."""
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    return lines[0] if lines else "Unknown"

def parse_jd(jd_text):
    """
    Main function — takes raw JD text, returns structured dict.
    """
    skills = extract_skills(jd_text)
    level = extract_experience_level(jd_text)
    title = extract_job_title(jd_text)

    return {
        "job_title": title,
        "experience_level": level,
        "skills_found": skills,
        "skills_count": len(skills),
        "raw_text": jd_text
    }


# Quick test — run this file directly to verify
if __name__ == "__main__":
    sample_jd = """
    Data Analyst — Junior
    We are looking for a junior data analyst with experience in Python, SQL, and Tableau.
    You should be comfortable with data visualization, Excel, and working with PostgreSQL databases.
    Familiarity with AWS and Git is a plus. Strong communication skills required.
    """

    result = parse_jd(sample_jd)
    print("Job Title:", result["job_title"])
    print("Level:", result["experience_level"])
    print("Skills Found:", result["skills_found"])
    print("Skills Count:", result["skills_count"])