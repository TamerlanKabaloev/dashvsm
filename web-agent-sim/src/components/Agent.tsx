import { Agent as AgentType } from '../store'

interface AgentProps {
  agent: AgentType
}

export const Agent = ({ agent }: AgentProps) => {
  // Smooth interpolation could be added here, but for now direct position update
  
  return (
    <group position={agent.position}>
      {/* Body */}
      <mesh position={[0, 0.9, 0]} castShadow>
        <capsuleGeometry args={[0.3, 1, 4, 8]} />
        <meshStandardMaterial color={agent.color} />
      </mesh>
      
      {/* Head */}
      <mesh position={[0, 1.6, 0]} castShadow>
        <sphereGeometry args={[0.25]} />
        <meshStandardMaterial color="#ffdbac" />
      </mesh>

      {/* ID Label (Optional) */}
      {/* <Text position={[0, 2.2, 0]} fontSize={0.2} color="white" anchorX="center" anchorY="middle">
        Agent
      </Text> */}
    </group>
  )
}

