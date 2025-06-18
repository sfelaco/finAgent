from typing import Any, Dict

from dotenv import load_dotenv
from langchain.schema import Document
from langchain_tavily import TavilySearch

from graph.state import GraphState

load_dotenv()
web_search_tool = TavilySearch(max_results=3)


async def web_search(state: GraphState) -> Dict[str, Any]:
    print("---WEB SEARCH---")
    rss_title = state["rss_title"]
    
    thread_id = state["thread_id"]    
    config = {"configurable": {"thread_id": thread_id}}
    tavily_response = web_search_tool.invoke({"query": rss_title},config=config)
    tavily_results = tavily_response["results"]
    joined_tavily_result = "\n".join(   
        [tavily_result["content"] for tavily_result in tavily_results]
    )
    web_results = Document(page_content=joined_tavily_result)

    documents = [web_results]
    return {"documents": documents, "rss_title": rss_title, "answer_language": state["answer_language"],
            "rss_link": state["rss_link"], "thread_id": state["thread_id"]}


if __name__ == "__main__":
    web_search(state={"question": "agent memory", "documents": None})
