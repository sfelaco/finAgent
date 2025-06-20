from finrobot.utils import get_current_date, register_keys_from_json
from finrobot.agents.workflow import SingleAssistant
import autogen


if __name__ == "__main__":
    
    # Read OpenAI API keys from a JSON file
    llm_config = {
        "config_list": autogen.config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={"model": ["gpt-4.1"]},
        ),
        "timeout": 120,
        "temperature": 0,
    }

    # Register FINNHUB API keys
    register_keys_from_json("config_api_keys")

    
    
    company = "RGTI"

    assitant = SingleAssistant(
        "Market_Analyst",
        llm_config,
        # set to "ALWAYS" if you want to chat instead of simply receiving the prediciton
        human_input_mode="NEVER",
    )

    assitant.chat(
        f"Use all the tools provided to retrieve information available for {company} upon {get_current_date()}. Analyze the positive developments and potential concerns of {company} "
        "with 2-4 most important factors respectively and keep them concise. Most factors should be inferred from company related news. "
        f"Then make a rough prediction (e.g. up/down by 2-3%) of the {company} stock price movement for next week. Provide a summary analysis to support your prediction."
        f"Usa the italian language"
    )