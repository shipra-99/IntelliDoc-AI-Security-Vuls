# 🧠 IntelliDoc AI – Local RAG Document Assistant

IntelliDoc AI is a fully local **Retrieval-Augmented Generation (RAG)** application that lets you upload PDF documents and ask intelligent questions about them using a locally running LLM.

Built with **Streamlit + LangChain + Ollama + ChromaDB**, it runs entirely on your machine — no external API calls required.

---

## 🚀 Features

- 📄 Upload and chat with multiple PDF documents  
- 🔎 Semantic search using vector embeddings  
- 🤖 Local LLM inference via Ollama  
- 🧠 Retrieval-Augmented Generation (RAG) pipeline  
- 💬 Clean Streamlit chat interface  
- 💾 Persistent vector store (ChromaDB)  

---

## 🏗️ Tech Stack

- **Frontend**: Streamlit  
- **LLM**: Ollama (Qwen2.5 / Mistral supported)  
- **Embeddings**: FastEmbed  
- **Vector Database**: ChromaDB  
- **Framework**: LangChain  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/intellidoc-ai.git
cd intellidoc-ai
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Mac/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Install & Setup Ollama

Download from:

https://ollama.com

Pull a model:

```bash
ollama pull qwen2.5
```

(Optional alternative)

```bash
ollama pull mistral
```

Ensure Ollama is running in the background.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

Open in browser:

```
http://localhost:8501
```

---

## 📂 How It Works

1. Upload a PDF  
2. Text is split into chunks  
3. Chunks are embedded using FastEmbed  
4. Stored in ChromaDB  
5. User query retrieves relevant chunks  
6. Context + Question → LLM → Final Answer  

---

## 📁 Project Structure

```
.
├── app.py
├── rag.py
├── requirements.txt
├── chroma_db/
└── README.md
```

---

## 🔐 Why Local RAG?

- No API costs  
- Full data privacy  
- Works offline  
- Fully customizable  
- Ideal for experimentation & research  

---
