import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"


def build_prompt(gap_analysis):
    """Build the instruction prompt from gap analysis data."""
    matched = ", ".join(gap_analysis["matched_skills"]) or "none"
    missing = ", ".join(gap_analysis["missing_skills"]) or "none"
    score = gap_analysis["match_score"]

    return (
        f"<s>[INST] A candidate's CV was compared against a job description.\n\n"
        f"Match score: {score}%\n"
        f"Skills already present: {matched}\n"
        f"Skills missing from CV: {missing}\n\n"
        "Based on this gap analysis, provide 3-5 specific, actionable suggestions "
        "the candidate can act on to improve their CV and better match this job. "
        "Be concise and practical. Return the suggestions as a numbered list. [/INST]"
    )


def generate_suggestions(gap_analysis):
    """
    Call the Hugging Face Inference API and return AI-generated CV improvement suggestions.

    Args:
        gap_analysis: Output dict from matcher.match(), containing match_score,
                      matched_skills, and missing_skills.

    Returns:
        str: Numbered list of actionable suggestions from the model.

    Raises:
        EnvironmentError: If HUGGINGFACE_API_KEY is not set.
        RuntimeError: If the API call fails.
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "HUGGINGFACE_API_KEY not set. Add it to your .env file."
        )

    prompt = build_prompt(gap_analysis)

    response = requests.post(
        HF_API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False,
            },
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Hugging Face API error {response.status_code}: {response.text}"
        )

    result = response.json()

    # HF returns a list of dicts: [{"generated_text": "..."}]
    if isinstance(result, list) and result:
        return result[0].get("generated_text", "").strip()

    raise RuntimeError(f"Unexpected response format from Hugging Face API: {result}")


if __name__ == "__main__":
    sample_gap = {
        "match_score": 42.5,
        "matched_skills": ["python", "sql", "communication"],
        "missing_skills": ["tableau", "aws", "docker"],
    }
    suggestions = generate_suggestions(sample_gap)
    print(suggestions)
