from langchain_core.globals import set_verbose, set_debug
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.utils import filter_complex_metadata

from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

set_debug(True)
set_verbose(True)

CODE_EXTENSIONS = {".java", ".py", ".js", ".ts", ".c", ".cpp", ".cs"}

# Path to your pre-loaded CWE knowledge base PDF
CWE_PDFS = ["cwe022.pdf", "cwe078.pdf"] 
CWE_DB_PATH  = "chroma_cwe_db"


class ChatPDF:

    def __init__(self, llm_model: str = "qwen2.5-coder:3b"):
        self.model = ChatOllama(model=llm_model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)

        # Prompt combines RAG-retrieved CWE knowledge + full code
        self.prompt = ChatPromptTemplate([
            ("system", """You are a security expert analyzing Java code for vulnerabilities.

You have been provided with two inputs:
1. VULNERABILITY KNOWLEDGE (retrieved from CWE database): describes known vulnerability patterns
2. CODE TO ANALYZE: the actual Java source code

Use the CWE knowledge to identify whether the code contains matching vulnerability patterns.
Pay special attention to PATH TRAVERSAL (CWE-022): file paths built from zip entry names without validation.

For EACH vulnerability found, specify:
1. Vulnerability type and CWE number
2. Exact method name and class name
3. The vulnerable line/pattern
4. Why it is exploitable
5. How to fix it"""),
            ("human", """--- VULNERABILITY KNOWLEDGE (from CWE database via RAG) ---
{cwe_context}

--- JAVA CODE TO ANALYZE ---
{code_context}

Question: {question}"""),
        ])

        self.vector_store = None      # for uploaded PDFs
        self.cwe_store = None         # for CWE knowledge base
        self.full_code = None         # raw code for direct analysis

        # Load CWE knowledge base if it exists
        self._load_cwe_store()

    def _load_cwe_store(self):
        embeddings = FastEmbedEmbeddings()
        if os.path.exists(CWE_DB_PATH):
            self.cwe_store = Chroma(
                persist_directory=CWE_DB_PATH,
                    embedding_function=embeddings
            )
        else:
            all_chunks = []
            for pdf in CWE_PDFS:
                if os.path.exists(pdf):
                    docs = PyPDFLoader(pdf).load()
                    chunks = self.text_splitter.split_documents(docs)
                    all_chunks.extend(filter_complex_metadata(chunks))
            if all_chunks:
                self.cwe_store = Chroma.from_documents(
                    documents=all_chunks,
                    embedding=embeddings,
                    persist_directory=CWE_DB_PATH,
                )
    # If neither exists, cwe_store stays None (graceful degradation)

    def _extract_relevant_code(self, code: str, max_chars: int = 5000) -> str:
        """Extract file-path-handling inner classes for focused analysis."""
        lines = code.split("\n")
        relevant, inside, brace_depth = [], False, 0

        for line in lines:
            if any(k in line for k in ["class Unpacker", "class Unwrap", "class Backslash"]):
                inside = True
                brace_depth = 0
            if inside:
                relevant.append(line)
                brace_depth += line.count("{") - line.count("}")
                if brace_depth <= 0 and len(relevant) > 3:
                    inside = False
                    relevant.append("\n")

        extracted = "\n".join(relevant)
        if len(extracted) < 200:
            extracted = code[:max_chars]
        return extracted[:max_chars]

    def _retrieve_cwe_context(self, query: str) -> str:
        """Retrieve relevant CWE knowledge for the query."""
        if not self.cwe_store:
            return "No CWE knowledge base loaded."
        retriever = self.cwe_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join(d.page_content for d in docs)

    def ingest(self, file_path: str):
        """Ingest PDF or source code files."""
        ext = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""

        if ext in CODE_EXTENSIONS:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            self.full_code = self._extract_relevant_code(raw)
        else:
            self.full_code = None
            docs = PyPDFLoader(file_path=file_path).load()
            chunks = self.text_splitter.split_documents(docs)
            chunks = filter_complex_metadata(chunks)
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=FastEmbedEmbeddings(),
                persist_directory="chroma_db",
            )

    def ask(self, query: str):
        if self.full_code:
            # RAG: retrieve CWE knowledge from Chroma
            cwe_context = self._retrieve_cwe_context(query)

            # Combine RAG knowledge + code and send to model
            messages = self.prompt.format_messages(
                cwe_context=cwe_context,
                code_context=self.full_code,
                question=query
            )
            return StrOutputParser().invoke(self.model.invoke(messages))

        # Fallback: PDF Q&A via standard RAG
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory="chroma_db",
                embedding_function=FastEmbedEmbeddings()
            )
        retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 10, "score_threshold": 0.0},
        )
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | ChatPromptTemplate([
                ("system", "You are a helpful assistant that answers questions about documents."),
                ("human", "Document context:\n{context}\n\nQuestion: {question}"),
            ])
            | self.model
            | StrOutputParser()
        )
        return chain.invoke(query)

    def clear(self):
        self.vector_store = None
        self.full_code = None