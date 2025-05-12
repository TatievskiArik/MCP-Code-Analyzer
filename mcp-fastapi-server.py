from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tools.readGraph import load_graph
from insturctions.instructionCreate import create_insturction
from messages.query_llm import send_query_to_llm
from tools.GraphBuilder import GraphBuilder
from memory.memoryOrch import create_session
from collections import OrderedDict
import os
import json

app = FastAPI(title="Code Analyzer MCP Server")

@app.get("/manifest")
async def manifest():
    response_data = OrderedDict([
        ("schema_version", "2025-05-11"),
        ("name", "Code Analyzer MCP Server"),
        ("description", "An MCP-compliant server that analyzes local Git repositories to extract module-level dependencies and builds a structured dependency graph. Users can query the graph using a connected LLM to gain insights into specific modules, their relationships, and their roles within the project architecture."),
        ("version", "1.0.3"),
        ("capabilities", OrderedDict([
            ("tools", True),
            ("resources", True),
            ("prompts", True)
        ])),
        ("endpoints", OrderedDict([
            ("resources", "/resources/list"),
            ("tools", "/tools/list"),
            ("prompts", "/prompts/list"),
            ("messages", "/messages/list"),
        ]))
    ])
    return JSONResponse(content=response_data)

@app.get("/prompts/list")
async def list_prompt():
    response_data = OrderedDict([
        ("status", "success"),
        ("message", "List of available prompts"),
        ("prompts", [
            {
                "name": "Create Dependency Graph",
                "description": "Enables LLM Questioning based on a created dependency graph from the provided Git repository"
            }
        ]),
        ("request_parameters", [{"prompt_name": "Name of the prompt from the list"}]),
        ("request_endpoint", "/prompts/get"),
        ("response_parameters", [
            {
                "status": "Request status",
                "prompt": "The prompt that was sent to the LLM",
            }
        ])
    ])
    return JSONResponse(content=response_data)

@app.get("/resources/list")
async def list_resources():
    try:
        file_names = [f for f in os.listdir("./files") if os.path.isfile(os.path.join("./files", f))]
        response_data = OrderedDict([
            ("status", "success"),
            ("message", "List of available resources"),
            ("resources", file_names),
            ("request_parameters", [{"resource_name": "Name of a resource from the list"}]),
            ("request_endpoint", "/resources/get"),
            ("response_parameters", [
                {
                    "status": "Request status",
                    "resource": "A dependency graph file containing nodes and arcs"
                }
            ])
        ])
        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages/list")
async def list_messages():
    try:
        file_names = [f for f in os.listdir("./memory/sessions") if os.path.isfile(os.path.join("./memory/sessions", f))]
        response_data = OrderedDict([
            ("status", "success"),
            ("message", "List of available sessions"),
            ("resources", file_names),
            ("request_parameters", [{"session_id": "ID of a session from the list"}]),
            ("request_endpoint", "/messages/get"),
            ("response_parameters", [
                {
                    "status": "Request status",
                    "messages": "A list representing the conversation history with the LLM"
                }
            ])
        ])
        return JSONResponse(content=response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/list")
async def list_tools():
    response_data = OrderedDict([
        ("status", "success"),
        ("message", "List of available tools"),
        ("tools", [
            {
                "name": "Analyze",
                "description": "Analyzes a local Git repository to extract module-level dependencies and builds a structured dependency graph.",
                "request_parameters": [{"git": "Path to the local Git repository"}],
                "request_endpoint": "/tools/analyze",
                "response_parameters": [
                    {
                        "status": "Request status",
                        "graph_path": "Path to the generated dependency graph file",
                        "session_id": "ID of the session"
                    }
                ]
            },
            {
                "name": "Query",
                "description": "Queries the dependency graph using a connected LLM to gain insights into specific modules, their relationships, and their roles within the project architecture.",
                "request_parameters": [{"query": "The query to be sent to the LLM"}, {"resource": "Path to the dependency graph file"}, {"session_id": "ID of the session"}],
                "request_endpoint": "/tools/query",
                "response_parameters": [
                    {
                        "status": "Request status",
                        "response": "Response from the LLM based on the query"
                    }
                ]
            }
        ])
    ])
    return JSONResponse(content=response_data)

class PromptRequest(BaseModel):
    prompt_name: str

class ResourceRequest(BaseModel):
    resource_name: str

class MessageRequest(BaseModel):
    session_id: str

class AnalyzeRequest(BaseModel):
    git: str

class QueryRequest(BaseModel):
    query: str
    graph: str
    session_id: str

@app.post("/prompts/get")
async def get_prompt(req: PromptRequest):
    if req.prompt_name != "Create Dependency Graph":
        raise HTTPException(status_code=404, detail=f"Prompt '{req.prompt_name}' not found")
    return {"status": "success", "message": create_insturction(["List of nodes"], ["List of arcs"])}

@app.post("/resources/get")
async def get_resource(req: ResourceRequest):
    file_path = os.path.join('./files', req.resource_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Resource '{req.resource_name}' not found")
    with open(file_path, 'r') as file:
        content = file.read()
    return {"status": "success", "resource": content}

@app.post("/messages/get")
async def get_messages(req: MessageRequest):
    file_path = os.path.join('./memory/sessions', req.session_id)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")
    with open(file_path, 'r') as file:
        content = file.read()
    return {"status": "success", "messages": content}

@app.post("/tools/analyze")
async def analyze_graph(req: AnalyzeRequest):
    if not os.path.isdir(req.git):
        raise HTTPException(status_code=400, detail=f"Provided path '{req.git}' is not a valid directory")
    try:
        currGraph = GraphBuilder(req.git)
        currGraph.build()
        dependencyGraph = currGraph.export_graph()
        session_id = create_session()
        return {"status": "success", "graph_path": dependencyGraph, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/query")
async def query_graph(req: QueryRequest):
    nodes, arcs = load_graph(req.graph)
    try:
        session_path = os.path.join('./memory/sessions', req.session_id)
        with open(session_path, 'r') as file:
            content = file.read()
        history = json.loads(content)
        if not history["messages"]:
            sys_msg = create_insturction(nodes, arcs)
            history["messages"].append({"role": "system", "content": sys_msg})
        history["messages"].append({"role": "user", "content": req.query})
        llm_response = send_query_to_llm(history["messages"])
        history["messages"].append({"role": "assistant", "content": llm_response})
        with open(session_path, 'w') as file:
            json.dump(history, file, indent=2)
        return {"status": "success", "response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
