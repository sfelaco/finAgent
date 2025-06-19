import os
import pytest
from unittest.mock import patch
from graph.nodes.telegram_notifier import telegram_notify
from graph.state import GraphState, NewsAnalysis

@patch("graph.nodes.telegram_notifier.requests.post")
def test_telegram_notify_success(mock_post):
    # Arrange
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    mock_post.return_value.status_code = 200
    na = NewsAnalysis(score=4, assets=["AAPL", "MSFT"], description="Test descrizione")
    state = GraphState(rss_title="Titolo di test", rss_link="https://example.com/news", news_analysis=na)

    # Act
    result = telegram_notify(state)

    # Assert
    assert result == {}
    assert mock_post.called
    args, kwargs = mock_post.call_args
    assert "sendMessage" in args[0]
    assert state["rss_title"] in kwargs["data"]["text"]
    assert state["rss_link"] in kwargs["data"]["text"]
    assert "AAPL" in kwargs["data"]["text"]

@patch("graph.nodes.telegram_notifier.requests.post")
def test_telegram_notify_no_token(mock_post):
    # Arrange
    if "TELEGRAM_BOT_TOKEN" in os.environ:
        del os.environ["TELEGRAM_BOT_TOKEN"]
    if "TELEGRAM_CHANNEL_ID" in os.environ:
        del os.environ["TELEGRAM_CHANNEL_ID"]
    na = NewsAnalysis(score=2, assets=["GOOG"], description="No token test")
    state = GraphState(rss_title="Titolo", rss_link="https://example.com", news_analysis=na)

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        telegram_notify(state)
    assert "Telegram token o channel id non configurati" in str(excinfo.value)
    assert not mock_post.called
    
@patch("graph.nodes.telegram_notifier.requests.post")
def test_telegram_notify_no_arg(mock_post):
    # Arrange
    if "TELEGRAM_BOT_TOKEN" in os.environ:
        del os.environ["TELEGRAM_BOT_TOKEN"]
    if "TELEGRAM_CHANNEL_ID" in os.environ:
        del os.environ["TELEGRAM_CHANNEL_ID"]
    state = None

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        telegram_notify(state)
    assert "Telegram token o channel id non configurati" in str(excinfo.value)
    assert not mock_post.called    