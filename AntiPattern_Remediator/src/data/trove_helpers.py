from typing import Iterable, Any, List, Optional

def trove_search_context(
    queries: Iterable[str],
    retriever: Optional[object] = None,
    retriever_tool: Optional[object] = None,
    cap: int = 8,
    signature_len: int = 160,
) -> str:
    """
    Fetch Trove docs (retriever OR retriever_tool) and return a compact context string.
    - Prefers a single retriever with .invoke(query) or .get_relevant_documents(query)
    - Falls back to retriever_tool.invoke({"query": ...})
    - Deduplicates by the first `signature_len` chars and caps at `cap`
    """
    # Normalize & de-dupelication queries (preserve order)
    qlist = [q.strip() for q in queries if q and q.strip()]
    qlist = list(dict.fromkeys(qlist))

    docs: List[Any] = []
    for q in qlist:
        try:
            if retriever is not None:
                if hasattr(retriever, "invoke"):
                    res = retriever.invoke(q)  # Runnable-style retrievers
                elif hasattr(retriever, "get_relevant_documents"):
                    # Try to pass cap as max_results if supported (TinyDB nicety)
                    try:
                        res = retriever.get_relevant_documents(q, max_results=cap)  # TinyDB supports this
                    except TypeError:
                        res = retriever.get_relevant_documents(q)
                else:
                    res = []
            elif retriever_tool is not None:
                res = retriever_tool.invoke({"query": q})
            else:
                res = []
        except Exception:
            res = []

        if isinstance(res, list):
            docs.extend(res)
        elif res:
            docs.append(_wrap_doc(res))


    unique: List[str] = []
    seen: set[str] = set()
    for d in docs:
        text = _extract_text(d)
        if not text:
            continue
        sig = text[:signature_len]
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(text)
        if len(unique) >= cap:
            break

    return "\n\n---\n\n".join(unique)


def _extract_text(doc: Any) -> str:
    if doc is None:
        return ""
    if hasattr(doc, "page_content"):
        return str(getattr(doc, "page_content"))
    if isinstance(doc, dict):
        for key in ("content", "text", "description", "title", "body", "page_content"):
            if key in doc:
                return str(doc[key])
    return str(doc).strip()


def _wrap_doc(x: Any):
    return type("Doc", (), {"page_content": str(x)})()
