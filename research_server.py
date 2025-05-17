# research_server.py
import os
import logging
from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
import os
from langchain_tavily import TavilySearch
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_ibm import ChatWatsonx
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

from dotenv import load_dotenv
load_dotenv(override=True)

WATSONX_API_KEY =  os.getenv('WATSONX_APIKEY')
WATSONX_PROJECT_ID =os.getenv('WATSONX_PROJECT_ID')
WATSONX_API_BASE = os.getenv('WATSONX_URL')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

server = Server()

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 8000,
    "min_new_tokens": 1,
    "repetition_penalty": 1.1
}
llm = ChatWatsonx(
    model_id= os.getenv('MODEL_ID'),
    url=WATSONX_API_BASE,
    apikey=WATSONX_API_KEY,
    project_id=WATSONX_PROJECT_ID,
    params=parameters,
)

tavily_search = TavilySearch(
    max_results=5,
    topic="general" 
)

def _tavily_search_fn(query: str) -> str:
    """Wraps the TavilySearch to work as a LangChain tool."""
    logging.info(f"Executing Tavily Search with query: {query}")
    try:
        response = tavily_search.invoke({"query": query})
        formatted_response = "\n---\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in response])
        logging.info(f"Search results: {formatted_response[:500]}...") # Log snippet
        return formatted_response
    except Exception as e:
        logging.error(f"Error during Tavily search: {e}")
        return f"Search failed: {e}"


search_tool = Tool(
    name="Tavily Search",
    func=_tavily_search_fn,
    description="Use this tool to perform real-time web searches for information. Focus your query on marketing trends, competitor analysis, and relevant keywords."
)

@server.agent()
async def research_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    This agent performs market research using web search to find trends,
    competitors, and keywords for a marketing topic.
    """
    logging.info("Research agent received input.")
    if not input or not input[0].parts:
        logging.warning("Received empty input.")
        yield Message(parts=[MessagePart(content="Error: No input received.")])
        return

    user_prompt = input[0].parts[0].content
    logging.info(f"User prompt: {user_prompt}")

    tools = [search_tool]
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True, 
        handle_parsing_errors=True 
    )

    try:
        agent_prompt = f"Perform marketing research for the following topic, focusing on recent trends, competitor activities, and relevant keywords. Use the Tavily Search tool effectively. Summarize your findings.\n\nTopic: {user_prompt}"
        logging.info(f"Running Langchain agent with prompt: {agent_prompt}")
        result = agent.invoke(agent_prompt)
        logging.info(f"Langchain agent result: {result}")
        output_content = str(result.get('output', result) if isinstance(result, dict) else result)
        yield Message(parts=[MessagePart(content=output_content)])

    except Exception as e:
        logging.error(f"Error during research agent execution: {e}", exc_info=True)
        yield Message(parts=[MessagePart(content=f"An error occurred during research: {e}")])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Marketing Research Server")
    server.run(port=8003)