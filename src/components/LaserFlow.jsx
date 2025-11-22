import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const LaserFlow = ({ 
  horizontalBeamOffset = 0.0, 
  verticalBeamOffset = 0.0,
  color = "#FFFFFF"
}) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const meshRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 2;
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true 
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Shader material
    const vertexShader = `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      uniform float time;
      uniform float horizontalOffset;
      uniform float verticalOffset;
      uniform vec3 color;
      varying vec2 vUv;

      float random(vec2 st) {
        return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
      }

      void main() {
        vec2 uv = vUv;
        
        // Horizontal laser beams
        float hBeam1 = smoothstep(0.01, 0.0, abs(uv.y - 0.3 - horizontalOffset - sin(time * 0.5) * 0.1));
        float hBeam2 = smoothstep(0.01, 0.0, abs(uv.y - 0.7 - horizontalOffset + sin(time * 0.7) * 0.1));
        
        // Vertical laser beams
        float vBeam1 = smoothstep(0.01, 0.0, abs(uv.x - 0.25 - verticalOffset - sin(time * 0.6) * 0.1));
        float vBeam2 = smoothstep(0.01, 0.0, abs(uv.x - 0.75 - verticalOffset + sin(time * 0.8) * 0.1));
        
        // Moving particles
        float particle1 = smoothstep(0.02, 0.0, length(uv - vec2(fract(time * 0.1), 0.3)));
        float particle2 = smoothstep(0.02, 0.0, length(uv - vec2(fract(time * 0.15 + 0.5), 0.7)));
        
        // Grid effect
        float grid = step(0.98, fract(uv.x * 20.0)) * step(0.98, fract(uv.y * 20.0)) * 0.3;
        
        // Combine effects
        float finalBeam = hBeam1 + hBeam2 + vBeam1 + vBeam2 + particle1 + particle2 + grid;
        
        // Apply color
        vec3 finalColor = color * finalBeam;
        
        gl_FragColor = vec4(finalColor, finalBeam * 0.8);
      }
    `;

    // Parse hex color to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16) / 255,
        g: parseInt(result[2], 16) / 255,
        b: parseInt(result[3], 16) / 255
      } : { r: 1, g: 1, b: 1 };
    };

    const rgbColor = hexToRgb(color);

    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        time: { value: 0 },
        horizontalOffset: { value: horizontalBeamOffset },
        verticalOffset: { value: verticalBeamOffset },
        color: { value: new THREE.Vector3(rgbColor.r, rgbColor.g, rgbColor.b) }
      },
      transparent: true,
      blending: THREE.AdditiveBlending
    });

    // Geometry
    const geometry = new THREE.PlaneGeometry(4, 4);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    meshRef.current = mesh;

    // Animation loop
    let animationFrameId;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      material.uniforms.time.value += 0.01;
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      renderer.dispose();
    };
  }, [horizontalBeamOffset, verticalBeamOffset, color]);

  return (
    <div
      ref={containerRef}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 1,
        pointerEvents: 'none'
      }}
    />
  );
};

export default LaserFlow;
