from typing import Iterable

def trove_search_context(
    queries: Iterable[str],
    retriever=None,
    retriever_tool=None,
    cap: int = 8,
) -> str:
    """
    Generic helper to fetch Trove docs (retriever OR retriever_tool) and return a compact context string.
    Keeps agent code simple; no classes, no protocols.
    """
    docs = []
    for q in queries:
        q = (q or "").strip()
        if not q:
            continue
        try:
            if retriever is not None:
                if hasattr(retriever, "get_relevant_documents"):
                    docs.extend(retriever.get_relevant_documents(q))
                elif hasattr(retriever, "invoke"):
                    docs.extend(retriever.invoke(q))
            elif retriever_tool is not None:
                res = retriever_tool.invoke({"query": q})
                docs.extend(res if isinstance(res, list) else [_wrap_doc(res)])
        except Exception:
            # Don't blow up the caller if retrieval hiccups
            continue

    # De-dup + cap
    unique, seen = [], set()
    for d in docs:
        text = getattr(d, "page_content", str(d)).strip()
        if not text:
            continue
        sig = text[:160]
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(text)
        if len(unique) >= cap:
            break

    return "\n\n---\n\n".join(unique)

def _wrap_doc(x):
    return type("Doc", (), {"page_content": str(x)})()
