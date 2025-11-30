import json, hashlib, os, datetime
from pathlib import Path
from config import EVIDENCE_DIR, REG

Path(EVIDENCE_DIR).mkdir(parents=True, exist_ok=True)
LOGFILE = Path(EVIDENCE_DIR) / f"toolkit_log_{REG}.log"
SHAFILE = Path(EVIDENCE_DIR) / f"toolkit_log_{REG}.sha256"

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def append_log(entry: dict):
    entry_ts = datetime.datetime.utcnow().isoformat()+"Z"
    entry_record = {"ts": entry_ts, **entry}
    s = json.dumps(entry_record, ensure_ascii=False)
    # ensure logfile exists
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(s + "\n")
    # update sha file atomically
    h = sha256_of_file(LOGFILE)
    tmp = SHAFILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(h + "\n")
    os.replace(tmp, SHAFILE)
    return entry_record

def read_log_tail(n=200):
    """Return last n lines (as a single string) from the logfile for UI tail view."""
    if not LOGFILE.exists():
        return "No log file yet."
    with open(LOGFILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    tail = "".join(lines[-n:])
    return tail
