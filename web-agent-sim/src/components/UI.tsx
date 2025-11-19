import { useSimulationStore } from '../store'

export const UI = () => {
  const {
    tunnelWidth, setTunnelWidth,
    tunnelLength, setTunnelLength,
    passengersPer15Min, setPassengersPer15Min,
    maxAgents, setMaxAgents,
    agentSpeedMin, agentSpeedMax, setAgentSpeedRange,
    isRunning, toggleSimulation, resetSimulation,
    agents, agentsSpawnedTotal
  } = useSimulationStore()

  // Crowd Density Calculation
  const density = agents.length / (tunnelWidth * tunnelLength)
  
  // Determine status based on Fruin Level of Service
  let status = 'Free Flow (LOS A)'
  let statusColor = '#4caf50' // Green
  let statusBg = 'rgba(76, 175, 80, 0.1)'
  
  if (density > 2.17) {
    status = 'JAM (LOS F)'
    statusColor = '#f44336' // Red
    statusBg = 'rgba(244, 67, 54, 0.2)'
  } else if (density > 1.08) {
    status = 'Congested (LOS E)'
    statusColor = '#ff5722' // Deep Orange
    statusBg = 'rgba(255, 87, 34, 0.15)'
  } else if (density > 0.72) {
    status = 'Restricted (LOS D)'
    statusColor = '#ff9800' // Orange
    statusBg = 'rgba(255, 152, 0, 0.1)'
  } else if (density > 0.43) {
    status = 'Dense (LOS C)'
    statusColor = '#ffc107' // Amber
    statusBg = 'rgba(255, 193, 7, 0.1)'
  }

  return (
    <div className="ui-panel">
      <style>{`
        .ui-panel {
          position: absolute;
          top: 20px;
          right: 20px;
          width: 300px;
          background: rgba(0, 0, 0, 0.8);
          padding: 20px;
          border-radius: 8px;
          color: white;
          font-family: sans-serif;
          backdrop-filter: blur(5px);
        }
        .control-group {
          margin-bottom: 15px;
        }
        label {
          display: block;
          margin-bottom: 5px;
          font-size: 14px;
          color: #ccc;
        }
        input[type="range"] {
          width: 100%;
        }
        .value {
          float: right;
          color: #4caf50;
        }
        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }
        button {
          flex: 1;
          padding: 10px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
          transition: background 0.2s;
        }
        .btn-primary {
          background: #2196f3;
          color: white;
        }
        .btn-primary:hover {
          background: #1976d2;
        }
        .btn-danger {
          background: #f44336;
          color: white;
        }
        .btn-danger:hover {
          background: #d32f2f;
        }
        .stats {
          margin-top: 20px;
          padding-top: 10px;
          border-top: 1px solid #444;
          font-size: 12px;
          color: #888;
        }
      `}</style>

      <h2>Simulation Controls</h2>

      <div className="control-group">
        <label>
          Tunnel Width <span className="value">{tunnelWidth}m</span>
        </label>
        <input 
          type="range" 
          min="1" max="20" step="0.5" 
          value={tunnelWidth} 
          onChange={(e) => setTunnelWidth(parseFloat(e.target.value))} 
        />
      </div>

      <div className="control-group">
        <label>
          Tunnel Length <span className="value">{tunnelLength}m</span>
        </label>
        <input 
          type="range" 
          min="5" max="50" step="1" 
          value={tunnelLength} 
          onChange={(e) => setTunnelLength(parseFloat(e.target.value))} 
        />
      </div>

      <div className="control-group">
        <label>
          Passengers / 15-min Peak
        </label>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <input 
            type="range" 
            min="0" max="10000" step="10" 
            value={passengersPer15Min} 
            onChange={(e) => setPassengersPer15Min(parseFloat(e.target.value))}
            style={{ flex: 1 }}
          />
          <input
            type="number"
            value={passengersPer15Min}
            onChange={(e) => setPassengersPer15Min(parseFloat(e.target.value) || 0)}
            style={{ width: '70px', padding: '5px', borderRadius: '4px', border: '1px solid #666', background: '#333', color: 'white' }}
          />
        </div>
      </div>

      <div className="control-group">
        <label>
          Total Agents (0 = Infinite)
        </label>
        <input 
          type="number" 
          min="0" step="1" 
          value={maxAgents} 
          onChange={(e) => setMaxAgents(parseInt(e.target.value) || 0)}
          style={{ width: '100%', padding: '5px', borderRadius: '4px', border: '1px solid #666', background: '#333', color: 'white' }}
        />
      </div>

      <div className="control-group" style={{ 
        marginTop: '20px', 
        padding: '10px', 
        background: statusBg, 
        borderRadius: '4px',
        border: `1px solid ${statusColor}`,
        transition: 'all 0.3s ease'
      }}>
        <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          Crowd Density
          <span style={{ color: statusColor, fontWeight: 'bold' }}>{density.toFixed(2)} p/m²</span>
        </label>
        
        <div style={{ width: '100%', height: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '5px', overflow: 'hidden' }}>
          <div style={{ 
            width: `${Math.min(density / 3 * 100, 100)}%`, 
            height: '100%', 
            background: statusColor,
            transition: 'width 0.3s, background 0.3s'
          }} />
        </div>
        
        <div style={{ 
          textAlign: 'center', 
          color: statusColor, 
          fontSize: '12px', 
          marginTop: '8px', 
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          {status}
        </div>
      </div>

      <div className="control-group">
        <label>
          Speed Range (m/s) <span className="value">{agentSpeedMin} - {agentSpeedMax}</span>


        </label>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input 
            type="number" 
            min="0.5" max="10" step="0.1" 
            value={agentSpeedMin} 
            onChange={(e) => setAgentSpeedRange(parseFloat(e.target.value), agentSpeedMax)} 
          />
          <input 
            type="number" 
            min="0.5" max="10" step="0.1" 
            value={agentSpeedMax} 
            onChange={(e) => setAgentSpeedRange(agentSpeedMin, parseFloat(e.target.value))} 
          />
        </div>
      </div>

      <div className="button-group">
        <button 
          className="btn-primary" 
          onClick={toggleSimulation}
          style={{ backgroundColor: isRunning ? '#ff9800' : '#4caf50' }}
        >
          {isRunning ? 'PAUSE' : 'START'}
        </button>
        <button className="btn-danger" onClick={resetSimulation}>
          RESET
        </button>
      </div>

      <div className="stats">
        Active Agents: {agents.length} <br/>
        Spawned: {agentsSpawnedTotal} / {maxAgents === 0 ? '∞' : maxAgents}
      </div>
    </div>
  )
}

