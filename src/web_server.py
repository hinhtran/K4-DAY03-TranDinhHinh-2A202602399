"""
🌐 MIXOLOGY AI CHATBOT WEB SERVER
Cung cấp giao diện web hiện đại (Sky Blue) kết nối trực tiếp với MCP Server và ReAct Agent.
"""

import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory

# Setup paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(base_dir, "src")
web_dir = os.path.join(base_dir, "web")
sys.path.insert(0, src_dir)

from providers import get_llm_provider
from mcp_server import MCPCocktailServer
from tools import SAVED_RECIPES
from prompts import CHATBOT_BASELINE_PROMPT, REACT_AGENT_SYSTEM_PROMPT, MAX_ITERATIONS
from app import run_react_agent, save_waterfall_trace

app = Flask(__name__, static_folder=web_dir, static_url_path="")

provider = get_llm_provider()
mcp_server = MCPCocktailServer()

@app.route("/")
def index():
    return send_from_directory(web_dir, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(web_dir, path)

@app.route("/api/test-cases", methods=["GET"])
def get_test_cases():
    test_cases_file = os.path.join(base_dir, "config", "test_cases.json")
    if os.path.exists(test_cases_file):
        with open(test_cases_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/trace", methods=["GET"])
def get_trace():
    trace_file = os.path.join(base_dir, "docs", "trace_waterfall.json")
    if os.path.exists(trace_file):
        with open(trace_file, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    mode = data.get("mode", "react")

    if not query:
        return jsonify({"error": "Empty query"}), 400

    if mode == "baseline":
        response = provider.generate(query, system_prompt=CHATBOT_BASELINE_PROMPT)
        return jsonify({
            "mode": "baseline",
            "finalAnswer": response,
            "traces": [],
            "savedRecipes": SAVED_RECIPES
        })
    else:
        # Run ReAct Agent with MCP Server
        traces = run_react_agent(query, provider, mcp_server)
        save_waterfall_trace(traces)
        
        # Find final answer
        final_answer = ""
        for t in reversed(traces):
            if t.get("action_type") == "FINAL_ANSWER":
                final_answer = t.get("output", "")
                break

        return jsonify({
            "mode": "react",
            "finalAnswer": final_answer,
            "traces": traces,
            "savedRecipes": SAVED_RECIPES
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("==========================================================")
    print(f"🍸 MIXOLOGY AI CHATBOT WEB UI ĐANG CHẠY TẠI:")
    print(f"👉 http://localhost:{port}")
    print(f"🌐 MCP Server: {mcp_server.server_name}")
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print("==========================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
