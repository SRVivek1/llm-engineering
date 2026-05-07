# Section-3 The GIST of AI agents

## Video-18 : Env. setup for LangChan Search agent project

### Create a new project and initialize

- mkdir react-search-agent
- uv init

### Add dependencies

- uv add langchain langchain-ollama langchain-tavily tavily-python
- uv add python-dotenv black isort

#### What is langchn tavily ?

- Reference: tavily.com
- Provides API for the agent with fast, secure and reliable web access.

- Other useful APIs provided by tavily are:
  - Tavily Extract
  - Tavily Crawl
  - Tavily Map

- And by the way, this is actually the most popular choice for integrating a web search into an AI agent.
- They're even featured in the official documentation of LangChain as the default service for a search engine when implementing agents.

#### What is tavily-python ?

- Explain in details at level-3 content level for intermediate level engineers.

### How to integrate Talivy to you lngchain app.

- Export the talivy api key in .env file.
- export TALIVY_API_KEY=--dummy-key--

### Defining tool function uing langchain to search internet

### Explain @tool decorator

- What is the purpose of using @tool decorator.
- What is it execution lifecycle.

- Execution Lifecycle
  1. LLM is called with the input request.
     - LLM Model will also receied the information of availale tools.
  2. Based on prompt, LLM decides which Tool to use to fullfill the request.
  3. LangChain then receives the instruction and executed the tool.
     - The result of the tool is then structured in the final respose as "ToolMessage".
  4. Now LLM is called with the response, and because LLM has all the info it choose to return the response and not to invoke anyother tool.

### Explains the inbuild Tavily tools available in langchain_tavily dependency
- TavilySearch: Inbuild tool for web searching.


### Fromatting the response of LLM using 'Pydantic' library.
- What is Pydantic ?
  - Pydantic is the most widely used data validation library for Python.
  - Fast and extensible, Pydantic plays nicely with your linters/IDE/brain. 
  - Define how data should be in pure, canonical Python 3.9+; validate it with Pydantic.


- Example:
  - Code:
    from pydantic import BaseModel, PositiveInt
    