from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import json
import re
from nltk.stem import PorterStemmer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

stemmer = PorterStemmer()
USE_STEMMING = True

# Load indexes
with open("inverted_index.json", "r") as f:
    inverted_index = json.load(f)

with open("positional_index.json", "r") as f:
    positional_index = json.load(f)

# Preprocess query
def preprocess_query(query):
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    operators_set = {"and", "or", "not"}
    processed_tokens = [stemmer.stem(token) if token not in operators_set and USE_STEMMING else token for token in tokens]
    terms = processed_tokens[0::2]
    ops = processed_tokens[1::2]
    return terms, ops

# Boolean Query Processing
def boolean_query(query):
    terms, ops = preprocess_query(query)
    if not terms:
        return []
    result = set(inverted_index.get(terms[0], []))
    for i, op in enumerate(ops):
        next_term = set(inverted_index.get(terms[i + 1], []))
        if op == "and":
            result &= next_term
        elif op == "or":
            result |= next_term
        elif op == "not":
            result -= next_term
    return list(result)

# Positional Query Processing
def positional_query(word1, word2, k):
    result_docs = set()
    word1, word2 = stemmer.stem(word1.lower()), stemmer.stem(word2.lower())
    if word1 in positional_index and word2 in positional_index:
        for doc in positional_index[word1]:
            if doc in positional_index[word2]:
                pos1 = positional_index[word1][doc]
                pos2 = positional_index[word2][doc]
                for p1 in pos1:
                    for p2 in pos2:
                        if abs(p1 - p2) <= k:
                            result_docs.add(doc)
                            break
    return list(result_docs)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    if "/" in query:
        parts = query.split("/")
        if len(parts) == 2:
            left_side = parts[0].strip().split()
            if len(left_side) == 2:
                word1, word2 = left_side
                try:
                    k = int(parts[1].strip())
                except ValueError:
                    return jsonify({"error": "Invalid k value"}), 400
                return jsonify({"results": positional_query(word1, word2, k)})
            else:
                return jsonify({"error": "Positional query format incorrect"}), 400
        else:
            return jsonify({"error": "Invalid query format"}), 400
    else:
        return jsonify({"results": boolean_query(query)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
