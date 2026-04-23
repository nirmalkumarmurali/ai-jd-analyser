from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_score(jd_text, cv_text):
    """Compute cosine similarity between JD and CV text using TF-IDF vectors."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([jd_text, cv_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def find_matched_skills(jd_skills, cv_skills):
    """Return skills present in both JD and CV (case-insensitive)."""
    jd_set = {s.lower() for s in jd_skills}
    cv_set = {s.lower() for s in cv_skills}
    return sorted(jd_set & cv_set)


def find_missing_skills(jd_skills, cv_skills):
    """Return JD skills not found in the CV."""
    jd_set = {s.lower() for s in jd_skills}
    cv_set = {s.lower() for s in cv_skills}
    return sorted(jd_set - cv_set)


def match(jd_parsed, cv_parsed):
    """
    Compare JD and CV parsed dicts and return a gap analysis result.

    Args:
        jd_parsed: Output dict from jd_parser.parse_jd().
        cv_parsed:  Output dict from cv_parser.parse_cv().

    Returns:
        dict with keys: match_score, matched_skills, missing_skills.
    """
    score = compute_tfidf_score(jd_parsed["raw_text"], cv_parsed["raw_text"])
    matched = find_matched_skills(jd_parsed["skills_found"], cv_parsed["skills_found"])
    missing = find_missing_skills(jd_parsed["skills_found"], cv_parsed["skills_found"])

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
    }


if __name__ == "__main__":
    from utils.jd_parser import parse_jd

    sample_jd = parse_jd(
        "Data Analyst — we need Python, SQL, Tableau, AWS, communication skills."
    )
    sample_cv = {
        "raw_text": "Experienced in Python and SQL. Used pandas and matplotlib. Strong communicator.",
        "skills_found": ["python", "sql", "pandas", "matplotlib", "communication"],
        "skills_count": 5,
        "keywords": [],
    }
    result = match(sample_jd, sample_cv)
    print("Match Score:", result["match_score"], "%")
    print("Matched:", result["matched_skills"])
    print("Missing:", result["missing_skills"])
