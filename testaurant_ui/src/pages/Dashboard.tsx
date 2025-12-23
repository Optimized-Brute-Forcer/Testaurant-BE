import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/client'
import './Dashboard.css'

interface Stats {
    workitems: number
    testcases: number
    testsuites: number
    executions: number
}

export default function Dashboard() {
    const { user, currentOrganization, organizations, isAdmin, logout, switchOrganization, leaveOrganization, deleteOrganization } = useAuth()
    const navigate = useNavigate()
    const [showOrgMenu, setShowOrgMenu] = useState(false)
    const [stats, setStats] = useState<Stats>({
        workitems: 0,
        testcases: 0,
        testsuites: 0,
        executions: 0
    })

    useEffect(() => {
        fetchStats()
    }, [])

    useEffect(() => {
        // Close menu when clicking outside
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement
            if (showOrgMenu && !target.closest('.user-menu-container')) {
                setShowOrgMenu(false)
            }
        }

        if (showOrgMenu) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [showOrgMenu])

    const fetchStats = async () => {
        try {
            const response = await apiClient.get('/testaurant/v1/bff/stats')
            setStats(response.data)
        } catch (error) {
            console.error('Failed to fetch stats', error)
        }
    }

    const currentOrg = organizations.find(org => org.organization_id === currentOrganization)

    return (
        <div className="dashboard">
            <nav className="navbar">
                <div className="navbar-brand">
                    <h1>🧪 Testaurant</h1>
                </div>

                <div className="navbar-menu">
                    <div className="user-menu-container">
                        <span
                            className="user-info clickable"
                            onClick={() => setShowOrgMenu(!showOrgMenu)}
                        >
                            {user?.name} • <span className="current-org-name">{currentOrg?.organization_name}</span> ▾
                        </span>

                        {showOrgMenu && (
                            <div className="org-dropdown">
                                <div className="dropdown-header">Switch Organization</div>
                                {organizations.map(org => (
                                    <div
                                        key={org.organization_id}
                                        className={`dropdown-item ${org.organization_id === currentOrganization ? 'active' : ''}`}
                                        onClick={() => {
                                            if (org.organization_id !== currentOrganization) {
                                                switchOrganization(org.organization_id)
                                            }
                                            setShowOrgMenu(false)
                                        }}
                                    >
                                        {org.organization_name}
                                        {org.organization_id === currentOrganization && ' ✓'}
                                    </div>
                                ))}
                                <div className="dropdown-divider"></div>
                                <div
                                    className="dropdown-item"
                                    onClick={() => navigate('/onboarding')}
                                >
                                    Join another Organization
                                </div>
                                <div
                                    className="dropdown-item danger"
                                    onClick={() => {
                                        if (window.confirm('Are you sure you want to leave this organization?')) {
                                            if (currentOrganization) leaveOrganization(currentOrganization)
                                        }
                                        setShowOrgMenu(false)
                                    }}
                                >
                                    Leave Organization
                                </div>
                                {isAdmin && (
                                    <div
                                        className="dropdown-item danger"
                                        onClick={() => {
                                            if (window.confirm('WARNING: Are you sure you want to PERMANENTLY delete this organization? This action cannot be undone.')) {
                                                if (currentOrganization) deleteOrganization(currentOrganization)
                                            }
                                            setShowOrgMenu(false)
                                        }}
                                    >
                                        Delete Organization
                                    </div>
                                )}
                                <div className="dropdown-divider"></div>
                                <div className="dropdown-item" onClick={() => logout()}>
                                    Logout
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </nav>

            <div className="dashboard-content">
                <div className="welcome-section">
                    <h2>Welcome to Testaurant!</h2>
                    <p>Your automated testing platform is ready to use.</p>
                </div>

                <div className="stats-grid">
                    <div className="stat-card clickable" onClick={() => navigate('/workitems')}>
                        <div className="stat-icon">📝</div>
                        <div className="stat-info">
                            <h3>Workitems</h3>
                            <p className="stat-value">{stats.workitems}</p>
                            <p className="stat-label">Total workitems</p>
                        </div>
                    </div>

                    <div className="stat-card clickable" onClick={() => navigate('/testcases')}>
                        <div className="stat-icon">✅</div>
                        <div className="stat-info">
                            <h3>Testcases</h3>
                            <p className="stat-value">{stats.testcases}</p>
                            <p className="stat-label">Total testcases</p>
                        </div>
                    </div>

                    <div className="stat-card clickable" onClick={() => navigate('/testsuites')}>
                        <div className="stat-icon">📦</div>
                        <div className="stat-info">
                            <h3>Testsuites</h3>
                            <p className="stat-value">{stats.testsuites}</p>
                            <p className="stat-label">Total testsuites</p>
                        </div>
                    </div>

                    <div className="stat-card clickable" onClick={() => navigate('/executions')}>
                        <div className="stat-icon">🚀</div>
                        <div className="stat-info">
                            <h3>Executions</h3>
                            <p className="stat-value">{stats.executions}</p>
                            <p className="stat-label">Total runs</p>
                        </div>
                    </div>
                </div>

                {isAdmin && (
                    <div className="quick-actions">
                        <h3>Quick Actions</h3>
                        <div className="action-buttons">
                            <button className="action-btn" onClick={() => navigate('/create/workitem')}>
                                <span className="action-icon">➕</span>
                                Create Workitem
                            </button>
                            <button className="action-btn" onClick={() => navigate('/create/testcase')}>
                                <span className="action-icon">📋</span>
                                Create Testcase
                            </button>
                            <button className="action-btn" onClick={() => navigate('/create/testsuite')}>
                                <span className="action-icon">📦</span>
                                Create Testsuite
                            </button>
                            <button className="action-btn" onClick={() => navigate('/run-tests')}>
                                <span className="action-icon">▶️</span>
                                Run Tests
                            </button>
                            <button className="action-btn" onClick={() => navigate('/members')}>
                                <span className="action-icon">👥</span>
                                Manage Members
                            </button>
                            <button className="action-btn" onClick={() => navigate('/resources')}>
                                <span className="action-icon">🔧</span>
                                Resources
                            </button>
                            <button className="action-btn" onClick={() => navigate('/join-requests')}>
                                <span className="action-icon">📩</span>
                                Review Requests
                            </button>
                        </div>
                    </div>
                )}

                <div className="info-section">
                    <h3>Getting Started</h3>
                    <div className="info-cards">
                        <div className="info-card">
                            <h4>1. Create Workitems</h4>
                            <p>Define individual test operations for REST APIs, SQL queries, or MongoDB operations.</p>
                        </div>
                        <div className="info-card">
                            <h4>2. Build Testcases</h4>
                            <p>Group workitems into testcases to test complete user flows.</p>
                        </div>
                        <div className="info-card">
                            <h4>3. Execute & Validate</h4>
                            <p>Run your tests and view detailed execution logs and validation results.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
