import React, { useState } from "react";
import axios from "axios";
import { FaSearch } from "react-icons/fa";
import { motion } from "framer-motion";
import "./App.css"; // Import the CSS file for styling

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchTime, setFetchTime] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);
    const startTime = performance.now();

    try {
      const response = await axios.get("http://127.0.0.1:8000/search", {
        params: { query },
        headers: { "Content-Type": "application/json" },
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

  return (
    <div className="container">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="search-box"
      >
        <h1 className="title"> Smart Document Search</h1>

        <div className="input-group">
          <FaSearch className="search-icon" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter search query..."
            className="search-input"
          />
          <button onClick={handleSearch} className="search-button">
            Search
          </button>
        </div>

        {loading && <p className="loading">Fetching results...</p>}
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
                <li key={doc.id} className="result-item">
                  <strong className="result-id">📄 Document ID:</strong> {doc.id}
                  <p
                    className="result-snippet"
                    dangerouslySetInnerHTML={{ __html: doc.snippet }}
                  />
                </li>
              ))}
            </motion.ul>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default App;
