from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import os
from nltk.stem import PorterStemmer

import difflib

app = Flask(__name__)
CORS(app)

stemmer = PorterStemmer()
USE_STEMMING = True
ABSTRACTS_FOLDER = "Abstracts"

# Load indexes
with open("inverted_index.json", "r") as f:
    inverted_index = json.load(f)

with open("positional_index.json", "r") as f:
    positional_index = json.load(f)


# Extract all words (keys) from the inverted index
all_words = list(inverted_index.keys())

def suggest_words(query, max_suggestions=5):
    query = query.lower().strip()
    if not query:
        return []

    # Get close matches
    close_matches = difflib.get_close_matches(query, all_words, n=max_suggestions, cutoff=0.75)  # Higher cutoff

    # Additional filtering: Prefer words that start with the query
    filtered_matches = [word for word in all_words if word.lower().startswith(query)]

    # Merge and remove duplicates while keeping order
    suggestions = list(dict.fromkeys(filtered_matches + close_matches))[:max_suggestions]

    return suggestions


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "")
    suggestions = suggest_words(query)
    return jsonify({"suggestions": suggestions})


# Preprocess query
def preprocess_query(query):
    query = query.lower().strip()
    
    if not query:
        return [], []  # Return empty lists if query is empty

    tokens = re.findall(r'\b\w+\b', query)
    operators_set = {"and", "or", "not"}
    
    if not tokens:
        return [], []

    processed_tokens = [stemmer.stem(token) if token not in operators_set and USE_STEMMING else token for token in tokens]

    # Ensure we have alternating terms and operators (term op term op term)
    if len(processed_tokens) % 2 == 0:
        return [], []  # Invalid format

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

        if i + 1 >= len(terms):  # Check to avoid index out of range
            break  # Stop processing if no next term exists

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
                        if abs(p1 - p2) <= k+1:
                            result_docs.add(doc)
                            break
    return list(result_docs)

# Function to extract a snippet from the document file
def get_document_snippet(doc_id, query_terms):
    file_path = os.path.join(ABSTRACTS_FOLDER, f"{doc_id}.txt")  # Document files are stored as "1.txt", "2.txt", etc.
    print(f"Looking for file: {file_path}")  # Debugging output

    if not os.path.exists(file_path):
        return "Document not found"
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        operators_set = {"and", "or", "not"}
        filtered_terms = [term for term in query_terms if term.lower() not in operators_set]

        for term in filtered_terms:
            pattern = re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE)
            content = pattern.sub(r'<mark>\1</mark>', content)

        # Return a snippet of 250 characters surrounding the first occurrence of any term
        first_match = re.search(r'<mark>.*?</mark>', content)
        if first_match:
            start_idx = max(0, first_match.start() - 50)  # Start 50 chars before the match
            end_idx = min(len(content), first_match.end() + 50)  # End 50 chars after the match
            return "..." + content[start_idx:end_idx] + "..."
        
        return content[:250] + "..."  # Fallback: Return first 250 chars if no match

    except Exception as e:
        return f"Error reading document: {str(e)}"

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    if "/" in query:  # Positional query
        parts = query.split("/")
        if len(parts) == 2:
            left_side = parts[0].strip().split()
            if len(left_side) == 2:
                word1, word2 = left_side
                try:
                    k = int(parts[1].strip())
                except ValueError:
                    return jsonify({"error": "Invalid k value"}), 400
                results = positional_query(word1, word2, k)
            else:
                return jsonify({"error": "Positional query format incorrect"}), 400
        else:
            return jsonify({"error": "Invalid query format"}), 400
    else:  # Boolean query
        results = boolean_query(query)

    # Fetch snippets for each document
    snippets = {doc: get_document_snippet(doc, query.split()) for doc in results}

    return jsonify({"results": results, "snippets": snippets})




# Full document fetch API

@app.route("/document", methods=["GET"])
def get_full_document():
    doc_id = request.args.get("doc_id")
    if not doc_id:
        return jsonify({"error": "Document ID is required"}), 400

    file_path = os.path.join(ABSTRACTS_FOLDER, f"{doc_id}.txt")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Document not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return jsonify({"doc_id": doc_id, "content": content})
    except Exception as e:
        return jsonify({"error": f"Error reading document: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)