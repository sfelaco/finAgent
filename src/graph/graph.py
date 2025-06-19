from graph.state import GraphState
from graph.nodes.news_analysis import analysis
from graph.nodes.websearch import web_search
from graph.nodes.telegram_notifier import telegram_notify
from langgraph.graph import END, StateGraph

def should_notify(state: GraphState) -> bool:
    na = state.get("news_analysis")
    if na is not None and hasattr(na, "score") and na.score >= 4:
        return "NOTIFIER"
    else:
        return END


def create_graph() : 
    workflow = StateGraph(GraphState)
    workflow.add_node("WEBSEARCH", web_search)
    workflow.add_node("NEWS_ANALYSIS", analysis)
    workflow.add_node("NOTIFIER", telegram_notify)
    
    workflow.set_entry_point("WEBSEARCH")
    workflow.add_edge("WEBSEARCH", "NEWS_ANALYSIS")

    workflow.add_conditional_edges(
        "NEWS_ANALYSIS",
        should_notify,
        {
            "NOTIFIER": "NOTIFIER",
            END: END
        }
    )
    workflow.add_edge("NOTIFIER", END)
    
    app = workflow.compile()
    return app


