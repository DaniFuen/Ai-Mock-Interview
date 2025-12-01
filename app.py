import streamlit as st
from streamlit_mic_recorder import speech_to_text
from PIL import Image

from ai_logic import (
    generate_question,
    get_feedback,
    summarize_session,
    question_to_audio_bytes,
)
from storage import load_history, save_session, build_session_record


# ---------- Styling ----------

def add_styles():
    st.markdown(
        """
        <style>
            /* Overall background */
            .stApp {
                background: radial-gradient(circle at top, #0b1120 0, #020617 45%, #000 100%);
            }

            /* Make almost all text white by default */
            body, .stApp, .stMarkdown, .stText, .stCaption,
            .stSelectbox label, .stSlider label, .stTextInput label,
            .stTextArea label {
                color: #ffffff !important;
            }

            /* Sidebar dark theme */
            [data-testid="stSidebar"] {
                background: #020617;
                color: #ffffff;
                border-right: 1px solid rgba(148, 163, 184, 0.3);
            }
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] div {
                color: #ffffff !important;
            }

            /* Main content card */
            .main-card {
                max-width: 1100px;
                margin: 1.5rem auto 2.5rem auto;
                padding: 1.8rem 2.2rem;
                background: #020617;
                border-radius: 1.5rem;
                box-shadow: 0 24px 60px rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(129, 140, 248, 0.5);
                color: #ffffff;
            }

            /* Make all text inside the main card white */
            .main-card p,
            .main-card span,
            .main-card label,
            .main-card h1,
            .main-card h2,
            .main-card h3,
            .main-card h4,
            .main-card h5 {
                color: #ffffff !important;
            }

            .hero-title {
                font-size: 2.3rem;
                font-weight: 700;
                color: #f9fafb;
                margin-bottom: 0.15rem;
            }

            .hero-subtitle {
                font-size: 0.98rem;
                color: #e5e7eb;
                margin-bottom: 0.9rem;
            }

            .pill {
                display: inline-block;
                padding: 0.2rem 0.7rem;
                margin-right: 0.35rem;
                border-radius: 999px;
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                background: #020617;
                color: #e5e7eb;
                border: 1px solid #1f2937;
            }

            .pill-primary {
                background: linear-gradient(90deg, #6366f1, #a855f7);
                color: white;
                border-color: transparent;
            }

            .section-label {
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.09em;
                color: #e5e7eb;
                margin-bottom: 0.2rem;
            }

            /* Zoom-style fake video frame */
            .zoom-frame {
                background: radial-gradient(circle at top, #020617 0, #020617 40%, #020617 100%);
                border-radius: 1.2rem;
                border: 1px solid rgba(148, 163, 184, 0.35);
                padding: 1rem 1.2rem;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 320px;
            }

            .zoom-header {
                display: flex;
                align-items: center;
                gap: 0.8rem;
                margin-bottom: 0.8rem;
            }

            .zoom-avatar {
                width: 70px;
                height: 70px;
                border-radius: 999px;
                background: linear-gradient(135deg, #6366f1, #a855f7);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.2rem;
                color: white;
                font-weight: 700;
            }

            .zoom-name-role {
                display: flex;
                flex-direction: column;
            }
            .zoom-name {
                font-weight: 600;
                color: #f9fafb;
            }
            .zoom-role {
                font-size: 0.8rem;
                color: #ffffff;  /* interview role text white */
            }

            .zoom-status {
                font-size: 0.8rem;
                color: #e5e7eb;
                margin-top: 0.4rem;
            }

            .mic-round {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 60px;
                height: 60px;
                border-radius: 999px;
                background: linear-gradient(135deg, #6366f1, #a855f7);
                color: white;
                font-size: 1.6rem;
                margin-top: 0.4rem;
            }

            /* Make labels white */
            .stTextArea label,
            .stTextInput label,
            .stSelectbox label,
            .stSlider label,
            .stAudio label {
                color: #ffffff !important;
            }

            /* Make the textarea dark with white text */
            textarea {
                background-color: #020617 !important;
                color: #ffffff !important;
                border: 1px solid #4f46e5 !important;
                border-radius: 0.75rem !important;
            }
            textarea::placeholder {
                color: #e5e7eb !important;
            }

            /* 🔮 Purple gradient "bars" for Mode, Target role, Difficulty, etc. */

            /* Text input (Target role) */
            .stTextInput input {
                background: linear-gradient(90deg, #6366f1, #a855f7) !important;
                color: #ffffff !important;
                border-radius: 0.75rem !important;
                border: none !important;
            }
            .stTextInput input::placeholder {
                color: #f9fafb !important;
            }

            /* Select boxes (Mode, Difficulty) */
            .stSelectbox > div > div {
                background: linear-gradient(90deg, #6366f1, #a855f7) !important;
                color: #ffffff !important;
                border-radius: 0.75rem !important;
                border: none !important;
            }

            /* Radio container (Interview type) - keep background dark */
            .stRadio > div {
                background: #020617 !important;
                border-radius: 0.75rem !important;
                padding: 0.3rem 0.6rem !important;
                border: 1px solid #4f46e5 !important;
            }

            /* ⭐ "Interview type" LABEL text white */
            .stRadio > label {
                color: #ffffff !important;
                opacity: 1 !important;
            }

            /* ⭐ Interview type OPTIONS text white ("Behavioral", etc.) */
            .stRadio div[role="radiogroup"] label,
            .stRadio div[role="radiogroup"] p,
            .stRadio div[role="radiogroup"] span {
                color: #ffffff !important;
                opacity: 1 !important;
            }

            /* Slider value text */
            .stSlider label, .stSlider span {
                color: #ffffff !important;
            }

            /* Audio player "bar" */
            audio {
                background: linear-gradient(90deg, #6366f1, #a855f7) !important;
                border-radius: 0.75rem !important;
            }

            /* Purple gradient buttons everywhere */
            button {
                background: linear-gradient(90deg, #6366f1, #a855f7) !important;
                color: white !important;
                border: none !important;
                padding: 0.6rem 1.2rem !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                transition: 0.2s ease-in-out !important;
            }
            button:hover {
                background: linear-gradient(90deg, #4f46e5, #9333ea) !important;
                transform: scale(1.03) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------- State helpers ----------

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "Interview"  # Interview or History

    if "stage" not in st.session_state:
        st.session_state.stage = "setup"  # setup, interview, summary

    if "role" not in st.session_state:
        st.session_state.role = ""

    if "interview_type" not in st.session_state:
        st.session_state.interview_type = "Behavioral"

    if "mode" not in st.session_state:
        st.session_state.mode = "Standard mock"  # Quick / Standard / Deep

    if "level" not in st.session_state:
        st.session_state.level = "beginner"

    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 3

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    if "job_text" not in st.session_state:
        st.session_state.job_text = ""

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "current_question" not in st.session_state:
        st.session_state.current_question = ""

    if "current_answer" not in st.session_state:
        st.session_state.current_answer = ""

    if "current_feedback" not in st.session_state:
        st.session_state.current_feedback = ""

    if "qa_list" not in st.session_state:
        st.session_state.qa_list = []

    if "overall_summary" not in st.session_state:
        st.session_state.overall_summary = ""

    if "error" not in st.session_state:
        st.session_state.error = ""

    # 👇 track previously asked questions to avoid repeats
    if "previous_questions" not in st.session_state:
        st.session_state.previous_questions = []


def reset_interview():
    st.session_state.stage = "setup"
    st.session_state.role = ""
    st.session_state.interview_type = "Behavioral"
    st.session_state.mode = "Standard mock"
    st.session_state.level = "beginner"
    st.session_state.total_questions = 3
    st.session_state.resume_text = ""
    st.session_state.job_text = ""
    st.session_state.current_index = 0
    st.session_state.current_question = ""
    st.session_state.current_answer = ""
    st.session_state.current_feedback = ""
    st.session_state.qa_list = []
    st.session_state.overall_summary = ""
    st.session_state.error = ""
    st.session_state.previous_questions = []


# ---------- Logic ----------

def start_interview():
    if not st.session_state.role.strip():
        st.warning("Please enter a target role.")
        return

    try:
        st.session_state.error = ""
        st.session_state.current_index = 1
        st.session_state.previous_questions = []

        # First question, with no previous questions
        q = generate_question(
            interview_type=st.session_state.interview_type,
            role=st.session_state.role,
            level=st.session_state.level,
            resume_text=st.session_state.resume_text,
            job_text=st.session_state.job_text,
            previous_questions=st.session_state.previous_questions,
        )
        st.session_state.current_question = q
        st.session_state.previous_questions.append(q)

        st.session_state.current_answer = ""
        st.session_state.current_feedback = ""
        st.session_state.qa_list = []
        st.session_state.overall_summary = ""
        st.session_state.stage = "interview"
    except Exception as e:
        st.session_state.error = f"Error starting interview: {e}"


def save_current_qa():
    if not st.session_state.current_question:
        return
    if not st.session_state.current_answer.strip():
        return

    st.session_state.qa_list.append(
        {
            "question": st.session_state.current_question,
            "answer": st.session_state.current_answer,
            "feedback": st.session_state.current_feedback,
        }
    )


def go_next_question():
    save_current_qa()

    if st.session_state.current_index >= st.session_state.total_questions:
        st.session_state.stage = "summary"
        return

    try:
        st.session_state.error = ""
        # current question is already in previous_questions from start_interview()

        st.session_state.current_index += 1
        q = generate_question(
            interview_type=st.session_state.interview_type,
            role=st.session_state.role,
            level=st.session_state.level,
            resume_text=st.session_state.resume_text,
            job_text=st.session_state.job_text,
            previous_questions=st.session_state.previous_questions,
        )
        st.session_state.current_question = q
        st.session_state.previous_questions.append(q)

        st.session_state.current_answer = ""
        st.session_state.current_feedback = ""
    except Exception as e:
        st.session_state.error = f"Error getting next question: {e}"


def create_overall_summary():
    if not st.session_state.qa_list:
        st.warning("No answers to summarize.")
        return

    try:
        st.session_state.error = ""
        st.session_state.overall_summary = summarize_session(
            role=st.session_state.role,
            interview_type=st.session_state.interview_type,
            qa_list=st.session_state.qa_list,
        )
    except Exception as e:
        st.session_state.error = f"Error creating summary: {e}"


# ---------- UI sections ----------

def render_sidebar():
    # Logo + title
    st.sidebar.markdown(
        """
        <div style="display:flex; justify-content: space-between; align-items:center; margin-bottom:0.75rem;">
            <div style="font-weight:700; font-size:1.1rem;">AI Mock Interviewer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logo image (only in sidebar)
    try:
        st.sidebar.image("assets/hero.png", use_column_width=True)
    except Exception:
        st.sidebar.write("")

    st.sidebar.markdown(
        "Use your **voice** to practice interviews and get instant feedback."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Navigation**")
    st.session_state.page = st.sidebar.radio(
        "Page",
        ["Interview", "History"],
        index=0 if st.session_state.page == "Interview" else 1,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Session status**")
    st.sidebar.write(f"Stage: {st.session_state.stage}")
    if st.session_state.stage != "setup":
        st.sidebar.write(
            f"Question {st.session_state.current_index} "
            f"of {st.session_state.total_questions}"
        )

    st.sidebar.markdown("---")
    if st.sidebar.button("Reset current interview"):
        reset_interview()


def render_setup():
    st.markdown('<div class="section-label">Step 1 · Configure</div>', unsafe_allow_html=True)
    st.subheader("Set up your voice interview 🎯")

    col_left = st.container()

    with col_left:
        # Mode
        st.session_state.mode = st.selectbox(
            "Mode",
            ["Quick drill", "Standard mock", "Deep session"],
            index=["Quick drill", "Standard mock", "Deep session"].index(
                st.session_state.mode
            ),
            help="Quick drill: 1–2 questions · Standard: 3–5 · Deep: 6–10",
        )

        st.session_state.role = st.text_input(
            "Target role",
            value=st.session_state.role,
            placeholder="For example: Junior Python Developer",
        )

        st.session_state.interview_type = st.radio(
            "Interview type",
            ["Behavioral", "Professional", "Resume-based"],
            index=["Behavioral", "Professional", "Resume-based"].index(
                st.session_state.interview_type
                if st.session_state.interview_type in
                ["Behavioral", "Professional", "Resume-based"]
                else "Behavioral"
            ),
            horizontal=True,
        )

        st.session_state.level = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(
                st.session_state.level
            ),
        )

        # Suggest number of questions from mode
        mode_defaults = {
            "Quick drill": 2,
            "Standard mock": 4,
            "Deep session": 8,
        }
        suggested = mode_defaults.get(st.session_state.mode, 4)

        current_default = (
            st.session_state.total_questions
            if st.session_state.total_questions
            else suggested
        )

        st.session_state.total_questions = st.slider(
            "Number of questions",
            min_value=1,
            max_value=10,
            value=current_default,
            help=f"Suggested for {st.session_state.mode}: {suggested} questions",
        )

        with st.expander("Optional: Paste your resume text"):
            st.session_state.resume_text = st.text_area(
                "Resume text",
                value=st.session_state.resume_text,
                height=110,
            )

        with st.expander("Optional: Paste job description"):
            st.session_state.job_text = st.text_area(
                "Job description",
                value=st.session_state.job_text,
                height=110,
            )

        if st.button("Start voice interview 🎤"):
            start_interview()

        if st.session_state.error:
            st.error(st.session_state.error)


def render_interview():
    st.markdown('<div class="section-label">Step 2 · Practice</div>', unsafe_allow_html=True)
    st.subheader("Live interview view 🎥")

    col_left, col_right = st.columns([1.1, 1.9])

    # LEFT SIDE: Zoom-style AI interviewer panel
    with col_left:
        # AI frame with question text inside
        st.markdown(
            f"""
            <div class="zoom-frame">
              <div>
                <div class="zoom-header">
                  <div class="zoom-avatar">AI</div>
                  <div class="zoom-name-role">
                    <div class="zoom-name">AI Interviewer</div>
                    <div class="zoom-role">{st.session_state.role or "Candidate Interview"}</div>
                  </div>
                </div>
                <div style="font-size:0.9rem; color:#e5e7eb; margin-bottom:0.7rem;">
                  {st.session_state.current_question or "No question yet."}
                </div>
              </div>
              <div>
            """,
            unsafe_allow_html=True,
        )

        # Question audio player inside the zoom frame
        st.markdown("**Listen to the question:**")
        audio_bytes = question_to_audio_bytes(st.session_state.current_question)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.caption("No question yet.")

        st.markdown(
            """
                <div class="zoom-status">
                  Status: Ready · Answer out loud or by typing on the right.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # RIGHT SIDE: record, answer box, buttons, feedback
    with col_right:
        st.caption(
            f"Mode: {st.session_state.mode} · "
            f"Type: {st.session_state.interview_type} · "
            f"Level: {st.session_state.level} · "
            f"Question {st.session_state.current_index} of {st.session_state.total_questions}"
        )

        # Record your answer ABOVE the answer box
        st.markdown("#### 🎙️ Record your answer")
        recorded_text = speech_to_text(
            language="en",
            use_container_width=True,
            just_once=True,
            key="answer_recorder",
        )
        if recorded_text:
            st.session_state.current_answer = recorded_text

        st.markdown("### Your answer (edit if needed)")
        st.session_state.current_answer = st.text_area(
            "Answer",
            value=st.session_state.current_answer,
            height=200,
        )

        col3, col4 = st.columns(2)
        with col3:
            if st.button("Get feedback ⭐"):
                if not st.session_state.current_answer.strip():
                    st.warning("Please answer first.")
                else:
                    try:
                        st.session_state.error = ""
                        st.session_state.current_feedback = get_feedback(
                            st.session_state.current_question,
                            st.session_state.current_answer,
                        )
                    except Exception as e:
                        st.session_state.error = f"Error getting feedback: {e}"

        with col4:
            if st.button("Next question ➡️"):
                go_next_question()

        if st.session_state.current_feedback:
            st.markdown("### AI feedback")
            st.write(st.session_state.current_feedback)

        if st.session_state.error:
            st.error(st.session_state.error)


def render_summary():
    st.markdown('<div class="section-label">Step 3 · Review</div>', unsafe_allow_html=True)
    st.subheader("Overall rating and feedback 📝")

    if not st.session_state.qa_list:
        st.info("No answers recorded yet.")
        return

    for i, item in enumerate(st.session_state.qa_list, start=1):
        st.markdown(f"#### Question {i}")
        st.write(item["question"])
        st.markdown("**Your answer:**")
        st.write(item["answer"])
        if item.get("feedback"):
            st.markdown("**Feedback:**")
            st.write(item["feedback"])
        st.markdown("---")

    if not st.session_state.overall_summary:
        if st.button("Generate overall rating 🧠"):
            create_overall_summary()

    if st.session_state.overall_summary:
        st.markdown("### Overall summary and score")
        st.write(st.session_state.overall_summary)

    if st.button("Save this interview to history 💾"):
        record = build_session_record(
            role=st.session_state.role,
            interview_type=st.session_state.interview_type,
            level=st.session_state.level,
            total_questions=st.session_state.total_questions,
            qa_list=st.session_state.qa_list,
            summary_text=st.session_state.overall_summary,
        )
        save_session(record)
        st.success("Interview saved to history.")

    if st.button("Start a new interview"):
        reset_interview()

    if st.session_state.error:
        st.error(st.session_state.error)


def render_history():
    st.markdown('<div class="section-label">History</div>', unsafe_allow_html=True)
    st.subheader("Past interview sessions 📚")

    history = load_history()
    if not history:
        st.info("No saved sessions yet.")
        return

    for i, session in enumerate(history, start=1):
        label = (
            f"Session {i} – {session['timestamp']} – "
            f"{session['role']} ({session['interview_type']}, {session['level']})"
        )
        with st.expander(label):
            st.markdown(f"**Role:** {session['role']}")
            st.markdown(f"**Type:** {session['interview_type']}")
            st.markdown(f"**Level:** {session['level']}")
            st.markdown(f"**Questions:** {session['total_questions']}")

            st.markdown("---")
            for j, item in enumerate(session["qa_list"], start=1):
                st.markdown(f"**Question {j}:** {item['question']}")
                st.markdown("Your answer:")
                st.write(item["answer"])
                if item.get("feedback"):
                    st.markdown("Feedback:")
                    st.write(item["feedback"])
                st.markdown("---")

            if session.get("summary"):
                st.markdown("**Final summary:**")
                st.write(session["summary"])


def main():
    st.set_page_config(
        page_title="AI Voice Interviewer",
        page_icon="🎤",
        layout="wide",
    )

    add_styles()
    init_state()
    render_sidebar()

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown('<div class="hero-title">AI Voice Interviewer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">'
        'Practice realistic mock interviews in dark mode with voice input, '
        ' and saved history.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<span class="pill pill-primary">Live Practice</span>'
        '<span class="pill">Behavioral</span>'
        '<span class="pill">Professional</span>'
        '<span class="pill">Resume-based</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if st.session_state.page == "Interview":
        if st.session_state.stage == "setup":
            render_setup()
        elif st.session_state.stage == "interview":
            render_interview()
        elif st.session_state.stage == "summary":
            render_summary()
        else:
            reset_interview()
    else:
        render_history()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
