from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.schema import Document

from graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from pydantic import BaseModel, Field
from graph.state import NewsAnalysis

load_dotenv()




llm = ChatOpenAI(temperature=0.5, model="gpt-4.1")
structured_llm_news_analysis = llm.with_structured_output(NewsAnalysis)


async def analysis(state: GraphState) -> Dict[str, Any]:
    print("---FINANCIAL ANALYSIS ---")
    documents = state["documents"]
    answer_language = state["answer_language"]
    
    prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(template="""
You are an expert financial analyst tasked with evaluating whether a series of news items represent a genuine opportunity to trade on the stock market and achieve capital gains.
An "opportunity" is defined as any event that could significantly impact the value of a stock, ETF, or index.

#Instructions
Carefully analyze the news, using both the provided information and your own financial and macroeconomic knowledge.

Assess the potential impact of the news on asset prices, also considering market trends and similar past events.

Assign a score to the identified opportunity.

List all involved assets (stocks or ETFs) and clearly indicate their tickers.

Explain the reasoning behind your score.

Highlight any risks or uncertainties related to the trade.

#Output Format
The score must be between 0 and 5: 0 = insufficient information, 1 = very low opportunity, 5 = maximum opportunity.

List of tickers for the involved assets (e.g., [AAPL, MSFT])

Detailed trading instructions: specify whether to buy or sell, suggest an entry price, stop loss, and take profit, and add a brief justification.

Always answer in {answer_language}.

"""),
        AIMessage(content = documents[0].page_content if documents else "")
    ]
)

    thread_id = state["thread_id"]    
    config = {"configurable": {"thread_id": thread_id}}
    
    chain = prompt | structured_llm_news_analysis
    result = chain.invoke(input = {"answer_language": answer_language},  config=config)
    state["news_analysis"] = result
    
    print(f"{state['rss_title']} - {result.score}/5")
    
    return {"news_analysis": result, "documents": documents, 
            "answer_language": state["answer_language"], "thread_id": thread_id,
            "rss_title": state["rss_title"], "rss_link": state["rss_link"]}
    

if __name__ == "__main__":
    analysis(state={"question": "agent memory", "documents": None})