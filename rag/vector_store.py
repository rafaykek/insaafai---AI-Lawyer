import numpy as np

def dense_vector_search(query_embedding: list[float], chunk_embeddings: list[list[float]], top_k: int = 5) -> list[tuple[int, float]]:
    """
    Performs dense vector similarity search using FAISS (or NumPy fallback).
    Returns list of tuples: [(chunk_index_in_list, similarity_score), ...]
    """
    if not query_embedding or not chunk_embeddings:
        return []

    num_chunks = len(chunk_embeddings)
    actual_top_k = min(top_k, num_chunks)

    query_arr = np.array([query_embedding], dtype=np.float32)
    chunks_arr = np.array(chunk_embeddings, dtype=np.float32)

    # Normalize vectors for cosine similarity
    query_norm = np.linalg.norm(query_arr, axis=1, keepdims=True)
    query_norm[query_norm == 0] = 1e-10
    query_arr = query_arr / query_norm

    chunks_norm = np.linalg.norm(chunks_arr, axis=1, keepdims=True)
    chunks_norm[chunks_norm == 0] = 1e-10
    chunks_arr = chunks_arr / chunks_norm

    try:
        import faiss
        dimension = query_arr.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors = cosine similarity
        index.add(chunks_arr)
        scores, indices = index.search(query_arr, actual_top_k)
        
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1:
                results.append((int(idx), float(score)))
        return results
    except Exception:
        # NumPy fallback for Cosine Similarity
        scores = np.dot(chunks_arr, query_arr.T).flatten()
        top_indices = np.argsort(scores)[::-1][:actual_top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices]
