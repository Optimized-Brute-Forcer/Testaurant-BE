import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import './ListPage.css'

interface Entity {
    id: string
    entity_id?: string
    name: string
    type?: string
    description?: string
    created_at: string
    created_by?: string
    created_by_name?: string
    last_ran_at?: string
    last_ran_by?: string
    last_ran_by_name?: string
    last_run_status?: string
}

export default function ListPage() {
    const navigate = useNavigate()
    const location = useLocation()
    const { isAdmin, user } = useAuth()
    const [loading, setLoading] = useState(true)
    const [items, setItems] = useState<Entity[]>([])
    const [searchTerm, setSearchTerm] = useState('')
    const [filterUser, setFilterUser] = useState('')
    const [activeCategory, setActiveCategory] = useState('all')
    const [running, setRunning] = useState<string | null>(null)
    const [expandedRow, setExpandedRow] = useState<string | null>(null)
    const [rowDetails, setRowDetails] = useState<any>(null)
    const [loadingDetails, setLoadingDetails] = useState(false)

    // Determine entity type from path
    const entityType = location.pathname.includes('workitems')
        ? 'workitems'
        : location.pathname.includes('testcases')
            ? 'testcases'
            : location.pathname.includes('testsuites')
                ? 'testsuites'
                : location.pathname.includes('members')
                    ? 'members'
                    : location.pathname.includes('join-requests')
                        ? 'join-requests'
                        : 'executions'

    const title = entityType === 'executions'
        ? 'Run History'
        : entityType === 'members'
            ? 'Organization Members'
            : entityType.charAt(0).toUpperCase() + entityType.slice(1)

    useEffect(() => {
        setExpandedRow(null)
        setRowDetails(null)
        fetchItems()
    }, [entityType])

    const fetchItems = async () => {
        setLoading(true)
        try {
            let url = `/testaurant/v1/bff/${entityType}`
            const currentOrgId = localStorage.getItem('current_organization')

            if (entityType === 'members' && currentOrgId) {
                url = `/testaurant/v1/organization/${currentOrgId}/members`
            } else if (entityType === 'join-requests' && currentOrgId) {
                url = `/testaurant/v1/organization/${currentOrgId}/join-requests?status=PENDING`
            }

            const response = await apiClient.get(url)
            const rawData = Array.isArray(response.data) ? response.data : (response.data.runs || response.data.items || [])

            const mapped = rawData.map((item: any, index: number) => {
                const id = item.id || item.workitem_id || item.testcase_id || item.testsuite_id || item.run_workitem_id || item.run_testcase_id || item.user_id || item.request_id || item._id || `unknown-${index}`
                return {
                    id: id,
                    entity_id: item.entity_id || id,
                    name: item.name || item.workitem_title || item.testcase_title || item.testsuite_title || item.email || `Run ${id}`,
                    type: item.type || (entityType === 'members' ? 'member' : (entityType !== 'executions' ? entityType.slice(0, -1) : 'unknown')),
                    description: item.description || item.testcase_subtitle || item.testsuite_subtitle,
                    email: item.email,
                    requested_role: item.requested_role,
                    role: item.role,
                    created_at: item.created_at || item.workitem_created_date || item.testcase_created_date || item.testsuite_created_date || item.run_workitem_created_date || item.run_testcase_created_date,
                    created_by: item.created_by || item.executor_context,
                    created_by_name: item.created_by_name || item.executor_name,
                    last_ran_at: item.last_ran_at || item.run_workitem_start_time || item.run_testcase_start_time,
                    last_ran_by: item.last_ran_by || item.executor_context,
                    last_ran_by_name: item.last_ran_by_name || item.executor_name,
                    last_run_status: item.last_run_status || item.execution_status || item.overall_status || item.status,
                    request_id: item.request_id // Preserve request_id for join requests
                }
            })
            setItems(mapped)
        } catch (error) {
            toast.error(`Failed to fetch ${entityType}`)
        } finally {
            setLoading(false)
        }
    }

    const toggleRow = async (id: string, type: string) => {
        if (expandedRow === id) {
            setExpandedRow(null)
            setRowDetails(null)
            return
        }

        setExpandedRow(id)
        if (entityType !== 'executions') return

        setLoadingDetails(true)
        try {
            const endpoint = `/testaurant/v1/bff/executions/${type}/${id}`
            const response = await apiClient.get(endpoint)
            setRowDetails(response.data)
        } catch (error) {
            toast.error('Failed to load details')
        } finally {
            setLoadingDetails(false)
        }
    }

    const handleDelete = async (id: string) => {
        const actionLabel = entityType === 'members' ? 'remove' : 'delete'
        if (!window.confirm(`Are you sure you want to ${actionLabel} this ${entityType.slice(0, -1)}?`)) return

        try {
            let url = `/testaurant/v1/bff/${entityType}/${id}`
            const currentOrgId = localStorage.getItem('current_organization')

            if (entityType === 'members' && currentOrgId) {
                url = `/testaurant/v1/organization/${currentOrgId}/members/${id}`
            }

            await apiClient.delete(url)
            toast.success(`${entityType.slice(0, -1)} ${actionLabel}ed successfully`)
            fetchItems()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || `Failed to ${actionLabel}`)
        }
    }

    const handleRun = async (id: string) => {
        setRunning(id)
        try {
            const singleType = entityType.slice(0, -1)
            const response = await apiClient.post(`/testaurant/v1/bff/run/${singleType}/${id}`)
            toast.success(`Run completed: ${response.data.execution_status || response.data.overall_status}`)
            fetchItems()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Execution failed')
        } finally {
            setRunning(null)
        }
    }

    const handleRoleUpdate = async (userId: string, newRole: string) => {
        try {
            const currentOrgId = localStorage.getItem('current_organization')
            if (!currentOrgId) return

            await apiClient.put(`/testaurant/v1/organization/${currentOrgId}/members/${userId}/role?role=${newRole}`)
            toast.success('Role updated successfully')
            fetchItems()
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to update role')
        }
    }

    const handleRequest = async (requestId: string, approve: boolean) => {
        try {
            const currentOrgId = localStorage.getItem('current_organization')
            if (!currentOrgId) return

            await apiClient.post(`/testaurant/v1/organization/${currentOrgId}/join-requests/${requestId}/handle?approve=${approve}`)
            toast.success(approve ? 'Request approved' : 'Request rejected')
            fetchItems()
        } catch (error: any) {
            toast.error('Failed to update request')
        }
    }

    const filteredItems = items.filter(item => {
        const matchesCategory = activeCategory === 'all' || item.type?.toLowerCase() === activeCategory.toLowerCase()
        const matchesSearch = !searchTerm ||
            item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (item.description && item.description.toLowerCase().includes(searchTerm.toLowerCase()))

        const matchesUser = !filterUser ||
            item.created_by_name?.toLowerCase().includes(filterUser.toLowerCase()) ||
            item.created_by?.toLowerCase().includes(filterUser.toLowerCase())

        return matchesCategory && matchesSearch && matchesUser
    })

    const getStatusBadge = (status?: string) => {
        if (!status) return <span className="text-muted">-</span>

        // Handle join request statuses
        if (status === 'APPROVED' || status === 'PENDING') {
            return <span className={`status-badge passed`}>{status}</span>
        }
        if (status === 'REJECTED') {
            return <span className={`status-badge failed`}>{status}</span>
        }

        // Handle test execution statuses
        const cls = status.toLowerCase() === 'passed' ? 'passed' : 'failed'
        return <span className={`status-badge ${cls}`}>{status}</span>
    }

    const uniqueUsers = Array.from(new Set(
        items.flatMap(i => [i.created_by_name, i.last_ran_by_name])
            .filter(Boolean) as string[]
    )).sort()

    const renderNestedDetails = () => {
        if (loadingDetails) return <div className="nested-loading">Loading nested data...</div>
        if (!rowDetails) return <div className="nested-empty">No extra info available.</div>

        if (rowDetails.testcase_results) {
            return (
                <div className="nested-list">
                    <h4 className="nested-title">Nested Testcases</h4>
                    <table className="nested-table">
                        <thead>
                            <tr>
                                <th>Testcase Title</th>
                                <th>Status</th>
                                <th>Start Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rowDetails.testcase_results.map((tc: any, idx: number) => (
                                <tr key={idx}>
                                    <td>{tc.testcase_title}</td>
                                    <td>{getStatusBadge(tc.overall_status)}</td>
                                    <td>{new Date(tc.run_testcase_start_time).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )
        }

        if (rowDetails.workitem_results) {
            return (
                <div className="nested-list">
                    <h4 className="nested-title">Nested Workitems</h4>
                    <table className="nested-table">
                        <thead>
                            <tr>
                                <th>Workitem Title</th>
                                <th>Status</th>
                                <th>Logs</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rowDetails.workitem_results.map((wi: any, idx: number) => (
                                <tr key={idx}>
                                    <td>{wi.workitem_title}</td>
                                    <td>{getStatusBadge(wi.execution_status)}</td>
                                    <td>
                                        <details>
                                            <summary className="text-tiny cursor-pointer">View Logs ({wi.execution_logs?.length || 0})</summary>
                                            <pre className="log-viewer">
                                                {wi.execution_logs?.map((l: any) => `[${l.log_type}] ${l.message}`).join('\n')}
                                            </pre>
                                        </details>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )
        }

        return (
            <div className="workitem-full-detail">
                <div className="detail-grid">
                    <div className="detail-card">
                        <h5>Configuration</h5>
                        <pre className="json-viewer">{JSON.stringify(rowDetails.workitem_config || {}, null, 2)}</pre>
                    </div>
                    <div className="detail-card">
                        <h5>Actual Response</h5>
                        <pre className="json-viewer">{JSON.stringify(rowDetails.actual_response || {}, null, 2)}</pre>
                    </div>
                </div>
                <div className="detail-card full-width">
                    <h5>Execution Logs</h5>
                    <div className="log-viewer">
                        {rowDetails.execution_logs?.map((log: any, idx: number) => (
                            <div key={idx} className={`log-entry ${log.log_type.toLowerCase()}`}>
                                <span className="log-type">[{log.log_type}]</span>
                                <span className="log-msg">{log.message}</span>
                                {log.payload && (
                                    <pre className="log-payload">{JSON.stringify(log.payload, null, 2)}</pre>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="list-page">
            <div className="list-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => navigate('/dashboard')}>
                        ← Back
                    </button>
                    <h1>{entityType === 'join-requests' ? 'Pending Join Requests' : title}</h1>
                </div>

                <div className="header-right">
                    {entityType !== 'executions' && entityType !== 'members' && entityType !== 'join-requests' && isAdmin && (
                        <button
                            className="btn-primary"
                            onClick={() => navigate(`/create/${entityType.slice(0, -1)}`)}
                        >
                            + Create {entityType.slice(0, -1)}
                        </button>
                    )}
                </div>
            </div>

            {entityType === 'executions' && (
                <div className="filter-cards">
                    <div
                        className={`filter-card ${activeCategory === 'all' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('all')}
                    >
                        <span className="card-icon">📁</span>
                        <span className="card-label">All</span>
                    </div>
                    <div
                        className={`filter-card ${activeCategory === 'workitem' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('workitem')}
                    >
                        <span className="card-icon">📝</span>
                        <span className="card-label">Workitems</span>
                    </div>
                    <div
                        className={`filter-card ${activeCategory === 'testcase' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('testcase')}
                    >
                        <span className="card-icon">✅</span>
                        <span className="card-label">Testcases</span>
                    </div>
                    <div
                        className={`filter-card ${activeCategory === 'testsuite' ? 'active' : ''}`}
                        onClick={() => setActiveCategory('testsuite')}
                    >
                        <span className="card-icon">📦</span>
                        <span className="card-label">Testsuites</span>
                    </div>
                </div>
            )}

            <div className="advanced-filters">
                <div className="filter-grid">
                    <div className="search-container full-width">
                        <span className="search-icon">🔍</span>
                        <input
                            type="text"
                            placeholder="Search by name, ID or description..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="search-container full-width">
                        <span className="search-icon">👤</span>
                        <input
                            type="text"
                            list="user-suggestions"
                            placeholder="Filter by user..."
                            value={filterUser}
                            onChange={(e) => setFilterUser(e.target.value)}
                        />
                        <datalist id="user-suggestions">
                            {uniqueUsers.map(user => (
                                <option key={user} value={user} />
                            ))}
                        </datalist>
                    </div>
                </div>
            </div>

            <div className="list-content">
                {loading ? (
                    <div className="loading-state">Loading {entityType}...</div>
                ) : filteredItems.length === 0 ? (
                    <div className="empty-state">
                        <p>{searchTerm || filterUser || activeCategory !== 'all' ? 'No results match your filters.' : `No ${entityType} found.`}</p>
                        {!searchTerm && !filterUser && activeCategory === 'all' && entityType !== 'executions' && (
                            <button
                                className="btn-secondary"
                                onClick={() => navigate(`/create/${entityType.slice(0, -1)}`)}
                            >
                                Create your first one
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="entity-table">
                            <thead>
                                <tr>
                                    <th style={{ width: '40px' }}></th>
                                    <th>Name / ID</th>
                                    {entityType === 'members' && <th>Role</th>}
                                    {entityType === 'workitems' && <th>Type</th>}
                                    {entityType === 'join-requests' && <th>Email</th>}
                                    {entityType === 'join-requests' && <th>Requested Role</th>}
                                    <th>{entityType === 'join-requests' ? 'Requested At' : 'Created By'}</th>
                                    {entityType !== 'join-requests' && <th>Last Ran</th>}
                                    {entityType !== 'join-requests' && <th>Last Result</th>}
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredItems.map(item => (
                                    <React.Fragment key={item.id}>
                                        <tr
                                            className={`entity-row ${expandedRow === item.id ? 'expanded-header' : ''}`}
                                            onClick={() => toggleRow(item.id, item.type || 'unknown')}
                                        >
                                            <td>
                                                {entityType === 'executions' && (
                                                    <span className={`expand-caret ${expandedRow === item.id ? 'open' : ''}`}>▶</span>
                                                )}
                                            </td>
                                            <td>
                                                <div className="name-cell">
                                                    <span className="font-medium">{item.name}</span>
                                                    <span className="text-tiny">{item.entity_id}</span>
                                                </div>
                                            </td>
                                            {entityType === 'members' && (
                                                <td>
                                                    <select
                                                        value={(item as any).role}
                                                        onChange={(e) => handleRoleUpdate(item.id, e.target.value)}
                                                        disabled={!isAdmin || item.id === user?.user_id} // Prevent self-demotion or non-admin changes
                                                        className="role-select-compact"
                                                        onClick={e => e.stopPropagation()}
                                                        style={{
                                                            padding: '4px 8px',
                                                            borderRadius: '4px',
                                                            background: 'rgba(255, 255, 255, 0.05)',
                                                            color: '#e2e8f0',
                                                            border: '1px solid rgba(255, 255, 255, 0.1)',
                                                            fontSize: '12px'
                                                        }}
                                                    >
                                                        <option value="ORG_ADMIN">Admin</option>
                                                        <option value="ORG_MEMBER">Member</option>
                                                    </select>
                                                </td>
                                            )}
                                            {entityType === 'workitems' && (
                                                <td><span className={`badge ${item.type?.toLowerCase()}`}>{item.type}</span></td>
                                            )}
                                            {entityType === 'join-requests' && (
                                                <>
                                                    <td><span className="text-small">{(item as any).email || 'N/A'}</span></td>
                                                    <td><span className="text-small">{(item as any).requested_role || 'ORG_MEMBER'}</span></td>
                                                </>
                                            )}
                                            <td>
                                                <div className="user-cell">
                                                    <span className="text-small">{item.created_by_name || item.created_by || 'Unknown'}</span>
                                                    <span className="text-tiny">{item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}</span>
                                                </div>
                                            </td>
                                            <td>
                                                {item.last_ran_at ? (
                                                    <div className="user-cell">
                                                        <span className="text-small">{new Date(item.last_ran_at).toLocaleString()}</span>
                                                        <span className="text-tiny">by {item.last_ran_by_name || item.last_ran_by || 'System'}</span>
                                                    </div>
                                                ) : entityType === 'join-requests' ? <span className="text-muted">-</span> : <span className="text-muted">-</span>}
                                            </td>
                                            {entityType !== 'join-requests' && <td>{getStatusBadge(item.last_run_status)}</td>}
                                            <td>
                                                <div className="action-row" onClick={(e) => e.stopPropagation()}>
                                                    {entityType === 'join-requests' && (
                                                        <>
                                                            {getStatusBadge(item.last_run_status)}
                                                            <button
                                                                className="btn-icon approve"
                                                                onClick={() => handleRequest((item as any).request_id || item.id, true)}
                                                                title="Approve"
                                                            >
                                                                ✅
                                                            </button>
                                                            <button
                                                                className="btn-icon reject"
                                                                onClick={() => handleRequest((item as any).request_id || item.id, false)}
                                                                title="Reject"
                                                            >
                                                                ❌
                                                            </button>
                                                            {isAdmin && (
                                                                <button
                                                                    className="btn-icon delete"
                                                                    onClick={() => handleDelete(item.id)}
                                                                    title="Delete"
                                                                >
                                                                    🗑️
                                                                </button>
                                                            )}
                                                        </>
                                                    )}
                                                    {entityType !== 'executions' && entityType !== 'members' && entityType !== 'join-requests' && (
                                                        <button
                                                            className={`btn-icon run ${running === item.id ? 'loading' : ''}`}
                                                            onClick={() => handleRun(item.id)}
                                                            disabled={!!running}
                                                            title="Run Now"
                                                        >
                                                            {running === item.id ? '⌛' : '▶️'}
                                                        </button>
                                                    )}
                                                    {entityType !== 'join-requests' && isAdmin && (
                                                        <button
                                                            className="btn-icon delete"
                                                            onClick={() => handleDelete(item.id)}
                                                            title="Delete"
                                                        >
                                                            🗑️
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                        {expandedRow === item.id && entityType === 'executions' && (
                                            <tr className="expanded-row">
                                                <td colSpan={7}>
                                                    <div className="expansion-content">
                                                        {renderNestedDetails()}
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div >
    )
}
