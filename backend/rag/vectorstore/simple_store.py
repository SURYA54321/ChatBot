import logging
import numpy as np
from typing import List, Tuple, Any

# Adjust this import path if your DocumentChunk model is located elsewhere
from documents.models import DocumentChunk 

logger = logging.getLogger(__name__)


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculates cosine similarity between two vector lists using NumPy.
    Memory footprint: ~1 MB RAM.
    """
    v1 = np.array(vec1, dtype=np.float32)
    v2 = np.array(vec2, dtype=np.float32)
    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    # Avoid division by zero
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return float(np.dot(v1, v2) / (norm_v1 * norm_v2))


def similarity_search_with_relevance_scores(
    query: str,
    user_id: Any,
    conversation_id: Any,
    embedding_model: Any,
    k: int = 5,
    score_threshold: float = 0.2,
) -> List[Tuple[Any, float]]:
    """
    Retrieves chunks from SQLite filtered by user and conversation, 
    then ranks them using Cosine Similarity.
    """
    try:
        # Step 1: Embed search query via remote HuggingFace API
        query_embedding = embedding_model.embed_query(query)
        
        # Step 2: Fetch chunks scoped exclusively to this user & conversation
        chunks = DocumentChunk.objects.filter(
            user_id=user_id, 
            conversation_id=conversation_id
        )
        
        scored_results = []
        
        for chunk in chunks:
            # FIX: Django JSONField is already a Python list. 
            # Directly access `chunk.embedding` without json.loads().
            chunk_embedding = chunk.embedding
            
            if not chunk_embedding:
                continue
                
            score = compute_cosine_similarity(query_embedding, chunk_embedding)
            
            if score >= score_threshold:
                scored_results.append((chunk, score))
                
        # Step 3: Sort highest similarity score first
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Step 4: Return top k results
        return scored_results[:k]
        
    except Exception as e:
        logger.error(f"Vector similarity search failed: {str(e)}")
        return []