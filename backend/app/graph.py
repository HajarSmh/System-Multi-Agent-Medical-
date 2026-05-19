from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from app.state import MedicalState
from app.nodes.supervisor import supervisor_node
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node


def create_graph(with_checkpointer: bool = True):
    """
    Compile le graphe médical.
    - with_checkpointer=True  → pour FastAPI (interrupt() nécessite MemorySaver)
    - with_checkpointer=False → pour LangGraph Studio (gère sa propre persistance)
    """
    builder = StateGraph(MedicalState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    builder.add_edge(START, "supervisor")

    def route_from_supervisor(state: MedicalState) -> str:
        next_agent = state.get("next", "FINISH")
        if next_agent == "FINISH":
            return END
        return next_agent

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            END: END,
        }
    )

    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    if with_checkpointer:
        return builder.compile(checkpointer=MemorySaver())
    else:
        return builder.compile()


# LangGraph Studio importe ce symbole → sans checkpointer
medical_graph = create_graph(with_checkpointer=False)