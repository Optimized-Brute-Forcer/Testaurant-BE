import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import { toast } from 'react-toastify'
import './OnboardingPage.css'

interface Organization {
    organization_id: string
    organization_name: string
    organization_description?: string
}

export default function OnboardingPage() {
    const navigate = useNavigate()
    const [view, setView] = useState<'select' | 'create' | 'join'>('select')
    const [orgs, setOrgs] = useState<Organization[]>([])
    const [myRequests, setMyRequests] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const [selectedRole, setSelectedRole] = useState('2') // Default ORG_MEMBER

    useEffect(() => {
        if (view === 'join') {
            fetchOrganizations()
            fetchMyRequests()
        }
    }, [view])

    const fetchMyRequests = async () => {
        try {
            const response = await apiClient.get('/testaurant/v1/organization/my-requests')
            setMyRequests(response.data)
        } catch (error) {
            // Optional error handling
        }
    }

    const fetchOrganizations = async () => {
        setLoading(true)
        try {
            const response = await apiClient.get('/testaurant/v1/organization/list')
            setOrgs(response.data)
        } catch (error) {
            toast.error('Failed to load organizations')
        } finally {
            setLoading(false)
        }
    }

    const handleJoin = async (orgId: string) => {
        setLoading(true)
        try {
            await apiClient.post(`/testaurant/v1/organization/join/${orgId}?role=${selectedRole}`)
            toast.info('Request sent to administrator for approval')
            fetchMyRequests()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to send join request')
        } finally {
            setLoading(false)
        }
    }

    const filteredOrgs = orgs.filter(org =>
        org.organization_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        org.organization_id.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="onboarding-container">
            <div className="onboarding-card">
                {view === 'select' && (
                    <div className="onboarding-content">
                        <h1>Welcome to Testaurant</h1>
                        <p className="subtitle">Choose how you want to get started</p>

                        <div className="onboarding-options">
                            <div className="onboarding-option" onClick={() => navigate('/organization/setup')}>
                                <div className="option-icon">🚀</div>
                                <div className="option-text">
                                    <h3>Create Organization</h3>
                                    <p>Start a new workspace for your team</p>
                                </div>
                            </div>

                            <div className="onboarding-option" onClick={() => setView('join')}>
                                <div className="option-icon">🤝</div>
                                <div className="option-text">
                                    <h3>Join Organization</h3>
                                    <p>Enter an existing organization</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {view === 'join' && (
                    <div className="onboarding-content">
                        <div className="content-header">
                            <button className="back-btn" onClick={() => setView('select')}>← Back</button>
                            <h2>Join Organization</h2>
                        </div>

                        <div className="org-search">
                            <input
                                type="text"
                                placeholder="Search by organization name or ID..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        <div className="org-list">
                            {loading ? (
                                <div className="loading-placeholder">Loading organizations...</div>
                            ) : filteredOrgs.length === 0 ? (
                                <div className="empty-placeholder">No organizations found.</div>
                            ) : (
                                filteredOrgs.map(org => {
                                    const pendingRequest = myRequests.find(r => r.organization_id === org.organization_id && r.status === 'PENDING')
                                    const rejectedRequest = myRequests.find(r => r.organization_id === org.organization_id && r.status === 'REJECTED')

                                    return (
                                        <div key={org.organization_id} className={`org-item ${pendingRequest ? 'pending' : ''}`}>
                                            <div className="org-info">
                                                <h4>{org.organization_name}</h4>
                                                <p>{org.organization_description || 'No description provided'}</p>
                                                <span className="org-id">ID: {org.organization_id}</span>
                                                {rejectedRequest && <span className="status-label rejected">Request Denied</span>}
                                                {!pendingRequest && (
                                                    <div className="role-select-container" onClick={e => e.stopPropagation()} style={{ marginTop: '8px' }}>
                                                        <select
                                                            className="role-select"
                                                            value={selectedRole}
                                                            onChange={(e) => setSelectedRole(e.target.value)}
                                                            style={{
                                                                padding: '6px',
                                                                borderRadius: '6px',
                                                                background: 'rgba(255,255,255,0.1)',
                                                                color: '#fff',
                                                                border: '1px solid rgba(255,255,255,0.2)'
                                                            }}
                                                        >
                                                            <option value="2">Request Member</option>
                                                            <option value="1">Request Admin</option>
                                                        </select>
                                                    </div>
                                                )}
                                            </div>
                                            <button
                                                className={`join-btn ${pendingRequest ? 'btn-pending' : ''}`}
                                                onClick={() => !pendingRequest && handleJoin(org.organization_id)}
                                                disabled={loading || !!pendingRequest}
                                            >
                                                {pendingRequest ? 'Requested' : 'Join'}
                                            </button>
                                        </div>
                                    )
                                })
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div className="onboarding-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
            </div>
        </div>
    )
}
