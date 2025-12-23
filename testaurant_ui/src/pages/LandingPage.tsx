import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './LandingPage.css'

export default function LandingPage() {
    const navigate = useNavigate()
    const { isAuthenticated } = useAuth()

    return (
        <div className="landing-container">
            <nav className="landing-nav">
                <div className="nav-logo">
                    <span className="logo-icon">🧪</span>
                    <span className="logo-text">Testaurant</span>
                </div>
                <div className="nav-actions">
                    {isAuthenticated ? (
                        <button className="nav-btn primary" onClick={() => navigate('/dashboard')}>
                            Dashboard
                        </button>
                    ) : (
                        <button className="nav-btn" onClick={() => navigate('/login')}>
                            Sign In
                        </button>
                    )}
                </div>
            </nav>

            <main className="landing-main">
                <div className="hero-section">
                    <div className="hero-content">
                        <h1 className="hero-title">
                            Testing that <span className="highlight">Tastes Better</span>.
                        </h1>
                        <p className="hero-subtitle">
                            The all-in-one automated testing platform for REST APIs, SQL Databases, and MongoDB collections.
                            Build, run, and scale your testing strategy with ease.
                        </p>
                        <div className="hero-cta">
                            <button className="cta-btn main" onClick={() => navigate('/login')}>
                                Get Started for Free
                            </button>
                            <button className="cta-btn secondary">
                                View Documentation
                            </button>
                        </div>
                    </div>
                    <div className="hero-visual">
                        <div className="glass-card main-viz">
                            <div className="viz-header">
                                <div className="viz-dots">
                                    <span></span><span></span><span></span>
                                </div>
                                <div className="viz-addr">api.testaurant.io/v1/run</div>
                            </div>
                            <div className="viz-body">
                                <div className="code-line"><span className="token-keyword">POST</span> /executions</div>
                                <div className="code-line indent-1">{"{"}</div>
                                <div className="code-line indent-2">"<span className="token-key">testsuite_id</span>": <span className="token-string">"ts_8829"</span>,</div>
                                <div className="code-line indent-2">"<span className="token-key">environment</span>": <span className="token-string">"QA"</span></div>
                                <div className="code-line indent-1">{"}"}</div>
                                <div className="status-badge success">Status: 200 OK</div>
                            </div>
                        </div>
                        <div className="floating-elements">
                            <div className="float-card c1">SQL</div>
                            <div className="float-card c2">REST</div>
                            <div className="float-card c3">NoSQL</div>
                        </div>
                    </div>
                </div>

                <div className="features-section">
                    <div className="feature-grid">
                        <div className="feature-card">
                            <div className="feat-icon">🎯</div>
                            <h3>Unified testing</h3>
                            <p>One platform for all your backend testing needs. No more context switching.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feat-icon">🛡️</div>
                            <h3>Enterprise RBAC</h3>
                            <p>Granular role-based access control for teams and organizations of all sizes.</p>
                        </div>
                        <div className="feature-card">
                            <div className="feat-icon">📈</div>
                            <h3>Real-time Analytics</h3>
                            <p>Track your test performance and execution trends with deep insights.</p>
                        </div>
                    </div>
                </div>
            </main>

            <footer className="landing-footer">
                <p>&copy; 2025 Testaurant. Crafted with 💜 for developers.</p>
            </footer>

            <div className="landing-bg">
                <div className="bg-orb p1"></div>
                <div className="bg-orb p2"></div>
                <div className="bg-orb p3"></div>
            </div>
        </div>
    )
}
