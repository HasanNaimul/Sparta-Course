"""LangChain tools for Credit Intelligence."""

from langchain_core.tools import ToolException, tool

import gate
import grounding
import knowledge_store as knowledge
from config import settings


@tool
def search_knowledge_base(query: str) -> str:
    """Search the Credit Intelligence knowledge base for borrower, facility, covenant, policy and credit-risk information."""

    try:
        results = knowledge.search(query, top_k=5)
    except RuntimeError as error:
        raise ToolException(f"Knowledge search failed: {error}") from error

    usable = [r for r in results if gate.is_usable(r, settings.relevance_floor, settings.rerank_floor)]

    if not usable:
        return grounding.REFUSAL

    return "\n\n".join(
        f"[{r['doc_id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
        for r in usable
    )