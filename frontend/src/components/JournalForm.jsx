import { useState } from 'react';

export default function JournalForm({ onEntryCreated, userId }) {
  const [ambience, setAmbience] = useState('forest');
  const [customAmbience, setCustomAmbience] = useState('');
  const [text, setText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const finalAmbience = ambience === 'other' ? customAmbience.trim() : ambience;
    if (!text.trim() || (ambience === 'other' && !finalAmbience)) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/api/journal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId,
          ambience: finalAmbience,
          text: text,
        }),
      });

      if (response.ok) {
        setText('');
        if (onEntryCreated) onEntryCreated();
      }
    } catch (error) {
      console.error('Failed to create entry:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="panel">
      <h2>Write Journal</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="ambience">Ambience</label>
          <select 
            id="ambience" 
            value={ambience} 
            onChange={(e) => {
              setAmbience(e.target.value);
              if (e.target.value !== 'other') setCustomAmbience('');
            }}
            disabled={isSubmitting}
            style={{ marginBottom: ambience === 'other' ? '0.5rem' : '0' }}
          >
            <option value="forest">Forest 🌲</option>
            <option value="ocean">Ocean 🌊</option>
            <option value="mountain">Mountain ⛰️</option>
            <option value="rain">Rain 🌧️</option>
            <option value="river">River 🏞️</option>
            <option value="waterfall">Waterfall 💦</option>
            <option value="night_forest">Night Forest 🦉</option>
            <option value="campfire">Campfire 🔥</option>
            <option value="other">Other...</option>
          </select>
          {ambience === 'other' && (
            <input
              type="text"
              placeholder="Enter custom ambience..."
              value={customAmbience}
              onChange={(e) => setCustomAmbience(e.target.value)}
              disabled={isSubmitting}
              required
            />
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="text">How do you feel today?</label>
          <textarea 
            id="text" 
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="I felt calm today after listening to the rain..."
            disabled={isSubmitting}
            required
          />
        </div>

        <button type="submit" className="btn" disabled={isSubmitting || !text.trim()}>
          {isSubmitting ? (
             <><span className="loader"></span> Saving...</>
          ) : 'Submit Entry'}
        </button>
      </form>
    </div>
  );
}
