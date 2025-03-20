import os
import json
import re
import nltk
from collections import defaultdict
from nltk.stem import PorterStemmer

nltk.download("punkt")

# Initialize stemmer
stemmer = PorterStemmer()

# Enable or disable stemming
USE_STEMMING = True

# Folder where text documents are stored
DOCS_FOLDER = "documents"

# Indexes
inverted_index = defaultdict(set)
positional_index = defaultdict(lambda: defaultdict(list))

# Process each document
for doc_id, filename in enumerate(os.listdir(DOCS_FOLDER)):
    file_path = os.path.join(DOCS_FOLDER, filename)
    if not filename.endswith(".txt"):
        continue  # Skip non-text files

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().lower()
        tokens = re.findall(r'\b\w+\b', text)  # Tokenize words

        for position, word in enumerate(tokens):
            stemmed_word = stemmer.stem(word) if USE_STEMMING else word
            inverted_index[stemmed_word].add(doc_id)
            positional_index[stemmed_word][doc_id].append(position)

# Convert sets to lists for JSON serialization
inverted_index = {word: list(doc_ids) for word, doc_ids in inverted_index.items()}

# Save indexes as JSON files
with open("inverted_index.json", "w") as f:
    json.dump(inverted_index, f, indent=4)

with open("positional_index.json", "w") as f:
    json.dump(positional_index, f, indent=4)

print("Indexing complete! Inverted and positional indexes saved.")
