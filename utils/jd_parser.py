import re
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Master skill list — broad coverage across job types
SKILL_KEYWORDS = [
    # --- Programming Languages ---
    "python", "java", "javascript", "typescript", "r", "scala", "c++", "sql", "bash",
    "julia", "go", "rust", "kotlin", "swift", "ruby", "php",

    # --- Data & Engineering ---
    "etl", "data pipeline", "data pipelines", "data modelling", "data modeling",
    "data warehousing", "data warehouse", "spark", "apache spark", "kafka",
    "apache kafka", "airflow", "apache airflow", "dbt", "hadoop",
    "ci/cd", "github actions", "docker", "kubernetes", "rest api", "rest apis",
    "microservices", "databricks", "redshift", "data lake", "data lakehouse",
    "data engineering", "data architecture",

    # --- Python Libraries ---
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy",
    "scikit-learn", "mlflow", "streamlit", "fastapi", "flask", "django",

    # --- Cloud Platforms & Services ---
    "aws", "azure", "gcp", "google cloud",
    "s3", "lambda", "ec2", "azure data factory", "blob storage",
    "azure devops", "bigquery", "cloud run", "cloud functions",
    "sagemaker", "vertex ai", "azure ml",

    # --- BI & Visualisation ---
    "power bi", "tableau", "looker", "qlik", "excel",
    "google data studio", "looker studio", "metabase", "superset",

    # --- ML & AI ---
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "xgboost",
    "lightgbm", "catboost", "hugging face", "transformers",
    "llm", "llms", "large language model", "prompt engineering",
    "generative ai", "rag", "reinforcement learning",
    "feature engineering", "model evaluation", "a/b testing",

    # --- Databases ---
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "snowflake", "bigquery", "cassandra", "dynamodb", "elasticsearch",
    "neo4j", "oracle", "sql server",

    # --- Business & Analyst Skills ---
    "financial modelling", "financial modeling", "forecasting",
    "market research", "stakeholder management", "requirements gathering",
    "project management", "agile", "scrum", "kanban", "jira", "confluence",
    "business analysis", "process improvement", "data analysis",
    "data visualization", "data wrangling", "statistics",
    "excel", "powerpoint", "google sheets",

    # --- Marketing & Operations ---
    "crm", "salesforce", "hubspot", "google analytics", "seo", "sem",
    "campaign management", "marketing automation", "a/b testing",
    "email marketing", "content marketing", "social media",
    "google ads", "facebook ads", "mixpanel", "segment",

    # --- DevOps & Infrastructure ---
    "terraform", "ansible", "jenkins", "gitlab", "bitbucket",
    "linux", "unix", "networking", "cloud infrastructure",
    "site reliability", "observability", "monitoring", "grafana", "prometheus",

    # --- Soft Skills ---
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "presentation", "collaboration",
    "time management", "attention to detail", "adaptability",
]

def clean_text(text):
    """Lowercase and remove special characters."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/+#.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_skills_from_dict(text):
    """Case-insensitive substring match against SKILL_KEYWORDS.

    Both the text and each skill keyword are normalized the same way
    (hyphens → spaces) so that e.g. 'scikit-learn', 'hugging face',
    'github actions', and 'power bi' all match correctly.
    """
    cleaned = clean_text(text)
    found = []
    for skill in SKILL_KEYWORDS:
        # Normalize hyphens to spaces so 'scikit-learn' matches 'scikit learn'
        normalized = skill.lower().replace("-", " ")
        if normalized in cleaned:
            found.append(skill)
    return found


def extract_skills_spacy(text):
    """Use spaCy NER + noun chunks to surface additional skill tokens."""
    doc = nlp(text[:100000])
    tokens = set()
    for chunk in doc.noun_chunks:
        token = clean_text(chunk.text)
        if len(token) > 2:
            tokens.add(token)
    for ent in doc.ents:
        token = clean_text(ent.text)
        if len(token) > 2:
            tokens.add(token)
    # Keep only tokens that match SKILL_KEYWORDS (normalize hyphens to spaces)
    return [skill for skill in SKILL_KEYWORDS if skill.lower().replace("-", " ") in tokens]


def extract_skills(text):
    """Combine dictionary matching and spaCy NER for full skill coverage."""
    dict_skills = extract_skills_from_dict(text)
    ner_skills = extract_skills_spacy(text)
    return list(set(dict_skills + ner_skills))

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