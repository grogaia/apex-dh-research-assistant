"""
APEX - Streamlit Frontend

Provides a single compose box with one "Send" action, similar to a
standard chat interface. Every answer is automatically followed by a set
of "Continue with" suggestions for concrete next steps. A follow-up
message carries forward a short summary of the previous turn, so a
question can build on the prior answer (e.g. "go deeper on X") without
starting from zero. Only the immediately preceding turn is carried
forward, not the full conversation history, which keeps token usage
roughly constant regardless of how long the conversation runs.

Run it with:
    streamlit run app.py
"""

import json

import streamlit as st
from rag_backend import index as index_a
from db_b import build_database_b
from answer_engine import answer_question, suggest_next_steps
from design import CUSTOM_CSS, LOGO_ICON_SVG, VERTEX_MARK_HERO

st.set_page_config(page_title="APEX", page_icon="apex_favicon.png")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Maps Reference Library file names to proper, human-readable citations for display.
CITATION_NAMES = {
    "01_foundation_wilkinson_fair_2016.pdf": "Wilkinson et al. (2016) — FAIR Principles",
    "01_foundation_tayler_dataprimer_2022.pdf": "Tayler et al. (2022) — Data Primer",
    "02_analysis_underwood_distant-reading_2017.pdf": "Underwood (2017) — Genealogy of Distant Reading",
    "02_analysis_clement_methodology-dh_2016.pdf": "Clement (2016) — Where Is Methodology in DH?",
    "02_analysis_perkins-roe_genai-research_2024.pdf": "Perkins & Roe (2024) — Generative AI Tools in Academic Research",
    "02_analysis_desapereira_mixed-methods_2019.pdf": "De Sá Pereira (2019) — Mixed Methodological DH",
    "03_hitl_guingrich_belief-offloading_2026.pdf": "Guingrich et al. (2026) — Belief Offloading in Human-AI Interaction",
    "03_hitl_kalai_why-llms-hallucinate_2025.pdf": "Kalai et al. (2025) — Why Language Models Hallucinate",
    "03_hitl_simons_llms-hpss_2025.pdf": "Simons et al. (2025) — LLMs for History, Philosophy, and Sociology of Science",
    "04_communication_sanz-tejeda_genai-reading-writing_2025.pdf": "Sanz-Tejeda et al. (2025) — Impact of GenAI on Academic Reading and Writing",
    "04_communication_zhang_visual-data-storytelling_2022.pdf": "Zhang et al. (2022) — A Visual Data Storytelling Framework",
}


def display_name(file_name):
    """Returns a readable citation for Reference Library files, or the plain
    filename for uploaded Corpus content (which has no citation)."""
    return CITATION_NAMES.get(file_name, file_name)


def render_sources(sources):
    seen = set()
    for db_label, file_name in sources:
        key = (db_label, file_name)
        if key not in seen:
            st.markdown(f'<div class="apex-source"><b>{db_label}</b>: {display_name(file_name)}</div>', unsafe_allow_html=True)
            seen.add(key)


def contextual_query(user_message, history):
    """
    Builds the actual query sent to APEX's retrieval + generation.

    If there's a previous turn, a short summary of it is prepended so the
    system can resolve follow-ups like "go deeper on that" - without
    carrying the FULL conversation (which would grow token usage with
    every turn). Only the last turn is used, keeping cost roughly
    constant regardless of conversation length.

    The raw `user_message` (not this augmented version) is what gets shown
    in the visible chat transcript - this function only affects what the
    model actually receives.
    """
    if not history:
        return user_message
    last = history[-1]
    return (
        f"Earlier in this conversation, the user asked: \"{last['question']}\" "
        f"and APEX answered (summary): \"{last['answer'][:400]}\"\n\n"
        f"Now, continuing that conversation, the user says: {user_message}"
    )


def refresh_next_steps(question_display, answer_text):
    """(Re)generate the automatic 'Continue with' suggestions for a given turn."""
    with st.spinner("Thinking about what comes next..."):
        next_steps, next_step_sources = suggest_next_steps(question_display, answer_text, index_a)
    st.session_state["next_steps"] = next_steps
    st.session_state["next_step_sources"] = next_step_sources


# --- Header ---
st.markdown(
    f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:0.1rem;">'
    f'{LOGO_ICON_SVG}<h1 style="margin:0; font-family:\'Lora\',serif; font-weight:600; '
    f'font-size:42px; color:var(--apex-ink); letter-spacing:-0.01em; line-height:1;">APEX</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="font-family:\'IBM Plex Sans\',sans-serif; font-weight:600; font-size:16px; '
    'letter-spacing:0.04em; text-transform:uppercase; color:var(--apex-muted); margin:0;">'
    'Augmented Project & Execution Engine</div>'
    '<hr style="border:none; border-top:1px solid var(--apex-border); margin:1.8rem 0;">',
    unsafe_allow_html=True,
)

# --- Sidebar: file upload for the Corpus ---
with st.sidebar:
    st.header("Your Corpus")

    if st.session_state.get("upload_error"):
        st.error(st.session_state["upload_error"])
    elif st.session_state.get("index_b") is not None:
        n = len(st.session_state.get("last_upload_names") or [])
        st.success(f"{n} file(s) loaded into your Corpus.")
    else:
        st.caption("No files uploaded yet. APEX will use its curated Reference Library.")

    uploaded_files = st.file_uploader(
        "Upload your project documents",
        type=[
            "pdf", "docx", "xlsx", "xls", "csv", "txt", "md", "xml",
            "pptx", "ppt", "epub",
        ],
        accept_multiple_files=True,
        help=(
            "Supported formats: PDF, Word (.docx), Excel (.xlsx/.xls), CSV, "
            "plain text (.txt), Markdown (.md), XML/TEI (.xml), PowerPoint "
            "(.pptx/.ppt), and EPUB (e-books - useful for digitized historical "
            "books). Note: TEI-XML is read as plain text, so markup tags are "
            "included alongside the content."
        ),
    )

    if uploaded_files:
        current_names = [f.name for f in uploaded_files]
        if st.session_state.get("last_upload_names") != current_names:
            with st.spinner("Reading your documents..."):
                index_b, upload_error = build_database_b(uploaded_files)
                st.session_state["index_b"] = index_b
                st.session_state["last_upload_names"] = current_names
                st.session_state["upload_error"] = upload_error
            st.rerun()  # so the status message above reflects this upload
    else:
        if st.session_state.get("index_b") is not None or st.session_state.get("upload_error") is not None:
            st.session_state["index_b"] = None
            st.session_state["upload_error"] = None
            st.session_state["last_upload_names"] = None
            st.rerun()  # so the status message above reflects the cleared state

    st.markdown("---")
    st.header("Save & Resume")

    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0
    if "input_version" not in st.session_state:
        st.session_state["input_version"] = 0
    if "conversation_saved" not in st.session_state:
        st.session_state["conversation_saved"] = True

    if st.session_state.get("history"):
        conversation_json = json.dumps(st.session_state["history"], ensure_ascii=False, indent=2)
        just_saved = st.download_button(
            "Save conversation",
            data=conversation_json,
            file_name="apex_conversation.json",
            mime="application/json",
            use_container_width=True,
        )
        if just_saved:
            st.session_state["conversation_saved"] = True
        if st.session_state.get("conversation_saved"):
            st.caption("Conversation saved.")
        else:
            st.caption("Unsaved changes.")
    else:
        st.caption("Start a conversation to enable saving.")

    # The dynamic key lets us fully reset this widget (clearing any
    # previously uploaded file) whenever the user starts a new conversation -
    # without it, Streamlit keeps holding onto the old file and would
    # silently reload it again on the next rerun.
    loaded_file = st.file_uploader(
        "Load a saved conversation",
        type=["json"],
        key=f"conversation_uploader_{st.session_state['uploader_version']}",
        help="Load a conversation file previously created with \"Save conversation\" above.",
    )
    if loaded_file is not None and st.session_state.get("loaded_conversation_name") != loaded_file.name:
        try:
            loaded_data = json.loads(loaded_file.getvalue().decode("utf-8"))
            if isinstance(loaded_data, list) and all("question" in t and "answer" in t for t in loaded_data):
                st.session_state["history"] = loaded_data
                st.session_state["loaded_conversation_name"] = loaded_file.name
                st.session_state["conversation_saved"] = True  # just loaded from disk, matches the file
                st.session_state["next_steps"] = None
                st.session_state["next_steps_pending"] = bool(loaded_data)
                st.success(f"Loaded '{loaded_file.name}' - {len(loaded_data)} turn(s).")
                st.rerun()
            else:
                st.error("This file doesn't look like a valid APEX conversation export.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            st.error("Couldn't read this file - is it a valid APEX conversation export?")

    if st.session_state.get("history"):
        if not st.session_state.get("confirm_reset"):
            if st.button("Start a new conversation"):
                st.session_state["confirm_reset"] = True
                st.rerun()
        else:
            if not st.session_state.get("conversation_saved"):
                st.warning("This will permanently delete your current, unsaved conversation.")
            else:
                st.caption("Start a new conversation? Your current one is already saved.")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Yes, start new", use_container_width=True):
                    st.session_state["uploader_version"] += 1  # forces the file uploader to reset
                    for key in ["history", "next_steps", "next_step_sources", "loaded_conversation_name", "confirm_reset"]:
                        st.session_state[key] = None
                    st.session_state["conversation_saved"] = True
                    st.rerun()
            with col_b:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["confirm_reset"] = False
                    st.rerun()

# --- Initialize conversation state (empty by default - see sidebar to resume a saved one) ---
if "history" not in st.session_state or st.session_state["history"] is None:
    st.session_state["history"] = []


def add_turn(question_display, answer_text, sources):
    """Append a turn. Does NOT save to disk automatically, and does NOT
    compute 'Continue with' suggestions yet - that happens right after
    rendering the transcript below, so the answer appears immediately
    instead of the user waiting for both the answer AND the suggestions
    before seeing anything."""
    history = st.session_state["history"]
    if history and history[-1]["question"] == question_display and history[-1]["answer"] == answer_text:
        return  # guards against an accidental duplicate append of the same turn
    history.append({"question": question_display, "answer": answer_text, "sources": sources})
    st.session_state["conversation_saved"] = False
    st.session_state["next_steps"] = None
    st.session_state["next_steps_pending"] = True


# --- Render the conversation so far ---
for turn in st.session_state["history"]:
    st.markdown(f'<div class="apex-turn-question">{turn["question"]}</div>', unsafe_allow_html=True)
    st.write(turn["answer"])
    render_sources(turn["sources"])
    st.markdown('<hr class="apex-turn-divider">', unsafe_allow_html=True)

# --- Compute "Continue with" suggestions AFTER the answer above is already
# rendered, so the user sees the answer right away instead of waiting for
# both the answer and the suggestions together. ---
if st.session_state.get("next_steps_pending") and st.session_state["history"]:
    last_turn = st.session_state["history"][-1]
    refresh_next_steps(last_turn["question"], last_turn["answer"])
    st.session_state["next_steps_pending"] = False

# --- Automatic "Continue with" suggestions - shown right after any answer ---
if st.session_state.get("next_steps"):
    st.markdown("#### Continue with")
    for i, step in enumerate(st.session_state["next_steps"]):
        if st.button(step, key=f"next_step_{i}"):
            index_b = st.session_state.get("index_b")
            with st.spinner("Working on it..."):
                answer_text, sources = answer_question(step, index_a, index_b)
            add_turn(step, answer_text, sources)
            st.rerun()

# --- Compose box: hero treatment when empty, compact once chatting ---
input_key = f"main_input_{st.session_state['input_version']}"

if not st.session_state["history"]:
    hero_html = (
        '<div style="text-align:center; margin: 1.8rem 0 1.8rem 0;">'
        '<div style="width:120px; height:120px; margin:0 auto 1rem auto; position:relative; display:flex; align-items:center; justify-content:center;">'
        '<div style="position:absolute; inset:-14px; border-radius:50%; background:radial-gradient(circle, var(--apex-accent-soft) 0%, transparent 72%); filter: blur(10px);"></div>'
        + VERTEX_MARK_HERO.replace("\n", "") +
        '</div>'
        '<div style="font-family:\'Lora\',serif; font-weight:500; font-size:26px; color:var(--apex-ink);">What would you like help with?</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)
    spacer_l, center, spacer_r = st.columns([1, 3, 1])
    with center:
        user_input = st.text_input(
            "Message",
            placeholder="e.g. 'Help me set up a corpus analysis' or 'Go deeper on the network analysis part'",
            label_visibility="collapsed",
            key=input_key,
        )
        send_clicked = st.button("Send", use_container_width=True)
else:
    st.markdown("#### Or type your own message")
    user_input = st.text_input(
        "Message",
        placeholder="e.g. 'Help me set up a corpus analysis' or 'Go deeper on the network analysis part'",
        label_visibility="collapsed",
        key=input_key,
    )
    col1, col2 = st.columns([1, 3])
    with col1:
        send_clicked = st.button("Send", use_container_width=True)

if send_clicked and not user_input.strip():
    st.warning("Please type a message first.")

if send_clicked and user_input.strip():
    query = contextual_query(user_input, st.session_state["history"])
    index_b = st.session_state.get("index_b")

    with st.spinner("Thinking..."):
        answer_text, sources = answer_question(query, index_a, index_b)
    add_turn(user_input, answer_text, sources)
    st.session_state["input_version"] += 1  # clears the compose box for the next message
    st.rerun()

# --- Quiet footer: short blurb, then more about APEX, tucked out of the way ---
st.markdown(
    '<hr style="border:none; border-top:1px solid var(--apex-border); margin:1.8rem 0;">'
    '<div style="margin:0 0 1.8rem 0;">'
    'APEX guides you through your Digital Humanities project as an ongoing '
    'conversation. Unlike a plain chat tool, it keeps a curated set of DH '
    'methodology sources in mind, works with your own uploaded material, and '
    'always tells you where an answer actually comes from.</div>',
    unsafe_allow_html=True,
)

with st.expander("FAQ"):
    faq = [
        (
            "What makes APEX different from a normal chat tool?",
            "APEX draws on a small set of hand-picked, openly licensed Digital "
            "Humanities sources - not just whatever a model happened to learn "
            "in training. It also applies that methodology specifically to "
            "your own uploaded material, and always tells you where an answer "
            "actually comes from.",
        ),
        (
            "Where does APEX's knowledge come from?",
            "Two places: a curated methodology library (called the Reference Library) covering "
            "DH research design, analysis methods, critical AI use, and "
            "communication - and, if you upload files, your own project "
            "material (your Corpus), which the methodology gets applied to.",
        ),
        (
            "How do I know an answer is trustworthy?",
            "Every answer labels its source: APEX's curated knowledge, your "
            "own documents, or general reasoning. When something isn't "
            "covered by the curated sources, APEX says so explicitly instead "
            "of quietly guessing.",
        ),
        (
            "Does APEX need an internet connection?",
            "No. APEX's language model runs fully locally via Ollama, and its "
            "embeddings and vector database also run on your machine. Nothing "
            "about your conversation is sent to an external server.",
        ),
        (
            "Can I pick up a conversation later?",
            "Yes. Use \"Save conversation\" in the sidebar to download your "
            "conversation as a file, and \"Load a saved conversation\" to bring "
            "it back whenever you want to continue - nothing is saved "
            "automatically without your say-so.",
        ),
    ]
    for i, (question, answer) in enumerate(faq):
        margin = "margin-top:0;" if i == 0 else ""
        st.markdown(f'<div class="apex-turn-question" style="{margin}">{question}</div>', unsafe_allow_html=True)
        st.write(answer)
