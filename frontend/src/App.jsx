import { useState, useEffect } from 'react';
import JournalForm from './components/JournalForm';
import JournalList from './components/JournalList';
import InsightsPanel from './components/InsightsPanel';

// For this assignment, we are mocking a single user session
const USER_ID = "user_123"; 

export default function App() {
  const [entries, setEntries] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Get all entries
      const entriesRes = await fetch(`http://localhost:8000/api/journal/${USER_ID}`);
      if (entriesRes.ok) {
        const entriesData = await entriesRes.json();
        // Sort by id descending to show newest first
        setEntries(entriesData.sort((a, b) => b.id - a.id));
      }

      // Get insights
      const insightsRes = await fetch(`http://localhost:8000/api/journal/insights/${USER_ID}`);
      if (insightsRes.ok) {
        const insightsData = await insightsRes.json();
        setInsights(insightsData);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="container">
      <header>
        <h1>AI Nature Journal</h1>
        <p className="subtitle">Reflect on your nature sessions and discover AI-driven emotional insights.</p>
      </header>

      <div className="grid-layout">
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <JournalForm 
            userId={USER_ID} 
            onEntryCreated={fetchData} 
          />
          <InsightsPanel insights={insights} />
        </div>

        {/* Right Column */}
        <div>
          {loading ? (
             <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
               <span className="loader" style={{ borderColor: 'rgba(99, 102, 241, 0.3)', borderTopColor: 'var(--primary)' }}></span>
               <p style={{ marginTop: '1rem' }}>Loading your journal...</p>
             </div>
          ) : (
            <JournalList entries={entries} onAnalyzeSuccess={fetchData} />
          )}
        </div>
      </div>
    </div>
  );
}
