import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.cache import Cache
from autogen.agentchat import ChatResult

from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.data_source.finnhub_utils import FinnHubUtils
from finrobot.functional.charting import MplFinanceUtils
from finrobot.agents.workflow import SingleAssistantShadow

from textwrap import dedent
from matplotlib import pyplot as plt
from PIL import Image


if __name__ == "__main__":
    
    config_list_4v = autogen.config_list_from_json(
        "../../OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4.1"],
        },
    )
    config_list_gpt4 = autogen.config_list_from_json(
        "../../OAI_CONFIG_LIST",
        filter_dict={
            "model": ["gpt-4.1"],
        },
    )

    # Register FINNHUB API keys for later use
    register_keys_from_json("../../config_api_keys")

    # Intermediate results/charts will be saved in this directory
    working_dir = "./coding"
    os.makedirs(working_dir, exist_ok=True)
    
    market_analyst = MultimodalConversableAgent(
    name="Market_Analyst",
    max_consecutive_auto_reply=10,
    llm_config={"config_list": config_list_4v, "temperature": 0},
    system_message=dedent("""
        Your are a Market Analyst. Your task is to analyze the financial data and market news.
        Reply "TERMINATE" in the end when everything is done.
        """)
    )
    
    data_provider = AssistantAgent(
        name="Data_Provider",
        llm_config={"config_list": config_list_gpt4, "temperature": 0},
        system_message=dedent("""
            You are a Data Provider. Your task is to provide charts and necessary market information.
            Use the functions you have been provided with.
            Reply "TERMINATE" in the end when everything is done.
            """)
    )
    user_proxy = UserProxyAgent(
        name="User_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "") and x.get(
            "content", "").endswith("TERMINATE"),
        code_execution_config={
            "work_dir": working_dir,
            "use_docker": False
        },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    )
    
    pdf_maker = SingleAssistantShadow(
        "Expert_Investor",
        llm_config={"config_list": config_list_gpt4, "temperature": 0},
        max_consecutive_auto_reply=None,
        human_input_mode="TERMINATE",
        system_message=dedent("""
            You are an Expert Investor. Your task is to analyze the financial data and market news.
            Use the information provided by the Data Provider and reply "TERMINATE" in the end when everything is done.
            """),
    )

    
    from finrobot.toolkits import register_toolkits

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
    register_toolkits(tools, data_provider, user_proxy)
    
    
    
    company = "BRNT"

    with Cache.disk() as cache:  # image cannot be cached
        list_chat: list[ChatResult] = autogen.initiate_chats(
            [
                {
                    "sender": user_proxy,
                    "recipient": data_provider,
                    "message": dedent(f"""
                    Gather information available upon {get_current_date()} for {company}, 
                    including its recent market news and a candlestick chart of the stock 
                    price trend. Save the chart in `{working_dir}/result.jpg`
                    """),           # As currently AutoGen has the bug of not respecting `work_dir` when using function call, we have to specify the directory
                    "clear_history": True,
                    "silent": False,
                    "summary_method": "last_msg",
                },
                {
                    "sender": user_proxy,
                    "recipient": market_analyst,
                    "message": dedent(f"""
                    With the stock price chart provided, along with recent market news of {company}, 
                    analyze the recent fluctuations of the stock and the potential relationship with 
                    market news. Provide your predictive analysis for the stock's trend in the coming 
                    week and propose a trading strategy based on your analysis, proposing a price target,
                    stop-loss, and take-profit levels. 
                    
                    Use the Italian language.
                    Reply TERMINATE when the task is done.
                    """),
                    "max_turns": 1,  # max number of turns for the conversation
                    "summary_method": "last_msg",
                    # cheated here for stability
                    "carryover": f"<img {working_dir}/result.jpg>"
                }            
                
            ]
        )
        
        
        report = list_chat[-1].chat_history[-1]["content"]
        message = dedent(
        f"""
          {report}
        
          Format the report it into a pdf.
        - All your file operations should be done in "{working_dir}". 
        - Display any image in the chat once generated.
          Reply TERMINATE when the task is done.
        """
       )       
        
        pdf_maker.chat(message, use_cache=True, max_turns=50,
               summary_method="last_msg" )
        
        

        # img = Image.open(f"{working_dir}/result.jpg")
        # plt.imshow(img)
        # plt.axis("off")  # Hide the axes
        # plt.show()