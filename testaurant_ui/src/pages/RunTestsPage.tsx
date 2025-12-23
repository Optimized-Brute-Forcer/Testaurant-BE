import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import apiClient from '../api/client'
import './ListPage.css'

interface RunnableItem {
    id: string
    name: string
    type: string
    description?: string
    created_by_name?: string
}

export default function RunTestsPage() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [items, setItems] = useState<RunnableItem[]>([])
    const [selectedType, setSelectedType] = useState('all')
    const [running, setRunning] = useState<string | null>(null)

    // Filters
    const [searchTerm, setSearchTerm] = useState('')
    const [filterUser, setFilterUser] = useState('')

    useEffect(() => {
        fetchRunnables()
    }, [])

    const fetchRunnables = async () => {
        setLoading(true)
        try {
            const response = await apiClient.get('/testaurant/v1/bff/runnable')
            setItems(response.data.items || [])
        } catch (error) {
            toast.error('Failed to fetch runnable items')
        } finally {
            setLoading(false)
        }
    }

    const handleRun = async (item: RunnableItem) => {
        setRunning(item.id)
        try {
            await apiClient.post(`/testaurant/v1/bff/run/${item.type}/${item.id}`)
            toast.success(`Run started for ${item.name}`)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Execution failed')
        } finally {
            setRunning(null)
        }
    }

    const filteredItems = items.filter(item => {
        const matchesType = selectedType === 'all' || item.type === selectedType
        const matchesSearch = !searchTerm ||
            item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.id?.toLowerCase().includes(searchTerm.toLowerCase())
        const matchesUser = !filterUser || item.created_by_name?.toLowerCase().includes(filterUser.toLowerCase())

        return matchesType && matchesSearch && matchesUser
    })

    const uniqueUsers = Array.from(new Set(
        items.map(i => i.created_by_name).filter(Boolean) as string[]
    )).sort()

    return (
        <div className="list-page">
            <div className="list-header">
                <div className="header-left">
                    <button className="back-btn" onClick={() => navigate('/dashboard')}>
                        ← Back
                    </button>
                    <h1>Run Tests</h1>
                </div>
            </div>

            <div className="filter-cards">
                <div
                    className={`filter-card ${selectedType === 'all' ? 'active' : ''}`}
                    onClick={() => setSelectedType('all')}
                >
                    <span className="card-icon">📁</span>
                    <span className="card-label">All</span>
                </div>
                <div
                    className={`filter-card ${selectedType === 'workitem' ? 'active' : ''}`}
                    onClick={() => setSelectedType('workitem')}
                >
                    <span className="card-icon">📝</span>
                    <span className="card-label">Workitems</span>
                </div>
                <div
                    className={`filter-card ${selectedType === 'testcase' ? 'active' : ''}`}
                    onClick={() => setSelectedType('testcase')}
                >
                    <span className="card-icon">✅</span>
                    <span className="card-label">Testcases</span>
                </div>
                <div
                    className={`filter-card ${selectedType === 'testsuite' ? 'active' : ''}`}
                    onClick={() => setSelectedType('testsuite')}
                >
                    <span className="card-icon">📦</span>
                    <span className="card-label">Testsuites</span>
                </div>
            </div>

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
                            list="user-suggestions-run"
                            placeholder="Filter by user..."
                            value={filterUser}
                            onChange={(e) => setFilterUser(e.target.value)}
                        />
                        <datalist id="user-suggestions-run">
                            {uniqueUsers.map(user => (
                                <option key={user} value={user} />
                            ))}
                        </datalist>
                    </div>
                </div>
            </div>

            <div className="list-content">
                {loading ? (
                    <div className="loading-state">Loading items...</div>
                ) : filteredItems.length === 0 ? (
                    <div className="empty-state">No items found matching your filters.</div>
                ) : (
                    <div className="table-container">
                        <table className="entity-table">
                            <thead>
                                <tr>
                                    <th>Name / ID</th>
                                    <th>Type</th>
                                    <th>Created By</th>
                                    <th>Description</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredItems.map(item => (
                                    <tr key={item.id}>
                                        <td>
                                            <div className="name-cell">
                                                <span className="font-medium">{item.name}</span>
                                                <span className="text-tiny">{item.id}</span>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`badge ${item.type}`}>{item.type}</span>
                                        </td>
                                        <td>{item.created_by_name || 'System'}</td>
                                        <td className="text-small text-muted">{item.description || '-'}</td>
                                        <td>
                                            <button
                                                className={`btn-primary btn-sm ${running === item.id ? 'loading' : ''}`}
                                                onClick={() => handleRun(item)}
                                                disabled={!!running}
                                            >
                                                {running === item.id ? '⌛ Running...' : '▶️ Run Now'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
