import React, { useEffect, useState } from 'react'

function PetSprite({ species, status, overclocked, bounce }) {
  const isCritical = status === 'CRITICAL'
  const isDegraded = status === 'DEGRADED'

  const primaryColor = overclocked
    ? '#fbbf24'
    : isCritical
    ? '#f87171'
    : isDegraded
    ? '#fb923c'
    : species === 'server-slime'
    ? '#34d399'
    : species === 'mecha-owl'
    ? '#38bdf8'
    : '#a78bfa'

  const eyeColor = overclocked ? '#fef08a' : isCritical ? '#ef4444' : '#22d3ee'

  return (
    <div className={`pet-sprite-wrap ${bounce ? 'pet-bounce' : ''} ${overclocked ? 'overclock-aura' : ''}`}>
      <svg viewBox="0 0 120 120" className="pet-svg" aria-label="Labagotchi sprite">
        {/* Glow ring */}
        <circle
          cx="60"
          cy="64"
          r="46"
          fill="none"
          stroke={primaryColor}
          strokeWidth="1.5"
          strokeDasharray="4 4"
          opacity="0.45"
        />
        {/* Shadow */}
        <ellipse cx="60" cy="104" rx="28" ry="6" fill="rgba(0,0,0,0.45)" />

        {species === 'cyber-cat' && (
          <g>
            {/* Ears */}
            <polygon points="30,44 26,20 46,34" fill={primaryColor} />
            <polygon points="90,44 94,20 74,34" fill={primaryColor} />
            <polygon points="32,40 30,26 42,35" fill="#1e1b4b" />
            <polygon points="88,40 90,26 78,35" fill="#1e1b4b" />
            {/* Head/Body */}
            <rect x="26" y="34" width="68" height="58" rx="14" fill={primaryColor} />
            {/* Visor screen */}
            <rect x="33" y="43" width="54" height="32" rx="8" fill="#090d16" stroke="#334155" strokeWidth="2" />
            {/* Whiskers / Antennas */}
            <line x1="18" y1="56" x2="28" y2="58" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" />
            <line x1="18" y1="64" x2="28" y2="64" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" />
            <line x1="102" y1="56" x2="92" y2="58" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" />
            <line x1="102" y1="64" x2="92" y2="64" stroke={eyeColor} strokeWidth="2.5" strokeLinecap="round" />
          </g>
        )}

        {species === 'server-slime' && (
          <g>
            {/* Antenna */}
            <line x1="60" y1="16" x2="60" y2="30" stroke={primaryColor} strokeWidth="4" />
            <circle cx="60" cy="14" r="5" fill={eyeColor} />
            {/* Slime dome */}
            <path
              d="M24,78 C24,42 36,28 60,28 C84,28 96,42 96,78 C96,90 84,94 60,94 C36,94 24,90 24,78 Z"
              fill={primaryColor}
            />
            {/* Face visor */}
            <rect x="34" y="46" width="52" height="30" rx="10" fill="#090d16" />
          </g>
        )}

        {species === 'mecha-owl' && (
          <g>
            {/* Crest */}
            <polygon points="60,16 48,32 72,32" fill={eyeColor} />
            {/* Body */}
            <rect x="28" y="30" width="64" height="62" rx="20" fill={primaryColor} />
            {/* Wings */}
            <rect x="18" y="46" width="12" height="34" rx="6" fill={primaryColor} opacity="0.85" />
            <rect x="90" y="46" width="12" height="34" rx="6" fill={primaryColor} opacity="0.85" />
            {/* Goggles */}
            <rect x="34" y="42" width="52" height="30" rx="8" fill="#090d16" stroke={eyeColor} strokeWidth="1.5" />
            {/* Beak */}
            <polygon points="60,64 55,57 65,57" fill="#fbbf24" />
          </g>
        )}

        {/* Facial Expressions inside Visor */}
        {isCritical ? (
          <g stroke="#ef4444" strokeWidth="3" strokeLinecap="round">
            <line x1="42" y1="52" x2="50" y2="60" />
            <line x1="50" y1="52" x2="42" y2="60" />
            <line x1="70" y1="52" x2="78" y2="60" />
            <line x1="78" y1="52" x2="70" y2="60" />
            <path d="M48,69 Q60,61 72,69" fill="none" />
          </g>
        ) : overclocked ? (
          <g>
            {/* Star / Lightning eyes */}
            <polygon points="46,49 49,56 55,56 50,60 52,66 46,62 40,66 42,60 37,56 43,56" fill="#fde047" />
            <polygon points="74,49 77,56 83,56 78,60 80,66 74,62 68,66 70,60 65,56 71,56" fill="#fde047" />
            <path d="M50,66 Q60,74 70,66" fill="none" stroke="#fde047" strokeWidth="3" strokeLinecap="round" />
          </g>
        ) : isDegraded ? (
          <g>
            <rect x="41" y="54" width="10" height="4" fill="#fb923c" />
            <rect x="69" y="54" width="10" height="4" fill="#fb923c" />
            <line x1="50" y1="67" x2="70" y2="67" stroke="#fb923c" strokeWidth="3" strokeLinecap="round" />
            {/* Sweat drop */}
            <path d="M84,42 C84,42 88,48 88,51 C88,53.5 86,55 84,55 C82,55 80,53.5 80,51 C80,48 84,42 84,42 Z" fill="#38bdf8" />
          </g>
        ) : (
          <g>
            <circle cx="46" cy="56" r="5" fill={eyeColor} />
            <circle cx="74" cy="56" r="5" fill={eyeColor} />
            <circle cx="44" cy="54" r="1.8" fill="#ffffff" />
            <circle cx="72" cy="54" r="1.8" fill="#ffffff" />
            <path d="M51,65 Q60,72 69,65" fill="none" stroke={eyeColor} strokeWidth="2.8" strokeLinecap="round" />
          </g>
        )}
      </svg>
    </div>
  )
}

function Sparkline({ history }) {
  if (!history || history.length === 0) {
    return <div className="spark-empty">No telemetry samples yet — click FEED PACKET!</div>
  }

  const values = history.map((h) => Number(h.avg_core_latency_ms || 0))
  const maxVal = Math.max(...values, 5)
  const width = 360
  const height = 68
  const pad = 8

  const points = values
    .map((v, i) => {
      const x =
        values.length === 1
          ? width / 2
          : pad + (i / (values.length - 1)) * (width - pad * 2)
      const y = height - pad - (v / maxVal) * (height - pad * 2)
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')

  const latest = values[values.length - 1]?.toFixed(2)

  return (
    <div className="sparkline-box">
      <div className="sparkline-header">
        <span>CORE LATENCY SPARKLINE ({values.length} SAMPLES)</span>
        <span className="spark-latest">{latest} ms avg</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="spark-svg">
        <polyline
          fill="none"
          stroke="#22d3ee"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        {values.map((v, i) => {
          const x =
            values.length === 1
              ? width / 2
              : pad + (i / (values.length - 1)) * (width - pad * 2)
          const y = height - pad - (v / maxVal) * (height - pad * 2)
          return <circle key={i} cx={x} cy={y} r="3" fill="#a78bfa" />
        })}
      </svg>
    </div>
  )
}

export default function App() {
  const [pet, setPet] = useState(null)
  const [history, setHistory] = useState([])
  const [firebaseMode, setFirebaseMode] = useState('loading...')
  const [loadingAction, setLoadingAction] = useState(false)
  const [bounce, setBounce] = useState(false)
  const [toast, setToast] = useState('')
  const [autoPing, setAutoPing] = useState(true)
  const [showCustomize, setShowCustomize] = useState(false)
  const [nameInput, setNameInput] = useState('')
  const [speciesInput, setSpeciesInput] = useState('cyber-cat')

  const triggerToast = (msg) => {
    setToast(msg)
    setBounce(true)
    setTimeout(() => setBounce(false), 700)
    setTimeout(() => setToast(''), 3200)
  }

  const fetchState = async () => {
    try {
      const res = await fetch('/api/state')
      const data = await res.json()
      setPet(data.pet)
      setHistory(data.history || [])
      setFirebaseMode(data.firebase_mode || 'local')
      if (!nameInput && data.pet?.name) {
        setNameInput(data.pet.name)
        setSpeciesInput(data.pet.species || 'cyber-cat')
      }
    } catch (err) {
      console.error('Failed to fetch state:', err)
    }
  }

  useEffect(() => {
    fetchState()
  }, [])

  useEffect(() => {
    if (!autoPing) return
    const timer = setInterval(() => {
      handleFeed(true)
    }, 30000)
    return () => clearInterval(timer)
  }, [autoPing])

  const handleFeed = async (silent = false) => {
    if (loadingAction) return
    setLoadingAction(true)
    try {
      const res = await fetch('/api/pet/feed', { method: 'POST' })
      const data = await res.json()
      setPet(data.pet)
      setHistory(data.history || [])
      setFirebaseMode(data.firebase_mode)
      if (!silent) {
        triggerToast(data.pet.overclocked ? '⚡ OVERCLOCK PING! +2x XP!' : '📡 Packet fed! Telemetry updated.')
      }
    } finally {
      setLoadingAction(false)
    }
  }

  const handleHeal = async () => {
    if (loadingAction) return
    setLoadingAction(true)
    try {
      const res = await fetch('/api/pet/heal', { method: 'POST' })
      const data = await res.json()
      setPet(data.pet)
      setHistory(data.history || [])
      triggerToast('💚 +15 Mood & +5 XP!')
    } finally {
      setLoadingAction(false)
    }
  }

  const handleCustomize = async (e) => {
    e.preventDefault()
    if (!nameInput.trim()) return
    setLoadingAction(true)
    try {
      const res = await fetch('/api/pet/customize', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: nameInput.trim(), species: speciesInput }),
      })
      const data = await res.json()
      setPet(data.pet)
      setShowCustomize(false)
      triggerToast(`✨Customized ${data.pet.name}!`)
    } finally {
      setLoadingAction(false)
    }
  }

  if (!pet) {
    return (
      <div className="loading-screen">
        <div className="crt-scanlines" />
        <p className="pixel-title">BOOTING LABAGOTCHI OS...</p>
      </div>
    )
  }

  const xpIntoLevel = pet.xp % 50
  const xpProgressPct = Math.min(100, Math.round((xpIntoLevel / 50) * 100))

  return (
    <div className="app-shell">
      <div className="crt-scanlines" />

      <header className="top-bar">
        <div>
          <span className="arcade-badge">CT 102 // ARCADE MONITOR</span>
          <h1 className="pixel-title">LABAGOTCHI</h1>
        </div>
        <div className="header-meta">
          <span className={`mode-pill ${pet.overclocked ? 'pill-gold' : ''}`}>
            DB: {firebaseMode}
          </span>
          <button
            type="button"
            className={`auto-btn ${autoPing ? 'auto-on' : ''}`}
            onClick={() => setAutoPing(!autoPing)}
          >
            {autoPing ? '⏱ AUTO-PING: ON (30s)' : '⏱ AUTO-PING: OFF'}
          </button>
        </div>
      </header>

      <main className="console-grid">
        {/* LEFT COLUMN: Virtual Pet Handheld Stage */}
        <section className="pet-card">
          <div className="pet-header">
            <div>
              <h2 className="pet-name">{pet.name}</h2>
              <span className="pet-subtitle">
                Lv.{pet.level} {pet.stage} • {pet.species.toUpperCase()}
              </span>
            </div>
            <span className={`status-chip status-${pet.status.toLowerCase()}`}>
              {pet.status}
            </span>
          </div>

          <div className="lcd-screen">
            {toast && <div className="floating-toast">{toast}</div>}
            <PetSprite
              species={pet.species}
              status={pet.status}
              overclocked={pet.overclocked}
              bounce={bounce}
            />
            <div className="lcd-caption">{pet.last_event}</div>
          </div>

          {/* Stat Bars */}
          <div className="stat-bars">
            <div className="stat-row">
              <div className="stat-label">
                <span>❤️ CORE HP (INFRASTRUCTURE)</span>
                <span>{pet.hp}%</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill fill-hp"
                  style={{ width: `${pet.hp}%` }}
                />
              </div>
            </div>

            <div className="stat-row">
              <div className="stat-label">
                <span>😊 MOOD / VIBE</span>
                <span>{pet.mood}%</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill fill-mood"
                  style={{ width: `${pet.mood}%` }}
                />
              </div>
            </div>

            <div className="stat-row">
              <div className="stat-label">
                <span>⚡ EXP ({pet.xp} TOTAL — NEXT LV AT {pet.level * 50})</span>
                <span>{xpIntoLevel}/50 XP</span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill fill-xp"
                  style={{ width: `${xpProgressPct}%` }}
                />
              </div>
            </div>
          </div>

          {/* Interactive Deck */}
          <div className="action-deck">
            <button
              type="button"
              className="arcade-btn btn-feed"
              onClick={() => handleFeed(false)}
              disabled={loadingAction}
            >
              {loadingAction ? 'PINGING LAN...' : '⚡ FEED PACKET (PING)'}
            </button>
            <button
              type="button"
              className="arcade-btn btn-heal"
              onClick={handleHeal}
              disabled={loadingAction}
            >
              💚 PET / HEAL
            </button>
            <button
              type="button"
              className="arcade-btn btn-cust"
              onClick={() => {
                setNameInput(pet.name)
                setSpeciesInput(pet.species)
                setShowCustomize(!showCustomize)
              }}
            >
              🎨 CUSTOMIZE
            </button>
          </div>

          {showCustomize && (
            <form className="customize-drawer" onSubmit={handleCustomize}>
              <div className="drawer-row">
                <label>PET NAME</label>
                <input
                  type="text"
                  maxLength={24}
                  value={nameInput}
                  onChange={(e) => setNameInput(e.target.value)}
                  placeholder="Enter pet name..."
                />
              </div>
              <div className="drawer-row">
                <label>CHASSIS / SPECIES</label>
                <select
                  value={speciesInput}
                  onChange={(e) => setSpeciesInput(e.target.value)}
                >
                  <option value="cyber-cat">Cyber-Cat (Neko Unit)</option>
                  <option value="server-slime">Server-Slime (Blob OS)</option>
                  <option value="mecha-owl">Mecha-Owl (Night Sentinel)</option>
                </select>
              </div>
              <button type="submit" className="arcade-btn btn-save">
                SAVE IDENTITY
              </button>
            </form>
          )}
        </section>

        {/* RIGHT COLUMN: Homelab Node Telemetry */}
        <section className="telemetry-card">
          <div className="telemetry-header">
            <h2>HOMELAB TELEMETRY MATRIX</h2>
            <p>
              Core nodes drive <strong>HP</strong>. Waking <strong>Ken (.35)</strong> triggers{' '}
              <span className="gold-text">OVERCLOCK (2x XP & Aura)</span> without penalizing HP when asleep.
            </p>
          </div>

          <div className="nodes-list">
            {(pet.last_nodes || []).map((node) => {
              const isBonus = node.role === 'bonus'
              return (
                <div
                  key={node.id}
                  className={`node-item ${node.online ? 'node-up' : isBonus ? 'node-sleep' : 'node-down'}`}
                >
                  <div className="node-left">
                    <span className="node-dot" />
                    <div>
                      <div className="node-title-row">
                        <span className="node-name">{node.name}</span>
                        <span className={`role-tag ${isBonus ? 'tag-bonus' : 'tag-core'}`}>
                          {isBonus ? 'BONUS BUFF' : 'CORE HP'}
                        </span>
                      </div>
                      <span className="node-sub">
                        {node.ip}:{node.port} — {node.desc}
                      </span>
                    </div>
                  </div>

                  <div className="node-right">
                    {node.online ? (
                      <>
                        <span className="latency-val">{node.latency_ms} ms</span>
                        <span className="node-state-badge badge-up">
                          {isBonus ? '⚡ AWAKE' : 'ONLINE'}
                        </span>
                      </>
                    ) : (
                      <span className={`node-state-badge ${isBonus ? 'badge-sleep' : 'badge-down'}`}>
                        {isBonus ? '💤 ASLEEP (NO PENALTY)' : '❌ OFFLINE'}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <Sparkline history={history} />
        </section>
      </main>
    </div>
  )
}
