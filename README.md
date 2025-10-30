# RAG Chat Assistant (Django)

A Django-based chat assistant with Retrieval-Augmented Generation (RAG), secure authentication, conversation memory, and a modern UI.

## Highlights

- **Authentication**: Django auth for register/login, CSRF, secure sessions; per‑user chat isolation. A lightweight guest mode lets users try the app before logging in.
- **Conversation Memory**: Chats and messages are persisted in Django models. The LLM receives recent turns for context in each reply.
- **RAG**: Upload PDFs per chat and toggle RAG on/off. The backend retrieves relevant chunks and augments the prompt before generation (`chat/services.py` + `services/ai_service.py`). The retriever is service‑based, so swapping to FAISS or Pinecone is straightforward.
- **Clean UI**: Gradient header, responsive sidebar, sticky composer, and dark/light aware auth pages. Loading state shows a “Thinking…” row during generation.

## Tech Stack

- **Framework**: Django (MVT)
- **Templates/CSS/JS**: Django templates, custom CSS, vanilla JS
- **LLM**: Hugging Face Inference API
- **PDF/RAG**: PyMuPDF or similar parsing (via services), custom retriever (swappable to FAISS/Pinecone)
- **DB**: SQLite for local dev; Postgres recommended in production

## Getting Started

### 1) Clone
```bash
git clone <your-repo-url>
cd RAG_PDF_Chatbot
```

### 2) Install
```bash
pip install -r requirements.txt
```

### 3) Environment
Create env vars (via shell/export or your platform’s settings):
```
HF_TOKEN=your_huggingface_token
# Optional vector store keys if you switch retriever later
# PINECONE_API_KEY=...
```

### 4) Migrate & run
```bash
python manage.py migrate
python manage.py runserver
```

## Usage

1. Log in (or try guest mode on the landing page).  
2. Create a chat and start messaging.  
3. Toggle “Use RAG” and upload PDFs to ground answers.  
4. Your conversations are saved and can be revisited from the sidebar.

## RAG Notes

The retriever is implemented as a service and can be swapped. If you require FAISS/Pinecone, add the client and wire it in `ConversationService` without changing views/templates.

## Deployment

This project runs cleanly on Railway or any Django-friendly host (Gunicorn + Postgres). See the included Railway guides for a quick path.


