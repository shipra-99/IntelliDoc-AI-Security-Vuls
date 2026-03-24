
````markdown
# 🧠 IntelliDoc AI – Local RAG Security Assistant

IntelliDoc AI is a fully local **Retrieval-Augmented Generation (RAG)** system for **document understanding and code vulnerability analysis**.

It allows you to upload PDFs or source code and ask intelligent questions — powered entirely by a **locally running LLM**, with no external API calls.

---

## 🚀 Features

- 📄 Chat with PDF documents  
- 💻 Analyze source code (Java, Python, JS, C/C++)  
- 🔐 Detect potential security vulnerabilities  
- 🧠 RAG with CWE-based knowledge retrieval  
- 🤖 Local LLM inference using Ollama  
- 🔎 Semantic search with vector embeddings  
- 💬 Simple Streamlit chat interface  

---

## 🏗️ Tech Stack

- **Frontend**: Streamlit  
- **LLM**: Ollama (Qwen2.5-Coder)  
- **Embeddings**: FastEmbed  
- **Vector DB**: ChromaDB  
- **Framework**: LangChain  

---

## ⚙️ Setup

```bash
git clone https://github.com/your-username/IntelliDoc-AI-Security-Vuls.git
cd IntelliDoc-AI-Security-Vuls


python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
````

Install Ollama and pull model:

```bash
ollama pull qwen2.5-coder:3b
```

---

## ▶️ Run

```bash
streamlit run app.py
```

Open: [http://localhost:8501](http://localhost:8501)

---

## 📂 How It Works

### 📄 PDF Mode

* Chunk → Embed → Store (ChromaDB)
* Retrieve relevant context → LLM answers

### 💻 Code Analysis Mode

* Upload code file
* Retrieve relevant **CWE knowledge**
* Combine code + retrieved context
* LLM identifies:

  * Vulnerability type (CWE)
  * Location in code
  * Explanation
  * Fix suggestions

---

## 🧠 Key Idea

Instead of relying only on the model, this system uses **RAG to inject external vulnerability knowledge (CWE)**, helping the LLM analyze **unseen code more effectively**.

---

## 🔐 Why Local?

* No data leaves your machine
* Full control over sensitive code
* No API costs
* Works offline

---

## 📁 Structure

```
app.py          # Streamlit UI
rag.py          # RAG + analysis pipeline
chroma_db/      # Document embeddings
chroma_cwe_db/  # CWE knowledge base
```

---

## ⚠️ Note

This is a **research prototype** built to explore how RAG can improve LLM-based security analysis.

---

```
