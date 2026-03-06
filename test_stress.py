#!/usr/bin/env python3
"""
Stress test para WA-BOT (/webhook + endpoints de soporte).
Simula N usuarios concurrentes enviando mensajes y mide latencia, errores y cuelgues.

Uso:
    python3 test_stress.py [--host http://localhost:8088] [--users 50] [--msgs 5]

Fases:
    1  Warm-up caliente   (5 users, secuencial)
    2  Carga liviana      (20 users, 3 msgs c/u)
    3  Carga pesada       (50 users, 5 msgs c/u)
    4  Pico de spike      (100 usuarios simultáneos en un solo burst)
    5  Resistencia        (20 users × 30 msgs durante ~1 min)
"""

import asyncio
import argparse
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

# ──────────────────────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────────────────────
DEFAULT_HOST    = "http://localhost:8088"
WEBHOOK_PATH    = "/webhook"
HEALTH_PATH     = "/health"
STATUS_PATH     = "/status"

# Timeout por request: si tarda más se cuenta como "cuelgue"
REQUEST_TIMEOUT = 15.0   # segundos
HANG_THRESHOLD  = 8.0    # segundos — a partir de acá se considera cuelgue

# Secuencias de mensajes realistas para simular navegación de menú
MENU_SEQUENCES = [
    ["1"],                          # Turnos → info
    ["1", "1"],                     # Turnos → Clínica Médica
    ["1", "3"],                     # Turnos → Cardiología
    ["1", "5"],                     # Turnos → Odontología
    ["2"],                          # Asuntos laborales
    ["3"],                          # Farmacia
    ["4"],                          # Afiliaciones
    ["6"],                          # Bocas de expendio
    ["6", "1"],                     # Bocas → Recreo Sur
    ["6", "3"],                     # Bocas → Ver ambas
    ["7"],                          # Compra orden
    ["7", "1"],                     # Compra → link directo
    ["0"],                          # Volver al menú
    ["99"],                         # Handoff → operador
    ["9"],                          # Opción inválida
    ["1", "0", "3"],                # Turnos, volver, Farmacia
    ["hola"],                       # Texto libre
    ["2", "0"],                     # Asuntos → volver
]

# ──────────────────────────────────────────────────────────────
#  RESULTADO ACUMULADO
# ──────────────────────────────────────────────────────────────
@dataclass
class Stats:
    phase: str
    latencies: list[float] = field(default_factory=list)
    errors: int = 0
    timeouts: int = 0
    hangs: int = 0
    ok: int = 0

    def record(self, latency: float, error: bool, timed_out: bool):
        if timed_out:
            self.timeouts += 1
            self.errors += 1
            return
        if error:
            self.errors += 1
        else:
            self.latencies.append(latency)
            self.ok += 1
            if latency >= HANG_THRESHOLD:
                self.hangs += 1

    def total(self) -> int:
        return self.ok + self.errors

    def pct(self, p: int) -> Optional[float]:
        if not self.latencies:
            return None
        s = sorted(self.latencies)
        idx = int(len(s) * p / 100)
        return s[min(idx, len(s) - 1)]

    def report(self):
        total = self.total()
        err_pct = (self.errors / total * 100) if total else 0
        print(f"\n  {'─'*52}")
        print(f"  📊 Fase: {self.phase}")
        print(f"  {'─'*52}")
        print(f"  Requests OK:      {self.ok:>6}  /  {total} ({100 - err_pct:.1f}%)")
        print(f"  Errores:          {self.errors:>6}  ({err_pct:.1f}%)")
        print(f"  Timeouts (>{REQUEST_TIMEOUT:.0f}s):  {self.timeouts:>6}")
        print(f"  Posibles cuelgues (>{HANG_THRESHOLD:.0f}s): {self.hangs:>4}")
        if self.latencies:
            print(f"  Latencia  p50:    {self.pct(50)*1000:>7.0f} ms")
            print(f"  Latencia  p90:    {self.pct(90)*1000:>7.0f} ms")
            print(f"  Latencia  p95:    {self.pct(95)*1000:>7.0f} ms")
            print(f"  Latencia  p99:    {self.pct(99)*1000:>7.0f} ms")
            print(f"  Latencia  médiana:{statistics.median(self.latencies)*1000:>6.0f} ms")
            print(f"  Latencia  máx:    {max(self.latencies)*1000:>7.0f} ms")
            print(f"  Latencia  mín:    {min(self.latencies)*1000:>7.0f} ms")
        print()

        # Diagnóstico
        if self.timeouts > 0:
            print(f"  ⚠️  {self.timeouts} requests se colgaron (timeout {REQUEST_TIMEOUT}s)")
        if self.hangs > 0:
            print(f"  🐌  {self.hangs} requests lentos (>{HANG_THRESHOLD}s) — posible contención de DB o WAHA")
        if err_pct > 5:
            print(f"  ❌  Tasa de error elevada ({err_pct:.1f}%) — revisar logs del contenedor")
        if not self.timeouts and not self.hangs and err_pct < 2:
            print(f"  ✅  Fase aprobada sin problemas detectados")


# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────
def make_webhook_payload(chat_id: str, text: str) -> dict:
    """Payload estilo WAHA (formato real del webhook)."""
    return {
        "id": f"msg_{int(time.time()*1000)}_{random.randint(1000,9999)}",
        "payload": {
            "from": chat_id,
            "chatId": chat_id,
            "body": text,
            "fromMe": False,
        }
    }


async def hit_webhook(
    client: httpx.AsyncClient,
    host: str,
    chat_id: str,
    text: str,
    stats: Stats,
    delay: float = 0.0,
):
    if delay > 0:
        await asyncio.sleep(delay)
    t0 = time.perf_counter()
    timed_out = False
    error = False
    try:
        r = await client.post(
            f"{host}{WEBHOOK_PATH}",
            json=make_webhook_payload(chat_id, text),
            timeout=REQUEST_TIMEOUT,
        )
        if r.status_code >= 500:
            error = True
    except httpx.TimeoutException:
        timed_out = True
    except Exception:
        error = True
    finally:
        latency = time.perf_counter() - t0
        stats.record(latency, error, timed_out)


async def check_health(host: str) -> tuple[bool, float]:
    """Verificar que el servidor responde."""
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            t0 = time.perf_counter()
            r = await c.get(f"{host}{HEALTH_PATH}")
            lat = time.perf_counter() - t0
            return r.status_code == 200, lat
    except Exception:
        return False, 0.0


async def check_status(host: str) -> tuple[bool, float]:
    """Llamar /status y medir latencia."""
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            t0 = time.perf_counter()
            r = await c.get(f"{host}{STATUS_PATH}")
            lat = time.perf_counter() - t0
            return r.status_code == 200, lat
    except Exception:
        return False, 0.0


def fake_phone(n: int) -> str:
    """Genera un chat_id realista."""
    return f"549341{5000000 + n}@c.us"


# ──────────────────────────────────────────────────────────────
#  FASES DE TEST
# ──────────────────────────────────────────────────────────────
async def phase_warmup(host: str) -> Stats:
    """Fase 1: 5 usuarios, mensajes secuenciales para calentar."""
    stats = Stats(phase="1 · Warm-up (5 users × 2 msgs, secuencial)")
    print("  → enviando mensajes warmup...")
    async with httpx.AsyncClient() as client:
        for i in range(5):
            chat = fake_phone(i)
            for text in ["hola", "1"]:
                await hit_webhook(client, host, chat, text, stats)
    return stats


async def phase_light(host: str, n_users: int = 20, n_msgs: int = 3) -> Stats:
    """Fase 2: N usuarios concurrentes, cada uno envía M msgs con delay pequeño."""
    stats = Stats(phase=f"2 · Carga liviana ({n_users} users × {n_msgs} msgs, concurrente)")
    print(f"  → {n_users} × {n_msgs} msgs concurrentes...")

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=200)) as client:
        tasks = []
        for i in range(n_users):
            chat = fake_phone(100 + i)
            seq = random.choice(MENU_SEQUENCES)
            for j, text in enumerate(seq[:n_msgs] if len(seq) >= n_msgs else seq):
                delay = random.uniform(0, 0.5)  # pequeño jitter
                tasks.append(hit_webhook(client, host, chat, text, stats, delay))
        await asyncio.gather(*tasks)
    return stats


async def phase_heavy(host: str, n_users: int = 50, n_msgs: int = 5) -> Stats:
    """Fase 3: 50 usuarios, 5 mensajes c/u, todos al mismo tiempo."""
    stats = Stats(phase=f"3 · Carga pesada ({n_users} users × {n_msgs} msgs, burst)")
    print(f"  → {n_users} × {n_msgs} msgs en burst...")

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=300)) as client:
        tasks = []
        for i in range(n_users):
            chat = fake_phone(1000 + i)
            seq = random.choice(MENU_SEQUENCES)
            msgs = (seq * ((n_msgs // len(seq)) + 1))[:n_msgs]
            for text in msgs:
                tasks.append(hit_webhook(client, host, chat, text, stats))
        await asyncio.gather(*tasks)
    return stats


async def phase_spike(host: str, n_simultaneous: int = 100) -> Stats:
    """Fase 4: Spike — N requests exactamente al mismo instante."""
    stats = Stats(phase=f"4 · Spike ({n_simultaneous} requests simultáneos)")
    print(f"  → {n_simultaneous} requests al mismo instante...")

    # Usar un event para disparar todos juntos
    ready = asyncio.Event()

    async def fire_one(client, idx):
        await ready.wait()
        chat = fake_phone(5000 + idx)
        text = random.choice(["1", "2", "3", "hola", "0", "99"])
        await hit_webhook(client, host, chat, text, stats)

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=500)) as client:
        tasks = [asyncio.create_task(fire_one(client, i)) for i in range(n_simultaneous)]
        await asyncio.sleep(0.05)  # dar tiempo para que todos queden esperando
        ready.set()
        await asyncio.gather(*tasks)
    return stats


async def phase_endurance(host: str, n_users: int = 20, duration_sec: int = 60) -> Stats:
    """Fase 5: Resistencia — N usuarios enviando msgs durante D segundos."""
    stats = Stats(phase=f"5 · Resistencia ({n_users} users × {duration_sec}s)")
    print(f"  → {n_users} usuarios activos durante {duration_sec}s...")

    end_time = time.perf_counter() + duration_sec
    interval_report = 10  # cada 10s mostrar progreso

    async def user_loop(client, user_idx):
        chat = fake_phone(9000 + user_idx)
        seq = MENU_SEQUENCES[user_idx % len(MENU_SEQUENCES)] * 20
        for text in seq:
            if time.perf_counter() >= end_time:
                break
            await hit_webhook(client, host, chat, text, stats)
            await asyncio.sleep(random.uniform(0.3, 1.5))

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
        # Spawn all user loops and a progress reporter
        async def reporter():
            t0 = time.perf_counter()
            while time.perf_counter() < end_time:
                await asyncio.sleep(interval_report)
                elapsed = time.perf_counter() - t0
                print(f"    [{elapsed:.0f}s] OK={stats.ok} err={stats.errors} timeouts={stats.timeouts}")

        tasks = [asyncio.create_task(user_loop(client, i)) for i in range(n_users)]
        tasks.append(asyncio.create_task(reporter()))
        await asyncio.gather(*tasks, return_exceptions=True)

    return stats


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="Stress test para WA-BOT")
    parser.add_argument("--host", default=DEFAULT_HOST, help="URL base del bot")
    parser.add_argument("--users", type=int, default=50, help="Usuarios en fase pesada")
    parser.add_argument("--spike", type=int, default=100, help="Requests en spike")
    parser.add_argument("--duration", type=int, default=60, help="Segundos de resistencia")
    parser.add_argument("--skip-endurance", action="store_true", help="Saltear fase de resistencia")
    parser.add_argument("--only", type=str, default=None,
                        help="Correr solo una fase: warmup|light|heavy|spike|endurance")
    args = parser.parse_args()

    host = args.host.rstrip("/")

    print()
    print("=" * 60)
    print("  🧪 WA-BOT STRESS TEST")
    print(f"  Host:    {host}")
    print(f"  Timeout: {REQUEST_TIMEOUT}s por request")
    print(f"  Hang:    >{HANG_THRESHOLD}s")
    print("=" * 60)

    # Pre-check
    print("\n📡 Verificando servidores...")
    ok_h, lat_h = await check_health(host)
    ok_s, lat_s = await check_status(host)
    if not ok_h:
        print(f"  ❌ El servidor no responde en {host}{HEALTH_PATH}")
        print("  Verificá que el contenedor wa-bot está corriendo: docker ps")
        sys.exit(1)
    print(f"  ✅ /health   →  {lat_h*1000:.0f} ms")
    print(f"  {'✅' if ok_s else '⚠️'} /status   →  {lat_s*1000:.0f} ms {'(error)' if not ok_s else ''}")

    all_stats = []

    def should_run(name: str) -> bool:
        return args.only is None or args.only.lower() == name

    # ── Fase 1 warm-up ───────────────────────────────────────
    if should_run("warmup"):
        print("\n🔥 Fase 1: Warm-up")
        s = await phase_warmup(host)
        s.report(); all_stats.append(s)

    # ── Fase 2 liviana ───────────────────────────────────────
    if should_run("light"):
        print("\n🟡 Fase 2: Carga liviana")
        s = await phase_light(host, n_users=20, n_msgs=3)
        s.report(); all_stats.append(s)

    # ── Fase 3 pesada ────────────────────────────────────────
    if should_run("heavy"):
        print("\n🔴 Fase 3: Carga pesada")
        s = await phase_heavy(host, n_users=args.users, n_msgs=5)
        s.report(); all_stats.append(s)

    # ── Fase 4 spike ─────────────────────────────────────────
    if should_run("spike"):
        print("\n⚡ Fase 4: Spike")
        s = await phase_spike(host, n_simultaneous=args.spike)
        s.report(); all_stats.append(s)

    # ── Fase 5 resistencia ───────────────────────────────────
    if should_run("endurance") and not args.skip_endurance:
        print(f"\n⏱️  Fase 5: Resistencia ({args.duration}s) — Ctrl+C para cancelar")
        s = await phase_endurance(host, n_users=20, duration_sec=args.duration)
        s.report(); all_stats.append(s)

    # ── Resumen global ───────────────────────────────────────
    if len(all_stats) > 1:
        total_ok      = sum(s.ok for s in all_stats)
        total_err     = sum(s.errors for s in all_stats)
        total_timeout = sum(s.timeouts for s in all_stats)
        total_hang    = sum(s.hangs for s in all_stats)
        all_lat       = [l for s in all_stats for l in s.latencies]

        print("=" * 60)
        print("  📋 RESUMEN GLOBAL")
        print("=" * 60)
        print(f"  Requests OK:       {total_ok}")
        print(f"  Errores:           {total_err}")
        print(f"  Timeouts:          {total_timeout}")
        print(f"  Cuelgues (>{HANG_THRESHOLD:.0f}s):  {total_hang}")
        if all_lat:
            s_all = sorted(all_lat)
            def pX(p): return s_all[min(int(len(s_all)*p/100), len(s_all)-1)]
            print(f"  Latencia p50:      {pX(50)*1000:.0f} ms")
            print(f"  Latencia p95:      {pX(95)*1000:.0f} ms")
            print(f"  Latencia p99:      {pX(99)*1000:.0f} ms")
            print(f"  Latencia máx:      {max(all_lat)*1000:.0f} ms")
        print()

        if total_timeout > 0 or total_hang > 5:
            print("  🚨 DIAGNÓSTICO:")
            if total_timeout > 0:
                print(f"     - {total_timeout} timeouts → el servidor se colgó bajo carga")
                print(f"       Verificar: docker logs wa-bot --tail 100")
                print(f"       Posible causa: SQLite write lock, WAHA bloqueado, o uvicorn sin workers")
            if total_hang > 5:
                print(f"     - {total_hang} requests lentos → contención en DB o llamadas a WAHA")
                print(f"       Revisar: pool de conexiones SQLite, timeouts de _send_wha()")
        else:
            print("  ✅ El servidor aguantó la carga sin cuelgues graves.")

    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Test interrumpido por usuario")
