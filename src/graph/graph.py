from graph.state import GraphState
from graph.nodes.news_scoring import analysis
from graph.nodes.websearch import web_search
from graph.nodes.telegram_notifier import telegram_notify
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.redis import RedisSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from graph.nodes.asset_analysis import human_feedback, asset_analysis
from dotenv import load_dotenv
import os


load_dotenv()

def should_notify(state: GraphState) -> str:
    na = state.get("news_scoring")
    if na is not None and hasattr(na, "score") and na.score >= 1:
        return "NOTIFIER"
    else:
        return END


def create_graph() : 
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    
    
    DB_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    with RedisSaver.from_conn_string(DB_URI) as checkpointer:
    
        checkpointer.setup()
    
        workflow = StateGraph(GraphState)
        workflow.add_node("WEBSEARCH", web_search)
        workflow.add_node("NEWS_ANALYSIS", analysis)
        workflow.add_node("NOTIFIER", telegram_notify)
        workflow.add_node("HUMAN_FEEDBACK", human_feedback)
        workflow.add_node("ASSET_ANALYSIS", asset_analysis)
        
        
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
        workflow.add_edge("NOTIFIER", "ASSET_ANALYSIS")
        workflow.add_edge("ASSET_ANALYSIS", "HUMAN_FEEDBACK")
        workflow.add_edge("HUMAN_FEEDBACK", "ASSET_ANALYSIS")
        workflow.add_edge("ASSET_ANALYSIS", END)
        
        app = workflow.compile(checkpointer=checkpointer, interrupt_before=["HUMAN_FEEDBACK"])
        
    return app


