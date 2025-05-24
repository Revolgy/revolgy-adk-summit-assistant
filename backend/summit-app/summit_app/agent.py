# Revolgy Business Solutions, a.s.

from google.adk.agents import Agent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool
from google.adk.tools import google_search
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
import os
import json

from summit_app import prompt

APP_NAME = "summit_app"
MODEL = "gemini-2.5-pro-preview-05-06"
DATASTORE_DOCS_ID = os.getenv("VERTEXAI_DATASTORE_DOCS_ID", "")
DATASTORE_PROD_RELEASES_ID = os.getenv("VERTEXAI_DATASTORE_PRODUCT_RELEASES_ID", "")
DATASTORE_APIS_ID = os.getenv("VERTEXAI_DATASTORE_APIS_ID", "")
USER_ID = "user_001"
SESSION_ID = "session_001"
session_service = InMemorySessionService()

# Retrieve summit information from a JSON file
def get_summit_info():
    try:
        with open("summit_app/summit_details.json") as f:
            summit_data = json.load(f)
        return summit_data
    except FileNotFoundError:
        print(f"Error retrieving summit information.")
        return None

summit_agent = Agent(
    name="summit_agent",
    model=MODEL,
    tools=[get_summit_info],
    instruction=prompt.summit_app_instruction_prompt,
    description="A helpful assistant for Google Cloud Summit Prague 2025.",
)

vertex_search_tool_docs = VertexAiSearchTool(data_store_id=DATASTORE_DOCS_ID)

gcp_docs_agent = Agent(
    name="gcp_docs_agent",
    model=MODEL,
    tools=[vertex_search_tool_docs],
    instruction=f"""You are a helpful assistant that answers questions based on information found in the document store: {DATASTORE_DOCS_ID}.
    Use the search tool to find relevant information before answering.
    If the answer isn't in the documents, say that you couldn't find the information.
    """,
    description="Answers questions using a specific Vertex AI Search datastore.",
)

vertex_search_tool_product_releases = VertexAiSearchTool(data_store_id=DATASTORE_PROD_RELEASES_ID)

gcp_prod_releases_agent = Agent(
    name="gcp_prod_releases_agent",
    model=MODEL,
    tools=[vertex_search_tool_product_releases],
    instruction=f"""You are a helpful assistant that answers questions based on information found in the document store: {DATASTORE_PROD_RELEASES_ID}.
    Use the search tool to find relevant information before answering.
    If the answer isn't in the documents, say that you couldn't find the information.
    """,
    description="Answers questions about Google Cloud Product releases.",
)

vertex_search_tool_apis = VertexAiSearchTool(data_store_id=DATASTORE_APIS_ID)

gcp_apis_agent = Agent(
    name="gcp_apis_agent",
    model=MODEL,
    tools=[vertex_search_tool_apis],
    instruction=f"""You are a helpful assistant that answers questions based on information found in the document store: {DATASTORE_APIS_ID}.
    Use the search tool to find relevant information before answering.
    If the answer isn't in the documents, say that you couldn't find the information.
    """,
    description="Answers questions about Google Cloud APIs.",
)

# Use Google Search to find generic information on the web as a fallback
google_search_agent = Agent(
    name="google_search_agent",
    model=MODEL,
    tools=[google_search],
    instruction="""You are a helpful assistant that answers questions using Google Search.
    Always use the search tool to find relevant information before answering.
    At the end of each answer, add a short fun fact from approximately 10 years ago about the keywords in a user's query.
    Add "Here is a fun fact from 10 years ago about " before the answer. And "It's impressive how much has
    changed since 10 years! A lifetime in technology!" after the answer.
    """,
    description="Answers questions using Google Search.",
)

# Create the root agent that combines all the tools
root_agent = Agent(
    name="summit_app",
    model=MODEL,
    description=(
        "providing users with information related to Google Cloud Summit Prague 2025, "
        "providing information about the event agenda "
        "providing information about the speakers "
        "providing information about the sessions "
    ),
    instruction=prompt.summit_app_instruction_prompt,
    output_key="summit",
    tools=[
        agent_tool.AgentTool(agent=summit_agent), 
        agent_tool.AgentTool(agent=gcp_docs_agent), 
        agent_tool.AgentTool(agent=google_search_agent),
        agent_tool.AgentTool(agent=gcp_prod_releases_agent),
        agent_tool.AgentTool(agent=gcp_apis_agent),
    ]
)

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

runner = Runner(
    agent=root_agent, # The agent we want to run
    app_name=APP_NAME,
    session_service=session_service
)
