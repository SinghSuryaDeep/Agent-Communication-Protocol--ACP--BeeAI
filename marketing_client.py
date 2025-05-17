# client.py
import asyncio
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart
from colorama import Fore, init
import os
init()

async def run_marketing_workflow(marketing_topic: str) -> None:
    """
    Orchestrates the marketing workflow:
    1. Researches the topic using the research_agent (Server 1).
    2. Generates content based on research using the content_agent (Server 2).
    """
    print(Fore.CYAN + f"--- Starting Marketing Workflow for: {marketing_topic} ---" + Fore.RESET)
    async with Client(base_url="http://localhost:8003") as research_client, \
               Client(base_url="http://localhost:8001") as content_client:

        print(Fore.LIGHTMAGENTA_EX + "\n--- Step 1: Researching Marketing Topic ---" + Fore.RESET)
        try:
            input_message = Message(parts=[MessagePart(content=marketing_topic)])
            run1 = await research_client.run_sync(
                agent="research_agent",
                input=[input_message] 
            )
            if run1.output and run1.output[0].parts:
                research_output = run1.output[0].parts[0].content
                print(Fore.LIGHTMAGENTA_EX + "Research Complete. Output Preview:" + Fore.RESET)
                print(Fore.LIGHTMAGENTA_EX + research_output[:500] + "..." + Fore.RESET)
            else:
                research_output = "No research results found."
                print(Fore.RED + "Research failed or returned no output." + Fore.RESET)

        except Exception as e:
            print(Fore.RED + f"Error during research step: {e}" + Fore.RESET)
            research_output = f"Error occurred during research: {e}"
        print(Fore.YELLOW + "\n--- Step 2: Generating Marketing Content ---" + Fore.RESET)
        content_input_text = f"""
        Original Marketing Request: {marketing_topic}

        Research Findings:
        ---
        {research_output}
        ---

        Based on the above, generate the requested marketing content (blog outline or social media ideas).
        """
        try:
            input_message_content = Message(parts=[MessagePart(content=content_input_text)])
            run2 = await content_client.run_sync(
                agent="content_agent",
                input=[input_message_content] 
            )
            if run2.output and run2.output[0].parts:
                final_content = run2.output[0].parts[0].content
                print(Fore.YELLOW + "\n--- Final Generated Marketing Content ---" + Fore.RESET)
                print(Fore.YELLOW + final_content + Fore.RESET)
            else:
                 print(Fore.RED + "Content generation failed or returned no output." + Fore.RESET)

        except Exception as e:
            print(Fore.RED + f"Error during content generation step: {e}" + Fore.RESET)
            print(Fore.RED + f"Final Output: An error occurred: {e}" + Fore.RESET)
        print(Fore.CYAN + "\n--- Marketing Workflow Completed ---" + Fore.RESET)

if __name__ == "__main__":
    topic = "Marketing strategies for launching a new plant-based food delivery service in 2025"
    asyncio.run(run_marketing_workflow(topic))