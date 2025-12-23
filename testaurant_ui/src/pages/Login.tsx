import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'
import './Login.css'

export default function Login() {
    const { login, isAuthenticated } = useAuth()
    const navigate = useNavigate()

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard')
        }
    }, [isAuthenticated, navigate])

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <h1>🧪 Testaurant</h1>
                    <p>Automated Testing Platform</p>
                </div>

                <div className="login-content">
                    <h2>Welcome Back</h2>
                    <p className="login-subtitle">
                        Sign in to access your testing workspace
                    </p>

                    <div className="google-login-wrapper">
                        <GoogleLogin
                            onSuccess={credentialResponse => {
                                if (credentialResponse.credential) {
                                    login(credentialResponse.credential)
                                }
                            }}
                            onError={() => {
                                toast.error('Google login failed')
                            }}
                            // Disabling oneTap temporarily to resolve (blocked:other) error
                            // useOneTap
                            // ux_mode="redirect"
                            theme="filled_black"
                            shape="pill"
                            width="340"
                            containerProps={{
                                style: {
                                    width: '100%',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    backgroundColor: 'transparent'
                                }
                            }}
                        />
                    </div>

                    <div className="login-features">
                        <div className="feature">
                            <span className="feature-icon">🔐</span>
                            <span>Multi-Organization RBAC</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🚀</span>
                            <span>REST, SQL & MongoDB Testing</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">📊</span>
                            <span>Comprehensive Audit Logs</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="login-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
                <div className="gradient-orb orb-3"></div>
            </div>
        </div>
    )
}
