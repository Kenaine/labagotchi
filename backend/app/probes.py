import asyncio
import re
import time
from typing import Any, Dict, List, Optional

HOMELAB_NODES: List[Dict[str, Any]] = [
    {
        "id": "proxmox",
        "name": "Proxmox VE",
        "ip": "192.168.1.34",
        "port": 8006,
        "role": "core",
        "desc": "Hypervisor Host (pve)",
    },
    {
        "id": "pihole",
        "name": "Pi-hole DNS",
        "ip": "192.168.1.36",
        "port": 53,
        "role": "core",
        "desc": "CT 100 Network DNS Guard",
    },
    {
        "id": "docker",
        "name": "Docker Host",
        "ip": "192.168.1.38",
        "port": 22,
        "role": "core",
        "desc": "CT 101 Container Engine",
    },
    {
        "id": "ai-admin",
        "name": "AI-Admin (Hermes)",
        "ip": "192.168.1.50",
        "port": 22,
        "role": "core",
        "desc": "CT 200 Autonomous Admin",
    },
    {
        "id": "ken",
        "name": "Ken (Gaming Rig / Ollama)",
        "ip": "192.168.1.35",
        "port": 11434,
        "role": "bonus",
        "desc": "GPU Rig — 2x XP & Overclock Aura",
    },
]


async def _tcp_probe(ip: str, port: int, timeout: float = 1.2) -> Optional[float]:
    start = time.perf_counter()
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return round(elapsed_ms, 2)
    except Exception:
        return None


async def _icmp_probe(ip: str, timeout_sec: int = 1) -> Optional[float]:
    start = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            "1",
            "-W",
            str(timeout_sec),
            ip,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec + 0.5)
        if proc.returncode == 0:
            text = stdout.decode("utf-8", errors="ignore")
            m = re.search(r"time=([\d.]+)\s*ms", text)
            if m:
                return round(float(m.group(1)), 2)
            return round((time.perf_counter() - start) * 1000.0, 2)
        return None
    except Exception:
        return None


async def probe_single_node(node: Dict[str, Any]) -> Dict[str, Any]:
    latency = await _tcp_probe(node["ip"], node["port"], timeout=1.2)
    if latency is None:
        latency = await _icmp_probe(node["ip"], timeout_sec=1)

    return {
        **node,
        "online": latency is not None,
        "latency_ms": latency,
    }


async def probe_all_nodes() -> List[Dict[str, Any]]:
    tasks = [probe_single_node(n) for n in HOMELAB_NODES]
    return list(await asyncio.gather(*tasks))
