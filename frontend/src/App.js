import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const response = await axios.get("http://127.0.0.1:8000/search", {
        params: { query },
        headers: { "Content-Type": "application/json" },
      });

      if (response.data.error) {
        setError(response.data.error);
        setResults([]);
      } else {
        setError("");
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
  };

  return (
    <div className="container">
      <h1>Document Search</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter query (Boolean or Positional)"
      />
      <button onClick={handleSearch}>Search</button>
      {error && <p className="error">{error}</p>}
      
      {results.length > 0 && (
        <div>
          <h3>Matching Document IDs:</h3>
          <p>{results.map((doc) => doc.id).join(", ")}</p>
        </div>
      )}
      
      <ul>
        {results.map((doc) => (
          <li key={doc.id}>
            <strong>Document ID:</strong> {doc.id}
            <p dangerouslySetInnerHTML={{ __html: doc.snippet }} />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
