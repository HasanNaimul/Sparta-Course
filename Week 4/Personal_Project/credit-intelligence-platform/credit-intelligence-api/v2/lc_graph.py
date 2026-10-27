"""LangGraph workflow for Credit Intelligence."""
import grounding
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from v2.lc_model import chat_model
from v2.lc_tools import search_knowledge_base

SYSTEM_PROMPT = (
    "You are a careful credit intelligence analyst. "
    "Use search_knowledge_base whenever the user asks about borrowers, facilities, covenants, policies or credit-risk information. "
    "Use only retrieved evidence. Do not use outside knowledge or infer missing facts. "
    "The evidence must explicitly contain the specific fact requested. "
    "Explicit negative evidence counts as an answer. "
    f'If the tool returns "{grounding.REFUSAL}", or the retrieved evidence does not explicitly answer the question, reply exactly and only: "{grounding.REFUSAL}" '
    "Otherwise answer only the question asked, keep the answer concise and cite the supporting document id in square brackets."
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