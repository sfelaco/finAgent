from finrobot.data_source.finnhub_utils import FinnHubUtils
from finrobot.utils import register_keys_from_json
from datetime import datetime, timedelta

if __name__ == "__main__":
    # Register FINNHUB API keys
    register_keys_from_json("../../config_api_keys")

    # Test get_company_news
    company = "TSLA"
    today = datetime.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    news = FinnHubUtils.get_company_news(company, start_date=yesterday, end_date=today)
    print(f"News for {company}:")
    for i in range(len(news)):
        print(news.iloc[[i]]['summary'].values[0])
