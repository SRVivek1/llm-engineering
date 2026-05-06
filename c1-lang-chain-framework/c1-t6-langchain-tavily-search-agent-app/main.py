import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from tavily import TavilyClient

# Load .env 
load_dotenv()


# Tavily search tool
tavily_client = TavilyClient()


@tool
def search(query: str) -> str:
    """
    Tool that Search the web for the given query and return the results.

    Args:
        query (str): The search query.
    Returns:
        str: The search results.
    """
    print(f"Searching for: {query}")

    #Integrate with Tavily Search API
    response = tavily_client.search(query=query)
    
    return f"Result: {response}"


def main():
    print("Hello from c1-t6-langchain-tavily-search-agent-app!")

    model_name = os.getenv("OLLAMA_QWEN_MODEL", "gemma3:270m")

    # tools
    tool_list = [search]

    llm = ChatOllama(model= model_name)
    agent = create_agent(model=llm, tools=tool_list)

    resp = agent.invoke({"messages":[HumanMessage(content="What is the weather like in Delhi today?")]})
    #print(f"Response - ToolMessage: {resp["messages"][2].content}")
    print(resp)


if __name__ == "__main__":
    main()
