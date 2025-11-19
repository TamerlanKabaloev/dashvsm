import { useFrame } from '@react-three/fiber'
import { Tunnel } from './Tunnel'
import { Agent } from './Agent'
import { useSimulationStore } from '../store'

export const Scene = () => {
  const agents = useSimulationStore(state => state.agents)
  const tick = useSimulationStore(state => state.tick)

  useFrame((_, delta) => {
    tick(delta)
  })

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight 
        position={[10, 20, 10]} 
        intensity={1} 
        castShadow 
        shadow-mapSize={[1024, 1024]}
      />
      
      {/* Grid helper for reference */}
      <gridHelper args={[100, 100, '#333', '#222']} position={[0, -0.01, 0]} />
      
      <Tunnel />
      
      {agents.map(agent => (
        <Agent key={agent.id} agent={agent} />
      ))}
    </>
  )
}

