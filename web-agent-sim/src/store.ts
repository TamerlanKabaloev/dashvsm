import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'

export interface Agent {
  id: string
  position: [number, number, number]
  velocity: [number, number, number]
  speed: number
  color: string
  target: [number, number, number]
}

interface SimulationState {
  // Parameters
  tunnelWidth: number
  tunnelLength: number
  passengersPer15Min: number // Replaces passengersPerHour
  maxAgents: number // 0 for infinite
  agentSpeedMin: number
  agentSpeedMax: number
  
  // State
  agents: Agent[]
  agentsSpawnedTotal: number
  isRunning: boolean
  lastSpawnTime: number

  // Actions
  setTunnelWidth: (width: number) => void
  setTunnelLength: (length: number) => void
  setPassengersPer15Min: (count: number) => void
  setMaxAgents: (count: number) => void
  setAgentSpeedRange: (min: number, max: number) => void
  toggleSimulation: () => void
  resetSimulation: () => void
  
  // Simulation Loop
  tick: (delta: number) => void
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  tunnelWidth: 4,
  tunnelLength: 10,
  passengersPer15Min: 900, // Default (equivalent to 3600/hr or 1/sec)
  maxAgents: 0, // Infinite by default
  agentSpeedMin: 2,
  agentSpeedMax: 4,
  
  agents: [],
  agentsSpawnedTotal: 0,
  isRunning: false,
  lastSpawnTime: 0,

  setTunnelWidth: (width) => set({ tunnelWidth: width }),
  setTunnelLength: (length) => set({ tunnelLength: length }),
  setPassengersPer15Min: (count) => set({ passengersPer15Min: count }),
  setMaxAgents: (count) => set({ maxAgents: count }),
  setAgentSpeedRange: (min, max) => set({ agentSpeedMin: min, agentSpeedMax: max }),
  
  toggleSimulation: () => set((state) => {
    // When starting, reset timer to avoid huge catch-up if paused for long
    if (!state.isRunning) {
      return { isRunning: true, lastSpawnTime: Date.now() }
    }
    return { isRunning: false }
  }),
  
  resetSimulation: () => set({ agents: [], agentsSpawnedTotal: 0, isRunning: false, lastSpawnTime: 0 }),

  tick: (delta) => {
    const { 
      agents, isRunning, passengersPer15Min, lastSpawnTime, 
      tunnelWidth, tunnelLength, agentSpeedMin, agentSpeedMax,
      maxAgents, agentsSpawnedTotal
    } = get()

    if (!isRunning) return

    const now = Date.now()
    let newAgents = [...agents]
    let newLastSpawnTime = lastSpawnTime
    let newAgentsSpawnedTotal = agentsSpawnedTotal

    // Spawning Logic
    // passengersPer15Min = agents / 15 min
    // 15 min = 15 * 60 * 1000 = 900,000 ms
    // interval (ms) = 900000 / passengersPer15Min
    const spawnInterval = passengersPer15Min > 0 ? 900000 / passengersPer15Min : Infinity
    
    const timeSinceLastSpawn = now - lastSpawnTime
    let agentsToSpawn = Math.floor(timeSinceLastSpawn / spawnInterval)
    
    // Cap max spawn per frame to prevent freeze on resume/high lag
    if (agentsToSpawn > 50) {
      agentsToSpawn = 50
      newLastSpawnTime = now // Skip catch-up if we capped it
    } else if (agentsToSpawn > 0) {
      newLastSpawnTime += agentsToSpawn * spawnInterval
    }

    if (agentsToSpawn > 0) {
        // Check limit
        if (maxAgents > 0) {
            const remaining = maxAgents - newAgentsSpawnedTotal
            if (remaining <= 0) agentsToSpawn = 0
            else if (agentsToSpawn > remaining) agentsToSpawn = remaining
        }

        for (let i = 0; i < agentsToSpawn; i++) {
            const startX = (Math.random() - 0.5) * (tunnelWidth - 1)
            // Distribute Z slightly to avoid perfect overlap if spawning multiple
            const startZ = -tunnelLength / 2 - (Math.random() * 2) 

            const speed = agentSpeedMin + Math.random() * (agentSpeedMax - agentSpeedMin)
            
            newAgents.push({
                id: uuidv4(),
                position: [startX, 0, startZ],
                velocity: [0, 0, 0],
                speed: speed,
                color: `hsl(${Math.random() * 360}, 70%, 50%)`,
                target: [startX, 0, tunnelLength / 2 + 2]
            })
        }
        newAgentsSpawnedTotal += agentsToSpawn
    }

    // Movement Logic
    newAgents = newAgents.map(agent => {
      // Simple movement along Z axis for now
      const dz = agent.speed * delta
      
      // Basic collision avoidance (very simple separation)
      let separationX = 0
      let separationZ = 0
      
      agents.forEach(other => {
        if (agent.id === other.id) return
        const dx = agent.position[0] - other.position[0]
        const distZ = agent.position[2] - other.position[2]
        const dist = Math.sqrt(dx*dx + distZ*distZ)
        
        if (dist < 0.8) { // Personal space radius
          separationX += dx / dist 
          separationZ += distZ / dist
        }
      })

      // Update position
      const nextX = agent.position[0] + separationX * delta * 2
      const nextZ = agent.position[2] + dz + separationZ * delta * 2

      // Constrain to tunnel width
      const constrainedX = Math.max(Math.min(nextX, tunnelWidth/2 - 0.5), -tunnelWidth/2 + 0.5)

      return {
        ...agent,
        position: [constrainedX, 0, nextZ] as [number, number, number]
      }
    }).filter(agent => agent.position[2] < tunnelLength / 2 + 5) // Remove agents that have exited far enough

    set({ agents: newAgents, lastSpawnTime: newLastSpawnTime, agentsSpawnedTotal: newAgentsSpawnedTotal })
  }
}))

