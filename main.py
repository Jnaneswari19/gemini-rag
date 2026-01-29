from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uuid
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = FastAPI()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory storage
documents = {}
index = None
id_map = {}

@app.get("/health")
def health():
    return {"status": "ok"}

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks for better semantic search."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global index, id_map
    doc_id = str(uuid.uuid4())
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    documents[doc_id] = {
        "filename": file.filename,
        "text": text
    }

    # Split into chunks
    chunks = chunk_text(text)

    for chunk in chunks:
        embedding = model.encode([chunk])
        embedding = np.array(embedding).astype("float32")

        if index is None:
            index = faiss.IndexFlatL2(embedding.shape[1])

        idx = len(id_map)
        index.add(embedding)
        id_map[idx] = (doc_id, chunk)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "message": f"Document uploaded successfully with {len(chunks)} chunks"
    }

class AskRequest(BaseModel):
    session_id: str
    document_ids: list[str]
    question: str

@app.post("/ask")
def ask(request: AskRequest):
    global index, id_map
    if index is None:
        return {"session_id": request.session_id, "question": request.question, "results": []}

    # Encode question
    q_embedding = model.encode([request.question])
    q_embedding = np.array(q_embedding).astype("float32")

    # Search top 5 matches
    D, I = index.search(q_embedding, k=5)

    results = []
    for idx in I[0]:
        if idx in id_map:
            doc_id, chunk = id_map[idx]
            if doc_id in request.document_ids:
                results.append({
                    "document_id": doc_id,
                    "filename": documents[doc_id]["filename"],
                    "chunk_id": idx,
                    "answer": chunk
                })

    return {
        "session_id": request.session_id,
        "question": request.question,
        "results": results
    }
