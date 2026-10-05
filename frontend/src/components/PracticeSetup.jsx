import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./PracticeSetup.css";

function formatApiError(errBody, fallback) {
  if (!errBody) return fallback;
  if (typeof errBody === "string") return errBody;
  if (errBody.error) return errBody.error;
  if (errBody.detail) {
    if (typeof errBody.detail === "string") return errBody.detail;
    if (errBody.detail.error) return errBody.detail.error;
  }
  return fallback;
}

function PracticeSetup() {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [presets, setPresets] = useState(null);
  const [history, setHistory] = useState([]);
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("patient");
  const [difficulty, setDifficulty] = useState("beginner");
  const [friendMode, setFriendMode] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [statusRes, presetsRes, historyRes] = await Promise.all([
          fetch("/api/status"),
          fetch("/api/presets"),
          fetch("/api/history?limit=5"),
        ]);
        const statusData = await statusRes.json();
        const presetsData = await presetsRes.json();
        const historyData = historyRes.ok ? await historyRes.json() : { sessions: [] };
        if (cancelled) return;
        setStatus(statusData);
        setPresets(presetsData);
        setHistory(historyData.sessions || []);
        if (presetsData.topics?.length && !topic) {
          setTopic(presetsData.topics[0]);
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(
            "Could not reach the backend. Start uvicorn on port 8000, then refresh."
          );
        }
      }
    }
    load();
    const id = setInterval(load, 8000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const practiceCard = presets?.practice_card;
  const friend = presets?.friend;
  const ready = status?.ready;

  const handleStart = () => {
    if (!topic.trim() || !ready) return;
    navigate("/live-arena", {
      state: {
        topic: topic.trim(),
        tone,
        difficulty,
        friendMode,
        autoStart: true,
      },
    });
  };

  return (
    <div className="practice-setup">
      <header className="setup-header">
        <p className="setup-kicker">Friend coaching mode</p>
        <h1 className="setup-title">Spar with a Friend</h1>
        <p className="setup-subtitle">
          Local open-weight practice for{" "}
          <strong>{friend?.name || "Sobaan"}</strong> (
          {friend?.relation || "debate classmate"}) — rehearse GDs without sending
          speech to a cloud chat app.
        </p>
      </header>

      {loadError && (
        <div className="setup-banner error">
          <p>{loadError}</p>
        </div>
      )}

      <div className="setup-grid">
        <section className="setup-card">
          <h2>Runtime</h2>
          {status ? (
            <>
              <div className="setup-meta-row">
                <span
                  className={`mode-pill ${status.local ? "local" : "cloud"}`}
                >
                  {status.local ? "Local · Ollama" : "Cloud · Groq"}
                </span>
                <span className="setup-model">{status.model}</span>
              </div>
              {!ready && (
                <div className="setup-checklist">
                  <p className="checklist-title">
                    Local model not ready
                    {status.detail ? `: ${status.detail}` : ""}
                  </p>
                  <ol>
                    {(status.checklist || []).map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ol>
                </div>
              )}
              {ready && (
                <p className="setup-ready">
                  Ready. Speech stays on this machine when using Ollama.
                </p>
              )}
            </>
          ) : (
            <p className="setup-muted">Checking provider…</p>
          )}
        </section>

        <section className="setup-card">
          <h2>Coach settings</h2>
          <label className="setup-toggle">
            <input
              type="checkbox"
              checked={friendMode}
              onChange={(e) => setFriendMode(e.target.checked)}
            />
            Friend coaching mode (recommended)
          </label>

          <div className="setup-field">
            <span className="field-label">Tone</span>
            <div className="chip-row">
              {(presets?.tones || ["patient", "firm", "rapid-fire"]).map((t) => (
                <button
                  key={t}
                  type="button"
                  className={`chip ${tone === t ? "active" : ""}`}
                  onClick={() => setTone(t)}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="setup-field">
            <span className="field-label">Difficulty</span>
            <div className="chip-row">
              {(presets?.difficulties || ["beginner", "intermediate"]).map(
                (d) => (
                  <button
                    key={d}
                    type="button"
                    className={`chip ${difficulty === d ? "active" : ""}`}
                    onClick={() => setDifficulty(d)}
                  >
                    {d}
                  </button>
                )
              )}
            </div>
          </div>
        </section>

        <section className="setup-card setup-card-wide">
          <h2>Topic</h2>
          <div className="chip-row wrap">
            {(presets?.topics || []).map((t) => (
              <button
                key={t}
                type="button"
                className={`chip ${topic === t ? "active" : ""}`}
                onClick={() => setTopic(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <input
            className="setup-topic-input"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Or type a custom campus GD / viva topic…"
          />
          <button
            className="setup-start-btn"
            type="button"
            disabled={!topic.trim() || !ready}
            onClick={handleStart}
          >
            Start Live Arena
          </button>
        </section>

        {practiceCard && (
          <section className="setup-card">
            <h2>Practice card</h2>
            <ol className="practice-tips">
              {practiceCard.tips.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ol>
            <p className="setup-muted">{practiceCard.success}</p>
          </section>
        )}

        <section className="setup-card">
          <h2>Past rounds (local)</h2>
          {history.length === 0 ? (
            <p className="setup-muted">No saved rounds yet.</p>
          ) : (
            <ul className="history-list">
              {history.map((s) => (
                <li key={s.id}>
                  <span className="history-topic">{s.topic}</span>
                  <span className="history-meta">
                    {s.tone} · {s.difficulty} · {s.provider}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

export { formatApiError };
export default PracticeSetup;
