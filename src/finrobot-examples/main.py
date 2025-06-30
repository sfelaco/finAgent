from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant
import autogen
from datetime import datetime, timedelta
from finrobot.data_source.yfinance_utils import YFinanceUtils


if __name__ == "__main__":
    
    # # Read OpenAI API keys from a JSON file
    # llm_config = {
    #     "config_list": autogen.config_list_from_json(
    #         "OAI_CONFIG_LIST",
    #         filter_dict={"model": ["gpt-4.1"]},
    #     ),
    #     "timeout": 120,
    #     "temperature": 0,
    # }

    # # Register FINNHUB API keys
    # register_keys_from_json("config_api_keys")

    
    
    # company = "RGTI"

    # assitant = SingleAssistant(
    #     "Market_Analyst",
    #     llm_config,
    #     # set to "ALWAYS" if you want to chat instead of simply receiving the prediciton
    #     human_input_mode="NEVER",
    # )

    # assitant.chat(
    #     f"Use all the tools provided to retrieve information available for {company} upon {get_current_date()}. Analyze the positive developments and potential concerns of {company} "
    #     "with 2-4 most important factors respectively and keep them concise. Most factors should be inferred from company related news. "
    #     f"Then make a rough prediction (e.g. up/down by 2-3%) of the {company} stock price movement for next week. Provide a summary analysis to support your prediction."
    #     f"Usa the italian language"
    # )

    # Example: Test YFinanceUtils.get_stock_data for the last month
    symbol = "ENL.F"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    df = YFinanceUtils.get_stock_data(
        symbol,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    print(df)

    # Example: Test MplFinanceUtils.plot_stock_price_chart for the last month
    # from finrobot.functional.charting import MplFinanceUtils
    # output_path = "result_chart.png"
    # MplFinanceUtils.plot_stock_price_chart(
    #     symbol,
    #     start_date.strftime("%Y-%m-%d"),
    #     end_date.strftime("%Y-%m-%d"),
    #     save_path=output_path
    # )
    # print(f"Chart saved to {output_path}")