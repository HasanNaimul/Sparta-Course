"""LangGraph workflow for Credit Intelligence."""

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from v2.lc_model import chat_model
from v2.lc_tools import search_knowledge_base

SYSTEM_PROMPT = (
    "You are a careful credit intelligence analyst. "
    "Use the search_knowledge_base tool whenever the user asks about borrowers, facilities, covenants, policies or credit-risk information. "
    "Use only retrieved evidence for factual Credit Intelligence answers. "
    "Do not invent missing facts. If the retrieved evidence does not answer the question, say that the provided documents do not answer it. "
    "Cite supporting document ids in square brackets."
)

TOOLS = [search_knowledge_base]
MODEL = chat_model().bind_tools(TOOLS)


def call_model(state: MessagesState) -> dict:
    response = MODEL.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
    return {"messages": [response]}


builder = StateGraph(MessagesState)

builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "model")

graph = builder.compile()