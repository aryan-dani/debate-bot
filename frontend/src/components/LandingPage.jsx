import { useNavigate } from "react-router-dom";
import "./LandingPage.css";

function LandingPage() {
    const navigate = useNavigate();

    const features = [
        {
            id: "practice",
            icon: "🤝",
            title: "Friend Practice",
            description:
                "One-screen setup for patient GD/viva coaching. Local Ollama by default so speech never leaves this laptop.",
            highlights: ["Practice card tips", "Tone & difficulty", "End-of-round report"],
            color: "cyan",
            path: "/setup",
        },
        {
            id: "live-arena",
            icon: "⚔️",
            title: "Live Arena",
            description:
                "Debate against a local open-weight model through Opening, Rebuttal, and Closing — LangGraph orchestrated.",
            highlights: ["Real-time Responses", "Patient coach tone", "Offline-friendly"],
            color: "pink",
            path: "/live-arena",
        },
        {
            id: "training",
            icon: "📊",
            title: "Training & Scoring",
            description:
                "Kind, specific feedback on coherence, evidence, fallacies, and filler words.",
            highlights: ["Performance Metrics", "Skill Assessment", "Improvement Tips"],
            color: "gradient",
            path: "/scoring",
        },
    ];

    return (
        <div className="landing-page">
            <section className="hero-section">
                <div className="hero-background">
                    <div className="hero-orb hero-orb-1"></div>
                    <div className="hero-orb hero-orb-2"></div>
                </div>

                <div className="hero-content">
                    <p className="hero-kicker">Spar with a Friend · built on DebateBot</p>
                    <h1 className="hero-title">
                        Local debate practice for
                        <span className="hero-highlight"> TODO_FRIEND_NAME </span>
                    </h1>
                    <p className="hero-subtitle">
                        Built for someone who freezes in group discussions. An open-weight
                        Ollama model + LangGraph coach runs on this machine so rehearsal
                        speech is not sent to a cloud chat app.
                    </p>
                    <div className="hero-cta">
                        <button
                            className="cta-primary"
                            onClick={() => navigate("/setup")}
                        >
                            Start friend practice
                            <span className="cta-arrow">→</span>
                        </button>
                        <button
                            className="cta-secondary"
                            onClick={() => navigate("/live-arena")}
                        >
                            Open Live Arena
                        </button>
                    </div>
                </div>

                <div className="hero-stats">
                    <div className="stat-item">
                        <span className="stat-number">3</span>
                        <span className="stat-label">Debate Stages</span>
                    </div>
                    <div className="stat-divider"></div>
                    <div className="stat-item">
                        <span className="stat-number">Local</span>
                        <span className="stat-label">Ollama first</span>
                    </div>
                    <div className="stat-divider"></div>
                    <div className="stat-item">
                        <span className="stat-number">GD</span>
                        <span className="stat-label">Campus presets</span>
                    </div>
                </div>
            </section>

            <section className="features-section">
                <div className="section-header">
                    <h2 className="section-title">What We Offer</h2>
                    <p className="section-subtitle">
                        Friend-first practice, then the classic DebateBot tools
                    </p>
                </div>

                <div className="features-grid">
                    {features.map((feature, index) => (
                        <div
                            key={feature.id}
                            className={`feature-card feature-card-${feature.color}`}
                            onClick={() => navigate(feature.path)}
                            style={{ animationDelay: `${index * 0.15}s` }}
                        >
                            <div className="feature-icon">{feature.icon}</div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                            <ul className="feature-highlights">
                                {feature.highlights.map((highlight, i) => (
                                    <li key={i}>
                                        <span className="highlight-dot"></span>
                                        {highlight}
                                    </li>
                                ))}
                            </ul>
                            <div className="feature-action">
                                <span>Explore</span>
                                <span className="feature-arrow">→</span>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}

export default LandingPage;
