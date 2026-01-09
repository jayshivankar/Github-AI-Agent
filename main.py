from dotenv import load_dotenv
import os
from github import fetch_issues
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from note import note_tool

load_dotenv()

def connect_to_vstore():
    embeddings = OpenAIEmbeddings()
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    desired_namespace = os.getenv("ASTRA_DB_KEYSPACE")

    if desired_namespace:
        ASTRA_DB_KEYSPACE = desired_namespace
    else:
        ASTRA_DB_KEYSPACE = None

    vstore = AstraDBVectorStore(
        embedding = embeddings,
        collection_name = 'github',
        apoi_endpoint = ASTRA_DB_API_ENDPOINT,
        token = ASTRA_DB_APPLICATION_TOKEN,
        keyspace = ASTRA_DB_KEYSPACE
    )
    return vstore

vstore = connect_to_vstore()
add_to_vstore = input("Do you want to update the issues? (y/N): ").lower() in [
    "yes",
    "y",
]

if add_to_vstore:
    owner = "techwithtim"
    repo = "Flask-Web-App-Tutorial"
    issues = fetch_issues(owner, repo)

    try:
        vstore.delete_collection()
    except:
        pass

    vstore = connect_to_vstore()
    vstore.add_documents(issues)

retriver = vstore.as_retriever(search_kwargs={"k":3})
retriver_tool = create_retriever_tool(
    retriver=retriver,
    name="GitHub Issues Retriever",
    description="Useful for answering questions about GitHub issues . For any questions about github issues, you must use this tool!"
)
prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.5)

tools = [retriver_tool,note_tool]
agent = create_tool_calling_agent(llm,tools,prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while (question := input("Ask a question about github issues (q to quit): ")) != "q":
    result = agent_executor.invoke({"input": question})
    print(result["output"])