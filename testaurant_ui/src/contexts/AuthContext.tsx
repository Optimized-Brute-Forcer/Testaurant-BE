import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import { toast } from 'react-toastify'

interface User {
    user_id: string
    email: string
    name: string
    google_id: string
    organizations: OrganizationMembership[]
}

interface OrganizationMembership {
    organization_id: string
    role: string
}

interface Organization {
    organization_id: string
    organization_name: string
}

interface AuthContextType {
    user: User | null
    organizations: Organization[]
    currentOrganization: string | null
    currentRole: string | null
    isAuthenticated: boolean
    isAdmin: boolean
    login: (idToken: string, organizationId?: string) => Promise<void>
    logout: () => void
    switchOrganization: (organizationId: string) => Promise<void>
    leaveOrganization: (organizationId: string) => Promise<void>
    deleteOrganization: (organizationId: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [organizations, setOrganizations] = useState<Organization[]>([])
    const [currentOrganization, setCurrentOrganization] = useState<string | null>(null)
    const [currentRole, setCurrentRole] = useState<string | null>(null)
    const navigate = useNavigate()

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token')
        const savedUser = localStorage.getItem('user')
        const savedOrgs = localStorage.getItem('organizations')
        const savedOrgId = localStorage.getItem('current_organization')
        const savedRole = localStorage.getItem('current_role')

        if (token && savedUser && savedOrgs) {
            setUser(JSON.parse(savedUser))
            setOrganizations(JSON.parse(savedOrgs))
            setCurrentOrganization(savedOrgId)

            if (savedRole && savedRole !== 'null') {
                setCurrentRole(savedRole)
            } else {
                setCurrentRole(null)
            }
        }
    }, [])

    const login = async (idToken: string, organizationId?: string) => {
        try {
            // Save original google id token for onboarding swaps if needed
            localStorage.setItem('google_id_token', idToken)

            const response = await apiClient.post('/testaurant/v1/auth/login', {
                id_token: idToken,
                organization_id: organizationId,
            })

            const { access_token, user: userData, organizations: orgs, current_role } = response.data

            localStorage.setItem('user', JSON.stringify(userData))
            localStorage.setItem('organizations', JSON.stringify(orgs))

            setUser(userData)
            setOrganizations(orgs)

            if (access_token && orgs.length > 0) {
                localStorage.setItem('access_token', access_token)

                // Set current organization from token or first org
                const orgId = organizationId || orgs[0]?.organization_id

                // Use current_role from backend response
                const role = current_role || null

                localStorage.setItem('current_organization', orgId)
                if (role) {
                    localStorage.setItem('current_role', role)
                } else {
                    localStorage.removeItem('current_role')
                }

                setCurrentOrganization(orgId)
                setCurrentRole(role)

                toast.success('Login successful!')
                navigate('/dashboard')
            } else {
                // No organization or partial token for onboarding
                if (access_token) {
                    localStorage.setItem('access_token', access_token)
                }
                localStorage.removeItem('current_organization')
                localStorage.removeItem('current_role')
                setCurrentOrganization(null)
                setCurrentRole(null)

                toast.info('Please select or create an organization to continue')
                navigate('/onboarding')
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Login failed')
            throw error
        }
    }

    const logout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        localStorage.removeItem('organizations')
        localStorage.removeItem('current_organization')
        localStorage.removeItem('current_role')
        localStorage.removeItem('google_id_token')
        setUser(null)
        setOrganizations([])
        setCurrentOrganization(null)
        setCurrentRole(null)
        navigate('/login')
        toast.info('Logged out successfully')
    }

    const switchOrganization = async (organizationId: string) => {
        const idToken = localStorage.getItem('google_id_token')
        if (idToken) {
            await login(idToken, organizationId)
        } else {
            toast.error('Session expired. Please login again.')
            logout()
        }
    }

    const leaveOrganization = async (organizationId: string) => {
        try {
            await apiClient.delete(`/testaurant/v1/organization/leave/${organizationId}`)
            toast.success('Left organization successfully')

            // Refresh user info
            const idToken = localStorage.getItem('google_id_token')
            if (idToken) {
                // Login again without org ID to trigger refresh and redirect to onboarding if needed
                await login(idToken)
            } else {
                logout()
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to leave organization')
        }
    }

    const deleteOrganization = async (organizationId: string) => {
        try {
            await apiClient.delete(`/testaurant/v1/organization/${organizationId}`)
            toast.success('Organization deleted successfully')

            // Refresh user info to reflect removal
            const idToken = localStorage.getItem('google_id_token')
            if (idToken) {
                await login(idToken)
            } else {
                logout()
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to delete organization')
            throw error
        }
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                organizations,
                currentOrganization,
                currentRole,
                isAuthenticated: !!user,
                isAdmin: currentRole === 'ORG_ADMIN' || currentRole === 'SUPER_ADMIN',
                login,
                logout,
                switchOrganization,
                leaveOrganization,
                deleteOrganization
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
