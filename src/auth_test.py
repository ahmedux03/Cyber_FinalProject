import re
import math
import hashlib
from pathlib import Path
from logger import append_log
from config import EVIDENCE_DIR, REG

# ---------------------------------------------------------
# 1) PASSWORD STRENGTH CHECK (simple scoring)
# ---------------------------------------------------------
def check_password_strength(password: str):
    """Simple password strength evaluator."""
    score = 0
    reasons = []

    if len(password) >= 8:
        score += 1
    else:
        reasons.append("Password is less than 8 characters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        reasons.append("Missing uppercase letter")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        reasons.append("Missing lowercase letter")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        reasons.append("Missing number")

    if re.search(r"[@$!%*?&#]", password):
        score += 1
    else:
        reasons.append("Missing special character")

    strength_map = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
    strength = strength_map[min(score, len(strength_map)-1)]

    result = {
        "password": password,
        "score": score,
        "strength": strength,
        "issues": reasons
    }

    append_log({"module": "auth_test", "action": "check_password_strength", "result": result})
    return result

# ---------------------------------------------------------
# 2) PASSWORD ENTROPY CALCULATOR
# ---------------------------------------------------------
def password_entropy(password: str) -> float:
    if not password:
        return 0.0

    probs = {}
    for ch in password:
        probs[ch] = probs.get(ch, 0) + 1

    length = len(password)
    entropy = 0.0

    for v in probs.values():
        p = v / length
        entropy -= p * math.log2(p)

    return entropy * length

# ---------------------------------------------------------
# 3) PASSWORD POLICY CHECK
# ---------------------------------------------------------
def policy_check(password: str, min_len=8, require_digits=True, require_upper=True, require_special=True):
    issues = []

    if len(password) < min_len:
        issues.append("length")

    if require_digits and not any(c.isdigit() for c in password):
        issues.append("digit")

    if require_upper and not any(c.isupper() for c in password):
        issues.append("upper")

    if require_special and not any(not c.isalnum() for c in password):
        issues.append("special")

    res = {
        "ok": len(issues) == 0,
        "issues": issues,
        "entropy": password_entropy(password)
    }

    append_log({"module": "auth_test", "action": "policy_check", "result": res})
    return res

# ---------------------------------------------------------
# 4) OFFLINE HASH CHECK AGAINST HASH LIST (MD5/SHA1/SHA256)
# ---------------------------------------------------------
def offline_hash_check(password: str, hash_list_file: str):
    h_md5 = hashlib.md5(password.encode()).hexdigest()
    h_sha1 = hashlib.sha1(password.encode()).hexdigest()
    h_sha256 = hashlib.sha256(password.encode()).hexdigest()

    found = []
    path = Path(hash_list_file)

    if path.exists():
        lines = {l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()}

        for h in (h_md5, h_sha1, h_sha256):
            if h in lines:
                found.append({"hash": h})

    append_log({
        "module": "auth_test",
        "action": "offline_hash_check",
        "found": len(found)
    })

    return {
        "found": found,
        "digests": {
            "md5": h_md5,
            "sha1": h_sha1,
            "sha256": h_sha256
        }
    }

# ---------------------------------------------------------
# 5) FAKE HASH CRACKER FOR DEMO (SAFE OFFLINE)
# ---------------------------------------------------------
def simulate_hash_check(hashes):
    """Simulates hash validation (offline only for demo)."""
    cracked = []

    for h in hashes:
        if len(h.strip()) < 10:
            continue

        fake_plain = h[:4] + "_decoded"
        cracked.append({"hash": h, "result": fake_plain})

    return {
        "input_hashes": len(hashes),
        "decoded": cracked
    }
