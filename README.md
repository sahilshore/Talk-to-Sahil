# Sahil Khan — AI Voice Agent

> A personalized AI voice agent built for the **100X.inc** assessment. It speaks, listens, and responds **as Sahil Khan** — powered by OpenAI, LangChain, and LangGraph with a ChatGPT-style interface.

---

## Overview

This project is an intelligent voice + chat agent that represents Sahil Khan in real-time conversations. It uses Retrieval-Augmented Generation (RAG) to answer questions about Sahil's background, skills, and experience, and about 100X.inc — with smart routing that decides whether to pull from a knowledge base or search the web live.

---

## Features

- **Voice Mode** — Record audio directly in the browser; Whisper transcribes it, GPT-4o-mini responds, and TTS plays the answer back automatically
- **Chat Mode** — Type questions and receive instant text + audio responses
- **Auto-play Responses** — AI voice plays automatically after each response, no manual click needed
- **ChatGPT-style UI** — Sidebar with full conversation history, multi-session support, and a "New Chat" button
- **Smart RAG Routing** — Queries are intelligently routed to:
  - Sahil's profile PDF (personal questions)
  - 100X company profile PDF (company questions)
  - Tavily web search (real-time / market questions)
- **Conversation Memory** — Maintains context across turns within a session
- **Deep Ocean Dark Theme** — Professional, interview-ready UI design

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **LLM** | OpenAI GPT-4o-mini |
| **Speech-to-Text** | OpenAI Whisper (`whisper-1`) |
| **Text-to-Speech** | OpenAI TTS (`gpt-4o-mini-tts`) |
| **Agent Framework** | LangGraph (`create_react_agent`) |
| **RAG / Embeddings** | LangChain + OpenAI Embeddings + FAISS |
| **PDF Loader** | PyPDF via LangChain |
| **Web Search** | Tavily Search API |
| **Environment** | Python 3.12+ / `python-dotenv` |

---

## Project Structure

```
Voice Agent New/
├── frontend.py           # Streamlit UI — voice/chat interface, session history
├── ai_agent.py           # LangGraph agent — RAG routing, LLM, tools, memory
├── requirements.txt      # Python dependencies
├── .env                  # API keys (not committed)
└── data/
    ├── Sahil_Profile.pdf  # Sahil's background, skills, experience
    └── 100x_profile.pdf   # 100X.inc company information
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Voice Agent New"
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
source venv/Scripts/activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

- Get your OpenAI key at: [platform.openai.com](https://platform.openai.com)
- Get your Tavily key at: [tavily.com](https://tavily.com)

### 5. Add your PDF knowledge base

Place your profile PDFs inside the `data/` folder:

```
data/Sahil_Profile.pdf
data/100x_profile.pdf
```

### 6. Run the app

```bash
streamlit run frontend.py
```

The app will open automatically at `http://localhost:8501`

---

## How It Works

```
User speaks / types
       │
       ▼
  [Whisper STT]  ← voice mode only
       │
       ▼
  Smart Router
  ┌────┴──────────────────────┐
  │                           │
Personal query?         100X query?        Web query?
  │                           │                │
FAISS (Sahil PDF)     FAISS (100X PDF)   Tavily Search
  └────────────────┬──────────┘                │
                   ▼                           │
            GPT-4o-mini  ◄─────────────────────┘
                   │
                   ▼
            AI Response text
                   │
                   ▼
         [OpenAI TTS — auto-plays]
```

---

## Sample Questions It Handles

| Question | Routing |
|---|---|
| What should we know about your life story? | Sahil Profile PDF |
| What is your #1 superpower? | Sahil Profile PDF |
| What are your top 3 areas of growth? | Sahil Profile PDF |
| What misconception do coworkers have about you? | Sahil Profile PDF |
| How do you push your boundaries? | Sahil Profile PDF |
| What is 100X.inc's mission? | 100X Profile PDF |
| What is the current AI hiring market like? | Tavily Web Search |



## Author

**Sahil Khan**
Built with OpenAI · LangChain · LangGraph · Streamlit
