"""LangGraph agent pipeline cho Vinhomes AI Advisor (BAN_THIET_KE_V2 Mục 6).

Flow:
  START → intent_node → rag_node (nếu cần) → profile_node → llm_node → END

Routing:
  - intent == handover/greeting/out_of_scope → bỏ qua RAG, vẫn chấm profile.
  - còn lại → rag_node lấy context → profile_node chấm điểm → llm_node trả lời.
"""

from langgraph.graph import END, StateGraph

from src.agents.nodes.intent_node import intent_node
from src.agents.nodes.llm_node import llm_node
from src.agents.nodes.profile_node import profile_node
from src.agents.nodes.rag_node import rag_node
from src.agents.state import AgentState


def _route_after_intent(state: AgentState) -> str:
    """Sau intent_node: các intent có fixed response thì skip RAG."""
    if state.get("trigger_handover") or state.get("intent") in (
        "greeting",
        "out_of_scope",
        "handover",
        "privacy",
    ):
        return "profile"
    return "rag"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent", intent_node)
    graph.add_node("rag", rag_node)
    graph.add_node("profile", profile_node)
    graph.add_node("llm", llm_node)

    graph.set_entry_point("intent")
    graph.add_conditional_edges("intent", _route_after_intent, {"rag": "rag", "profile": "profile"})
    graph.add_edge("rag", "profile")
    graph.add_edge("profile", "llm")
    graph.add_edge("llm", END)

    return graph.compile()


agent = build_graph()
