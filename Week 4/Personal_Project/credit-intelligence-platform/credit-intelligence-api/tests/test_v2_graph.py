from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from v2.lc_graph import build_graph


@tool
def fake_search(query: str) -> str:
    """Search a fake Credit Intelligence knowledge base."""
    return "[credit-doc-test] COV-4201 requires net leverage not to exceed 4.5x."


class ToolCallingModel:
    def invoke(self, messages):
        if isinstance(messages[-1], ToolMessage):
            return AIMessage(content="COV-4201 requires net leverage not to exceed 4.5x [credit-doc-test].")

        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "fake_search",
                    "args": {"query": "What does COV-4201 require?"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )


class DirectModel:
    def invoke(self, messages):
        return AIMessage(content="Hello.")


def test_graph_calls_tool_then_answers():
    graph = build_graph(model=ToolCallingModel(), tools=[fake_search])
    result = graph.invoke({"messages": [("user", "What does COV-4201 require?")]})

    assert any(isinstance(message, ToolMessage) for message in result["messages"])
    assert "4.5x" in result["messages"][-1].content
    assert "[credit-doc-test]" in result["messages"][-1].content


def test_graph_can_finish_without_tool():
    graph = build_graph(model=DirectModel(), tools=[fake_search])
    result = graph.invoke({"messages": [("user", "Hello")]})

    assert result["messages"][-1].content == "Hello."
    assert not any(isinstance(message, ToolMessage) for message in result["messages"])