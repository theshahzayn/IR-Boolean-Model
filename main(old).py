import os
import re
import json
from collections import defaultdict
from nltk.stem import PorterStemmer

USE_STEMMING = True

stemmer = PorterStemmer()

def load_stopwords(filepath):
    with open(filepath, 'r') as file:
        return set(file.read().split())

# Preprocess text
def preprocess_text(text, stopwords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    if USE_STEMMING:
        return [stemmer.stem(word) for word in words if word not in stopwords]
    else:
        return [word for word in words if word not in stopwords]

# Build Inverted and Positional Indexes
def build_indexes(abstracts_dir, stopwords):
    inverted_index = defaultdict(set)
    positional_index = defaultdict(lambda: defaultdict(list))
    
    for filename in sorted(os.listdir(abstracts_dir)):
        filepath = os.path.join(abstracts_dir, filename)
        try:
            doc_id = int(os.path.splitext(filename)[0])
        except ValueError:
            doc_id = filename
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            words = preprocess_text(file.read(), stopwords)
            for pos, word in enumerate(words):
                inverted_index[word].add(doc_id)
                positional_index[word][doc_id].append(pos)
    
    return inverted_index, positional_index

# Save Inverted Index 
def save_inverted_index(index, filename):
    with open(filename, 'w') as file:
        json.dump({key: list(value) for key, value in index.items()}, file, indent=4)

# Save Positional Index 
def save_positional_index(index, filename):
    out = {}
    for term, doc_dict in index.items():
        out[term] = {str(doc_id): positions for doc_id, positions in doc_dict.items()}
    with open(filename, 'w') as file:
        json.dump(out, file, indent=4)

# Preprocess query
def preprocess_query(query):
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    operators_set = {'and', 'or', 'not'}
    processed_tokens = []
    for token in tokens:
        if token in operators_set or not USE_STEMMING:
            processed_tokens.append(token)
        else:
            processed_tokens.append(stemmer.stem(token))
    terms = processed_tokens[0::2]
    ops = processed_tokens[1::2]
    return terms, ops

# Boolean Query Processing
def boolean_query(query, inverted_index):
    terms, ops = preprocess_query(query)
    if not terms:
        return set()
    result = inverted_index.get(terms[0], set())
    for i, op in enumerate(ops):
        next_term = inverted_index.get(terms[i + 1], set())
        if op == "and":
            result &= next_term
        elif op == "or":
            result |= next_term
        elif op == "not":
            result -= next_term
    return result

# Positional Query Processing
def positional_query(word1, word2, k, positional_index):
    result_docs = set()
    if word1 in positional_index and word2 in positional_index:
        for doc in positional_index[word1]:
            if doc in positional_index[word2]:
                pos1 = positional_index[word1][doc]
                pos2 = positional_index[word2][doc]
                for p1 in pos1:
                    for p2 in pos2:
                        if abs(p1 - p2) <= k:
                            result_docs.add(doc)
                            break  # Found a valid position; no need to check more positions for this doc
    return result_docs

stopwords_path = "Stopword-List.txt"
abstracts_dir = "Abstracts"

# Load stopwords
stopwords = load_stopwords(stopwords_path)

# Build indexes
inverted_index, positional_index = build_indexes(abstracts_dir, stopwords)

# Save the indexes in separate files
save_inverted_index(inverted_index, "inverted_index.json")
save_positional_index(positional_index, "positional_index.json")

print("Indexes built and saved successfully!")
print("\nSample inverted index entries:")


# uery processing loop
while True:
    user_query = input("\nEnter your query (or type 'exit' to quit): ")
    if user_query.lower() == 'exit':
        break
    
    # Check if it's a positional query (format: 'word1 word2 / k')
    if '/' in user_query:
        parts = user_query.split('/')
        if len(parts) == 2:
            left_side = parts[0].strip().split()
            if len(left_side) == 2:
                word1, word2 = left_side
                try:
                    k = int(parts[1].strip())
                except ValueError:
                    print("Invalid k value in positional query.")
                    continue

                # Preprocess words for query
                if USE_STEMMING:
                    word1 = stemmer.stem(word1.lower())
                    word2 = stemmer.stem(word2.lower())
                else:
                    word1 = word1.lower()
                    word2 = word2.lower()
                result = positional_query(word1, word2, k, positional_index)
            else:
                print("Positional query must contain exactly two words before '/'.")
                continue
        else:
            print("Invalid positional query format.")
            continue
    else:
        result = boolean_query(user_query, inverted_index)
    
    print("Matching Documents:", sorted(result))
