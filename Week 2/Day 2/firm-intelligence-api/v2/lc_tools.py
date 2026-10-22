"""Our search tool, written for LangChain.

Retrieval is wrapped, not rewritten:
the tool calls our existing knowledge_store.search().
"""

from langchain_core.tools import ToolException, tool

from routers import knowledge_store as knowledge


@tool
def search_knowledge_base(query: str) -> str:
    """Search the firm intelligence knowledge base for documents relevant to firms, jurisdictions, compliance or market commentary."""
    try:
        results = knowledge.search(query, top_k=3)
    except RuntimeError as error:
        raise ToolException(f"Error: {error}") from error

    if not results:
        return "No relevant documents found."

    return "\n\n".join(f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}" for r in results)