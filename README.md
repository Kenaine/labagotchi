# Labagotchi 👾

A retro arcade virtual pet web application whose **HP, Mood, XP, and Evolution Stage** are driven by live latency and uptime checks across a Proxmox homelab.

Built with **React (Vite)**, **FastAPI**, and **Firebase / Firestore** (`firebase-admin` with zero-config local store fallback).

## Features
- **Live Infrastructure Telemetry:** Concurrently probes core homelab nodes (`Proxmox VE`, `Pi-hole DNS`, `Docker Host`, `AI-Admin`) via async TCP & ICMP checks.
- **Overclock Buff Mechanic:** Probes the optional gaming/GPU rig (`Ken / Ollama`). Sleeping gaming rigs do **not** penalize pet HP—waking the rig triggers **OVERCLOCKED** mode (`2x XP` gain + golden aura + mood boost).
- **Interactive Handheld Console:**
  - **⚡ Feed Packet (Ping):** Triggers live LAN probes, logs telemetry, and awards XP.
  - **💚 Pet / Heal:** Restores Mood (`+15`) and grants bonus XP (`+5`).
  - **🎨 Customize:** Rename your pet and switch between 3 animated SVG species (`Cyber-Cat`, `Server-Slime`, `Mecha-Owl`).
  - **📈 Latency Sparkline:** Plots rolling average core latency across the last 20 checks.

## Project Structure
```text
labagotchi/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI endpoints & game state engine
│   │   ├── probes.py      # Async TCP + ICMP homelab node prober
│   │   └── db.py          # Firebase / Firestore repository (Cloud, Emulator, or Local JSON)
│   ├── tests/
│   │   └── test_api.py    # Pytest TDD suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Retro CRT/LCD console & SVG sprite renderer
│   │   ├── App.css        # Arcade styling & animations
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── labagotchi-api.service # Systemd unit for FastAPI backend (:8000)
└── labagotchi-web.service # Systemd unit for Vite preview server (:5173)
```

## Quick Start

### 1. Backend (FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_api.py -v
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
