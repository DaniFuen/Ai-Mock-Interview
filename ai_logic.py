import streamlit as st
import requests
from gtts import gTTS
import io

# -------------------------------------
# Read Gemini API key from secrets.toml
# -------------------------------------

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing in .streamlit/secrets.toml")

# ✅ Updated model + updated endpoint
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _call_gemini(prompt: str) -> str:
    """
    Call Gemini API using updated model (2.5 flash).
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY in secrets")

    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    resp = requests.post(GEMINI_URL, headers=headers, params=params, json=data)

    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text}")

    payload = resp.json()
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Unexpected Gemini response format: {e}\n{payload}")


# ---------- Question generation ----------

def generate_question(
    interview_type,
    role,
    level,
    resume_text="",
    job_text="",
    previous_questions=None,
):
    """
    Generate a new interview question with Gemini 2.5 flash.
    """
    if previous_questions is None:
        previous_questions = []

    previous_block = ""
    if previous_questions:
        joined = "\n".join(f"- {q}" for q in previous_questions)
        previous_block = (
            "These questions were already asked. Do NOT repeat any of them:\n"
            f"{joined}\n"
        )

    prompt = f"""
You are an AI interview system. Generate ONE new interview question.

INTERVIEW TYPE: {interview_type}
ROLE: {role}
LEVEL: {level}

{previous_block}

Resume:
{resume_text}

Job description:
{job_text}

Rules:
- Only one question
- No numbers
- No extra text
"""

    try:
        text = _call_gemini(prompt).strip()
        if not text:
            return "Can you tell me about a recent challenge you faced and how you handled it?"
        return text
    except Exception as e:
        st.error(f"Error generating question from Gemini: {e}")
        return "Can you tell me about a recent challenge you faced and how you handled it?"


# ---------- Feedback ----------

def get_feedback(question: str, answer: str) -> str:
    """
    Give structured feedback with Gemini 2.5 flash.
    """
    prompt = f"""
You are an experienced interviewer.

Question: {question}
Answer: {answer}

Give:
1. Score 1-10
2. What they did well
3. What to improve
4. How to rewrite it better
"""

    try:
        return _call_gemini(prompt).strip()
    except Exception as e:
        st.error(f"Error generating feedback from Gemini: {e}")
        return "Sorry, I could not generate feedback right now. Please try again."


# ---------- Summary ----------

def summarize_session(role: str, interview_type: str, qa_list: list) -> str:
    """
    Full interview summary.
    """
    qa_text = ""
    for i, item in enumerate(qa_list, start=1):
        q = item.get("question", "")
        a = item.get("answer", "")
        f = item.get("feedback", "")
        qa_text += f"\nQuestion {i}:\n{q}\nAnswer:\n{a}\nFeedback:\n{f}\n"

    prompt = f"""
ROLE: {role}
INTERVIEW TYPE: {interview_type}

Full session:
{qa_text}

Make a summary with:
- Overall score
- Top 3 strengths
- Top 3 improvements
- 3 action items for this week
"""

    try:
        return _call_gemini(prompt).strip()
    except Exception as e:
        st.error(f"Error generating summary from Gemini: {e}")
        return "Sorry, I could not generate a summary right now. Please try again."


# ---------- TTS ----------

def question_to_audio_bytes(question: str):
    """
    Convert question text to MP3 using gTTS.
    """
    if not question:
        return None

    try:
        tts = gTTS(text=question, lang="en")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        st.warning(f"Could not generate audio for the question: {e}")
        return None