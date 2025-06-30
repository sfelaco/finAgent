from typing import List, TypedDict
from pydantic import BaseModel, Field
from langchain.schema import Document

class NewsScore(BaseModel):

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
        news_scoring: answer to the news analysis
        thread_id: identifier of the thread processing the request
        asset_to_analyze: the asset to analyze in the thread
        analysis_path: path to the analysis results
    """

    rss_title: str
    rss_link: str
    documents: Document
    answer_language: str
    news_scoring: NewsScore
    thread_id: int
    asset_to_analyze: str
    analysis_path: str
