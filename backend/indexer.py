import os
import re
import json
from collections import defaultdict
from nltk.stem import PorterStemmer

# Whether to use stemming or not
USE_STEMMING = True
stemmer = PorterStemmer()

def load_stopwords(filepath):
    with open(filepath, 'r') as file:
        return set(file.read().split())

# Preprocess text 

# lowering text, removing stopwords, and applying stemming
def preprocess_text(text, stopwords):
    text = text.lower()

    words = re.findall(r'\b\w+\b', text)

    if USE_STEMMING:
        return [stemmer.stem(word) for word in words if word not in stopwords]
    else:
        return [word for word in words if word not in stopwords]

# Building Inverted and Positional Indexes
def build_indexes(abstracts_dir, stopwords):
    inverted_index = defaultdict(set)
    positional_index = defaultdict(lambda: defaultdict(list))
    dictionary = set()  # Store unique terms in a set
    term_frequency = defaultdict(int)  # Term frequency across all documents
    doc_count = 0
    
    for filename in sorted(os.listdir(abstracts_dir)):
        filepath = os.path.join(abstracts_dir, filename)
        try:
            doc_id = int(os.path.splitext(filename)[0])
        except ValueError:
            doc_id = filename
        
        doc_count += 1
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            words = preprocess_text(file.read(), stopwords)
            # Add unique words to the dictionary set and calculate term frequency
            for word in words:
                dictionary.add(word)
                term_frequency[word] += 1
                inverted_index[word].add(doc_id)
                positional_index[word][doc_id].append(words.index(word))
    
    # Additional statistics
    stats = {
        'total_unique_terms': len(dictionary),
        'total_documents': doc_count,
        'term_frequency': term_frequency
    }
    
    return inverted_index, positional_index, dictionary, stats

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

# Save Dictionary Terms and Statistics
def save_dictionary(dictionary, stats, filename):
    output = {
        'dictionary_terms': list(dictionary),  # Only the unique terms
        'statistics': stats  # Including additional statistics
    }
    with open(filename, 'w') as file:
        json.dump(output, file, indent=4)

def main():
    stopwords_path = "Stopword-List.txt"
    abstracts_dir = "Abstracts"
    
    # Load stopwords
    stopwords = load_stopwords(stopwords_path)
    
    # Build indexes
    inverted_index, positional_index, dictionary, stats = build_indexes(abstracts_dir, stopwords)
    
    # Save the indexes and dictionary in separate files
    save_inverted_index(inverted_index, "inverted_index.json")
    save_positional_index(positional_index, "positional_index.json")
    save_dictionary(dictionary, stats, "dictionary_terms_with_stats.json")
    
    print("Indexes and dictionary saved successfully!")

if __name__ == "__main__":
    main()
