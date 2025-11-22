import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import PillNav from './PillNav'
import LightRays from './LightRays'
import '../styles/Login.css'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [loginAttempts, setLoginAttempts] = useState(0)
  const [activeHref, setActiveHref] = useState('/login')
  const maxAttempts = 3

  const { signIn } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Check if max attempts reached
    if (loginAttempts >= maxAttempts) {
      setError(`Maximum login attempts (${maxAttempts}) reached. Please try again later.`)
      return
    }

    setError('')
    setLoading(true)

    try {
      const { data, error } = await signIn(email, password)

      if (error) {
        // Check if it's a configuration error
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
          setError('⚠️ Supabase not configured. Add your credentials to the .env file and restart the server.')
          setLoading(false)
          return
        }

        setLoginAttempts(prev => prev + 1)
        const remainingAttempts = maxAttempts - (loginAttempts + 1)
        
        if (remainingAttempts > 0) {
          setError(`${error.message}. ${remainingAttempts} attempt(s) remaining.`)
        } else {
          setError(`Maximum login attempts reached. Please try again later.`)
        }
        return
      }

      // Reset attempts on successful login
      setLoginAttempts(0)
      navigate('/dashboard')
    } catch (err) {
      setError('⚠️ Connection error. Check your Supabase credentials in .env file.')
    } finally {
      setLoading(false)
    }
  }

  const isDisabled = loginAttempts >= maxAttempts || loading

  return (
    <div className="login-container">
      {/* Light Rays Background */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0, zIndex: 1 }}>
        <LightRays
          raysOrigin="top-center"
          raysColor="#ffffff"
          raysSpeed={1.5}
          lightSpread={0.8}
          rayLength={1.2}
          followMouse={true}
          mouseInfluence={0.1}
          noiseAmount={0.1}
          distortion={0.05}
        />
      </div>

      {/* Pill Navigation Bar */}
      <PillNav
        logo="/holocrypt-logo.png"
        logoAlt="HoloCrypt"
        items={[
          { label: 'Home', href: '/' },
          { label: 'About', href: '/about' },
          { label: 'Get Started', href: '/register' }
        ]}
        activeHref={activeHref}
        ease="power2.easeOut"
        baseColor="#000000"
        pillColor="#ffffff"
        hoveredPillTextColor="#ffffff"
        pillTextColor="#000000"
      />

      <div className="login-content">
        <div className="login-card">
          <h2 className="login-title">Welcome Back</h2>
        
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                id="email"
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
                disabled={isDisabled}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Password</label>
              <input
                id="password"
                type="password"
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                disabled={isDisabled}
              />
            </div>

            {error && (
              <div className="error-message">{error}</div>
            )}

            {loginAttempts > 0 && loginAttempts < maxAttempts && (
              <div className="info-message">
                Login attempts: {loginAttempts}/{maxAttempts}
              </div>
            )}

            <button 
              type="submit" 
              className="btn-primary"
              disabled={isDisabled}
            >
              {loading ? 'Logging in...' : 'Sign In'}
            </button>

            <div className="login-footer">
              <p>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/register')}
                  className="link-button"
                  disabled={loading}
                >
                  Create Account
                </button>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login
