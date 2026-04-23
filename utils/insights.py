import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def build_prompt(gap_analysis):
    """Build the instruction prompt from gap analysis data."""
    matched = ", ".join(gap_analysis["matched_skills"]) or "none"
    missing = ", ".join(gap_analysis["missing_skills"]) or "none"
    score = gap_analysis["match_score"]

    return (
        f"A candidate's CV was compared against a job description.\n\n"
        f"Match score: {score}%\n"
        f"Skills already present: {matched}\n"
        f"Skills missing from CV: {missing}\n\n"
        "Based on this gap analysis, provide 3-5 specific, actionable suggestions "
        "the candidate can act on to improve their CV and better match this job. "
        "Be concise and practical. Return the suggestions as a numbered list."
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

    client = InferenceClient(
        provider="novita",
        api_key=os.getenv("HUGGINGFACE_API_KEY"),
    )

    prompt = build_prompt(gap_analysis)

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-1B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        stream=False,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    sample_gap = {
        "match_score": 42.5,
        "matched_skills": ["python", "sql", "communication"],
        "missing_skills": ["tableau", "aws", "docker"],
    }
    suggestions = generate_suggestions(sample_gap)
    print(suggestions)
