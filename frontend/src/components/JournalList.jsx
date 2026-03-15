import { useState } from 'react';

export default function JournalList({ entries, onAnalyzeSuccess }) {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null);

  const handleAnalyze = async (entry) => {
    setAnalyzingId(entry.id);
    setAnalysisResult(null); // Clear previous
    
    try {
      const response = await fetch('http://localhost:8000/api/journal/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: entry.text,
          id: entry.id,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisResult({ id: entry.id, ...data });
        if (onAnalyzeSuccess) onAnalyzeSuccess();
      }
    } catch (error) {
      console.error('Failed to analyze entry:', error);
    } finally {
      setAnalyzingId(null);
    }
  };

  return (
    <div className="panel">
      <h2>Previous Entries</h2>
      {entries.length === 0 ? (
        <p className="subtitle">No entries yet. Write your first journal entry!</p>
      ) : (
        <div className="entries-container">
          {entries.map((entry) => (
            <div key={entry.id} className="entry-card">
              <div className="entry-header">
                <span>{new Date(entry.created_at).toLocaleDateString()}</span>
                <span className="ambience-badge">{entry.ambience}</span>
              </div>
              <p className="entry-text">{entry.text}</p>
              
              {!entry.emotion && analyzingId !== entry.id && (
                <button 
                  className="btn btn-secondary" 
                  onClick={() => handleAnalyze(entry)}
                  disabled={analyzingId === entry.id}
                  style={{ width: 'auto', padding: '0.5rem 1rem' }}
                >
                  Analyze with AI ✨
                </button>
              )}
              {analyzingId === entry.id && (
                 <button className="btn btn-secondary" disabled style={{ width: 'auto', padding: '0.5rem 1rem' }}>
                    Analyzing...
                 </button>
              )}

              {/* Show analysis if it exists on the entry, or if we just analyzed it */}
              {((analysisResult && analysisResult.id === entry.id) || entry.emotion) && (() => {
                const analysisToRender = (analysisResult && analysisResult.id === entry.id) 
                  ? analysisResult 
                  : { emotion: entry.emotion, keywords: entry.keywords || [], summary: entry.summary };

                return (
                  <div className="analysis-result">
                    <div className="insight-row">
                      <div className="insight-label">Emotion:</div>
                      <div className="insight-value" style={{ textTransform: 'capitalize', fontWeight: 'bold' }}>
                        {analysisToRender.emotion}
                      </div>
                    </div>
                    <div className="insight-row">
                       <div className="insight-label">Keywords:</div>
                       <div className="insight-value tag-list">
                         {analysisToRender.keywords.map((kw, i) => (
                           <span key={i} className="tag">{kw}</span>
                         ))}
                       </div>
                    </div>
                    <div className="insight-row">
                       <div className="insight-label">Summary:</div>
                       <div className="insight-value">{analysisToRender.summary}</div>
                    </div>
                  </div>
                );
              })()}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
