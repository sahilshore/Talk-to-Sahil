from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import base64
import streamlit as st
import tempfile
from openai import OpenAI
from ai_agent import get_ai_response

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Sahil – AI Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #070f1c !important;
    border-right: 1px solid #0e2a45;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #7dd3fc !important;
}
[data-testid="stSidebar"] hr { border-color: #0e2a45; }

/* ── Main background ── */
.stApp {
    background: linear-gradient(160deg, #060e1a 0%, #091424 60%, #060e1a 100%);
}
.stApp p, .stApp span, .stApp label { color: #cbd5e1; }

/* ── New Chat button ── */
div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #0284c7, #0ea5e9);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    box-shadow: 0 4px 18px rgba(14, 165, 233, 0.4);
    transition: all 0.2s ease;
}
div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8);
    box-shadow: 0 6px 24px rgba(56, 189, 248, 0.55);
    transform: translateY(-1px);
}

/* ── Sidebar conversation buttons ── */
div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: rgba(14, 165, 233, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.3);
    border-radius: 8px;
    font-weight: 500;
}
div[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
    background: rgba(14, 165, 233, 0.22);
}

/* ── Chat input ── */
div[data-testid="stChatInput"] textarea {
    background-color: #0d1f35 !important;
    color: #e2e8f0 !important;
    border: 1px solid #0369a1 !important;
    border-radius: 14px !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    background: transparent;
}

/* ── Toggle ── */
.stToggle label { color: #38bdf8 !important; }

/* ── Title gradient ── */
h2 {
    background: linear-gradient(90deg, #38bdf8, #7dd3fc, #bae6fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Mic record button ── */
[data-testid="stAudioInput"] button:first-of-type {
    width: 56px !important;
    height: 56px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #0284c7, #0ea5e9) !important;
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.55) !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
[data-testid="stAudioInput"] button:first-of-type:hover {
    box-shadow: 0 0 32px rgba(56, 189, 248, 0.75) !important;
    transform: scale(1.06) !important;
}
[data-testid="stAudioInput"] button:first-of-type svg {
    width: 24px !important;
    height: 24px !important;
    color: #ffffff !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #060e1a; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(#0284c7, #0ea5e9);
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ── Autoplay helper ────────────────────────────────────────────
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f'<audio autoplay style="width:100%; margin-top:8px;">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3">'
        f'</audio>',
        unsafe_allow_html=True,
    )

# ── Session state ──────────────────────────────────────────────
if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state.conversations = {
        first_id: {"title": "New Chat", "messages": []}
    }
    st.session_state.current_conv_id = first_id

if "mode" not in st.session_state:
    st.session_state.mode = "voice"

if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None

if "autoplay_audio_path" not in st.session_state:
    st.session_state.autoplay_audio_path = None

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("##    Sahil Agent")

    if st.button("＋  New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.conversations[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_conv_id = new_id
        st.rerun()

    st.markdown("---")
    st.markdown("**Recent**")

    for conv_id in reversed(list(st.session_state.conversations.keys())):
        conv = st.session_state.conversations[conv_id]
        is_active = conv_id == st.session_state.current_conv_id
        if st.button(
            conv["title"],
            key=f"conv_{conv_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_conv_id = conv_id
            st.rerun()

# ── Main area ──────────────────────────────────────────────────
current_conv = st.session_state.conversations[st.session_state.current_conv_id]

col_title, col_toggle = st.columns([5, 1])
with col_title:
    st.markdown("## 🎤 Sahil Khan — Voice Agent")
with col_toggle:
    voice_on = st.toggle("🎙️ Voice", value=(st.session_state.mode == "voice"))
    st.session_state.mode = "voice" if voice_on else "chat"

# ── Message history ────────────────────────────────────────────
for msg in current_conv["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🎤"):
            st.write(msg["content"])
            audio_path = msg.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                if audio_path == st.session_state.autoplay_audio_path:
                    # Autoplay latest response, then clear flag
                    autoplay_audio(audio_path)
                    st.session_state.autoplay_audio_path = None
                else:
                    # Older messages: show a regular player for replay
                    st.audio(audio_path)

# ── Process & respond ──────────────────────────────────────────
def process_and_respond(user_text: str):
    user_text = user_text.strip()
    if not user_text:
        return

    # Auto-title from first message
    if not current_conv["messages"]:
        current_conv["title"] = (
            user_text[:35] + "…" if len(user_text) > 35 else user_text
        )

    current_conv["messages"].append({"role": "user", "content": user_text})

    with st.spinner("Thinking…"):
        ai_text = get_ai_response(user_text)

    # TTS
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        speech_path = f.name

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=ai_text,
    ) as response:
        response.stream_to_file(speech_path)

    current_conv["messages"].append(
        {"role": "assistant", "content": ai_text, "audio_path": speech_path}
    )
    st.session_state.autoplay_audio_path = speech_path
    st.rerun()

# ── Input area ─────────────────────────────────────────────────
if st.session_state.mode == "chat":
    user_input = st.chat_input("Ask me anything…")
    if user_input:
        process_and_respond(user_input)
else:
    audio = st.audio_input("🎙️ Tap to record, tap again to stop")
    if audio:
        audio_bytes = audio.getbuffer().tobytes()
        audio_hash = hash(audio_bytes)

        if audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                tmp_path = f.name

            with st.spinner("Transcribing…"):
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(tmp_path, "rb"),
                    language="en",
                )

            user_text = result.text.strip()
            if user_text:
                process_and_respond(user_text)
