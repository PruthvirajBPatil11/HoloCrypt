import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import PillNav from './PillNav'
import Threads from './Threads'
import '../styles/Dashboard.css'

const Dashboard = () => {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [activeHref, setActiveHref] = useState('/dashboard')

  const handleLogout = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="dashboard-container">
      {/* Threads Background */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0, zIndex: 1 }}>
        <Threads
          amplitude={1}
          distance={0}
          enableMouseInteraction={true}
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

      <div className="dashboard-content">
        <div className="dashboard-card">
          <h1 className="dashboard-title">Welcome to HoloCrypt</h1>
          
          <div className="user-info">
            <p className="info-text"><strong>Email:</strong> {user?.email}</p>
            <p className="info-text"><strong>User ID:</strong> {user?.id?.substring(0, 8)}...</p>
          </div>

          <div className="dashboard-main">
            <p className="dashboard-desc">You are successfully authenticated!</p>
            <p className="dashboard-desc">Start encrypting your images with multi-layer security.</p>
          </div>

          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
