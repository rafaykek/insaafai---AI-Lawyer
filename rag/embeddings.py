import numpy as np

_model_instance = None

def get_embedding_model():
    """Lazy load SentenceTransformer model."""
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"[Warning] SentenceTransformer fallback active: {e}")
            _model_instance = "fallback"
    return _model_instance

def get_embedding(text: str) -> list[float]:
    """Generates dense embedding vector for a single text string."""
    return get_embeddings([text])[0]

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates dense embedding vectors for a list of text strings."""
    if not texts:
        return []

    model = get_embedding_model()
    
    if model != "fallback":
        embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()
    
    # Lightweight deterministic hashing fallback if PyTorch/Transformer is unavailable
    results = []
    for text in texts:
        vec = np.zeros(384, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            idx = abs(hash(word)) % 384
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        results.append(vec.tolist())
    return results
