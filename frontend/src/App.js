import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const response = await axios.get(`http://127.0.0.1:8000/search`, {
        params: { query },
      });
      if (response.data.error) {
        setError(response.data.error);
        setResults([]);
      } else {
        setError("");
        setResults(response.data.results);
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
      <ul>
        {results.map((doc, index) => (
          <li key={index}>Document ID: {doc}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
