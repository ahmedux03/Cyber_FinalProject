import socket
import concurrent.futures
import time
from logger import append_log

def scan_port(target, port, timeout=1, banner_grab=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            start = time.time()
            result = s.connect_ex((target, port))
            end = time.time()
            entry = {
                "port": port,
                "status": "open" if result == 0 else "closed",
                "latency_ms": round((end - start) * 1000, 2)
            }
            if result == 0 and banner_grab:
                try:
                    s.sendall(b"\r\n")
                    s.settimeout(0.5)
                    data = s.recv(1024)
                    entry["banner"] = data.decode(errors="ignore").strip()
                except Exception:
                    entry["banner"] = None
            return entry
    except Exception as e:
        return {"port": port, "status": "error", "error": str(e)}

def run_scan(target, ports, max_workers=50, banner_grab=False):
    append_log({"module": "scanner", "target": target, "ports": ports})
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(scan_port, target, p, 1, banner_grab) for p in ports]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    return {
        "target": target,
        "results": sorted(results, key=lambda x: x.get("port", 0)),
        "total_open": sum(1 for r in results if r.get("status") == "open")
    }

# alias for compatibility
sync_port_scan = run_scan
