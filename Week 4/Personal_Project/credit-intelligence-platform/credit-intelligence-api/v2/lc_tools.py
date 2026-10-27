"""LangChain tools for Credit Intelligence."""

from langchain_core.tools import ToolException, tool

import knowledge_store as knowledge


@tool
def search_knowledge_base(query: str) -> str:
    """Search the Credit Intelligence knowledge base for borrower, facility, covenant, policy and credit-risk information."""

    try:
        results = knowledge.search(query, top_k=5)
    except RuntimeError as error:
        raise ToolException(f"Knowledge search failed: {error}") from error

    if not results:
        return "No relevant documents found."

    return "\n\n".join(
        f"[{r['doc_id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
        for r in results
    )