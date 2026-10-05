import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import LandingPage from "./components/LandingPage";
import PracticeSetup from "./components/PracticeSetup";
import DebateInput from "./components/DebateInput";
import DebateArena from "./components/DebateArena";
import LiveDebateArena from "./components/LiveDebateArena";
import Scoring from "./components/Scoring";
import { formatApiError } from "./components/PracticeSetup";
import "./App.css";

function App() {
  const [debateData, setDebateData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [checklist, setChecklist] = useState(null);

  const handleStartDebate = async (topic) => {
    setIsLoading(true);
    setError(null);
    setChecklist(null);

    try {
      const response = await fetch("/api/debate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic,
          friend_mode: true,
          tone: "patient",
          difficulty: "beginner",
        }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = data.detail || data;
        if (detail.checklist) setChecklist(detail.checklist);
        throw new Error(formatApiError(detail, "Failed to generate debate"));
      }

      setDebateData(data);
    } catch (err) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setDebateData(null);
    setError(null);
    setChecklist(null);
  };

  return (
    <div className="app">
      <Navbar />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/setup" element={<PracticeSetup />} />
        <Route
          path="/debate"
          element={
            <>
              <header className="header">
                <h1 className="title">The AI Debate</h1>
                {debateData && <p className="subtitle">{debateData.topic}</p>}
                {!debateData && !isLoading && (
                  <p className="subtitle">Enter a topic to start the debate</p>
                )}
              </header>

              <main className="main-content">
                {!debateData && !isLoading && (
                  <DebateInput onSubmit={handleStartDebate} />
                )}

                {isLoading && (
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p className="loading-text">Generating debate arguments...</p>
                    <p className="loading-subtext">
                      Local Ollama can take longer than cloud APIs — hang tight
                    </p>
                  </div>
                )}

                {error && (
                  <div className="error-container">
                    <p className="error-text">Error: {error}</p>
                    {checklist && (
                      <ol className="error-checklist">
                        {checklist.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ol>
                    )}
                    <button onClick={handleReset} className="retry-btn">
                      Try Again
                    </button>
                  </div>
                )}

                {debateData && !isLoading && (
                  <>
                    {debateData.practice_card && (
                      <div className="debate-practice-card">
                        <strong>Practice card</strong>
                        <ol>
                          {debateData.practice_card.tips.map((tip, i) => (
                            <li key={i}>{tip}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                    <DebateArena data={debateData} />
                    <div className="reset-container">
                      <button onClick={handleReset} className="new-debate-btn">
                        Start New Debate
                      </button>
                    </div>
                  </>
                )}
              </main>
            </>
          }
        />
        <Route path="/live-arena" element={<LiveDebateArena />} />
        <Route path="/scoring" element={<Scoring />} />
      </Routes>
    </div>
  );
}

export default App;
