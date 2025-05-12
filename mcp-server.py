from flask import Flask, request, jsonify, Response
from tools.readGraph import load_graph
from insturctions.instructionCreate import create_insturction
from messages.query_llm import send_query_to_llm
from tools.GraphBuilder import GraphBuilder
from memory.memoryOrch import create_session
import os
from collections import OrderedDict
import json
import uuid

app = Flask(__name__)

# --------------- MCP Server GET Requests --------------- #

@app.route('/manifest', methods=['GET'])
def manifest():
    response_data = OrderedDict([
        ("schema_version", "2025-05-11"),
        ("name", "Code Analyzer MCP Server"),
        ("description", "An MCP-compliant server that analyzes local Git repositories to extract module-level dependencies and builds a structured dependency graph. Users can query the graph using a connected LLM to gain insights into specific modules, their relationships, and their roles within the project architecture."),
        ("version", "1.0.1"),
        ("capabilities", OrderedDict([
            ("tools", True),
            ("resources", True),
            ("prompts", True)
        ])),
        ("endpoints", OrderedDict([
            ("resources", "/resources/list"),
            ("tools", "/tools/list"),
            ("prompts", "/prompts/list")
        ]))
    ])
    return Response(json.dumps(response_data), mimetype='application/json')

@app.route('/prompts/list', methods=['GET'])
def listPrompt():
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

    return Response(json.dumps(response_data), mimetype='application/json')

@app.route('/resources/list', methods=['GET'])
def listResources():
    files_folder = './files'
    try:
        file_names = [f for f in os.listdir(files_folder) if os.path.isfile(os.path.join(files_folder, f))]
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
        return Response(json.dumps(response_data), mimetype='application/json')
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/messages/list', methods=['GET'])
def listMessages():
    files_folder = './memory/sessions'
    try:
        file_names = [f for f in os.listdir(files_folder) if os.path.isfile(os.path.join(files_folder, f))]
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
        return Response(json.dumps(response_data), mimetype='application/json')
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/tools/list', methods=['GET'])
def listTools():
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
                "request_parameters": [{"query": "The query to be sent to the LLM"}, {"resource": "Path to the dependency graph file"},{"session_id": "ID of the session"}],
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
    return Response(json.dumps(response_data), mimetype='application/json')

# --------------- MCP Server POST Requests --------------- #

@app.route('/prompts/get', methods=['POST'])
def getPrompt():
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing JSON payload"}), 400
    prompt_name = data.get('prompt_name')
    if not prompt_name:
        return jsonify({
            "status": "error",
            "error": "Missing 'prompt_name' in payload"}), 400
    if prompt_name != "Create Dependency Graph":
        return jsonify({
            "status": "error",
            "error": f"Prompt '{prompt_name}' not found"}), 404
    return jsonify({
        "status": "success",
        "message": create_insturction(["List of nodes"],["List of arcs"]),})

@app.route('/resources/get', methods=['POST'])
def getResource():
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing JSON payload"}), 400
    resource_name = data.get('resource_name')
    if not resource_name:
        return jsonify({
            "status": "error",
            "error": "Missing 'resource_name' in payload"}), 400
    file_path = os.path.join('./files', resource_name)
    if not os.path.isfile(file_path):
        return jsonify({
            "status": "error",
            "error": f"Resource '{resource_name}' not found"}), 404
    with open(file_path, 'r') as file:
        content = file.read()
    return jsonify({
        "status": "success",
        "resource": content}), 200

@app.route('/messages/get', methods=['POST'])
def getMessages():
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing JSON payload"}), 400
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({
            "status": "error",
            "error": "Missing 'session_id' in payload"}), 400
    file_path = os.path.join('./memory/sessions', session_id)
    if not os.path.isfile(file_path):
        return jsonify({
            "status": "error",
            "error": f"Session '{session_id}' not found"}), 404
    with open(file_path, 'r') as file:
        content = file.read()
    return jsonify({
        "status": "success",
        "messages": content}), 200

@app.route('/tools/analyze', methods=['POST'])
def analyzeGraph():
    #Check validity of the request
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "error": "Missing JSON payload"}), 400
    git_repo = data.get('git')
    if not git_repo:
        return jsonify({
            "status": "error",
            "error": "Missing 'git' path in payload"}), 400
    if not os.path.isdir(git_repo):
        return jsonify({
            "status": "error",
            "error": f"Provided path '{git_repo}' is not a valid directory"}), 400
    #Build dependency graph
    try:
        currGraph = GraphBuilder(git_repo)
        currGraph.build()
        dependencyGraph = currGraph.export_graph()
        session_id = create_session()
        return jsonify({
            "status": "success",
            "graph_path": dependencyGraph,
            "session_id":session_id}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/tools/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    query = data.get('query')
    graph = data.get('graph')
    session_id = data.get('session_id')
    if (not query) or (not graph) or (not session_id):
        return jsonify({"error": "Missing Atrributes query/graph"}), 400
    nodes, arcs = load_graph(graph)
    try:
        with open(os.path.join('./memory/sessions', session_id), 'r') as file:
            content = file.read()
        history = json.loads(content)
        if history["messages"] == []:
            sys_msg = create_insturction(nodes,arcs)
            history["messages"].append({"role": "system", "content": sys_msg})
            history["messages"].append({"role": "user", "content": query})
            llm_response = send_query_to_llm(history["messages"])
            history["messages"].append({"role": "assistant", "content": llm_response})
            with open(os.path.join('./memory/sessions', session_id), 'w') as file:
                json.dump(history, file, indent=2)
        else:
            sys_msg = history["messages"][0]["content"]
            history["messages"].append({"role": "user", "content": query})
            llm_response = send_query_to_llm(history["messages"])
            history["messages"].append({"role": "assistant", "content": llm_response})
            with open(os.path.join('./memory/sessions', session_id), 'w') as file:
                json.dump(history, file, indent=2)
        return jsonify({
            "status": "success",
            "response":llm_response}), 200
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True,port=5000)
