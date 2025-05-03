from typing import Annotated
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.types import interrupt
from langgraph.prebuilt import ToolNode, tools_condition

@tool
def human_assistance_tool(query: str):
    """Request assistance from human"""
    # when the AI call this tool, it will get interrupt and wait until the we get any reponse from support.py
    # it will save everything as a checkpoint in db and exit 
    human_response = interrupt({"query": query}) # human response will get from support.py when Command resumes with data
    
    return human_response["data"] # after human input, the tool will resume

tools = [human_assistance_tool]

# create tool node (from prebuild langgraph)
tool_node = ToolNode(tools=tools)

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools=tools)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    """
    the assertion is checking that the number of tool calls in the message object is either 0 or 1 (not more than 1). This means the code is enforcing that the LLM can only make at most one tool call per message.
    """
    assert len(message.tool_calls) <= 1
    # only run if last messages is not a tool call
    # read existing messages and adding the llm messages
    return {"messages": [message]}

# initializing graph
graph_builder = StateGraph(State)

# creating nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# creating edges
graph_builder.add_edge(START, "chatbot")

# checking for tool condition
graph_builder.add_conditional_edges("chatbot", tools_condition)
# after tool condition will goto chatbot again
graph_builder.add_edge("tools", "chatbot")

graph_builder.add_edge("chatbot", END)

# Without any memory
graph = graph_builder.compile()

# creates a new graph with given checkpointer
def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)