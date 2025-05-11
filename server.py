from flask import Flask, request, jsonify
from tools.readGraph import load_graph
from insturctions.instructionCreate import create_insturction
from messages.query_llm import send_query_to_llm
from tools.GraphBuilder import GraphBuilder
import os

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    #Check validity of the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    git_repo = data.get('git')
    if not git_repo:
        return jsonify({"error": "Missing 'git' path in payload"}), 400
    if not os.path.isdir(git_repo):
        return jsonify({"error": f"Provided path '{git_repo}' is not a valid directory"}), 400
    
    #Build dependency graph
    try:
        currGraph = GraphBuilder(git_repo)
        currGraph.build()
        dependencyGraph = currGraph.export_graph()
        return jsonify({"graph_path": dependencyGraph}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500



@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400
    query = data.get('query')
    graph = data.get('graph')
    if (not query) or (not graph):
        return jsonify({"error": "Missing Atrributes query/graph"}), 400
    
    nodes, arcs = load_graph(graph)
    sys_msg = create_insturction(nodes,arcs)
    try:
        llm_response = send_query_to_llm(query,sys_msg)
        return jsonify({"response": llm_response}), 200
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
