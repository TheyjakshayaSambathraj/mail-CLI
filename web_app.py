from flask import Flask, request, jsonify

from imap_client import fetch_all_emails, search_emails
from semantic_search import semantic_search_emails, semantic_search_with_scores
import os
app = Flask(__name__)

@app.route("/", methods=["GET"])
def homepage():
    return """
    <h2>📧 IMAP Email API</h2>
    <p>This is a simple web API that connects to an email inbox via IMAP.</p>
    <h3>Available Endpoints:</h3>
    <ul>
        <li><strong>POST /fetch</strong><br>
            <em>Fetch recent emails from your inbox</em><br>
            <code>
            {
                "imap_host": "imap.gmail.com",<br>
                "email": "your_email@gmail.com",<br>
                "password": "your_app_password"
            }
            </code>
        </li>
        <br>
        <li><strong>POST /search</strong><br>
            <em>Search your emails for a keyword</em><br>
            <code>
            {
                "imap_host": "imap.gmail.com",<br>
                "email": "your_email@gmail.com",<br>
                "password": "your_app_password",<br>
                "keyword": "invoice"
            }
            </code>
        </li>
        <br>
        <li><strong>POST /semantic-search</strong><br>
            <em>Perform semantic search on your emails with AI similarity scoring</em><br>
            <code>
            {
                "imap_host": "imap.gmail.com",<br>
                "email": "your_email@gmail.com",<br>
                "password": "your_app_password",<br>
                "query": "meeting tomorrow",<br>
                "top_k": 5,<br>
                "min_threshold": 0.1,<br>
                "include_scores": true
            }
            </code>
        </li>
    </ul>
    <p>Use tools like <strong>Postman</strong> or <strong>curl</strong> to send POST requests to these endpoints.</p>
    """

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.json
    try:
        emails = fetch_all_emails(
            data["imap_host"], data["email"], data["password"], folder=data.get("folder", "INBOX")
        )
        return jsonify(emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    try:
        emails = search_emails(
            data["imap_host"], data["email"], data["password"], data["keyword"], folder=data.get("folder", "INBOX")
        )
        return jsonify(emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/semantic-search", methods=["POST"])
def semantic_search():
    data = request.json
    try:
        # Validate required fields
        required_fields = ["imap_host", "email", "password", "query"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get optional parameters
        top_k = data.get("top_k", 5)
        folder = data.get("folder", "INBOX")
        include_scores = data.get("include_scores", False)
        min_threshold = data.get("min_threshold", 0.1)  # Default threshold
        
        # Validate threshold
        if min_threshold < 0.0 or min_threshold > 1.0:
            return jsonify({"error": "min_threshold must be between 0.0 and 1.0"}), 400
        
        # Perform semantic search
        if include_scores:
            results = semantic_search_with_scores(
                data["imap_host"], data["email"], data["password"], 
                data["query"], folder=folder, top_k=top_k, min_threshold=min_threshold
            )
            # Convert to JSON-serializable format with score categories
            response = []
            for email, score in results:
                # Categorize scores
                if score >= 0.5:
                    score_category = "high"
                elif score >= 0.3:
                    score_category = "medium"
                elif score >= 0.1:
                    score_category = "low"
                else:
                    score_category = "very_low"
                
                response.append({
                    "email": email,
                    "similarity_score": float(score),
                    "score_category": score_category,
                    "threshold_used": min_threshold
                })
            
            return jsonify({
                "results": response,
                "total_found": len(response),
                "threshold_used": min_threshold,
                "query": data["query"]
            })
        else:
            emails = semantic_search_emails(
                data["imap_host"], data["email"], data["password"], 
                data["query"], folder=folder, top_k=top_k, min_threshold=min_threshold
            )
            return jsonify({
                "emails": emails,
                "total_found": len(emails),
                "threshold_used": min_threshold,
                "query": data["query"]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_web_api():
    print("Starting Flask API on http://localhost:10000")
   
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

