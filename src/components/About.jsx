import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import PillNav from './PillNav'
import LightRays from './LightRays'
import ScrollStack, { ScrollStackItem } from './ScrollStack'
import '../styles/About.css'

const About = () => {
  const navigate = useNavigate()
  const [activeHref, setActiveHref] = useState('/about')

  return (
    <div className="about-container">
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

      {/* About Content */}
      <div className="about-content">
        <ScrollStack
          itemDistance={150}
          itemScale={0.05}
          itemStackDistance={40}
          stackPosition="30%"
          scaleEndPosition="15%"
          baseScale={0.9}
          useWindowScroll={false}
        >
          <ScrollStackItem itemClassName="stack-hero">
            <h1 className="stack-title">HoloCrypt</h1>
            <p className="stack-description">
              Revolutionizing private communication through invisible encryption. 
              Hide your secrets in plain sight with multi-layer steganography.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-1">
            <h2 className="stack-title">Invisible by Design</h2>
            <p className="stack-description">
              Every ordinary image becomes a multilayer encrypted container. Hide messages, 
              files, or identity-based data inside a photo without changing its appearance. 
              To the outside world, it looks like a regular image—but it secretly carries 
              encrypted information meant only for specific recipients.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-2">
            <h2 className="stack-title">Identity-Based Access</h2>
            <p className="stack-description">
              One image, multiple secrets. Each hidden layer unlocks only for its intended 
              recipient based on their unique identity. The same image can reveal completely 
              different content to different people—making communication truly private and 
              context-aware.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-3">
            <h2 className="stack-title">Multi-Layer Encryption</h2>
            <p className="stack-description">
              Embed multiple encrypted layers in one file. Each layer is independently secured 
              with its own encryption key. Share different information with different recipients 
              using a single, innocent-looking image. Perfect for secure group communications 
              where privacy levels vary.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-4">
            <h2 className="stack-title">Seamless Integration</h2>
            <p className="stack-description">
              No suspicious attachments, no complex workflows. Share your encrypted images 
              through any platform—social media, email, messaging apps—without raising flags. 
              HoloCrypt recognizes who is accessing the file and unlocks only the layers meant 
              for them.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-5">
            <h2 className="stack-title">Credit-Based Economy</h2>
            <p className="stack-description">
              Built-in credit system ensures controlled usage and sustainability. Users spend 
              credits to encode, decode, or unlock higher-level hidden layers. This gamified 
              economy prevents misuse while adding an engaging layer to secure communication. 
              Earn credits through participation, or purchase them for premium features.
            </p>
          </ScrollStackItem>

          <ScrollStackItem itemClassName="stack-card-6">
            <h2 className="stack-title">Get Started Today</h2>
            <p className="stack-description">
              Join thousands of users who trust HoloCrypt for secure, private communication. 
              No technical expertise required—our intuitive interface makes encryption as 
              simple as sharing a photo. Start hiding your secrets in plain sight.
            </p>
            <button 
              className="stack-cta-button"
              onClick={() => navigate('/register')}
            >
              Create Free Account →
            </button>
          </ScrollStackItem>
        </ScrollStack>
      </div>
    </div>
  )
}

export default About
