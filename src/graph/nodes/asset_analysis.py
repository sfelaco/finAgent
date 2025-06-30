from langgraph.prebuilt import ToolNode
from finrobot.data_source.finnhub_utils import FinnHubUtils
from finrobot.functional.charting import MplFinanceUtils
from graph.state import GraphState

tools = [
    {
        "function": FinnHubUtils.get_company_news,
        "name": "get_company_news",
        "description": "retrieve market news related to designated company"
    },
    {
        "function": MplFinanceUtils.plot_stock_price_chart,
        "name": "plot_stock_price_chart",
        "description": "plot stock price chart of designated company"
    }
]


tool_node = ToolNode([])

def human_feedback(state: GraphState) -> GraphState:
    """
    Process human feedback and prepare for asset analysis.
    """
    print("---human_feedback---")
    asset = state.get("asset_to_analyze", "Unknown")
    thread_id = state.get("thread_id", "Unknown")
    print(f"Processing human feedback for asset: {asset}, thread_id: {thread_id}")
    
    # Return the state unchanged, this is just a processing step
    return state


def asset_analysis(state: GraphState) -> GraphState:
    """
    Analyze the asset based on the provided state.
    This function can be extended to include more complex analysis logic.
    """
    print("---asset_analysis---")
    
    # Get the asset to analyze from the state
    asset = state.get("asset_to_analyze", "AAPL")  # Default to Apple if no asset is set
    print(f"Analyzing asset: {asset}")
    
    # try:
    #     # Get company news
    #     news = FinnHubUtils.get_company_news(asset)
        
    #     if news is not None and not news.empty:
    #         print(f"News for {asset}:")
    #         for i in range(min(3, len(news))):  # Show up to 3 news items
    #             summary = news.iloc[i]['summary'] if 'summary' in news.columns else "No summary available"
    #             print(f"- {summary}")
    #     else:
    #         print(f"No news found for {asset}")
        
    #     # Plot stock price chart
    #     try:
    #         MplFinanceUtils.plot_stock_price_chart(asset)
    #         print(f"Stock price chart generated for {asset}")
    #     except Exception as chart_error:
    #         print(f"Could not generate chart for {asset}: {str(chart_error)}")
            
    # except Exception as e:
    #     print(f"Error during asset analysis: {str(e)}")
    
    # Return the updated state
    return state