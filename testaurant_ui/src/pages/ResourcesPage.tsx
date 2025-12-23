
import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import apiClient from '../api/client'
import { FaDatabase, FaCode, FaPlus, FaTrash, FaEdit } from 'react-icons/fa'
import { toast } from 'react-toastify'
import './ResourcesPage.css'
import { useNavigate } from 'react-router-dom'

interface DatabaseCredential {
    database_type: string
    host: string
    port: number
    username: string
    password?: string
    database_name: string
}

interface EnvironmentVariable {
    key: string
    value: string
    description?: string
}

export default function ResourcesPage() {
    const { isAdmin, currentOrganization } = useAuth()
    const navigate = useNavigate()
    const [activeTab, setActiveTab] = useState<'connections' | 'env-vars'>('connections')

    // Connections State
    const [connections, setConnections] = useState<DatabaseCredential[]>([])
    const [showAddConnection, setShowAddConnection] = useState(false)
    const [connectionForm, setConnectionForm] = useState<DatabaseCredential>({
        database_type: 'MYSQL',
        host: '',
        port: 3306,
        username: '',
        password: '',
        database_name: ''
    })
    // We track if we are in "edit mode" just to update UI title, 
    // but logically "Save" handles upsert based on host/port/db.
    const [isEditingConnection, setIsEditingConnection] = useState(false)


    // Env Vars State
    const [envVars, setEnvVars] = useState<EnvironmentVariable[]>([])
    const [showAddEnvVar, setShowAddEnvVar] = useState(false)
    const [newEnvVar, setNewEnvVar] = useState<EnvironmentVariable>({
        key: '',
        value: '',
        description: ''
    })

    useEffect(() => {
        if (currentOrganization) {
            fetchConnections()
            fetchEnvVars()
        }
    }, [currentOrganization])

    const fetchConnections = async () => {
        if (!currentOrganization) return
        try {
            const res = await apiClient.get(`/testaurant/v1/organization/${currentOrganization}/credentials`)
            setConnections(res.data)
        } catch (error) {
            console.error(error)
            toast.error('Failed to fetch connections')
        }
    }

    const fetchEnvVars = async () => {
        if (!currentOrganization) return
        try {
            const res = await apiClient.get(`/testaurant/v1/organization/${currentOrganization}/env-vars`)
            setEnvVars(res.data)
        } catch (error) {
            console.error(error)
            toast.error('Failed to fetch environment variables')
        }
    }

    const handleDeleteConnection = async (conn: DatabaseCredential) => {
        if (!window.confirm(`Delete connection to ${conn.database_name}?`)) return
        try {
            await apiClient.delete(`/testaurant/v1/organization/${currentOrganization}/credentials`, {
                params: {
                    host: conn.host,
                    port: conn.port,
                    database_name: conn.database_name
                }
            })
            toast.success('Connection deleted')
            fetchConnections()
        } catch (error) {
            toast.error('Failed to delete connection')
        }
    }

    const handleEditConnection = (conn: DatabaseCredential) => {
        setConnectionForm({
            ...conn,
            password: '' // Clear masked password, force re-entry or leave blank logic? 
            // Actually backend requires password. If user leaves blank, we can't send blank.
            // So user MUST re-enter password to edit.
        })
        setIsEditingConnection(true)
        setShowAddConnection(true)
    }

    const handleSaveConnection = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!connectionForm.password) {
            toast.warn('Please enter the password')
            return
        }

        try {
            // endpoint app/controllers/organization_controller.py:146 expects { database_credentials: List[...] }
            await apiClient.post(`/testaurant/v1/organization/${currentOrganization}/databases`, {
                database_credentials: [connectionForm]
            })
            toast.success(isEditingConnection ? 'Connection updated' : 'Connection added')
            setShowAddConnection(false)
            setConnectionForm({
                database_type: 'MYSQL',
                host: '',
                port: 3306,
                username: '',
                password: '',
                database_name: ''
            })
            setIsEditingConnection(false)
            fetchConnections()
        } catch (error) {
            console.error(error)
            toast.error('Failed to save connection')
        }
    }


    const handleDeleteEnvVar = async (key: string) => {
        if (!window.confirm(`Delete variable ${key}?`)) return
        try {
            await apiClient.delete(`/testaurant/v1/organization/${currentOrganization}/env-vars/${key}`)
            toast.success('Variable deleted')
            fetchEnvVars()
        } catch (error) {
            toast.error('Failed to delete variable')
        }
    }

    const handleAddEnvVar = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            await apiClient.post(`/testaurant/v1/organization/${currentOrganization}/env-vars`, newEnvVar)
            toast.success('Variable added')
            setShowAddEnvVar(false)
            setNewEnvVar({ key: '', value: '', description: '' })
            fetchEnvVars()
        } catch (error) {
            toast.error('Failed to add variable')
        }
    }

    return (
        <div className="resources-page">
            <div className="resources-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => navigate('/dashboard')}>
                        ← Back
                    </button>
                    <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
                        <FaDatabase /> Resources
                    </h1>
                </div>
            </div>

            {/* Tabs */}
            <div className="resources-tabs">
                <button
                    className={`tab-btn ${activeTab === 'connections' ? 'active' : ''}`}
                    onClick={() => setActiveTab('connections')}
                >
                    <FaDatabase /> Connections
                </button>
                <button
                    className={`tab-btn ${activeTab === 'env-vars' ? 'active' : ''}`}
                    onClick={() => setActiveTab('env-vars')}
                >
                    <FaCode /> Environment Variables
                </button>
            </div>

            {/* Connections Tab */}
            {activeTab === 'connections' && (
                <div>
                    <div className="section-actions">
                        {!showAddConnection && isAdmin && (
                            <button
                                className="add-btn"
                                onClick={() => {
                                    setConnectionForm({
                                        database_type: 'MYSQL',
                                        host: '',
                                        port: 3306,
                                        username: '',
                                        password: '',
                                        database_name: ''
                                    })
                                    setIsEditingConnection(false)
                                    setShowAddConnection(true)
                                }}
                            >
                                <FaPlus /> Add Connection
                            </button>
                        )}
                    </div>

                    {showAddConnection && (
                        <div className="add-form-card">
                            <h3 className="text-white mb-4">{isEditingConnection ? 'Edit Connection' : 'New Connection'}</h3>
                            <form onSubmit={handleSaveConnection}>
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label>Type</label>
                                        <select
                                            value={connectionForm.database_type}
                                            onChange={e => setConnectionForm({ ...connectionForm, database_type: e.target.value })}
                                            className="form-input bg-gray-800"
                                        >
                                            <option value="MYSQL">MySQL</option>
                                            <option value="POSTGRESQL">PostgreSQL</option>
                                            <option value="MONGODB">MongoDB</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Host</label>
                                        <input
                                            type="text"
                                            value={connectionForm.host}
                                            onChange={e => setConnectionForm({ ...connectionForm, host: e.target.value })}
                                            className="form-input"
                                            placeholder="localhost"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Port</label>
                                        <input
                                            type="number"
                                            value={connectionForm.port}
                                            onChange={e => setConnectionForm({ ...connectionForm, port: parseInt(e.target.value) })}
                                            className="form-input"
                                            placeholder="3306"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Database Name</label>
                                        <input
                                            type="text"
                                            value={connectionForm.database_name}
                                            onChange={e => setConnectionForm({ ...connectionForm, database_name: e.target.value })}
                                            className="form-input"
                                            placeholder="my_db"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Username</label>
                                        <input
                                            type="text"
                                            value={connectionForm.username}
                                            onChange={e => setConnectionForm({ ...connectionForm, username: e.target.value })}
                                            className="form-input"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Password</label>
                                        <input
                                            type="password"
                                            value={connectionForm.password || ''}
                                            onChange={e => setConnectionForm({ ...connectionForm, password: e.target.value })}
                                            className="form-input"
                                            placeholder={isEditingConnection ? "Enter new password" : ""}
                                            required={!isEditingConnection} // Required on create, ostensibly required on update too to save
                                        />
                                        {isEditingConnection && <span className="text-tiny text-gray-500">Must re-enter password to update</span>}
                                    </div>
                                </div>
                                <div className="form-actions">
                                    <button
                                        type="button"
                                        onClick={() => setShowAddConnection(false)}
                                        className="cancel-btn"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="save-btn"
                                    >
                                        Save Connection
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="resources-table-container">
                        <table className="resources-table">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Connection</th>
                                    <th>Database</th>
                                    <th>User</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {connections.map((conn, idx) => (
                                    <tr key={idx}>
                                        <td><span className={`badge ${conn.database_type === 'MONGODB' ? 'mongo' : 'sql'}`}>{conn.database_type}</span></td>
                                        <td>{conn.host}:{conn.port}</td>
                                        <td>{conn.database_name}</td>
                                        <td>{conn.username}</td>
                                        <td>
                                            {isAdmin && (
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => handleEditConnection(conn)}
                                                        className="delete-btn text-blue-400 hover:text-blue-300"
                                                        title="Edit Connection"
                                                    >
                                                        <FaEdit />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteConnection(conn)}
                                                        className="delete-btn"
                                                        title="Delete Connection"
                                                    >
                                                        <FaTrash />
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                                {connections.length === 0 && (
                                    <tr><td colSpan={5} className="empty-message">No database connections found.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Env Vars Tab */}
            {activeTab === 'env-vars' && (
                <div>
                    <div className="section-actions">
                        {!showAddEnvVar && (
                            <button
                                className="add-btn"
                                onClick={() => setShowAddEnvVar(true)}
                            >
                                <FaPlus /> Add Variable
                            </button>
                        )}
                    </div>

                    {showAddEnvVar && (
                        <div className="add-form-card">
                            <form onSubmit={handleAddEnvVar}>
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label>Key</label>
                                        <input
                                            type="text"
                                            value={newEnvVar.key}
                                            onChange={e => setNewEnvVar({ ...newEnvVar, key: e.target.value })}
                                            className="form-input"
                                            placeholder="e.g. adminServiceBaseUrl"
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Value</label>
                                        <input
                                            type="text"
                                            value={newEnvVar.value}
                                            onChange={e => setNewEnvVar({ ...newEnvVar, value: e.target.value })}
                                            className="form-input"
                                            placeholder="https://api.example.com"
                                            required
                                        />
                                    </div>
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Description (Optional)</label>
                                        <input
                                            type="text"
                                            value={newEnvVar.description}
                                            onChange={e => setNewEnvVar({ ...newEnvVar, description: e.target.value })}
                                            className="form-input"
                                            placeholder="What is this variable for?"
                                        />
                                    </div>
                                </div>
                                <div className="form-actions">
                                    <button
                                        type="button"
                                        onClick={() => setShowAddEnvVar(false)}
                                        className="cancel-btn"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="save-btn"
                                    >
                                        Save Variable
                                    </button>
                                </div>
                            </form>
                        </div>
                    )}

                    <div className="resources-table-container">
                        <table className="resources-table">
                            <thead>
                                <tr>
                                    <th>Key</th>
                                    <th>Value</th>
                                    <th>Description</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {envVars.map((v, idx) => (
                                    <tr key={idx}>
                                        <td><span className="key-cell">{v.key}</span></td>
                                        <td><span className="value-cell">{v.value}</span></td>
                                        <td className="desc-cell">{v.description || '-'}</td>
                                        <td>
                                            <button
                                                onClick={() => handleDeleteEnvVar(v.key)}
                                                className="delete-btn"
                                                title="Delete Variable"
                                            >
                                                <FaTrash />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {envVars.length === 0 && (
                                    <tr><td colSpan={4} className="empty-message">No environment variables found.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    )
}
