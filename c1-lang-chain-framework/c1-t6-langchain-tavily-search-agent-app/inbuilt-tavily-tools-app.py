import os
from unittest import result

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

# from tavily import TavilyClient
from langchain_tavily import TavilySearch

# Load .env
load_dotenv()


# LLM Model
ollama = ChatOllama(model=os.getenv("OLLAMA_QWEN_MODEL", "qwen3.5:0.8b"))
# Tavily built-in search tool.
inbuilt_tools = [TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))]

# Create the agent
agent = create_agent(model=ollama, tools=inbuilt_tools)

def main():
    print(
        "Hello from c1-t6-langchain-tavily-search-agent-app, with inbuilt Tavily Search tool!"
    )

    #search_query = "Search for 3 job posting for an AI engineer in bangalore city with langchain skills on linkedin."
    search_query = "Anthropic latest AI models"
    result = agent.invoke({"messages": [HumanMessage(content=search_query)]})

    print(result)


if __name__ == "__main__":
    main()
