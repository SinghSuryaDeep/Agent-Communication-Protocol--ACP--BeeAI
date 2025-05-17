# content_server.py
import logging
from collections.abc import AsyncGenerator
import os
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from crewai import Crew, Task, Agent, LLM


WATSONX_API_KEY =  os.getenv('WATSONX_APIKEY')
WATSONX_PROJECT_ID =os.getenv('WATSONX_PROJECT_ID')
WATSONX_API_BASE = os.getenv('WATSONX_URL')

server = Server()

llm = LLM(
    model= os.getenv('MODEL_ID_2'),
    api_base=WATSONX_API_BASE,
    api_key=WATSONX_API_KEY,
    project_id=WATSONX_PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 8000,
        "min_new_tokens": 1,
        "repetition_penalty": 1.01
    }
)


marketing_agent = Agent(
    role="Expert Marketing Content Strategist",
    goal="Create compelling marketing content outlines or ideas based on provided research.",
    backstory="""You are a seasoned marketing professional with a knack for transforming research
                 findings into actionable and creative content strategies. You excel at understanding
                 market trends and consumer interests to develop engaging materials.""",
    verbose=True,
    allow_delegation=False, 
    llm=llm,
    max_retry_limit=3
)


@server.agent()
async def content_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    This agent generates marketing content (e.g., outlines, ideas) based on
    provided research and a marketing topic.
    """
    logging.info("Content agent received input.")
    if not input or not input[0].parts:
        logging.warning("Received empty input.")
        yield Message(parts=[MessagePart(content="Error: No input received.")])
        return
    input_content = input[0].parts[0].content
    logging.info(f"Received input content:\n{input_content[:500]}...") # Log snippet
    task_description = f"""
    Analyze the following input which contains an original marketing request and research findings.

    Based on this information, generate a detailed outline for a marketing blog post
    OR a list of creative social media post ideas. Choose the format that seems most
    appropriate based on the implicit goal of the request and the research findings.

    Ensure the generated content incorporates key trends and keywords identified in the research.
    Make the output clear, structured, and ready for a copywriter to expand upon.

    Input:
    ---
    {input_content}
    ---
    """

    content_task = Task(
        description=task_description,
        expected_output="A structured blog post outline or a list of social media post ideas, incorporating research insights.",
        agent=marketing_agent, 
    )
    crew = Crew(
        agents=[marketing_agent],
        tasks=[content_task],
        verbose=True
    )
    logging.info("Starting Crew execution...")
    try:
        task_output = await crew.kickoff_async()
        logging.info("Crew execution completed successfully.")
        logging.info(f"Crew output:\n{task_output}")
        yield Message(parts=[MessagePart(content=str(task_output))])

    except Exception as e:
        logging.error(f"Error during Crew execution: {e}", exc_info=True)
        yield Message(parts=[MessagePart(content=f"An error occurred during content generation: {e}")])
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Marketing Content Server...")
    server.run(port=8001)