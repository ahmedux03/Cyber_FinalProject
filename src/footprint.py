import asyncio, aiohttp, json, socket
from pathlib import Path
from logger import append_log
from config import EVIDENCE_DIR, REG

COMMON_PATHS = ["admin","login","dashboard","api",".git","robots.txt","sitemap.xml"]
COMMON_SUBS = ["dev","test","staging","api","www","app"]

async def check_paths(base_url, paths=COMMON_PATHS, rate_limit=5):
    results=[]
    sem = asyncio.Semaphore(rate_limit)
    async with aiohttp.ClientSession() as session:
        async def worker(p):
            async with sem:
                try:
                    url = f"{base_url.rstrip('/')}/{p}"
                    async with session.get(url, timeout=5) as r:
                        code = r.status
                        results.append({"path":p,"url":url,"status":code})
                except Exception:
                    results.append({"path":p,"url":url,"status":"err"})
        await asyncio.gather(*(worker(p) for p in paths))
    out = Path(EVIDENCE_DIR)/f"footprint_paths_{REG}.json"
    out.write_text(json.dumps(results, indent=2))
    append_log({"module":"footprint","action":"paths","base":base_url,"out":str(out)})
    return results

async def probe_subdomains(domain, subs=COMMON_SUBS, rate_limit=5):
    results=[]
    sem = asyncio.Semaphore(rate_limit)
    async def worker(sname):
        async with sem:
            host = f"{sname}.{domain}"
            try:
                socket.gethostbyname(host)
                results.append({"sub":sname,"host":host,"resolved":True})
            except Exception:
                results.append({"sub":sname,"host":host,"resolved":False})
    await asyncio.gather(*(worker(s) for s in subs))
    out = Path(EVIDENCE_DIR)/f"footprint_subs_{REG}.json"
    out.write_text(json.dumps(results, indent=2))
    append_log({"module":"footprint","action":"subs","domain":domain,"out":str(out)})
    return results

# sync wrappers for Streamlit UI (call from main thread)
def run_directory_finder(base_url, paths=COMMON_PATHS, rate_limit=5):
    return asyncio.run(check_paths(base_url, paths=paths, rate_limit=rate_limit))

def run_subdomain_finder(domain, subs=COMMON_SUBS, rate_limit=5):
    return asyncio.run(probe_subdomains(domain, subs=subs, rate_limit=rate_limit))
