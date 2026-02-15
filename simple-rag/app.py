  #!/bin/env python3
import os
import time
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

# Page configuration with custom theme
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

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main background gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #ffd700, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: gradient 3s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #e0e7ff;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #ffd700;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
        border: 2px dashed #ffd700;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        background: rgba(255,255,255,0.15);
        border-color: #ff6b6b;
        transform: translateY(-2px);
    }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 25px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 10px 30px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input field */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 12px 20px;
        background: rgba(255,255,255,0.9);
        color: #1a202c;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input::placeholder {
    color: #64748b;  /* ← ADD THIS - gray placeholder text */
    opacity: 1;
    }
    
            
    .stTextInput > div > div > input:focus {
        border-color: #ffd700;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Success message */
    .upload-success {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 15px;
        border-radius: 15px;
        color: #1a365d;
        font-weight: 600;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(132, 250, 176, 0.3);
    }
    
    /* Info box */
    .info-box {
        background: rgba(255,255,255,0.1);
        border-left: 4px solid #ffd700;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #e0e7ff;
    }
    
    /* Stats container */
    .stats-container {
        display: flex;
        justify-content: space-around;
        padding: 20px;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        margin: 20px 0;
    }
    
    /* Pulse animation for active status */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-active {
        color: #10b981;
        animation: pulse 2s infinite;
    }
    
    /* Sidebar headers */
    .sidebar-header {
        color: #ffd700;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        
    }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display animated header"""
    st.markdown('<h1 class="main-header">🧠 IntelliDoc AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Intelligent Document Companion Powered by Advanced RAG Technology</p>', unsafe_allow_html=True)
    

def display_stats():
    """Display statistics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Documents Loaded",
            value=len(st.session_state.get("uploaded_files", [])),
            delta="Active" if len(st.session_state.get("uploaded_files", [])) > 0 else "None"
        )
    
    with col2:
        st.metric(
            label="Messages",
            value=len(st.session_state.get("messages", [])) // 2,
            delta="+1" if len(st.session_state.get("messages", [])) > 0 else "0"
        )
    
    with col3:
        total_time = sum(st.session_state.get("processing_times", []))
        st.metric(
            label="⚡ Total Processing",
            value=f"{total_time:.2f}s",
            delta="Fast" if total_time < 10 else "Normal"
        )
    
    with col4:
        status = "🟢 Ready" if st.session_state.get("assistant") else "🔴 Initializing"
        st.metric(
            label="🤖 AI Status",
            value=status,
            delta="Online"
        )


def display_messages():
    """Enhanced message display with better styling"""
    if len(st.session_state["messages"]) > 0:
        st.markdown("---")
        st.subheader("💭 Conversation History")
        
        for i, (msg, is_user) in enumerate(st.session_state["messages"]):
            message(msg, is_user=is_user, key=str(i), avatar_style="avataaars" if is_user else "bottts")
        
        st.session_state["thinking_spinner"] = st.empty()
    else:
        st.info("👋 Upload a document and start asking questions!")


def process_input():
    """Process user input with enhanced feedback"""
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        
        # Add user message immediately
        st.session_state["messages"].append((user_text, True))
        
        # Show thinking animation
        with st.session_state["thinking_spinner"], st.spinner("🤔 Analyzing your question..."):
            start_time = time.time()
            agent_text = st.session_state["assistant"].ask(user_text)
            response_time = time.time() - start_time
        
        # Add AI response
        st.session_state["messages"].append((agent_text, False))
        st.session_state["processing_times"].append(response_time)
        
        # Clear input
        st.session_state["user_input"] = ""


def read_and_save_file():
    """Enhanced file processing with progress tracking"""
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""
    st.session_state["uploaded_files"] = []
    st.session_state["processing_times"] = []

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], st.spinner(f"🔄 Processing {file.name}..."):
            t0 = time.time()
            st.session_state["assistant"].ingest(file_path)
            t1 = time.time()
            processing_time = t1 - t0

        st.session_state["uploaded_files"].append(file.name)
        st.session_state["processing_times"].append(processing_time)
        
        success_msg = f"✅ Successfully processed **{file.name}** in {processing_time:.2f} seconds"
        st.session_state["messages"].append((success_msg, False))
        
        os.remove(file_path)

def sidebar_config():
    """Enhanced sidebar with controls"""
    with st.sidebar:
        st.markdown("### ⚡ Quick Actions")
        
        # Full-width Clear Chat button
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state["messages"] = []
            st.rerun()

        st.markdown("---")
        
        # Tips section
        with st.expander("💡 Pro Tips", expanded=False):
            st.markdown("""
            - **Upload multiple PDFs** for cross-document queries
            - **Adjust temperature** for more creative or precise answers
            - **Use specific questions** for better results
            - **Check document chunks** to optimize retrieval
            """)
        
        # System info
        with st.expander("ℹ️ System Information", expanded=False):
            st.markdown(f"""
            - **Model**: Mistral-7B (Ollama)
            - **Vector DB**: ChromaDB
            - **Embedding**: FastEmbed
            - **Framework**: LangChain
            - **Documents**: {len(st.session_state.get("uploaded_files", []))}
            """)
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 2rem;'>
            <p>🧠 Powered by IntelliDoc AI</p>
        </div>
        """, unsafe_allow_html=True)


def main_content():
    """Main content area"""
    # Display header
    display_header()
    
    # Display stats dashboard
    display_stats()
    
    st.markdown("---")
    
    # File uploader section
    st.markdown("### 📤 Upload Your Documents")
    st.markdown('<div class="info-box">Drag and drop your PDF files here or click to browse. Multiple files supported!</div>', unsafe_allow_html=True)
    
    st.file_uploader(
        "Upload documents",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )
    
    st.session_state["ingestion_spinner"] = st.empty()
    
    # Display uploaded files
    if st.session_state.get("uploaded_files"):
        with st.expander("📁 Uploaded Documents", expanded=True):
            for idx, filename in enumerate(st.session_state["uploaded_files"], 1):
                st.markdown(f"**{idx}.** {filename}")
    
    st.markdown("---")
    
    # Chat interface
    display_messages()
    
    # Input section
    st.markdown("### Ask Anything")
    st.text_input(
        "Type your question here...",
        key="user_input",
        on_change=process_input,
        placeholder="What would you like to know about your documents?",
        label_visibility="collapsed"
    )
    
    # Suggested questions
    if len(st.session_state.get("messages", [])) == 0 and len(st.session_state.get("uploaded_files", [])) > 0:
        st.markdown("#### 💡 Suggested Questions:")
        cols = st.columns(3)
        
        suggestions = [
            "📝 Summarize the main points",
            "🔍 What are the key findings?",
            "📊 Extract important data"
        ]
        
        for col, suggestion in zip(cols, suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state["user_input"] = suggestion.split(" ", 1)[1]
                    process_input()
                    st.rerun()


def page():
    """Main page layout"""
    # Initialize session state
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()
        st.session_state["uploaded_files"] = []
        st.session_state["processing_times"] = []
    
    # Sidebar configuration
    sidebar_config()
    
    # Main content
    main_content()


if __name__ == "__main__":
    page()