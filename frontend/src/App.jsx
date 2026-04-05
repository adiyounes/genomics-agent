import { useState } from "react"
import axios from "axios"
import "./index.css"

const API_URL = "http://localhost:8000"

export default function App() {
  const [geneName, setGeneName] = useState("")
  const [conditionName, setConditionName] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleSearch() {
    // Reset previous results
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/research`, {
        gene_name: geneName,
        condition_name: conditionName,
      })
      setResult(response.data)
    } catch (err) {
      // err.response exists when the server replied with an error code
      // err.message exists when the request never reached the server
      setError(
        err.response?.data?.detail || err.message || "Something went wrong."
      )
    } finally {
      // always runs — success or failure
      setLoading(false)
    }
  }

  // Parse the bullet point string into an array of individual bullets
  function parseBullets(summary) {
    return summary
      .split("\n")
      .filter((line) => line.trim().startsWith("- "))
      .map((line) => line.trim().slice(2)) // remove the "- " prefix
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Genomics Research Agent</h1>
        <p>AI-powered literature search for gene–condition pairs</p>
      </header>

      {/* Search form */}
      <div className="card search-card">
        <div className="inputs">
          <div className="field">
            <label htmlFor="gene">Gene name</label>
            <input
              id="gene"
              type="text"
              placeholder="e.g. BRCA1"
              value={geneName}
              onChange={(e) => setGeneName(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="condition">Condition</label>
            <input
              id="condition"
              type="text"
              placeholder="e.g. breast cancer"
              value={conditionName}
              onChange={(e) => setConditionName(e.target.value)}
            />
          </div>
        </div>
        <button
          className="btn"
          onClick={handleSearch}
          disabled={loading || !geneName.trim() || !conditionName.trim()}
        >
          {loading ? "Searching..." : "Search latest research"}
        </button>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="status">
          <div className="dot loading" />
          <span>
            Searching PubMed, fetching abstracts, summarising with Claude...
          </span>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="status error">
          <div className="dot error-dot" />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Status bar */}
          <div className="status">
            <div className="dot" />
            <span>
              Found papers — summarised top {result.sources.length} in{" "}
              {result.attempts} attempt{result.attempts > 1 ? "s" : ""}
            </span>
            {result.warning && (
              <span className="warning-badge">{result.warning}</span>
            )}
          </div>

          {/* Summary card */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Research summary</span>
              <span className="badge">RELEVANT</span>
            </div>

            <div className="bullets">
              {parseBullets(result.summary).map((bullet, i) => (
                <div key={i} className="bullet">
                  <div className="bullet-dot" />
                  <p>{bullet}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Sources */}
          <div className="sources">
            <h3>Sources</h3>
            {result.sources.map((source) => (
              <div key={source.pmid} className="source-item">
                <div>
                  <div className="source-title">{source.title}</div>
                  <div className="source-meta">
                    {source.authors} · {source.journal} · {source.year}
                  </div>
                </div>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="source-link"
                >
                  PubMed ↗
                </a>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
