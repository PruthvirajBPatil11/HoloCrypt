import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import PillNav from './PillNav'
import LightRays from './LightRays'
import '../styles/Register.css'

const Register = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [activeHref, setActiveHref] = useState('/register')

  const { signUp } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    setLoading(true)

    try {
      const { data, error } = await signUp(email, password)

      if (error) {
        // Check if it's a configuration error
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
          setError('⚠️ Supabase not configured. Add your credentials to the .env file and restart the server.')
          return
        }
        setError(error.message)
        return
      }

      setSuccess(true)
      // Note: Supabase sends a confirmation email by default
      // You can configure this in your Supabase project settings
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (err) {
      setError('⚠️ Connection error. Check your Supabase credentials in .env file.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-container">
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

      <div className="register-content">
        <div className="register-card">
          <h2 className="register-title">Create Account</h2>
        
          <form onSubmit={handleSubmit} className="register-form">
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
                disabled={loading}
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
                placeholder="Enter your password (min 6 characters)"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                className="form-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                required
                disabled={loading}
              />
            </div>

            {error && (
              <div className="error-message">{error}</div>
            )}

            {success && (
              <div className="success-message">
                Registration successful! 
                <br /><br />
                <strong>Important:</strong> Check your email for a confirmation link before logging in.
                <br />
                Redirecting to login...
              </div>
            )}

            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Registering...' : 'Create Account'}
            </button>

            <div className="register-footer">
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/login')}
                  className="link-button"
                  disabled={loading}
                >
                  Sign In
                </button>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Register
