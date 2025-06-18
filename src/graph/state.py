from typing import List, TypedDict
from pydantic import BaseModel, Field
from langchain.schema import Document

class NewsAnalysis(BaseModel):

    score: int = Field(
        description="The score of the opportunity where 1 is the lowest value and 5 is the highest"
    )
    assets: List[str] = Field(
        description="The list of stocks or ETF involved"
    )
    description: str = Field(
        description="A brief description of the opportunity and how I can make a profit from it and the motivation of the score"
    )

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        rss_title: title of the RSS feed
        rss_link: link to the RSS feed
        documents: documents retrieved from the web search
        answer_language: language of the answer
        news_analysis: answer to the news analysis
        thread_id: identifier of the thread processing the request
    """

    rss_title: str
    rss_link: str
    documents: Document
    answer_language: str
    news_analysis: NewsAnalysis
    thread_id: int

