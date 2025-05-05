# Checkpointing in LangGraph with Human-in-the-Loop

This project demonstrates how to implement checkpointing in LangGraph with a human-in-the-loop system using MongoDB for state persistence.

![Human in Loop LangGraph Flow](checkpoint_human_in_loop_langgraph.png)

## Overview

The system implements a conversational AI with human support capabilities, where:

- The conversation state is persisted in MongoDB
- The AI can request human assistance when needed
- The system can resume from the last checkpoint after human input

## Architecture

### Components

1. **Main Application** (`main.py`)

   - Handles the primary chat interface
   - Manages the conversation flow
   - Integrates with MongoDB for state persistence
   - Streams responses in real-time

2. **Support Interface** (`support.py`)

   - Provides human assistance interface
   - Processes AI requests for help
   - Allows support staff to respond to queries
   - Resumes conversation flow after human input

3. **Graph Definition** (`graph.py`)
   - Defines the LangGraph workflow
   - Implements the human assistance tool
   - Sets up conditional routing based on tool calls
   - Configures the chat model and state management

### Flow Description

1. **Initial User Input**

   - User enters a query through the main interface
   - The system initializes a conversation with a unique thread ID
   - State is persisted in MongoDB

2. **AI Processing**

   - The LLM (GPT-4) processes the user input
   - Can either:
     - Respond directly to the user
     - Request human assistance using `human_assistance_tool`

3. **Human Assistance Flow**

   - When AI calls `human_assistance_tool`:
     - Current state is checkpointed in MongoDB
     - Support interface is notified
     - Main process waits for human input
   - Support staff:
     - Views the user's query
     - Provides resolution
     - System resumes from checkpoint

4. **State Management**
   - All conversations are stored with unique thread IDs
   - States are persisted between sessions
   - System can recover from interruptions
   - Supports multiple concurrent conversations

## Technical Details

### MongoDB Configuration

```
MONGODB_URI = "mongodb://admin:admin@localhost:27017/"
```

### State Structure

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

### Key Features

1. **Checkpointing**

   - Uses `MongoDBSaver` for state persistence
   - Automatic state recovery
   - Thread-based conversation tracking

2. **Tool Conditions**

   - Single tool call per response
   - Conditional routing based on tool usage
   - Seamless integration with LangGraph flow

3. **Real-time Streaming**
   - Step-by-step result streaming
   - Immediate response visibility
   - Event-based message handling

## Usage

1. **Start the MongoDB Server**

   ```bash
   docker-compose -f docker-compose.db.yml up -d
   ```

2. **Run the Main Application**

   ```bash
   python main.py
   ```

3. **Run the Support Interface** (in a separate terminal)

   ```bash
   python support.py
   ```

4. **Interact with the System**
   - Enter queries in the main interface
   - Monitor support requests in the support interface
   - View conversation flow and checkpoints in MongoDB

## Example Interaction

1. User: "I need help with my account settings"
2. AI: Evaluates the query and might call human_assistance_tool
3. Support Staff: Receives notification and provides guidance
4. AI: Resumes conversation with human-provided information
5. User: Receives comprehensive response combining AI and human expertise
