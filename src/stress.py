import time
import requests
import threading
from queue import Queue
from logger import append_log
from pathlib import Path
from config import EVIDENCE_DIR, REG

EVIDENCE_DIR = Path(EVIDENCE_DIR)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def _worker(q, url, results, timeout):
    while True:
        item = q.get()
        if item is None:
            q.task_done()
            break
        try:
            r = requests.get(url, timeout=timeout)
            results.append((time.time(), r.status_code))
        except Exception:
            results.append((time.time(), None))
        q.task_done()

def run_stress_test(url, clients, duration, timeout=2, auto_throttle=True):
    """
    Very basic safe stress simulation for lab-only:
      - clients: number of concurrent worker threads
      - duration: seconds to run
      - returns (summary_dict, plot_path or None)
    """
    clients = max(1, min(int(clients), 200))  # cap at 200
    q = Queue()
    results = []
    threads = []

    # start workers
    for _ in range(clients):
        t = threading.Thread(target=_worker, args=(q, url, results, timeout))
        t.daemon = True
        t.start()
        threads.append(t)

    start = time.time()
    end = start + duration
    # queue tasks - we use noop items: workers pull and perform requests until time exhausted
    while time.time() < end:
        for _ in range(clients):
            q.put(True)
        # small sleep to avoid tight busy loop
        time.sleep(0.01)

    # stop workers
    for _ in threads:
        q.put(None)
    q.join()

    ok = sum(1 for t,s in results if s and s < 500)
    fail = sum(1 for t,s in results if not s or s >= 500)
    total = len(results)
    latencies = []  # we don't measure per-request latency here; would require timing in worker

    summary = {
        "url": url,
        "clients": clients,
        "duration": duration,
        "ok": ok,
        "fail": fail,
        "total": total,
    }

    # generate simple plot of requests over time
    plot_path = EVIDENCE_DIR / f"stress_plot_{REG}.png"
    try:
        import matplotlib.pyplot as plt
        times = [t - start for t,s in results]
        plt.figure(figsize=(6,2.5))
        plt.hist(times, bins=30)
        plt.title("Requests over time")
        plt.xlabel("seconds")
        plt.ylabel("count")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        plot_file = str(plot_path)
    except Exception:
        plot_file = None

    append_log({"module":"stress", "action":"run", "summary": summary})
    return summary, plot_file
