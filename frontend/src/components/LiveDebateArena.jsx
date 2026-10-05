import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import RoundTabs from "./RoundTabs";
import UserPosition from "./UserPosition";
import AICounterposition from "./AICounterposition";
import { formatApiError } from "./PracticeSetup";
import "./LiveDebateArena.css";

const SAMPLE_TOPICS = [
    "Placements matter more than CGPA for campus careers",
    "Mandatory attendance should be abolished in college",
    "Social media makes it harder for shy students to speak up",
    "Viva: Defend one design choice you made in a recent project",
];

const DEFAULT_TIPS = [
    'Start with a template: "My point is X because Y."',
    "Say one clear sentence, then add one reason — stop talking after two points.",
    "If you freeze, restate the topic in your own words, then give your first claim.",
];

function LiveDebateArena() {
    const location = useLocation();
    const navState = location.state || {};

    const [topic, setTopic] = useState(navState.topic || "");
    const [tone, setTone] = useState(navState.tone || "patient");
    const [difficulty, setDifficulty] = useState(navState.difficulty || "beginner");
    const [friendMode, setFriendMode] = useState(
        navState.friendMode !== undefined ? navState.friendMode : true
    );
    const [hasStarted, setHasStarted] = useState(Boolean(navState.autoStart && navState.topic));
    const [showPracticeCard, setShowPracticeCard] = useState(
        Boolean(navState.autoStart && navState.topic)
    );
    const [practiceTips, setPracticeTips] = useState(DEFAULT_TIPS);
    const [currentRound, setCurrentRound] = useState("opening");
    const [userArguments, setUserArguments] = useState({
        opening: [],
        rebuttal: [],
        closing: [],
    });
    const [aiResponses, setAiResponses] = useState({
        opening: [],
        rebuttal: [],
        closing: [],
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [checklist, setChecklist] = useState(null);
    const [report, setReport] = useState(null);
    const [reportLoading, setReportLoading] = useState(false);

    useEffect(() => {
        fetch("/api/presets")
            .then((r) => (r.ok ? r.json() : null))
            .then((data) => {
                if (data?.practice_card?.tips) {
                    setPracticeTips(data.practice_card.tips);
                }
            })
            .catch(() => {});
    }, []);

    const handleStartDebate = (selectedTopic) => {
        setTopic(selectedTopic);
        setHasStarted(true);
        setShowPracticeCard(true);
        setError(null);
        setChecklist(null);
        setReport(null);
    };

    const handleSubmitArgument = async (argument) => {
        const newUserArg = { text: argument, id: Date.now(), type: "user" };
        setUserArguments((prev) => ({
            ...prev,
            [currentRound]: [...prev[currentRound], newUserArg],
        }));

        setIsLoading(true);
        setError(null);
        setChecklist(null);

        try {
            const allHistory = [];
            ["opening", "rebuttal", "closing"].forEach((round) => {
                userArguments[round].forEach((arg) => {
                    allHistory.push({ type: "user", text: arg.text });
                });
                aiResponses[round].forEach((resp) => {
                    allHistory.push({ type: "ai", text: resp.text });
                });
            });
            allHistory.push({ type: "user", text: argument });

            const response = await fetch("/api/live-counter", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    topic: topic,
                    user_argument: argument,
                    round: currentRound,
                    argument_history: allHistory,
                    friend_mode: friendMode,
                    tone,
                    difficulty,
                }),
            });

            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const detail = data.detail || data;
                if (detail.checklist) setChecklist(detail.checklist);
                throw new Error(
                    formatApiError(detail, "Failed to generate counter-argument")
                );
            }

            setAiResponses((prev) => ({
                ...prev,
                [currentRound]: [
                    ...prev[currentRound],
                    {
                        text: data.counter_argument,
                        id: Date.now(),
                        points: data.points,
                        type: "ai",
                    },
                ],
            }));
        } catch (err) {
            console.error("Error generating counter-argument:", err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNextRound = () => {
        const rounds = ["opening", "rebuttal", "closing"];
        const currentIndex = rounds.indexOf(currentRound);
        if (currentIndex < rounds.length - 1) {
            setCurrentRound(rounds[currentIndex + 1]);
        }
    };

    const handleFinishRound = async () => {
        setReportLoading(true);
        setError(null);
        try {
            const userTurns = [];
            ["opening", "rebuttal", "closing"].forEach((round) => {
                userArguments[round].forEach((arg) => {
                    userTurns.push({ round, text: arg.text });
                });
            });
            const allHistory = [];
            ["opening", "rebuttal", "closing"].forEach((round) => {
                userArguments[round].forEach((arg) => {
                    allHistory.push({ type: "user", text: arg.text, round });
                });
                aiResponses[round].forEach((resp) => {
                    allHistory.push({ type: "ai", text: resp.text, round });
                });
            });

            const response = await fetch("/api/round-report", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    topic,
                    user_turns: userTurns,
                    argument_history: allHistory,
                    tone,
                    difficulty,
                    friend_mode: friendMode,
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const detail = data.detail || data;
                if (detail.checklist) setChecklist(detail.checklist);
                throw new Error(formatApiError(detail, "Failed to build report"));
            }
            setReport(data.report);
        } catch (err) {
            setError(err.message);
        } finally {
            setReportLoading(false);
        }
    };

    const canAdvance = userArguments[currentRound].length > 0;
    const closingDone = userArguments.closing.length > 0;

    if (!hasStarted) {
        return (
            <div className="live-arena-container">
                <div className="topic-selection">
                    <h1 className="arena-title">Live Debate Arena</h1>
                    <p className="arena-subtitle">
                        Select a campus GD topic — or start from Practice setup for
                        tone and difficulty.
                    </p>

                    <div className="topic-input-section">
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="Enter a debate topic..."
                            className="topic-input-field"
                        />
                        <button
                            className="start-debate-btn"
                            onClick={() => handleStartDebate(topic)}
                            disabled={!topic.trim()}
                        >
                            Start Debate
                        </button>
                    </div>

                    <div className="coach-inline">
                        <label>
                            Tone
                            <select value={tone} onChange={(e) => setTone(e.target.value)}>
                                <option value="patient">patient</option>
                                <option value="firm">firm</option>
                                <option value="rapid-fire">rapid-fire</option>
                            </select>
                        </label>
                        <label>
                            Difficulty
                            <select
                                value={difficulty}
                                onChange={(e) => setDifficulty(e.target.value)}
                            >
                                <option value="beginner">beginner</option>
                                <option value="intermediate">intermediate</option>
                            </select>
                        </label>
                        <label className="friend-check">
                            <input
                                type="checkbox"
                                checked={friendMode}
                                onChange={(e) => setFriendMode(e.target.checked)}
                            />
                            Friend mode
                        </label>
                    </div>

                    <div className="sample-topics-section">
                        <p className="sample-label">Or choose a topic:</p>
                        <div className="sample-topic-chips">
                            {SAMPLE_TOPICS.map((sampleTopic, index) => (
                                <button
                                    key={index}
                                    className="topic-chip"
                                    onClick={() => handleStartDebate(sampleTopic)}
                                >
                                    {sampleTopic}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="live-arena-container">
            <div className="arena-header">
                <h1 className="debate-topic">{topic}</h1>
                <p className="arena-coach-meta">
                    {tone} · {difficulty}
                    {friendMode ? " · friend coaching" : ""}
                </p>
                <RoundTabs
                    currentRound={currentRound}
                    onRoundChange={setCurrentRound}
                    completedRounds={{
                        opening: userArguments.opening.length > 0,
                        rebuttal: userArguments.rebuttal.length > 0,
                        closing: userArguments.closing.length > 0,
                    }}
                />
            </div>

            {showPracticeCard && (
                <div className="practice-card-banner">
                    <div>
                        <strong>Practice card</strong>
                        <ol>
                            {practiceTips.map((tip, i) => (
                                <li key={i}>{tip}</li>
                            ))}
                        </ol>
                    </div>
                    <button type="button" onClick={() => setShowPracticeCard(false)}>
                        Got it
                    </button>
                </div>
            )}

            {error && (
                <div className="arena-error">
                    <p>Error: {error}</p>
                    {checklist && (
                        <ol className="arena-checklist">
                            {checklist.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ol>
                    )}
                    <button onClick={() => setError(null)}>Dismiss</button>
                </div>
            )}

            {isLoading && (
                <p className="local-loading-hint">
                    Local model is thinking — a 3B Ollama run can take a few seconds…
                </p>
            )}

            <div className="arena-content">
                <UserPosition
                    currentRound={currentRound}
                    arguments={userArguments[currentRound]}
                    onSubmit={handleSubmitArgument}
                    onNextRound={handleNextRound}
                    canAdvance={canAdvance && currentRound !== "closing"}
                />
                <AICounterposition
                    currentRound={currentRound}
                    responses={aiResponses[currentRound]}
                    isLoading={isLoading}
                />
            </div>

            {closingDone && !report && (
                <div className="finish-round-bar">
                    <button
                        type="button"
                        className="finish-round-btn"
                        onClick={handleFinishRound}
                        disabled={reportLoading}
                    >
                        {reportLoading ? "Writing report…" : "Finish round & get report"}
                    </button>
                </div>
            )}

            {report && (
                <div className="round-report-card">
                    <h2>End-of-round report</h2>
                    <p className="report-headline">{report.headline}</p>
                    <h3>Did well</h3>
                    <ul>
                        {(report.did_well || []).map((line, i) => (
                            <li key={`w-${i}`}>{line}</li>
                        ))}
                    </ul>
                    <h3>Try next</h3>
                    <ul>
                        {(report.try_next || []).map((line, i) => (
                            <li key={`t-${i}`}>{line}</li>
                        ))}
                    </ul>
                    <p className="filler-note">{report.filler_note}</p>
                </div>
            )}
        </div>
    );
}

export default LiveDebateArena;
