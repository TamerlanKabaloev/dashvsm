import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stats } from '@react-three/drei'
import { Scene } from './components/Scene'
import { UI } from './components/UI'

function App() {
  return (
    <>
      <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
        <Canvas shadows camera={{ position: [10, 10, 10], fov: 50 }}>
          <color attach="background" args={['#1e1e1e']} />
          <Scene />
          <OrbitControls makeDefault />
          <Stats />
        </Canvas>
      </div>
      <UI />
    </>
  )
}

export default App

