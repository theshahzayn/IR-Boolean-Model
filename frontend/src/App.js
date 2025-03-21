import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { FaSearch } from "react-icons/fa";
import { motion } from "framer-motion";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchTime, setFetchTime] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [activeSuggestion, setActiveSuggestion] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [lastAcceptedSuggestion, setLastAcceptedSuggestion] = useState("");
  const [typingTimeout, setTypingTimeout] = useState(null);

  const [fullDocument, setFullDocument] = useState(null);
  const [docLoading, setDocLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);


  const inputRef = useRef(null);
  const suggestionBoxRef = useRef(null);

  useEffect(() => {
    if (query.length > 1 && query !== lastAcceptedSuggestion) {
      if (typingTimeout) {
        clearTimeout(typingTimeout);
      }
      setTypingTimeout(setTimeout(() => fetchSuggestions(query), 500)); 
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [query]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        suggestionBoxRef.current &&
        !suggestionBoxRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchSuggestions = async (input) => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/suggest", {
        params: { query: input },
      });
      setSuggestions(response.data.suggestions || []);
      setShowSuggestions(true);
    } catch (err) {
      console.error("Error fetching suggestions:", err);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setLastAcceptedSuggestion(suggestion);
    setShowSuggestions(false);
    setSuggestions([]); // Clear suggestions list
  };

  const handleKeyDown = (e) => {
    if (e.key === "ArrowDown") {
      setActiveSuggestion((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === "ArrowUp") {
      setActiveSuggestion((prev) => (prev > 0 ? prev - 1 : 0));
    } else if (e.key === "Enter") {
      if (activeSuggestion >= 0 && suggestions.length > 0) {
        setQuery(suggestions[activeSuggestion]);
        setLastAcceptedSuggestion(suggestions[activeSuggestion]);
        setShowSuggestions(false);
        setSuggestions([]); // Clear suggestions list
      }
    }
  };

  const handleSearch = async (e) => {

    e.preventDefault(); // Prevents the page from reloading

    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResults([]);
    setShowSuggestions(false);
    const startTime = performance.now();

    try {
      const response = await axios.get("http://127.0.0.1:8000/search", {
        params: { query },
      });

      const endTime = performance.now();
      setFetchTime(((endTime - startTime) / 1000).toFixed(5));

      if (response.data.error) {
        setError(response.data.error);
        setResults([]);
      } else {
        setResults(
          response.data.results.map((docId) => ({
            id: docId,
            snippet: response.data.snippets[docId] || "Snippet not available",
          }))
        );
      }
    } catch (err) {
      setError("Error fetching results.");
      setResults([]);
    }
    setLoading(false);
  };


  const fetchFullDocument = async (docId) => {
    setDocLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/document", {
        params: { doc_id: docId },
      });
      setFullDocument(response.data);
      setIsModalOpen(true); // Open the modal
    } catch (err) {
      console.error("Error fetching document:", err);
      setFullDocument({ error: "Error loading document" });
    }
    setDocLoading(false);
  };

  return (
    <div className="container">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="search-box"
      >
        <h1 className="title">ShahQuery</h1>

        <div className="input-group-container">
          <div className="input-group">
            <FaSearch className="search-icon" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter search query..."
              className="search-input"
              onFocus={() => query.length > 1 && setShowSuggestions(true)}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSearch}
              className="search-button"
            >
              Search
            </motion.button>
          </div>

          {/* Suggestions should be outside input-group but inside input-group-container */}
          {showSuggestions && suggestions.length > 0 && (
            <ul className="suggestions" ref={suggestionBoxRef}>
              {suggestions.map((suggestion, index) => (
                <li
                  key={index}
                  className={index === activeSuggestion ? "active-suggestion" : ""}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                   <FaSearch className="suggestion-icon" />
                  {suggestion}
                </li>
              ))}
            </ul>
          )}
        </div>



        {loading && (
          <motion.p
            className="loading"
            animate={{ opacity: [0, 1], transition: { repeat: Infinity, duration: 1 } }}
          >
            Fetching results...
          </motion.p>
        )}
        {error && <p className="error">{error}</p>}

        {results.length > 0 && (
          <div className="results">
            <p className="results-info">
              {results.length} result(s) fetched in {fetchTime} sec
            </p>
            <motion.ul
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="results-list"
            >
              {results.map((doc) => (
                <li key={doc.id} className="result-item" onClick={() => fetchFullDocument(doc.id)}>
                  <strong className="result-id">📄 Document ID:</strong> {doc.id}
                  <p className="result-snippet" dangerouslySetInnerHTML={{ __html: doc.snippet }} />
                </li>
              ))}
            </motion.ul>
          </div>
        )}
      </motion.div>

      {isModalOpen && fullDocument && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setIsModalOpen(false)}>×</button>
            <h2>Document {fullDocument.doc_id}</h2>
            <p>{fullDocument.content}</p>
          </div>
        </div>
      )}

    </div>

  );
}

export default App;
