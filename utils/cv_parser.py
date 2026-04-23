import pdfplumber
import re
import spacy

from utils.jd_parser import SKILL_KEYWORDS, clean_text, extract_skills

# Reuse the same spaCy model
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file using pdfplumber."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_keywords_spacy(text):
    """Use spaCy to extract noun chunks and named entities as additional keywords."""
    doc = nlp(text[:100000])  # cap to avoid memory issues on large CVs
    keywords = set()
    for chunk in doc.noun_chunks:
        token = clean_text(chunk.text)
        if len(token) > 2:
            keywords.add(token)
    for ent in doc.ents:
        token = clean_text(ent.text)
        if len(token) > 2:
            keywords.add(token)
    return list(keywords)


def parse_cv(pdf_path):
    """
    Parse a CV PDF and return a structured dict matching jd_parser output format.

    Args:
        pdf_path: Path to the CV PDF file (str or file-like object).

    Returns:
        dict with keys: raw_text, skills_found, skills_count, keywords.
    """
    raw_text = extract_text_from_pdf(pdf_path)
    skills = extract_skills(raw_text)
    keywords = extract_keywords_spacy(raw_text)

    return {
        "raw_text": raw_text,
        "skills_found": skills,
        "skills_count": len(skills),
        "keywords": keywords,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m utils.cv_parser <path_to_cv.pdf>")
    else:
        result = parse_cv(sys.argv[1])
        print("Skills Found:", result["skills_found"])
        print("Skills Count:", result["skills_count"])
        print("Keyword sample:", result["keywords"][:10])
