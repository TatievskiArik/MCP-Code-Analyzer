# 📦 Code Analyzer MCP Server

A dual-server Python project implementing an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) compliant interface for analyzing local Git repositories. The system generates a dependency graph of Python modules and enables AI-driven exploration of code relationships using Azure OpenAI.

---

## 🚀 Features
- Analyze Python codebases to construct module-level dependency graphs
- Query insights about specific modules using an LLM
- MCP-compliant endpoints (resources, tools, prompts, messages)
- Supports both **Flask** and **FastAPI** server implementations
- JSON-based memory and session management
- Azure OpenAI integration for intelligent querying

---

## 🏗️ Project Structure
```
├── mcp-server.py               # Flask implementation
├── mcp-fastapi-server.py       # FastAPI implementation
├── tools/
│   ├── DependencyAnalyzer.py   # Extracts imports and usages from Python files
│   ├── Graph.py                # Graph structure with Node and Arc classes
│   ├── GraphBuilder.py         # Builds graph from repo
│   └── readGraph.py            # Loads saved graph files
├── messages/
│   └── query_llm.py            # Sends query to Azure OpenAI
├── instructions/
│   └── instructionCreate.py    # Generates system prompts for LLM
├── memory/
│   └── memoryOrch.py           # Manages session creation and persistence
├── files/                      # Stores exported graph JSONs
├── memory/sessions/           # Stores session logs
└── .env                        # Azure OpenAI credentials
```

---

## ⚙️ Installation
### 1. Clone the repository
```bash
git clone https://github.com/yourusername/code-analyzer-mcp.git
cd code-analyzer-mcp
```

### 2. Set up virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file in the root directory
```ini
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

---

## 🖥️ Running the Servers
You can run either the **Flask** or **FastAPI** server.

### ✅ Flask Server
```bash
python mcp-server.py
```

### ✅ FastAPI Server (recommended)
```bash
uvicorn mcp-fastapi-server:app --reload --port 5000
```
- Docs available at: [http://localhost:5000/docs](http://localhost:5000/docs)

---

## 📡 API Endpoints
Both servers expose the same endpoint structure:

| Method | Endpoint           | Description |
|--------|--------------------|-------------|
| GET    | `/manifest`        | MCP metadata and capabilities |
| GET    | `/tools/list`      | List available tools (Analyze, Query) |
| POST   | `/tools/analyze`   | Submit Git path and return a graph |
| POST   | `/tools/query`     | Submit query and graph to get LLM response |
| GET    | `/resources/list`  | List saved graphs |
| POST   | `/resources/get`   | Retrieve specific graph file |
| GET    | `/messages/list`   | List available sessions |
| POST   | `/messages/get`    | Retrieve session messages |
| GET    | `/prompts/list`    | List prompt templates |
| POST   | `/prompts/get`     | Retrieve prompt content |

---

## 🔍 Future Improvements
1. 🔁 **Refactor shared logic** (e.g., graph building, session handling) into utilities
2. 🧪 **Add unit/integration tests** using `pytest`
3. 🗃️ **Replace flat-file memory** with Redis or a lightweight DB
4. 📉 **Profile performance** for larger repos
5. 🧼 **Improve error messages and logging**
6. 🌐 **Add OpenAPI schema validation** for better client tooling

---

## 🧠 How It Works
- The user provides a local Git path
- Server builds a dependency graph between modules using AST parsing
- The graph is stored in JSON format
- The user can send a question (e.g., "What does module X do?")
- The system constructs an LLM prompt with graph context
- Azure OpenAI responds with a helpful explanation

---

## 🧪 Sample Usage
```bash
curl -X POST http://localhost:5000/tools/analyze -H "Content-Type: application/json" \
    -d '{"git": "C:/path/to/your/local/git/repo"}'

curl -X POST http://localhost:5000/tools/query -H "Content-Type: application/json" \
    -d '{"query": "How does X relate to Y?", "graph": "./files/xxx.json", "session_id": "..."}'
```
