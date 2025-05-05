from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from dotenv import load_dotenv
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from pydantic import BaseModel # validation layer (same as zod)

load_dotenv()

client = wrap_openai(OpenAI())

# Schemas Defination
class DetectCallResponse(BaseModel):
    is_question_ai: bool
    
class CodingAIResponse(BaseModel):
    answer: str

# Object defines the structure of our chatbot
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    
def detect_query(state: State):
    user_message = state.get("user_message")
    
    SYSTEM_PROMPT = """
        You are an AI assitant. Your job is to detect if the use's quey is related to coding question or not.
        
        Return the response in specific JSON Boolean only
    """
    
    # open ai call -> is coding ques?
    result = client.beta.chat.completions.parse(
        model = "gpt-4o-mini",
        response_format = DetectCallResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    
    print(result.choices[0].message.parsed)
    
    state["is_coding_question"] = result.choices[0].message.parsed.is_question_ai
    
    return state

def solve_coding_question(state: State):
    # if the question is coding...
    user_message = state.get("user_message")
    
    SYSTEM_PROMPT = """
        You are an AI assitant. Your job is to solve the coding question.  
    """
    
    # Open AI Call
    result = client.beta.chat.completions.parse(
        model = "gpt-4.1",
        response_format = CodingAIResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT },
            {"role": "user", "content": user_message}
        ]
    )
    
    print(result.choices[0].message.parsed)
    
    state["ai_message"] = result.choices[0].message.parsed.answer
    
    return state

def solve_simple_question(state: State):
    # if the question is coding...
    user_message = state.get("user_message")
    
    # Open AI Call - mini model
    SYSTEM_PROMPT = """
        You are an AI assitant. Your job is to chat with user.  
    """
    
    # Open AI Call
    result = client.beta.chat.completions.parse(
        model = "gpt-4o-mini",
        response_format = CodingAIResponse,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT },
            {"role": "user", "content": user_message}
        ]
    )
    
    print(result.choices[0].message.parsed)
    
    state["ai_message"] = result.choices[0].message.parsed.answer
    
    return state

def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]: #listing possible ways
    if state["is_coding_question"]:
        return "solve_coding_question"
    
    else:
        return "solve_simple_question"

# Initializing Graph
graph_builder = StateGraph(State)


# Creating Nodes
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)
graph_builder.add_node("route_edge", route_edge)

# Adding Edges
graph_builder.add_edge(START, "detect_query")

# as route_edge is the conditional edge, it'll return -> solve_coding_question | solve_simple_question
graph_builder.add_conditional_edges("detect_query", route_edge)

graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

# Run
graph = graph_builder.compile()

# Use
def call_graph():
    initial_state = {
        "user_message": "can you explain pydentic python ?",
        "ai_message": "",
        "is_coding_question": False
    }
    
    result = graph.invoke(initial_state)
    
    print("final Result", result)

call_graph()