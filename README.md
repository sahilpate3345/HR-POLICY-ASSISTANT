<<<<<<< HEAD
# Acme Corp HR Policy Assistant

An advanced, production-ready Retrieval-Augmented Generation (RAG) assistant designed to help employees of Acme Corp query company HR policies with high accuracy. The project features input/output safety guardrails, Portkey LLM gateway integration, LangSmith tracing, and automated correctness/groundedness evaluation.

---

## Features

- **Dynamic RAG Pipeline**: Combines Jina AI Embeddings (`jina-embeddings-v2-base-en`) and Qdrant Cloud Vector Database to store and retrieve company policies.
- **Section-Aware Document Chunking**: A custom chunking algorithm that parses the HR policy document, preserves section headers (e.g., Leave, WFH, probation), and appends header context to each chunk.
- **Custom Robust LLM Client**: A resilient LLM wrapper (`GroqLLM`) that retries requests across a set of fallback models (e.g., `groq/compound`, `groq/compound-mini`, `qwen/qwen3.6-27b`) if the primary model fails or encounters rate limits.
- **Portkey Gateway Routing**: Routes LLM calls securely through the Portkey AI Gateway using tenant provider tags, hiding raw provider keys from the application code.
- **Strict Safety Guardrails**:
  - **Input Guardrail**: Screens user questions against prompt injection / jailbreak attempts and unauthorized requests for other employees' private data (salary, medical info).
  - **Output Guardrail**: Validates generated answers to block PII leaks, unauthorized promises (e.g., approving leaves on behalf of the company), and suspicious links or toxic content.
- **LangSmith Observability**: Complete tracing of prompt inputs, vector retrievals, LLM invocations, and tool outputs.
- **Automated LLM-as-a-Judge Evaluation**: Includes a suite of test cases evaluated against a LangSmith dataset, utilizing `openevals` correctness and groundedness judges.

---

## Directory Structure

```text
HR Policy Assistant/
│
├── data/
│   ├── hr_policy.txt           # Raw Acme Corp HR Policy text document
│   └── vectorstore.json        # Cached/local vector database information
│
├── hr_assistant/
│   ├── __init__.py             # Module initialization
│   ├── agent.py                # HRAgentExecutor and system instructions
│   ├── config.py               # Main application configuration & secret validation
│   ├── document_loader.py      # SimpleDocument loader wrapper
│   ├── embeddings.py           # Jina AI Embeddings client implementation
│   ├── evaluate.py             # Evaluation runner CLI
│   ├── evaluation.py           # LangSmith dataset and openevals judge setup
│   ├── gateway.py              # Portkey AI Gateway integration settings
│   ├── guardrails.py           # Input and Output LLM-based safety guardrails
│   ├── llm.py                  # Groq LLM client wrapper with model fallbacks
│   ├── logger.py               # Central logger configuration
│   ├── pipeline.py             # RAG pipeline orchestration (Ingestion, Search, Ask)
│   ├── splitter.py             # Custom section-preserving text splitter
│   ├── tools.py                # Search tool wrapper for the vector store retriever
│   ├── tracing.py              # LangSmith tracing check & initialization
│   └── vector_store.py         # Qdrant Vector Store interface
│
├── .env                        # Local configuration and API secrets
├── app.py                      # Streamlit-based Chat UI
├── architecture.md             # System design & Mermaid workflows documentation
├── architecutre.md             # Redirection helper for spelling typo
├── main.py                     # CLI tool for interactive chat or single queries
└── requirements.txt            # Python dependencies list
```

---

## Setup & Installation

### 1. Prerequisites
Make sure you have Python 3.10+ installed.

### 2. Clone and Install Dependencies
Navigate to your workspace directory and install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (based on the template below) and supply your API credentials:
```env
# Core API Keys
JINA_API_KEY="your-jina-ai-api-key"
GROQ_API_KEY="your-groq-api-key"
PORTKEY_API_KEY="your-portkey-api-key"

# Qdrant Cloud Configuration
QDRANT_URL="https://your-qdrant-cloud-instance.qdrant.io"
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_COLLECTION_NAME="hr-assistant"

# LangSmith Tracing & Evaluation (Optional)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your-langsmith-api-key"
LANGSMITH_PROJECT="HR-ASSISTANT"

# Safety Guard Model
GUARD_MODEL_NAME="openai/gpt-oss-safeguard-20b"
LLM_MODEL_NAME="groq/compound"
```

---

## Usage

The application provides two entry points for querying policies: a Command Line Interface (CLI) and a Streamlit-based Web interface.

### 1. Streamlit Web Chat Interface
Start the interactive Web UI:
```bash
streamlit run app.py
```
This launches a browser session where you can chat with the assistant and ask questions like:
- *"How many sick days do I get per year?"*
- *"Can I work from home 3 days a week?"*

### 2. Command Line Interface (CLI)
You can run the assistant in interactive chat mode or run single queries directly.

- **Interactive Mode**:
  ```bash
  python main.py
  ```
- **Single Query Mode**:
  ```bash
  python main.py --query "How long is the probation period?"
  ```
- **Custom Document Ingestion**:
  You can dynamically load a different policy document:
  ```bash
  python main.py --file path/to/custom_policy.txt --query "What is the notice period?"
  ```

---

This evaluation script tests the HR Assistant using 10 predefined HR policy questions. For each question, it retrieves relevant source contexts, generates an answer using the configured LLM, and evaluates the response using an LLM-based judge (`openai/gpt-oss-20b` via Portkey). The evaluation results are automatically recorded and available in the LangSmith project dashboard for analysis and performance tracking.
