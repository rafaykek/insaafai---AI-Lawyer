import re
from models import Chunk
from rag.embeddings import get_embedding, get_embeddings
from rag.vector_store import dense_vector_search

def tokenize_text(text: str) -> list[str]:
    """Simple alphanumeric word tokenization for BM25 search."""
    return re.findall(r'\w+', text.lower())

def run_bm25_search(query: str, chunks: list[Chunk]) -> list[tuple[int, float]]:
    """
    Runs BM25 sparse keyword search using rank_bm25 (or fallback word overlap).
    Returns list of tuples: [(chunk_idx, bm25_score)] sorted descending.
    """
    if not query or not chunks:
        return []

    tokenized_corpus = [tokenize_text(c.text) for c in chunks]
    tokenized_query = tokenize_text(query)

    if not tokenized_query:
        return []

    try:
        from rank_bm25 import BM25Okapi
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(tokenized_query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [(idx, float(score)) for idx, score in ranked if score > 0]
    except Exception:
        # Fallback simple keyword overlap scoring
        query_set = set(tokenized_query)
        scored = []
        for idx, tokens in enumerate(tokenized_corpus):
            overlap = len(set(tokens).intersection(query_set))
            if overlap > 0:
                scored.append((idx, float(overlap)))
        return sorted(scored, key=lambda x: x[1], reverse=True)

def retrieve(query: str, case_id: int, top_k: int = 5, rrf_k: int = 60) -> list[dict]:
    """
    Case-Isolated Hybrid Retrieval using BM25 + Dense Vector Search + RRF Fusion.
    Guarantees ONLY chunks belonging to case_id are searched and retrieved.
    """
    if not query or not case_id:
        return []

    # 1. STRICT CASE ISOLATION: Fetch chunks belonging ONLY to this case_id
    case_chunks = Chunk.query.filter_by(case_id=case_id).all()
    if not case_chunks:
        return []

    num_chunks = len(case_chunks)

    # 2. Sparse Search (BM25)
    bm25_results = run_bm25_search(query, case_chunks)
    bm25_ranks = {chunk_idx: rank for rank, (chunk_idx, score) in enumerate(bm25_results)}

    # 3. Dense Search (FAISS / Vector Store)
    query_emb = get_embedding(query)
    chunk_texts = [c.text for c in case_chunks]
    chunk_embs = get_embeddings(chunk_texts)
    
    dense_results = dense_vector_search(query_emb, chunk_embs, top_k=num_chunks)
    dense_ranks = {chunk_idx: rank for rank, (chunk_idx, score) in enumerate(dense_results)}

    # 4. Reciprocal Rank Fusion (RRF)
    # RRF score = sum( 1 / (rrf_k + rank) )
    rrf_scores = {}
    for idx in range(num_chunks):
        score = 0.0
        if idx in bm25_ranks:
            score += 1.0 / (rrf_k + bm25_ranks[idx])
        if idx in dense_ranks:
            score += 1.0 / (rrf_k + dense_ranks[idx])
        
        if score > 0:
            rrf_scores[idx] = score

    # Sort chunks by RRF score descending
    sorted_indices = sorted(rrf_scores.keys(), key=lambda idx: rrf_scores[idx], reverse=True)

    # Format final Top-K retrieved chunks with rich metadata
    retrieved_chunks = []
    for idx in sorted_indices[:top_k]:
        chunk_obj = case_chunks[idx]
        retrieved_chunks.append({
            'id': chunk_obj.id,
            'text': chunk_obj.text,
            'filename': chunk_obj.filename,
            'page': chunk_obj.page,
            'chunk_index': chunk_obj.chunk_index,
            'case_id': chunk_obj.case_id,
            'document_id': chunk_obj.document_id,
            'rrf_score': round(rrf_scores[idx], 4)
        })

    return retrieved_chunks
