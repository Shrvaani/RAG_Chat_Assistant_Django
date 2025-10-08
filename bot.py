# bot.py — Chat + Document Q&A (RAG + Reliable Delete + Confirmed Clear-All + No Auto Chat)
import os, json, time, hashlib
from tempfile import NamedTemporaryFile
from typing import List
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from supabase import create_client
from pinecone import Pinecone, ServerlessSpec

# ===========================================
# ENV SETUP
# ===========================================
load_dotenv()
st.set_page_config(page_title="Chat + Document Q&A (RAG)", layout="wide")

HF_TOKEN = os.getenv("HF_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME", "rag-chat-index")
MODEL = "openai/gpt-oss-20b"

assert all([HF_TOKEN, SUPABASE_URL, SUPABASE_KEY, PINECONE_API_KEY]), "⚠️ Missing API credentials!"

# ===========================================
# CLIENTS
# ===========================================
llm_client = InferenceClient(model=MODEL, token=HF_TOKEN)
emb_client = InferenceClient(model="sentence-transformers/all-mpnet-base-v2", token=HF_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
if PINECONE_INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX, dimension=768, metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(PINECONE_INDEX)

# ===========================================
# STYLE
# ===========================================
st.markdown("""
<style>
:root{--grad:linear-gradient(90deg,#8b5cf6,#6366f1);--radius:10px;}
section[data-testid="stSidebar"]{background:#f5f3ff!important;border-right:1px solid #e9d5ff;}
section[data-testid="stSidebar"] h2,h3{color:#4f46e5;font-weight:700;}
.stButton>button{background:var(--grad)!important;color:white!important;border:none!important;
border-radius:8px;padding:0.4rem 0.8rem;font-weight:600;transition:0.2s;}
.stButton>button:hover{filter:brightness(1.1);}
.stFileUploader>section{border:2px dashed #c7d2fe!important;border-radius:var(--radius)!important;}
h1{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
font-weight:800;text-align:center;margin-top:-0.5rem;margin-bottom:0.3rem;}
p.desc{text-align:center;color:#6b7280;margin-top:-10px;}
.stChatMessage[data-testid="assistant-message"] .stMarkdown{
background:#f3f4f6;border-left:4px solid #6366f1;border-radius:var(--radius);padding:0.7rem;}
.stChatMessage[data-testid="user-message"] .stMarkdown{
background:#eef2ff;border-right:4px solid #a855f7;border-radius:var(--radius);padding:0.7rem;}
</style>
""", unsafe_allow_html=True)

# ===========================================
# HELPERS
# ===========================================
def get_user_id():
    """Generate a unique user ID based on session info"""
    # Create a unique identifier for this user session
    session_info = f"{st.session_state.get('_streamlit_session_id', 'default')}_{time.time()}"
    return hashlib.md5(session_info.encode()).hexdigest()[:16]

def embed_texts(txts: List[str]) -> List[List[float]]:
    arr = emb_client.feature_extraction(txts)
    if isinstance(arr, list) and isinstance(arr[0], list):
        return [[float(x) for x in v] for v in arr]
    arr = np.array(arr, dtype=float)
    return [row.tolist() for row in arr.reshape(len(txts), -1)]

def retrieve(q: str, chat_id: str, top_k=10, thr=0.01):
    qv = embed_texts([q])[0]
    # Get PDF IDs for this specific chat
    pdfs_in_chat = supabase.table("pdfs").select("id").eq("chat_id", chat_id).execute().data
    pdf_ids = [pdf["id"] for pdf in pdfs_in_chat]
    
    if not pdf_ids:
        return [], []  # No PDFs in this chat
    
    # Query only vectors from PDFs in this chat
    res = index.query(
        vector=qv, 
        top_k=top_k, 
        include_metadata=True,
        filter={"pdf_id": {"$in": pdf_ids}}  # Only search within this chat's PDFs
    )
    hits = [m for m in res["matches"] if m["score"] >= thr] or res["matches"][:3]
    ctx, src = [], []
    for i, m in enumerate(hits):
        md = m["metadata"]
        ctx.append(f"[S{i+1}] {md.get('text','')}")
        src.append({"page": md.get("page"), "chunk_id": md.get("chunk_id")})
    return ctx, src

def build_prompt(ctxs, q, use_rag=True):
    if use_rag:
        c = "\n\n".join(ctxs) or "(No relevant context found.)"
        sys = ("You are a helpful assistant. Use the provided document context as evidence. "
               "Cite sources like [S1],[S2] if used. If unsure, say 'I don't know'.")
        return f"{sys}\n\nContext:\n{c}\n\nQuestion: {q}"
    return f"You are a helpful assistant.\n\nQuestion: {q}"

def supabase_chats(uid): return supabase.table("chats").select("*").eq("user_id", uid).execute().data
def supabase_msgs(cid): return supabase.table("messages").select("*").eq("chat_id", cid).order("created_at").execute().data
def insert_chat(uid,title): return supabase.table("chats").insert({"user_id":uid,"title":title}).execute().data[0]["id"]
def insert_msg(cid,role,txt,src): supabase.table("messages").insert({"chat_id":cid,"role":role,"content":txt,"sources":json.dumps(src)}).execute()

def cleanup_old_pdf_vectors(pdf_id):
    """Remove old vectors for a PDF when re-uploading"""
    try:
        # Delete vectors that start with this pdf_id
        index.delete(filter={"pdf_id": pdf_id})
    except Exception as e:
        print(f"Warning: Could not cleanup old vectors: {e}")

# ===========================================
# RELIABLE DELETE HELPERS
# ===========================================
def cascade_delete_chat(chat_id: str, title: str):
    """Sequential verified delete with retries."""
    with st.spinner(f"🧹 Deleting '{title}'..."):
        for _ in range(5):
            supabase.table("pdfs").delete().eq("chat_id", chat_id).execute()
            supabase.table("messages").delete().eq("chat_id", chat_id).execute()
            time.sleep(0.25)
            pdfs_left = supabase.table("pdfs").select("id").eq("chat_id", chat_id).execute().data
            msgs_left = supabase.table("messages").select("id").eq("chat_id", chat_id).execute().data
            if not pdfs_left and not msgs_left:
                break
            time.sleep(0.4)
        if not pdfs_left and not msgs_left:
            supabase.table("chats").delete().eq("id", chat_id).execute()
            st.success(f"✅ Chat '{title}' deleted successfully!")
        else:
            st.warning(f"⚠️ Chat '{title}' still has linked records; please retry.")

def cascade_clear_all():
    """Reliable cleanup for UUID tables."""
    with st.spinner("🧹 Clearing all chats..."):
        chats = supabase.table("chats").select("id").execute().data
        if not chats:
            st.info("No chats to clear.")
            return False
        chat_ids = [c["id"] for c in chats]
        for cid in chat_ids:
            supabase.table("pdfs").delete().eq("chat_id", cid).execute()
            supabase.table("messages").delete().eq("chat_id", cid).execute()
            time.sleep(0.1)
        for cid in chat_ids:
            supabase.table("chats").delete().eq("id", cid).execute()
            time.sleep(0.05)
        st.success("✅ All chats and PDFs removed successfully!")
        return True

# ===========================================
# STATE
# ===========================================
S = st.session_state
if "uid" not in S: 
    S.uid = get_user_id()
    # Store the user ID for this session
    st.session_state.user_id = S.uid
if "cid" not in S or not S.cid:
    chats = supabase_chats(S.uid)
    S.cid = chats[0]["id"] if chats else None
if "msgs" not in S:
    S.msgs = supabase_msgs(S.cid) if S.cid else []
if "rename_id" not in S: S.rename_id = None
if "rename_value" not in S: S.rename_value = ""
if "confirm_clear" not in S: S.confirm_clear = False

# ===========================================
# SIDEBAR
# ===========================================
with st.sidebar:
    st.header("Sessions")
    st.caption(f"User: {S.uid[:8]}...")  # Show first 8 chars of user ID
    level = st.selectbox("Reasoning Level", ["Low","Medium","High"], index=1)
    use_rag = st.toggle("Use RAG (ground answers in PDFs when available)", value=True)

    if st.button("New Chat", use_container_width=True):
        S.cid = insert_chat(S.uid, f"Chat {int(time.time())}")
        S.msgs = []; st.rerun()

    st.subheader("Conversations")
    chats = supabase_chats(S.uid)

    if not chats:
        st.info("No chats yet. Click 'New Chat' to start.")
    for c in chats:
        if st.button(c["title"], key=f"chat_{c['id']}", use_container_width=True):
            S.cid = c["id"]; S.msgs = supabase_msgs(S.cid); S.rename_id=None; st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Rename", key=f"rename_{c['id']}", use_container_width=True):
                S.rename_id = c["id"]; S.rename_value = c["title"]; st.rerun()
        with col2:
            if st.button("Delete", key=f"delete_{c['id']}", use_container_width=True):
                cascade_delete_chat(c["id"], c["title"])
                if c["id"] == S.cid:
                    S.cid = None; S.msgs = []
                st.rerun()

        # Inline rename
        if S.rename_id == c["id"]:
            new_title = st.text_input("Rename chat", value=S.rename_value,
                                      key=f"rename_input_{c['id']}", label_visibility="collapsed")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("Save", key=f"save_{c['id']}", use_container_width=True):
                    if new_title.strip():
                        supabase.table("chats").update({"title": new_title.strip()}).eq("id", c["id"]).execute()
                        S.rename_id=None; S.rename_value=""; st.success("Chat renamed!"); st.rerun()
                    else: st.warning("Title cannot be empty.")
            with rc2:
                if st.button("Cancel", key=f"cancel_{c['id']}", use_container_width=True):
                    S.rename_id=None; S.rename_value=""; st.rerun()

    st.divider()
    
    # Clear all chats with confirmation
    if not S.confirm_clear:
        if st.button("🗑 Clear All Chats", use_container_width=True, type="secondary"):
            S.confirm_clear = True
            st.rerun()
    else:
        st.warning("⚠️ This will permanently delete ALL chats and uploaded PDFs.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, delete", use_container_width=True, type="primary"):
                if cascade_clear_all():
                    S.cid = None
                    S.msgs = []
                S.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                S.confirm_clear = False
                st.rerun()

    st.caption("HF Token: ✅ set")

# ===========================================
# HEADER
# ===========================================
st.markdown("<h1>RAG Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='desc'>Freely available models on Hugging Face Inference API • Upload PDFs for grounded answers with citations.</p>", unsafe_allow_html=True)

# ===========================================
# PDF UPLOAD
# ===========================================
if use_rag:
    files = st.file_uploader("📤 Upload PDF(s)", type="pdf", accept_multiple_files=True)
    if files and S.cid:
        for f in files:
            # Check if PDF with same name already exists in THIS SPECIFIC CHAT only
            existing_pdfs = supabase.table("pdfs").select("*").eq("chat_id", S.cid).eq("filename", f.name).execute().data
            
            # Debug: Show what we found
            all_pdfs_in_chat = supabase.table("pdfs").select("*").eq("chat_id", S.cid).execute().data
            st.caption(f"Debug: Chat {S.cid} has {len(all_pdfs_in_chat)} total PDFs")
            if all_pdfs_in_chat:
                st.caption(f"Debug: PDFs in this chat: {[pdf['filename'] for pdf in all_pdfs_in_chat]}")
            
            if existing_pdfs:
                # PDF already exists in this chat, clean up old vectors and update
                old_pdf_id = existing_pdfs[0]["id"]
                cleanup_old_pdf_vectors(old_pdf_id)
                pid = old_pdf_id
                st.info(f"🔄 Updating existing PDF in this chat: {f.name}")
            else:
                # New PDF for this chat, insert record
                rec = supabase.table("pdfs").insert({"chat_id": S.cid, "filename": f.name}).execute()
                pid = rec.data[0]["id"]
                st.info(f"📄 New PDF uploaded to this chat: {f.name}")
            
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f.read()); path = tmp.name
            loader = PyMuPDFLoader(path)
            pages = loader.load() or PyPDFLoader(path).load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=400)
            chunks = splitter.split_documents(pages)
            texts = [c.page_content for c in chunks]
            vecs = embed_texts(texts)
            upserts = [(f"{pid}_{i}", v, {"pdf_id": pid, "chunk_id": i, "page": c.metadata.get("page"), "text": t})
                       for i, (v, t, c) in enumerate(zip(vecs, texts, chunks))]
            index.upsert(vectors=upserts)
            os.unlink(path)  # Clean up temp file
        st.success("✅ PDF(s) uploaded and embedded.")
    elif files and not S.cid:
        st.warning("⚠️ Create a chat before uploading PDFs.")

# ===========================================
# CHAT DISPLAY
# ===========================================
if S.cid and S.msgs:
    for m in S.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant" and m.get("sources"):
                try:
                    srcs = json.loads(m["sources"])
                    with st.expander("Sources"):
                        for s in srcs:
                            st.caption(f"📄 Page {s.get('page')} (chunk {s.get('chunk_id')})")
                except: pass

# ===========================================
# CHAT INPUT
# ===========================================
if S.cid:
    if q := st.chat_input("Type your message here..."):
        insert_msg(S.cid, "user", q, [])
        S.msgs.append({"role": "user", "content": q})
        with st.chat_message("user"): st.markdown(q)
        ctx, src = retrieve(q, S.cid) if use_rag else ([], [])
        prompt = build_prompt(ctx, q, use_rag)
        ans = ""
        with st.chat_message("assistant"):
            box = st.empty()
            try:
                resp = llm_client.chat_completion(
                    model=MODEL, messages=[{"role":"user","content":prompt}],
                    max_tokens=2000, temperature=0.4, stream=True
                )
                for chunk in resp:
                    delta = getattr(chunk.choices[0],"delta",None)
                    tok = getattr(delta,"content","") if delta else ""
                    ans += str(tok or ""); box.markdown(ans+"▌")
                box.markdown(ans)
            except Exception:
                gen = llm_client.text_generation(prompt,max_new_tokens=2000,temperature=0.4)
                ans = gen if isinstance(gen,str) else str(gen)
                box.markdown(ans)
        insert_msg(S.cid,"assistant",ans,src)
        S.msgs.append({"role":"assistant","content":ans,"sources":json.dumps(src)})
else:
    st.info("🗨️ Create a chat to start conversing.")
