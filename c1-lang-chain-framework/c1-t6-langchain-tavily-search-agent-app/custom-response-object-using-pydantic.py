import os
from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# from tavily import TavilyClient
from langchain_tavily import TavilySearch


# Pyndatic custom response model and data validation
from pydantic import BaseModel, Field

# Load .env
load_dotenv()


# Response model using Pydantic
class Source(BaseModel):
    """Schema for the source used by the agent"""
    url: str = Field(description="The URL of the source")


class AgentResponse(BaseModel):
    """Schema for the Agent response and sources"""

    answer: str = Field(description="The agent's answer to the query.")
    sources: List[Source] = Field(default_factory=list, description="List of sources used to generate the answer.")


# LLM Model

# Ollama
"""
# GPT-OSS-120B Limitation:

langchain.agents.structured_output.StructuredOutputValidationError: Failed to parse structured output for tool 'AgentResponse': Native structured output expected valid JSON for AgentResponse, but parsing failed: Expecting value: line 1 column 1 (char 0)..
During task with name 'model' and id '6f65b4fc-59c8-cad3-4d8c-0e14f6a5d1ca'
"""
#llm_model = ChatOllama(model=os.getenv("OLLAMA_CLOUD_GPT_OSS_120B"), temperature=0.0)

"""
# GEMMA4_31B Limitation:

The LLM didn't procssed the AgentResponse schema and retuned usual text response.
"""
#llm_model = ChatOllama(model=os.getenv("OLLAMA_CLOUD_GEMMA4_31B"), temperature=0.0)


# GROQ Model
"""
 GROQ Limitation:
 groq.BadRequestError: Error code: 400 - {'error': {'message': 'json mode cannot be combined with tool/function calling', 'type': 'invalid_request_error', 'param': 'response_format'}}
"""
#llm_model = ChatGroq(model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"), api_key=os.getenv("GROQ_API_KEY"))


# Google AI Studio Model
# Note:gemini-3.1-pro-preview - Is returing the expected 'structured_response' in LLM response.
llm_model = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_GEMINI_3_1_PRO_PREVIEW"))



# Tavily built-in search tool.
inbuilt_tools = [TavilySearch(max=3)]

# Create the agent
#Pass the response class for the agent
agent = create_agent(model=llm_model, tools=inbuilt_tools, response_format=AgentResponse)

def main():
    print(
        "Hello from c1-t6-langchain-tavily-search-agent-app, with inbuilt Tavily Search tool!"
    )

    #search_query = "Search for 3 job posting for an AI engineer in bangalore city with langchain skills on linkedin."
    search_query = "Ai jobs in bangalore with langchain skills on linkedin."
    result = agent.invoke({"messages": HumanMessage(content=search_query)})

    print(result)
    print("\n\n********************\nStructured Response:\n\n")

    print(result["structured_response"])


if __name__ == "__main__":
    main()
