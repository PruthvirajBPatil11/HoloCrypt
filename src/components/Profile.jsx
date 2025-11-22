import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import PillNav from './PillNav'
import LightRays from './LightRays'
import '../styles/Profile.css'

const Profile = () => {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [activeHref, setActiveHref] = useState('/profile')

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  // Extract user info
  const email = user?.email || 'Not available'
  const userId = user?.id || 'Not available'
  const createdAt = user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Not available'
  const lastSignIn = user?.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString() : 'Not available'

  return (
    <div className="profile-container">
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
          { label: 'Home', href: '/dashboard' },
          { label: 'About', href: '/about' },
          { label: 'Profile', href: '/profile' }
        ]}
        activeHref={activeHref}
        ease="power2.easeOut"
        baseColor="#000000"
        pillColor="#ffffff"
        hoveredPillTextColor="#ffffff"
        pillTextColor="#000000"
      />

      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              {email.charAt(0).toUpperCase()}
            </div>
            <h2 className="profile-title">User Profile</h2>
          </div>

          <div className="profile-details">
            <div className="detail-row">
              <label className="detail-label">Email Address</label>
              <p className="detail-value">{email}</p>
            </div>

            <div className="detail-row">
              <label className="detail-label">User ID</label>
              <p className="detail-value">{userId}</p>
            </div>

            <div className="detail-row">
              <label className="detail-label">Account Created</label>
              <p className="detail-value">{createdAt}</p>
            </div>

            <div className="detail-row">
              <label className="detail-label">Last Sign In</label>
              <p className="detail-value">{lastSignIn}</p>
            </div>
          </div>

          <div className="profile-actions">
            <button onClick={() => navigate('/dashboard')} className="btn-primary">
              Back to Dashboard
            </button>
            <button onClick={handleLogout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
