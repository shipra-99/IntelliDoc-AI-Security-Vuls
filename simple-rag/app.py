#!/bin/env python3
import os
import time
import tempfile
import streamlit as st
from rag import ChatPDF, CODE_EXTENSIONS

st.set_page_config(
    page_title="IntelliDoc AI - Smart Document Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/shipra-99',
        'Report a bug': "https://github.com/shipra-99/IntelliDoc-AI",
        'About': "# IntelliDoc AI\nYour intelligent document companion powered by RAG technology."
    }
)

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%); }
    .main-header {
        font-size: 3.5rem; font-weight: 800;
        background: linear-gradient(120deg, #ffd700, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; text-align: center; padding: 1rem;
        animation: gradient 3s ease infinite; background-size: 200% 200%;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .subtitle { text-align: center; font-size: 1.2rem; color: #e0e7ff; margin-bottom: 2rem; font-weight: 300; }
    .stAlert { border-radius: 15px; border: none; box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #ffd700; }
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px;
        border: 2px dashed #ffd700; transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        background: rgba(255,255,255,0.15); border-color: #ff6b6b; transform: translateY(-2px);
    }
    .stChatMessage { border-radius: 15px; padding: 15px; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton > button {
        border-radius: 25px; border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; font-weight: 600; padding: 10px 30px;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6); }
    .stTextInput > div > div > input {
        border-radius: 25px; border: 2px solid #667eea; padding: 12px 20px;
        background: rgba(255,255,255,0.9); color: #1a202c; transition: all 0.3s ease;
    }
    .stTextInput > div > div > input::placeholder { color: #64748b; opacity: 1; }
    .stTextInput > div > div > input:focus { border-color: #ffd700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.5); }
    .info-box {
        background: rgba(255,255,255,0.1); border-left: 4px solid #ffd700;
        padding: 15px; border-radius: 8px; margin: 10px 0; color: #e0e7ff;
    }
    .sidebar-header { color: #ffd700; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)


def display_header():
    st.markdown('<h1 class="main-header">🧠 IntelliDoc AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Intelligent Document Companion Powered by Advanced RAG Technology</p>', unsafe_allow_html=True)


def display_stats():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 Documents Loaded", len(st.session_state.get("uploaded_files", [])),
                  delta="Active" if st.session_state.get("uploaded_files") else "None")
    with col2:
        st.metric("💬 Messages", len(st.session_state.get("messages", [])) // 2,
                  delta="+1" if st.session_state.get("messages") else "0")
    with col3:
        total_time = sum(st.session_state.get("processing_times", []))
        st.metric("⚡ Total Processing", f"{total_time:.2f}s",
                  delta="Fast" if total_time < 10 else "Normal")
    with col4:
        status = "🟢 Ready" if st.session_state.get("assistant") else "🔴 Initializing"
        st.metric("🤖 AI Status", status, delta="Online")


def display_messages():
    if st.session_state["messages"]:
        st.markdown("---")
        st.subheader("💭 Conversation History")
        for msg, is_user in st.session_state["messages"]:
            with st.chat_message("user" if is_user else "assistant"):
                st.write(msg)
        st.session_state["thinking_spinner"] = st.empty()
    else:
        st.info("👋 Upload a PDF or Java/Python source file and start asking questions!")


def process_input():
    if st.session_state["user_input"] and st.session_state["user_input"].strip():
        user_text = st.session_state["user_input"].strip()
        st.session_state["messages"].append((user_text, True))

        with st.session_state["thinking_spinner"], st.spinner("🔍 Analyzing for vulnerabilities..."):
            t0 = time.time()
            agent_text = st.session_state["assistant"].ask(user_text)
            response_time = time.time() - t0

        st.session_state["messages"].append((agent_text, False))
        st.session_state["processing_times"].append(response_time)
        st.session_state["user_input"] = ""


def read_and_save_file():
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    st.session_state["uploaded_files"] = []
    st.session_state["processing_times"] = []

    for file in st.session_state["file_uploader"]:
        ext = "." + file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        suffix = ext if ext else ".tmp"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"🔄 Processing {file.name}..."):
            t0 = time.time()
            st.session_state["assistant"].ingest(file_path)
            t1 = time.time()

        st.session_state["uploaded_files"].append(file.name)
        st.session_state["processing_times"].append(t1 - t0)
        st.session_state["messages"].append(
            (f"✅ Successfully processed **{file.name}** in {t1 - t0:.2f}s", False)
        )
        os.remove(file_path)


def sidebar_config():
    with st.sidebar:
        st.markdown("### ⚡ Quick Actions")

        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state["messages"] = []
            st.rerun()

        st.markdown("---")

        with st.expander("💡 Pro Tips", expanded=False):
            st.markdown("""
            - **Upload Java files** directly for vulnerability analysis
            - **Ask specific questions** like *"Which methods are vulnerable?"*
            - **Upload CWE-Bench-Java samples** to replicate the paper's experiment
            - **Compare results** with and without RAG context
            """)

        with st.expander("ℹ️ System Information", expanded=False):
            st.markdown(f"""
            - **Model**: CodeLlama-7B (Ollama)
            - **Vector DB**: ChromaDB
            - **Embedding**: FastEmbed
            - **Framework**: LangChain
            - **Supported files**: PDF, Java, Python, JS, C/C++
            - **Documents loaded**: {len(st.session_state.get("uploaded_files", []))}
            """)

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 2rem;'>
            <p>🧠 Powered by IntelliDoc AI</p>
        </div>
        """, unsafe_allow_html=True)


def main_content():
    display_header()
    display_stats()
    st.markdown("---")

    st.markdown("### 📤 Upload Your Documents")
    st.markdown(
        '<div class="info-box">Upload PDF documents <b>or source code files</b> (.java, .py, .js, .c, .cpp) for vulnerability analysis!</div>',
        unsafe_allow_html=True
    )

    # Accept PDFs and source code files
    accepted_types = ["pdf", "java", "py", "js", "ts", "c", "cpp", "cs"]
    st.file_uploader(
        "Upload documents",
        type=accepted_types,
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    st.session_state["ingestion_spinner"] = st.empty()

    if st.session_state.get("uploaded_files"):
        with st.expander("📁 Uploaded Files", expanded=True):
            for idx, fname in enumerate(st.session_state["uploaded_files"], 1):
                st.markdown(f"**{idx}.** {fname}")

    st.markdown("---")
    display_messages()

    st.markdown("### 🔍 Ask Anything")
    st.text_input(
        "Type your question here...",
        key="user_input",
        on_change=process_input,
        placeholder="e.g. Which methods are vulnerable? What type of vulnerability is present?",
        label_visibility="collapsed"
    )

    # Security-focused suggested questions
    if not st.session_state.get("messages") and st.session_state.get("uploaded_files"):
        st.markdown("#### 💡 Suggested Questions:")
        cols = st.columns(3)
        suggestions = [
            "🔐 Which methods are vulnerable?",
            "🐛 What type of vulnerability is present?",
            "🛠️ How should this vulnerability be fixed?",
        ]
        for col, suggestion in zip(cols, suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state["user_input"] = suggestion.split(" ", 1)[1]
                    process_input()
                    st.rerun()


def page():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "assistant" not in st.session_state:
        st.session_state["assistant"] = ChatPDF()
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []
    if "processing_times" not in st.session_state:
        st.session_state["processing_times"] = []

    sidebar_config()
    main_content()


if __name__ == "__main__":
    page()