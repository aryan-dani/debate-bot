import { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
    const [isVisible, setIsVisible] = useState(true);
    const [lastScrollY, setLastScrollY] = useState(0);
    const [status, setStatus] = useState(null);
    const location = useLocation();

    useEffect(() => {
        const handleScroll = () => {
            const currentScrollY = window.scrollY;

            if (currentScrollY < 50) {
                setIsVisible(true);
            } else if (currentScrollY < lastScrollY) {
                setIsVisible(true);
            } else if (currentScrollY > lastScrollY && currentScrollY > 100) {
                setIsVisible(false);
            }

            setLastScrollY(currentScrollY);
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, [lastScrollY]);

    useEffect(() => {
        setIsVisible(true);
        setLastScrollY(0);
    }, [location]);

    useEffect(() => {
        let cancelled = false;
        async function loadStatus() {
            try {
                const res = await fetch("/api/status");
                if (!res.ok) return;
                const data = await res.json();
                if (!cancelled) setStatus(data);
            } catch {
                /* backend may be down during first paint */
            }
        }
        loadStatus();
        const id = setInterval(loadStatus, 10000);
        return () => {
            cancelled = true;
            clearInterval(id);
        };
    }, []);

    return (
        <nav className={`navbar ${isVisible ? "visible" : "hidden"}`}>
            <div className="navbar-container">
                <div className="navbar-links">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                    >
                        Home
                    </NavLink>
                    <NavLink
                        to="/setup"
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                    >
                        Practice
                    </NavLink>
                    <NavLink
                        to="/debate"
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                    >
                        AI Debate
                    </NavLink>
                    <NavLink
                        to="/live-arena"
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                    >
                        Live Arena
                    </NavLink>
                    <NavLink
                        to="/scoring"
                        className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                    >
                        Training
                    </NavLink>
                </div>
                {status && (
                    <span
                        className={`nav-mode-badge ${status.local ? "local" : "cloud"}`}
                        title={status.ready ? status.model : status.detail || "Not ready"}
                    >
                        {status.local ? "Local · Ollama" : "Cloud · Groq"}
                    </span>
                )}
            </div>
        </nav>
    );
}

export default Navbar;
