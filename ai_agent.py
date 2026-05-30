import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

# =====================================================
# LOAD VECTOR STORE FUNCTION  ✅ ADD THIS
# =====================================================

def load_vectorstore(path: str):
    loader = PyPDFLoader(path)
    docs = loader.load_and_split()
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(docs, embeddings)

# =====================================================
# LOAD VECTOR STORES (TWO PDFs)
# =====================================================

@st.cache_resource
def init_vectorstores():
    sahil_db = load_vectorstore("data/sahil_profile.pdf")
    x100_db = load_vectorstore("data/100x_profile.pdf")
    return sahil_db, x100_db

SAHIL_DB, X100_DB = init_vectorstores()

# =====================================================
# MEMORY (LIMITED TO SAVE TOKENS)
# =====================================================

CHAT_HISTORY = InMemoryChatMessageHistory()
MAX_HISTORY_MESSAGES = 4

# =====================================================
# TOOLS
# =====================================================

tavily_tool = TavilySearch(max_results=3)

# =====================================================
# SMART ROUTING FUNCTIONS
# =====================================================

def is_about_me(query: str) -> bool:
    keywords = [
        "you", "your", "sahil", "background", "education",
        "skills", "experience", "life", "career", "resume"
    ]
    q = query.lower()
    return any(k in q for k in keywords)


def is_about_100x(query: str) -> bool:
    keywords = [
        "100x", "company", "startup", "nik shah",
        "founder", "mission", "culture", "role"
    ]
    q = query.lower()
    return any(k in q for k in keywords)


def needs_web_search(query: str) -> bool:
    keywords = [
        "current", "today", "latest", "market",
        "news", "trend", "hiring", "salary"
    ]
    q = query.lower()
    return any(k in q for k in keywords)

# =====================================================
# SYSTEM PROMPT (SHORT ANSWERS)
# =====================================================

SYSTEM_PROMPT = """
You are Sahil Khan.

CRITICAL IDENTITY RULE:
- Never say you are an AI, model, assistant, or chatbot.
- You are Sahil Khan, speaking directly in first person.

LANGUAGE RULE (MANDATORY):
- Always respond in clear, professional ENGLISH.
- Do NOT change language based on user input.
- Do NOT translate or switch languages unless the user explicitly asks
  (for example: "reply in Hindi" or "translate this to Urdu").

RESPONSE STYLE:
- Keep answers short and impactful (3–5 lines max).
- Be confident, clear, and human.
- Do NOT over-explain.
- Summarize first; expand only if explicitly asked.

CONTENT RULES:
1. Questions about me → use my background context.
2. Questions about 100x → use company context.
3. Situational or behavioral questions → answer like a thoughtful human.
4. Current or market-related questions → use web search only if needed.
5. Clarity > completeness.
"""


# =====================================================
# MAIN FUNCTION
# =====================================================

def get_ai_response(user_query: str) -> str:

    # ---------- CONDITIONAL RAG ----------
    context = ""

    if is_about_me(user_query):
        retriever = SAHIL_DB.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(user_query)
        context = "\n".join(d.page_content for d in docs)

    elif is_about_100x(user_query):
        retriever = X100_DB.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(user_query)
        context = "\n".join(d.page_content for d in docs)

    # ---------- LLM ----------
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=180
    )

    # ---------- CONDITIONAL TOOLS ----------
    tools = [tavily_tool] if needs_web_search(user_query) else []

    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    # ---------- MESSAGE BUILD ----------
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    if context:
        messages.append(
            SystemMessage(content=f"Relevant context:\n{context}")
        )

    messages += CHAT_HISTORY.messages[-MAX_HISTORY_MESSAGES:]
    messages.append(HumanMessage(content=user_query))

    # ---------- RUN AGENT ----------
    response = agent.invoke({"messages": messages})
    ai_text = response["messages"][-1].content

    # ---------- UPDATE MEMORY ----------
    CHAT_HISTORY.add_message(HumanMessage(content=user_query))
    CHAT_HISTORY.add_message(AIMessage(content=ai_text))

    return ai_text
