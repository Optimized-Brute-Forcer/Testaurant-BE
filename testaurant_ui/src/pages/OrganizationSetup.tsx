import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/client'
import { toast } from 'react-toastify'
import './OrganizationSetup.css'

interface DatabaseCredential {
    database_type: 'MYSQL' | 'POSTGRESQL' | 'MONGODB'
    host: string
    port: number
    username: string
    password: string
    database_name: string
}

interface Team {
    team_name: string
    team_description: string
    manager_email: string
}

export default function OrganizationSetup() {
    const navigate = useNavigate()
    const { user, login } = useAuth()

    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)

    // Organization details
    const [orgName, setOrgName] = useState('')
    const [orgDescription, setOrgDescription] = useState('')

    // Teams
    const [teams, setTeams] = useState<Team[]>([])
    const [currentTeam, setCurrentTeam] = useState<Team>({
        team_name: '',
        team_description: '',
        manager_email: ''
    })

    // Database credentials
    const [databases, setDatabases] = useState<DatabaseCredential[]>([])
    const [currentDb, setCurrentDb] = useState<DatabaseCredential>({
        database_type: 'MYSQL',
        host: '',
        port: 3306,
        username: '',
        password: '',
        database_name: ''
    })

    const addTeam = () => {
        if (!currentTeam.team_name) {
            toast.error('Team name is required')
            return
        }
        setTeams([...teams, currentTeam])
        setCurrentTeam({ team_name: '', team_description: '', manager_email: '' })
        toast.success('Team added')
    }

    const removeTeam = (index: number) => {
        setTeams(teams.filter((_, i) => i !== index))
    }

    const addDatabase = () => {
        if (!currentDb.host || !currentDb.username || !currentDb.database_name) {
            toast.error('Host, username, and database name are required')
            return
        }
        setDatabases([...databases, currentDb])
        setCurrentDb({
            database_type: 'MYSQL',
            host: '',
            port: 3306,
            username: '',
            password: '',
            database_name: ''
        })
        toast.success('Database credentials added')
    }

    const removeDatabase = (index: number) => {
        setDatabases(databases.filter((_, i) => i !== index))
    }

    const handleSubmit = async () => {
        if (!orgName) {
            toast.error('Organization name is required')
            return
        }

        setLoading(true)
        try {
            const response = await apiClient.post('/testaurant/v1/organization/create', {
                organization_name: orgName,
                organization_description: orgDescription,
                admin_email: user?.email,
                teams: teams.length > 0 ? teams : null,
                database_credentials: databases.length > 0 ? databases : null
            })

            toast.success('Organization created successfully!')

            // Re-login to get new token with organization context
            const idToken = localStorage.getItem('google_id_token')
            if (idToken) {
                await login(idToken, response.data.organization_id)
            } else {
                navigate('/login')
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create organization')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="org-setup-container">
            <div className="org-setup-card">
                <div className="org-setup-header">
                    <h1>🏢 Organization Setup</h1>
                    <p>Set up your testing organization</p>
                </div>

                {/* Progress Steps */}
                <div className="progress-steps">
                    <div className={`step ${step >= 1 ? 'active' : ''}`}>
                        <div className="step-number">1</div>
                        <div className="step-label">Organization</div>
                    </div>
                    <div className={`step ${step >= 2 ? 'active' : ''}`}>
                        <div className="step-number">2</div>
                        <div className="step-label">Teams</div>
                    </div>
                    <div className={`step ${step >= 3 ? 'active' : ''}`}>
                        <div className="step-number">3</div>
                        <div className="step-label">Databases</div>
                    </div>
                    <div className={`step ${step >= 4 ? 'active' : ''}`}>
                        <div className="step-number">4</div>
                        <div className="step-label">Review</div>
                    </div>
                </div>

                {/* Step 1: Organization Details */}
                {step === 1 && (
                    <div className="step-content">
                        <h2>Organization Details</h2>
                        <p className="step-description">You will be the admin of this organization</p>

                        <div className="form-group">
                            <label>Organization Name *</label>
                            <input
                                type="text"
                                value={orgName}
                                onChange={(e) => setOrgName(e.target.value)}
                                placeholder="e.g., Acme Corp Testing"
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label>Description</label>
                            <textarea
                                value={orgDescription}
                                onChange={(e) => setOrgDescription(e.target.value)}
                                placeholder="Brief description of your organization"
                                className="form-textarea"
                                rows={3}
                            />
                        </div>

                        <div className="form-actions">
                            <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
                                Cancel
                            </button>
                            <button className="btn-primary" onClick={() => setStep(2)}>
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 2: Teams */}
                {step === 2 && (
                    <div className="step-content">
                        <h2>Teams (Optional)</h2>
                        <p className="step-description">Create teams to organize your members</p>

                        <div className="form-group">
                            <label>Team Name</label>
                            <input
                                type="text"
                                value={currentTeam.team_name}
                                onChange={(e) => setCurrentTeam({ ...currentTeam, team_name: e.target.value })}
                                placeholder="e.g., Backend Team"
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label>Team Description</label>
                            <input
                                type="text"
                                value={currentTeam.team_description}
                                onChange={(e) => setCurrentTeam({ ...currentTeam, team_description: e.target.value })}
                                placeholder="Brief description"
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label>Manager Email (Optional)</label>
                            <input
                                type="email"
                                value={currentTeam.manager_email}
                                onChange={(e) => setCurrentTeam({ ...currentTeam, manager_email: e.target.value })}
                                placeholder="manager@example.com"
                                className="form-input"
                            />
                        </div>

                        <button className="btn-add" onClick={addTeam}>
                            + Add Team
                        </button>

                        {teams.length > 0 && (
                            <div className="items-list">
                                <h3>Added Teams ({teams.length})</h3>
                                {teams.map((team, index) => (
                                    <div key={index} className="item-card">
                                        <div className="item-info">
                                            <h4>{team.team_name}</h4>
                                            <p>{team.team_description || 'No description'}</p>
                                            {team.manager_email && <span className="item-meta">Manager: {team.manager_email}</span>}
                                        </div>
                                        <button className="btn-remove" onClick={() => removeTeam(index)}>
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="form-actions">
                            <button className="btn-secondary" onClick={() => setStep(1)}>
                                Back
                            </button>
                            <button className="btn-primary" onClick={() => setStep(3)}>
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Database Credentials */}
                {step === 3 && (
                    <div className="step-content">
                        <h2>Database Credentials (Optional)</h2>
                        <p className="step-description">Add database connections for testing</p>

                        <div className="form-group">
                            <label>Database Type</label>
                            <select
                                value={currentDb.database_type}
                                onChange={(e) => setCurrentDb({
                                    ...currentDb,
                                    database_type: e.target.value as any,
                                    port: e.target.value === 'MONGODB' ? 27017 : e.target.value === 'POSTGRESQL' ? 5432 : 3306
                                })}
                                className="form-select"
                            >
                                <option value="MYSQL">MySQL</option>
                                <option value="POSTGRESQL">PostgreSQL</option>
                                <option value="MONGODB">MongoDB</option>
                            </select>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Host *</label>
                                <input
                                    type="text"
                                    value={currentDb.host}
                                    onChange={(e) => setCurrentDb({ ...currentDb, host: e.target.value })}
                                    placeholder="localhost or IP"
                                    className="form-input"
                                />
                            </div>

                            <div className="form-group">
                                <label>Port *</label>
                                <input
                                    type="number"
                                    value={currentDb.port}
                                    onChange={(e) => setCurrentDb({ ...currentDb, port: parseInt(e.target.value) })}
                                    className="form-input"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Username *</label>
                            <input
                                type="text"
                                value={currentDb.username}
                                onChange={(e) => setCurrentDb({ ...currentDb, username: e.target.value })}
                                placeholder="Database username"
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label>Password *</label>
                            <input
                                type="password"
                                value={currentDb.password}
                                onChange={(e) => setCurrentDb({ ...currentDb, password: e.target.value })}
                                placeholder="Database password"
                                className="form-input"
                            />
                        </div>

                        <div className="form-group">
                            <label>Database Name *</label>
                            <input
                                type="text"
                                value={currentDb.database_name}
                                onChange={(e) => setCurrentDb({ ...currentDb, database_name: e.target.value })}
                                placeholder="Database name"
                                className="form-input"
                            />
                        </div>

                        <button className="btn-add" onClick={addDatabase}>
                            + Add Database
                        </button>

                        {databases.length > 0 && (
                            <div className="items-list">
                                <h3>Added Databases ({databases.length})</h3>
                                {databases.map((db, index) => (
                                    <div key={index} className="item-card">
                                        <div className="item-info">
                                            <h4>{db.database_type} - {db.database_name}</h4>
                                            <p>{db.username}@{db.host}:{db.port}</p>
                                        </div>
                                        <button className="btn-remove" onClick={() => removeDatabase(index)}>
                                            Remove
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="form-actions">
                            <button className="btn-secondary" onClick={() => setStep(2)}>
                                Back
                            </button>
                            <button className="btn-primary" onClick={() => setStep(4)}>
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 4: Review */}
                {step === 4 && (
                    <div className="step-content">
                        <h2>Review & Create</h2>
                        <p className="step-description">Review your organization setup</p>

                        <div className="review-section">
                            <h3>Organization</h3>
                            <div className="review-item">
                                <span className="review-label">Name:</span>
                                <span className="review-value">{orgName}</span>
                            </div>
                            <div className="review-item">
                                <span className="review-label">Description:</span>
                                <span className="review-value">{orgDescription || 'None'}</span>
                            </div>
                            <div className="review-item">
                                <span className="review-label">Admin:</span>
                                <span className="review-value">{user?.email}</span>
                            </div>
                        </div>

                        {teams.length > 0 && (
                            <div className="review-section">
                                <h3>Teams ({teams.length})</h3>
                                {teams.map((team, index) => (
                                    <div key={index} className="review-item">
                                        <span className="review-label">{team.team_name}:</span>
                                        <span className="review-value">
                                            {team.manager_email ? `Manager: ${team.manager_email}` : 'No manager'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}

                        {databases.length > 0 && (
                            <div className="review-section">
                                <h3>Databases ({databases.length})</h3>
                                {databases.map((db, index) => (
                                    <div key={index} className="review-item">
                                        <span className="review-label">{db.database_type}:</span>
                                        <span className="review-value">{db.database_name}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="form-actions">
                            <button className="btn-secondary" onClick={() => setStep(3)}>
                                Back
                            </button>
                            <button
                                className="btn-primary"
                                onClick={handleSubmit}
                                disabled={loading}
                            >
                                {loading ? 'Creating...' : 'Create Organization'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
