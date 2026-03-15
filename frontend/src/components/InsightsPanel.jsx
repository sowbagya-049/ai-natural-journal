export default function InsightsPanel({ insights }) {
  if (!insights || insights.totalEntries === 0) {
    return (
      <div className="panel">
        <h2>Insights</h2>
        <p className="subtitle">Insights will appear here once you write your first entry.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Your Insights</h2>
      
      <div className="insights-grid">
        <div className="stat-box">
          <div className="stat-value">{insights.totalEntries}</div>
          <div className="stat-label">Total Entries</div>
        </div>
        
        <div className="stat-box">
          <div className="stat-value" style={{ 
            textTransform: 'capitalize',
            fontSize: insights.topEmotion && insights.topEmotion.length > 8 ? '1.2rem' : '1.8rem'
          }}>
            {insights.topEmotion || 'N/A'}
          </div>
          <div className="stat-label">Top Emotion</div>
        </div>
        
        <div className="stat-box" style={{ gridColumn: 'span 2' }}>
          <div className="stat-value" style={{ textTransform: 'capitalize', fontSize: '1.4rem' }}>
            {insights.mostUsedAmbience || 'N/A'}
          </div>
          <div className="stat-label">Most Used Ambience</div>
        </div>
      </div>

      {insights.recentKeywords && insights.recentKeywords.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem', color: 'var(--text-muted)' }}>
            Recent Keywords
          </h3>
          <div className="tag-list">
            {insights.recentKeywords.map((kw, i) => (
              <span key={i} className="tag">{kw}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
