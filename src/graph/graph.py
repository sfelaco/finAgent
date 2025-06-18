from graph.state import GraphState
from graph.nodes.news_analysis import analysis
from graph.nodes.websearch import web_search
from langgraph.graph import END, StateGraph




def create_graph() : 
    workflow = StateGraph(GraphState)
    workflow.add_node("WEBSEARCH", web_search)
    workflow.add_node("NEWS_ANALYSIS", analysis)
    
    workflow.set_entry_point("WEBSEARCH")
    workflow.add_edge("WEBSEARCH", "NEWS_ANALYSIS")
    workflow.add_edge("NEWS_ANALYSIS", END)
    
    app = workflow.compile()
    return app


