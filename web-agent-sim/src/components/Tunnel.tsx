import { useSimulationStore } from '../store'

export const Tunnel = () => {
  const width = useSimulationStore(state => state.tunnelWidth)
  const length = useSimulationStore(state => state.tunnelLength)

  return (
    <group position={[0, 0, 0]}>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[width, length]} />
        <meshStandardMaterial color="#444" />
      </mesh>

      {/* Left Wall */}
      <mesh position={[-width / 2, 1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.2, 3, length]} />
        <meshStandardMaterial color="#666" transparent opacity={0.5} />
      </mesh>

      {/* Right Wall */}
      <mesh position={[width / 2, 1.5, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.2, 3, length]} />
        <meshStandardMaterial color="#666" transparent opacity={0.5} />
      </mesh>

      {/* Entry Line Marker */}
      <mesh position={[0, 0.01, -length / 2]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[width, 0.2]} />
        <meshBasicMaterial color="green" />
      </mesh>

      {/* Exit Line Marker */}
      <mesh position={[0, 0.01, length / 2]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[width, 0.2]} />
        <meshBasicMaterial color="red" />
      </mesh>
    </group>
  )
}

