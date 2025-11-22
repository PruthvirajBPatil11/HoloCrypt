import { useNavigate } from 'react-router-dom'
import { useRef, useState } from 'react'
import GridScan from './GridScan'
import ClickSpark from './ClickSpark'
import PillNav from './PillNav'
import '../styles/LandingPage.css'

const LandingPage = () => {
  const navigate = useNavigate()
  const revealImgRef = useRef(null)
  const [activeHref, setActiveHref] = useState('/')

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const el = revealImgRef.current
    if (el) {
      el.style.setProperty('--mx', `${x}px`)
      el.style.setProperty('--my', `${y}px`)
    }
  }

  const handleMouseLeave = () => {
    const el = revealImgRef.current
    if (el) {
      el.style.setProperty('--mx', '-9999px')
      el.style.setProperty('--my', '-9999px')
    }
  }

  return (
    <ClickSpark
      sparkColor='#fff'
      sparkSize={10}
      sparkRadius={15}
      sparkCount={8}
      duration={400}
    >
      <div className="landing-container" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeave}>
        {/* Grid Scan Background */}
        <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0, zIndex: 1 }}>
          <GridScan
            sensitivity={0.55}
            lineThickness={1}
            linesColor="#ffffff"
            gridScale={0.1}
            scanColor="#ffffff"
            scanOpacity={0.3}
            enablePost
            bloomIntensity={0.4}
            chromaticAberration={0.001}
            noiseIntensity={0.01}
          />
        </div>

        {/* Reveal Effect Layer */}
        <div
          ref={revealImgRef}
          className="reveal-layer"
        />

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
      
      {/* Hero Section */}
      <main className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Hide secrets in plain sight
          </h1>
          <p className="hero-subtitle">
            Transform ordinary images into secure, encrypted containers. One image, multiple hidden layers—each revealed only to its intended recipient.
          </p>
          <div className="cta-buttons">
            <button className="cta-primary" onClick={() => navigate('/register')}>
              Start Encrypting Free
            </button>
            <button className="cta-secondary" onClick={() => navigate('/login')}>
              Sign In
            </button>
          </div>
        </div>
      </main>
    </div>
    </ClickSpark>
  )
}

export default LandingPage
