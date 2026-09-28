# InsaafAI — Simple Flask Platform Foundation

**InsaafAI** is an AI-powered legal consultancy platform designed to assist clients with legal document analysis, case understanding, and consultation support.

This repository contains the **Platform Foundation, RAG Ingestion (Phase 2A), and Hybrid Retrieval + Grounded Generation (Phase 2B)** implementation. It is structured to be simple, modular, readable, and easy to explain to students in a classroom setting.

> [!NOTE]
> **Phase 2B Status:** Complete RAG Pipeline is **OPERATIONAL**. Customer questions undergo strict case-isolated BM25 + Dense FAISS search fused via Reciprocal Rank Fusion (RRF), passed to LLM Grounded Generation (Asad), and return grounded answers with exact source citations.

---

## 1. Complete RAG Pipeline Architecture

```text
                    CUSTOMER QUESTION
                            │
                            ▼
                    CASE ID (CASE-XXXXX)
                            │
                            ▼
              ┌───────────────────────────┐
              │ CASE-ISOLATED HYBRID RAG  │
              └─────────────┬─────────────┘
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
   Sparse Keyword Search          Dense Vector Search
       (BM25Okapi)                 (SentenceTransformer
            │                          + FAISS)
            └──────────────┬───────────────┘
                           ▼
              Reciprocal Rank Fusion (RRF)
                  rrf_score = Σ 1/(60+rank)
                           │
                           ▼
                    TOP-K CHUNKS (5)
                           │
                           ▼
          Prompt Augmentation (System + Case Context + Chunks + Chat History)
                           │
                           ▼
         LLM Generation (Google GenAI / Asad Grounded Engine)
                           │
                           ▼
         Grounded Response + Exact Document & Page Citations
```

## 1. Customer Workflow

```text
Landing Page (/)
      ↓
Book AI Consultancy (/onboarding)
      ↓
Customer Onboarding & File Upload
      ↓
Case Creation (CASE-XXXXX)
      ↓
Case Summary View (/case/CASE-XXXXX)
      ↓
Consultation Chat (/chat/CASE-XXXXX)
      ↓
Asad — AI Legal Consultant (Dynamic Welcome & Placeholder Responses)
```

---

## 2. Architecture: Current vs. Future Phase

### Current Phase (Platform Foundation)

```text
Landing Page
      ↓
Onboarding Form & Document Upload
      ↓
Case Creation (SQLite Persistence)
      ↓
Dynamic Welcome Message from Asad
      ↓
Customer Message
      ↓
Placeholder Assistant Response
```

### Future Phase (RAG Pipeline Integration)

```text
Customer Question
      ↓
Document Parser & Text Extraction
      ↓
Chunking Engine
      ↓
Embeddings Generator
      ↓
Vector Database Retrieval (Top-K Chunks)
      ↓
Prompt Context Formulation
      ↓
LLM Grounded Response
      ↓
Sources & Citations
```

---

## 3. Project Structure

```text
insaafai/
│
├── app.py                 # Flask application factory and entry point
├── config.py              # Application settings and directory paths
├── requirements.txt       # Minimal Python dependencies
├── README.md              # Project documentation
│
├── models/                # SQLAlchemy database models
│   ├── __init__.py        # Database instance and model exports
│   ├── customer.py        # Customer model
│   ├── case.py            # Case model (with CASE-XXXXX generator)
│   ├── document.py        # Document upload model
│   └── message.py         # Chat conversation message model
│
├── routes/                # Modular Flask Blueprints
│   ├── __init__.py        # Blueprint exports
│   ├── main.py            # Landing page routes
│   ├── consultation.py    # Onboarding and case creation routes
│   └── chat.py            # Consultation chat routes
│
├── templates/             # HTML templates (Jinja2)
│   ├── base.html          # Base layout with header & footer
│   ├── index.html         # Landing page
│   ├── onboarding.html    # Customer intake form
│   ├── case.html          # Case summary page
│   └── chat.html          # Chat interface
│
├── static/                # Static web assets
│   ├── css/
│   │   └── style.css      # Legal-tech design system styles
│   └── js/
│       └── chat.js        # Vanilla JS chat client logic
│
├── uploads/               # Uploaded case documents storage
└── instance/              # SQLite database (insaafai.db)
```

---

## 4. Database Schema Overview

```text
CASE-10231 (Case)
├── Customer (name, location, jurisdiction)
├── Documents (filename, filepath, document_type)
└── Messages (role: user/assistant, content, timestamp)
```

- **Customer**: Holds personal details (`name`, `location`, `jurisdiction`).
- **Case**: Connects a customer to a unique case ID (`CASE-10231`), consultancy type, and problem description.
- **Document**: Stores uploaded document file references per case.
- **Message**: Persists the consultation history for the case.

---

## 5. How to Install & Run

### Prerequisites

- Python 3.9+ installed on your system.

### Step 1: Clone or Navigate to Directory

```bash
cd insaafai
```

### Step 2: Create & Activate Virtual Environment (Optional but Recommended)

On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

Open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 6. Current Limitations & Next Steps

1. **No Real AI/LLM Integration**: Responses are currently generated via `generate_placeholder_response()`.
2. **No Authentication**: Cases are accessed directly via case ID URLs for classroom demonstration.
3. **No Text Extraction**: Uploaded files (`.pdf`, `.docx`, `.txt`) are saved to `uploads/` but not yet parsed into embeddings or vector indices.

In the next phase, `generate_placeholder_response()` in `routes/chat.py` will be cleanly swapped with `generate_rag_response()` without altering the database schema, models, or template structure.
