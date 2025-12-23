// ... (imports)
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import { useAuth } from '../contexts/AuthContext' // Import useAuth
import './CreatePage.css'

interface DatabaseCredential {
    database_type: string
    host: string
    port: number
    username: string
    database_name: string
}

interface EnvironmentVariable {
    key: string
    value: string
    description?: string
}

export default function CreatePage() {
    const { type } = useParams<{ type: string }>()
    const navigate = useNavigate()
    const { currentOrganization } = useAuth() // Get currentOrg
    const [loading, setLoading] = useState(false)

    // Resources State
    const [connections, setConnections] = useState<DatabaseCredential[]>([])
    const [envVars, setEnvVars] = useState<EnvironmentVariable[]>([])

    // ... (existing state)
    // Workitem State
    const [workitemData, setWorkitemData] = useState({
        name: '',
        description: '',
        workitem_type: 'REST',
        rest_config: {
            method: 'GET',
            path: '',
            headers: {},
            query_params: {},
            body: ''
        },
        sql_config: {
            query: '',
            query_type: 'SELECT',
            database_name: 'default'
        },
        mongo_config: {
            collection: '',
            operation: 'FIND',
            query: '{}',
            document: '{}',
            database_name: 'default'
        }
    })

    // ... (testcase/suite state)
    const [testcaseData, setTestcaseData] = useState({
        name: '',
        description: '',
        workitem_ids: [] as string[]
    })
    const [testsuiteData, setTestsuiteData] = useState({
        name: '',
        description: '',
        testcase_ids: [] as string[]
    })

    const [availableWorkitems, setAvailableWorkitems] = useState<any[]>([])
    const [availableTestcases, setAvailableTestcases] = useState<any[]>([])

    useEffect(() => {
        if (type === 'testcase') {
            fetchWorkitems()
        } else if (type === 'testsuite') {
            fetchTestcases()
        } else if (type === 'workitem' && currentOrganization) {
            fetchResources()
        }
    }, [type, currentOrganization])

    const fetchResources = async () => {
        try {
            const [connRes, envRes] = await Promise.all([
                apiClient.get(`/testaurant/v1/organization/${currentOrganization}/credentials`),
                apiClient.get(`/testaurant/v1/organization/${currentOrganization}/env-vars`)
            ])
            setConnections(connRes.data)
            setEnvVars(envRes.data)
        } catch (error) {
            console.error("Failed to fetch resources", error)
        }
    }

    // ... (fetchWorkitems, fetchTestcases, handleCreate existing logic)
    const fetchWorkitems = async () => {
        try {
            const response = await apiClient.get('/testaurant/v1/bff/workitems')
            setAvailableWorkitems(response.data)
        } catch (error) {
            toast.error('Failed to fetch workitems')
        }
    }

    const fetchTestcases = async () => {
        try {
            const response = await apiClient.get('/testaurant/v1/bff/testcases')
            setAvailableTestcases(response.data)
        } catch (error) {
            toast.error('Failed to fetch testcases')
        }
    }

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            let endpoint = ''
            let data = {}

            if (type === 'workitem') {
                endpoint = '/testaurant/v1/bff/workitems'
                data = {
                    name: workitemData.name,
                    description: workitemData.description,
                    workitem_type: workitemData.workitem_type,
                    rest_config: workitemData.workitem_type === 'REST' ? workitemData.rest_config : null,
                    sql_config: workitemData.workitem_type === 'SQL' ? workitemData.sql_config : null,
                    mongo_config: workitemData.workitem_type === 'MONGO' ? workitemData.mongo_config : null
                }
            } else if (type === 'testcase') {
                endpoint = '/testaurant/v1/bff/testcases'
                data = testcaseData
            } else if (type === 'testsuite') {
                endpoint = '/testaurant/v1/bff/testsuites'
                data = testsuiteData
            }

            await apiClient.post(endpoint, data)
            toast.success(`${type} created successfully!`)
            navigate('/dashboard')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || `Failed to create ${type}`)
        } finally {
            setLoading(false)
        }
    }

    const insertEnvVar = (field: string, value: string) => {
        // Helper to insert env var into text inputs
        // For simplicity, just appending or replacing could be done, 
        // but appending at cursor position is better. 
        // Since we don't have refs for every input easily managed here without complex logic,
        // we'll just append to end for now or user can copy paste from the dropdown.
        // Actually, let's just copy to clipboard or append.
        // Let's UPDATE state directly.
        if (field === 'path') {
            setWorkitemData(prev => ({
                ...prev,
                rest_config: { ...prev.rest_config, path: prev.rest_config.path + `{{${value}}}` }
            }))
        } else if (field === 'body') {
            setWorkitemData(prev => ({
                ...prev,
                rest_config: { ...prev.rest_config, body: prev.rest_config.body + `{{${value}}}` }
            }))
        }
    }

    const renderEnvVarSelector = (field: 'path' | 'body') => (
        <select
            className="env-var-select ml-2 bg-gray-700 text-xs rounded border border-gray-600 text-gray-300"
            onChange={(e) => {
                if (e.target.value) {
                    insertEnvVar(field, e.target.value)
                    e.target.value = '' // Reset
                }
            }}
        >
            <option value="">Insert Var...</option>
            {envVars.map(v => (
                <option key={v.key} value={v.key}>{v.key}</option>
            ))}
        </select>
    )

    const renderWorkitemForm = () => (
        <div className="form-section">
            <div className="form-group">
                <label>Workitem Name</label>
                <input
                    type="text"
                    value={workitemData.name}
                    onChange={(e) => setWorkitemData({ ...workitemData, name: e.target.value })}
                    placeholder="e.g. Get User Profile"
                    required
                />
            </div>
            <div className="form-group">
                <label>Description</label>
                <textarea
                    value={workitemData.description}
                    onChange={(e) => setWorkitemData({ ...workitemData, description: e.target.value })}
                    placeholder="What does this workitem do?"
                />
            </div>
            <div className="form-group">
                <label>Type</label>
                <select
                    value={workitemData.workitem_type}
                    onChange={(e) => setWorkitemData({ ...workitemData, workitem_type: e.target.value })}
                >
                    <option value="REST">REST API</option>
                    <option value="SQL">SQL Query</option>
                    <option value="MONGO">MongoDB Operation</option>
                </select>
            </div>

            {workitemData.workitem_type === 'REST' && (
                <div className="config-section">
                    <h4>REST Configuration</h4>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Method</label>
                            <select
                                value={workitemData.rest_config.method}
                                onChange={(e) => setWorkitemData({
                                    ...workitemData,
                                    rest_config: { ...workitemData.rest_config, method: e.target.value }
                                })}
                            >
                                <option value="GET">GET</option>
                                <option value="POST">POST</option>
                                <option value="PUT">PUT</option>
                                <option value="DELETE">DELETE</option>
                                <option value="PATCH">PATCH</option>
                            </select>
                        </div>
                        <div className="form-group flex-grow">
                            <label>
                                Path
                                {renderEnvVarSelector('path')}
                            </label>
                            <input
                                type="text"
                                value={workitemData.rest_config.path}
                                onChange={(e) => setWorkitemData({
                                    ...workitemData,
                                    rest_config: { ...workitemData.rest_config, path: e.target.value }
                                })}
                                placeholder="/v1/users/{userId} or {{BASE_URL}}/users"
                                required
                            />
                        </div>
                    </div>
                    {/* Headers could also use env vars but skipping for brevity as path/body are most common */}
                    {(['POST', 'PUT', 'PATCH'].includes(workitemData.rest_config.method)) && (
                        <div className="form-group">
                            <label>
                                Request Body (JSON)
                                {renderEnvVarSelector('body')}
                            </label>
                            <textarea
                                className="code-editor"
                                value={workitemData.rest_config.body}
                                onChange={(e) => setWorkitemData({
                                    ...workitemData,
                                    rest_config: { ...workitemData.rest_config, body: e.target.value }
                                })}
                                placeholder='{ "name": "John" }'
                            />
                        </div>
                    )}
                </div>
            )}

            {workitemData.workitem_type === 'SQL' && (
                <div className="config-section">
                    <h4>SQL Configuration</h4>
                    <div className="form-group">
                        <label>Database Connection</label>
                        <select
                            value={workitemData.sql_config.database_name}
                            onChange={(e) => setWorkitemData({
                                ...workitemData,
                                sql_config: { ...workitemData.sql_config, database_name: e.target.value }
                            })}
                        >
                            <option value="default">Default</option>
                            {connections.filter(c => ['MYSQL', 'POSTGRESQL'].includes(c.database_type)).map(c => (
                                <option key={`${c.host}:${c.database_name}`} value={c.database_name}>
                                    {c.database_name} ({c.host})
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Query Type</label>
                        <select
                            value={workitemData.sql_config.query_type}
                            onChange={(e) => setWorkitemData({
                                ...workitemData,
                                sql_config: { ...workitemData.sql_config, query_type: e.target.value }
                            })}
                        >
                            <option value="SELECT">SELECT</option>
                            <option value="INSERT">INSERT</option>
                            <option value="UPDATE">UPDATE</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>SQL Query</label>
                        <textarea
                            className="code-editor"
                            value={workitemData.sql_config.query}
                            onChange={(e) => setWorkitemData({
                                ...workitemData,
                                sql_config: { ...workitemData.sql_config, query: e.target.value }
                            })}
                            placeholder="SELECT * FROM users WHERE id = {userId}"
                            required
                        />
                    </div>
                </div>
            )}

            {workitemData.workitem_type === 'MONGO' && (
                <div className="config-section">
                    <h4>MongoDB Configuration</h4>
                    <div className="form-group">
                        <label>Database Connection</label>
                        <select
                            value={workitemData.mongo_config.database_name}
                            onChange={(e) => setWorkitemData({
                                ...workitemData,
                                mongo_config: { ...workitemData.mongo_config, database_name: e.target.value }
                            })}
                        >
                            <option value="default">Default</option>
                            {connections.filter(c => c.database_type === 'MONGODB').map(c => (
                                <option key={`${c.host}:${c.database_name}`} value={c.database_name}>
                                    {c.database_name} ({c.host})
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Collection</label>
                            <input
                                type="text"
                                value={workitemData.mongo_config.collection}
                                onChange={(e) => setWorkitemData({
                                    ...workitemData,
                                    mongo_config: { ...workitemData.mongo_config, collection: e.target.value }
                                })}
                                placeholder="users"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Operation</label>
                            <select
                                value={workitemData.mongo_config.operation}
                                onChange={(e) => setWorkitemData({
                                    ...workitemData,
                                    mongo_config: { ...workitemData.mongo_config, operation: e.target.value }
                                })}
                            >
                                <option value="FIND">FIND</option>
                                <option value="INSERT">INSERT</option>
                                <option value="UPDATE">UPDATE</option>
                                <option value="DELETE">DELETE</option>
                                <option value="AGGREGATE">AGGREGATE</option>
                            </select>
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Query / Filter (JSON)</label>
                        <textarea
                            className="code-editor"
                            value={workitemData.mongo_config.query}
                            onChange={(e) => setWorkitemData({
                                ...workitemData,
                                mongo_config: { ...workitemData.mongo_config, query: e.target.value }
                            })}
                            placeholder='{ "_id": "{userId}" }'
                        />
                    </div>
                </div>
            )}
        </div>
    )

    // ... (renderTestcaseForm, renderTestsuiteForm, return)
    const renderTestcaseForm = () => (
        // ... (unchanged)
        <div className="form-section">
            <div className="form-group">
                <label>Testcase Name</label>
                <input
                    type="text"
                    value={testcaseData.name}
                    onChange={(e) => setTestcaseData({ ...testcaseData, name: e.target.value })}
                    placeholder="e.g. User Signup Flow"
                    required
                />
            </div>
            <div className="form-group">
                <label>Description</label>
                <textarea
                    value={testcaseData.description}
                    onChange={(e) => setTestcaseData({ ...testcaseData, description: e.target.value })}
                    placeholder="What flow does this testcase cover?"
                />
            </div>
            <div className="form-group">
                <label>Components (Workitems)</label>
                <div className="item-selection-grid">
                    {availableWorkitems.map(item => (
                        <label key={item.workitem_id} className="item-checkbox">
                            <input
                                type="checkbox"
                                checked={testcaseData.workitem_ids.includes(item.workitem_id)}
                                onChange={(e) => {
                                    const ids = e.target.checked
                                        ? [...testcaseData.workitem_ids, item.workitem_id]
                                        : testcaseData.workitem_ids.filter(id => id !== item.workitem_id)
                                    setTestcaseData({ ...testcaseData, workitem_ids: ids })
                                }}
                            />
                            <div className="item-info">
                                <span className="item-name">{item.name}</span>
                                <span className="item-badge">{item.workitem_type}</span>
                            </div>
                        </label>
                    ))}
                    {availableWorkitems.length === 0 && (
                        <p className="no-items">No workitems found. Create some first!</p>
                    )}
                </div>
            </div>
        </div>
    )

    const renderTestsuiteForm = () => (
        // ... (unchanged)
        <div className="form-section">
            <div className="form-group">
                <label>Testsuite Name</label>
                <input
                    type="text"
                    value={testsuiteData.name}
                    onChange={(e) => setTestsuiteData({ ...testsuiteData, name: e.target.value })}
                    placeholder="e.g. Regression Suite"
                    required
                />
            </div>
            <div className="form-group">
                <label>Description</label>
                <textarea
                    value={testsuiteData.description}
                    onChange={(e) => setTestsuiteData({ ...testsuiteData, description: e.target.value })}
                    placeholder="When should this suite be run?"
                />
            </div>
            <div className="form-group">
                <label>Testcases</label>
                <div className="item-selection-grid">
                    {availableTestcases.map(tc => (
                        <label key={tc.testcase_id} className="item-checkbox">
                            <input
                                type="checkbox"
                                checked={testsuiteData.testcase_ids.includes(tc.testcase_id)}
                                onChange={(e) => {
                                    const ids = e.target.checked
                                        ? [...testsuiteData.testcase_ids, tc.testcase_id]
                                        : testsuiteData.testcase_ids.filter(id => id !== tc.testcase_id)
                                    setTestsuiteData({ ...testsuiteData, testcase_ids: ids })
                                }}
                            />
                            <div className="item-info">
                                <span className="item-name">{tc.name}</span>
                            </div>
                        </label>
                    ))}
                    {availableTestcases.length === 0 && (
                        <p className="no-items">No testcases found. Create some first!</p>
                    )}
                </div>
            </div>
        </div>
    )

    return (
        <div className="create-page">
            <div className="create-header">
                <button className="back-btn" onClick={() => navigate('/dashboard')}>
                    ← Back to Dashboard
                </button>
                <h1>Create New {type?.charAt(0).toUpperCase()}{type?.slice(1)}</h1>
            </div>

            <form className="create-form" onSubmit={handleCreate}>
                {type === 'workitem' && renderWorkitemForm()}
                {type === 'testcase' && renderTestcaseForm()}
                {type === 'testsuite' && renderTestsuiteForm()}

                <div className="form-actions">
                    <button
                        type="button"
                        className="btn-secondary"
                        onClick={() => navigate('/dashboard')}
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        className="btn-primary"
                        disabled={loading}
                    >
                        {loading ? 'Creating...' : `Create ${type}`}
                    </button>
                </div>
            </form>
        </div>
    )
}
