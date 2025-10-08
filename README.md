# 🦉 Chat + Document Q&A (RAG)

A powerful chatbot application that combines conversational AI with document-grounded question answering using Retrieval-Augmented Generation (RAG).

## Features

- 💬 **Multi-session Chat**: Create and manage multiple chat sessions
- 📄 **PDF Upload**: Upload PDFs to ground answers in your documents
- 🔍 **RAG Pipeline**: Uses Pinecone vector database for semantic search
- 📚 **Source Citations**: Answers include citations to source documents
- 🎯 **Flexible Mode**: Toggle between RAG mode and free chat
- ✨ **Modern UI**: Beautiful gradient design with smooth interactions

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Hugging Face Inference API (OpenAI GPT-OSS-20B)
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Vector DB**: Pinecone
- **Storage**: Supabase
- **PDF Processing**: PyMuPDF, LangChain

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd RAG_PDF_Chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file with:

```env
HF_TOKEN=your_huggingface_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-chat-index
```

### 4. Set up Supabase tables

Create the following tables in your Supabase project:

**chats table:**
```sql
CREATE TABLE chats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**messages table:**
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  sources TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**pdfs table:**
```sql
CREATE TABLE pdfs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5. Run locally

```bash
streamlit run bot.py
```

## Deployment to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository and `bot.py`
5. Add your secrets in the Streamlit Cloud dashboard (Settings → Secrets)
6. Deploy!

## Environment Variables for Streamlit Cloud

In Streamlit Cloud, add these secrets:

```toml
HF_TOKEN = "your_huggingface_token"
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
PINECONE_API_KEY = "your_pinecone_api_key"
PINECONE_INDEX_NAME = "rag-chat-index"
```

## Usage

1. **Create a Chat**: Click "New Chat" in the sidebar
2. **Upload PDFs** (optional): Upload documents to ground your answers
3. **Ask Questions**: Type your questions in the chat input
4. **View Sources**: Expand source citations to see where answers came from
5. **Manage Sessions**: Rename or delete chats as needed

## License

MIT

