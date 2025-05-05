from graph import graph, create_chat_graph
from langgraph.checkpoint.mongodb import MongoDBSaver

MONGODB_URI = "mongodb://admin:admin@localhost:27017/"
config = {"configurable": {"thread_id": "3"}} # thread_id is to uniquely identify each flow of state

def init():
    # for each init(); storing messages in mongodb, so that when it execute again it will load from that state
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
        
        while True:
            user_input = input("> ")
            """
                graph.stream: Step-by-step results (real-time)
                graph.invoke: Just the final result (wait until complete)
            """
            for event in graph_with_mongo.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
        
init()