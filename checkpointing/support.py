from graph import graph, create_chat_graph
from langgraph.checkpoint.mongodb import MongoDBSaver
import json
from langgraph.types import Command

MONGODB_URI = "mongodb://admin:admin@localhost:27017/"
config = {"configurable": {"thread_id": "3"}}

def init():
    # storing messages in mongodb, so that when it execute again it will load from that state
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
        
        state = graph_with_mongo.get_state(config=config)
        for messages in state.values["messages"]:
            messages.pretty_print()
        
        last_message = state.values["messages"][-1]
        # check if last messages is tool_call?
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        
        user_query = None

        for call in tool_calls:
            # if tool call is "human_assistance_tool"
            if call.get("function", {}).get("name") == "human_assistance_tool":
                # get args of human_assistance_tool
                args = call["function"].get("arguments", "{}")
                
                try:
                    args_dict = json.loads(args)
                    # from args load the query args -> human_response = interrupt({"query": query})
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("Failed to decode function arguments.")
        
        print("User is trying to ask: ", user_query)
        
        # Take answer from support
        ans = input("Resolution > ")
        
        # Invoke the graph again to continue
        resume_command = Command(resume={"data": ans})
        for event in graph_with_mongo.stream(resume_command, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()
                    
init()