import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

HISTORY_FILE = Path("interview_history.json")


def load_history() -> List[Dict[str, Any]]:
    """Load all past interview sessions from JSON file."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_session(session: Dict[str, Any]) -> None:
    """Append one session to the JSON history file."""
    history = load_history()
    history.append(session)

    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_session_record(
    role: str,
    interview_type: str,
    level: str,
    total_questions: int,
    qa_list: List[Dict[str, str]],
    summary_text: str,
) -> Dict[str, Any]:
    """Create a clean dict for one saved interview."""
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "role": role,
        "interview_type": interview_type,
        "level": level,
        "total_questions": total_questions,
        "qa_list": qa_list,
        "summary": summary_text,
    }

