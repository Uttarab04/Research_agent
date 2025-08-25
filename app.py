# app.py
from flask import Flask, request, jsonify
from agent.search import search_papers

app = Flask(__name__)

@app.route('/')
def home():
    return "<h2>Welcome to Research Agent API</h2><p>Use <code>/search?query=your+topic</code> to fetch papers.</p>"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    print(f"🔍 Received query: {query}")  # Add this
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    results = search_papers(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

