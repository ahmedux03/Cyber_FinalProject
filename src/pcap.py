import json
from pathlib import Path
from logger import append_log
from config import EVIDENCE_DIR, REG

def capture_scapy(duration=10, iface=None, count=0, timeout=None):
    """
    Capture using scapy for 'duration' seconds (or count packets).
    Returns path + summary.
    """
    try:
        from scapy.all import sniff, wrpcap
    except Exception as e:
        raise RuntimeError("Scapy not available or requires privileges.") from e

    timeout = duration if timeout is None else timeout
    pkts = sniff(iface=iface, count=count, timeout=timeout)
    outpath = Path(EVIDENCE_DIR)/f"capture_{REG}.pcap"
    wrpcap(str(outpath), pkts)
    summary={}
    for p in pkts:
        try:
            proto = p.payload.name
            summary[proto] = summary.get(proto,0)+1
        except Exception:
            summary["unknown"] = summary.get("unknown",0)+1
    outjson = Path(EVIDENCE_DIR)/f"pcap_summary_{REG}.json"
    outjson.write_text(json.dumps({"count":len(pkts),"summary":summary}, indent=2))
    append_log({"module":"pcap","action":"capture","out":str(outpath),"summary_path":str(outjson)})
    return str(outpath), {"count": len(pkts), "summary": summary}

def analyze_pcap_file(pcap_file):
    try:
        import pyshark
    except Exception:
        raise RuntimeError("pyshark not available.")
    cap = pyshark.FileCapture(pcap_file, only_summaries=True)
    counts={}
    total=0
    for s in cap:
        proto = s.protocol
        counts[proto] = counts.get(proto,0)+1
        total+=1
    outjson = Path(EVIDENCE_DIR)/f"pcap_parsed_{REG}.json"
    outjson.write_text(json.dumps({"count":total,"protocols":counts}, indent=2))
    append_log({"module":"pcap","action":"analyze","in":str(pcap_file),"out":str(outjson)})
    return {"parsed":str(outjson)}
