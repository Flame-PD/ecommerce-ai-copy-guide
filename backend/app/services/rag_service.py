import os
import json
import pickle
from typing import List, Optional, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rag_data")
DOCS_PATH = os.path.join(RAG_DIR, "docs.json")
VECTORIZER_PATH = os.path.join(RAG_DIR, "vectorizer.pkl")
MATRIX_PATH = os.path.join(RAG_DIR, "matrix.pkl")

os.makedirs(RAG_DIR, exist_ok=True)

_docs: List[Dict] = []
_vectorizer: Optional[TfidfVectorizer] = None
_matrix = None


def _load():
    global _docs, _vectorizer, _matrix
    if os.path.exists(DOCS_PATH):
        with open(DOCS_PATH, "r", encoding="utf-8") as f:
            _docs = json.load(f)
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(MATRIX_PATH):
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
        with open(MATRIX_PATH, "rb") as f:
            _matrix = pickle.load(f)


def _save():
    with open(DOCS_PATH, "w", encoding="utf-8") as f:
        json.dump(_docs, f, ensure_ascii=False, indent=2)
    if _vectorizer is not None:
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(_vectorizer, f)
    if _matrix is not None:
        with open(MATRIX_PATH, "wb") as f:
            pickle.dump(_matrix, f)


def _rebuild():
    global _vectorizer, _matrix
    if not _docs:
        _vectorizer = TfidfVectorizer()
        _matrix = None
        return
    texts = [d["text"] for d in _docs]
    _vectorizer = TfidfVectorizer()
    _matrix = _vectorizer.fit_transform(texts)
    _save()


def add_knowledge(text: str, metadata: dict) -> str:
    global _docs
    _load()
    embedding_id = metadata.get("embedding_id") or f"doc_{len(_docs)}"
    # 删除旧条目
    _docs = [d for d in _docs if d["id"] != embedding_id]
    _docs.append({"id": embedding_id, "text": text, "metadata": metadata})
    _rebuild()
    return embedding_id


def search_knowledge(query: str, top_k: int = 5, product_id: Optional[int] = None) -> List[dict]:
    _load()
    if not _docs or _matrix is None:
        return []
    candidates = _docs
    if product_id is not None:
        candidates = [d for d in _docs if d["metadata"].get("product_id") == product_id]
    if not candidates:
        return []
    q_vec = _vectorizer.transform([query])
    indices = [i for i, d in enumerate(_docs) if d in candidates]
    sub_matrix = _matrix[indices]
    scores = cosine_similarity(q_vec, sub_matrix)[0]
    ranked = sorted(zip(indices, scores), key=lambda x: -x[1])[:top_k]
    results = []
    for idx, score in ranked:
        d = _docs[idx]
        results.append({
            "id": d["id"],
            "document": d["text"],
            "distance": float(1 - score),
            "metadata": d["metadata"],
        })
    return results


def delete_knowledge(embedding_id: str) -> bool:
    global _docs
    _load()
    original_len = len(_docs)
    _docs = [d for d in _docs if d["id"] != embedding_id]
    if len(_docs) < original_len:
        _rebuild()
        return True
    return False


def sync_product_knowledge(product: dict):
    texts = []
    meta = {
        "product_id": product.get("id"),
        "product_name": product.get("name", ""),
        "type": "product",
    }
    base = f"商品名称：{product.get('name', '')}\n分类：{product.get('category', '')}\n价格：{product.get('price', '')}\n描述：{product.get('description', '')}"
    specs = product.get("specs") or []
    if specs:
        base += f"\n规格：{', '.join(specs)}"
    texts.append((base, meta))
    for idx, item in enumerate(product.get("knowledge_items", [])):
        text = f"问题：{item.get('question', '')}\n回答：{item.get('answer', '')}"
        texts.append((text, {**meta, "type": "qa", "index": idx}))
    return texts
