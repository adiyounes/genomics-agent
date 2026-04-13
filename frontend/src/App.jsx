import { useState } from "react";
import axios from "axios"
import "./index.css"

const API_URL = "http://54.195.19.197:8000"
export default function App() {
  const [geneName, setGeneName] = useState("")
  const [conditionName, setConditionName] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleSearch() {
    setError(null)
    setResult(null)
    setLoading(true)

    try{
      const response = await axios.post(`${API_URL}/research`,{
        gene_name: geneName,
        condition_name: conditionName
      })
      setResult(response.data)
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Something went wrong"
      )
  } finally {
    setLoading(false)
    }
  }
  function parseBullets(summary) {
    return summary
      .split("\n")
      .filter((line) => line.trim().startsWith("- "))
      .map((line) => line.trim().slice(2))
  }

  return(
    <div className="app">
      <header className="header">
        <h1>Genomics Research Agent</h1>
        <p>AI-powered literature search for gene-condition pairs</p>
      </header>
      <div className="card search-card">
        <div className="inputs">
          <div className="field">
            <label htmlFor="gene">Gene Name</label>
            <input type="text" 
                    name="gene_name_input"  
                    id="gene"
                    placeholder="BRCA1"
                    value={geneName}
                    onChange={(e) => setGeneName(e.target.value)} />
          </div>
          <div className="field">
              <label htmlFor="condition">Condition</label>
              <input type="text"
                      id="condition"
                      placeholder="Condition"
                      name="condition_input"
                      value={conditionName}
                      onChange={(e) => setConditionName(e.target.value)} />
          </div>
        </div>
        <button className="btn"
                onClick={handleSearch}
                disabled={loading || !geneName.trim() || !conditionName.trim()}
                >{loading ? "Searching..." : "Search latest reasearch"}  
                </button>
      </div>
      {loading && (
          <div className="status">
            <div className="dot loading" />
              <span>
                Searching PubMed, fetching summerising
              </span>
          </div>
      )}

      {error && (
        <div className="status error">
          <div className="dot error-dot">
          </div>
          <span>{error}</span>
        </div>
      )}
      {result && (
        <>
          <div className="status">
            <div className="dot">
              </div>
              <span>
                Found papers : summerised top {result.sources.length} in {" "}
                {result.attempts} attempt{result.attempts > 1 ? "s" : ""}
              </span>
              {
                result.warning && (
                  <span className="warning-badge">{result.warning}</span>
                )
              }

          </div>
          <div className="card">
              <div className="card-header">
                  <span className="card-title">Research summary</span>
                  <span className="badge">RELEVANT</span>
              </div>
              <div className="bullets">
                  {
                    parseBullets(result.summary).map((bullet,i) => (
                      <div key={i} className="bullet">
                        <div className="bullet-dot"/>
                        <p>{bullet}</p>
                      </div>
                    ))
                  }
            </div>
          </div>
          <div className="sources">
                <h3>Sources</h3>
                {result.sources.map((source)=>(
                  <div key={source.pmid} className="source-item">
                    <div>
                      <div className="source-title">{source.title}</div>
                      <div className="source-meta">
                        {source.authors} - {source.journal} - {source.year}
                      </div>
                    </div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="source-link"
                    >PubMed ↗
                    </a>
                  </div>
                ))}
          </div>
        </>
      )}
    </div>
  )
}
