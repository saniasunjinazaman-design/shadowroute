#!/usr/bin/env python3
"""Monitor the selected BIRD route for the configured lab prefix."""
import argparse
import datetime
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import time

PROJECT = Path(__file__).resolve().parents[1]
LOG = PROJECT / "logs" / "alerts.jsonl"
BASELINE = {"10.150.0.0/24": 150}
ROUTER = "as152brd-router0-10.152.0.254"


def selected_path(output, prefix):
    if "Table master4:" not in output:
        raise ValueError("Expected master4 table is absent")
    records, current_prefix, record, in_table = [], None, None, False
    for line in output.splitlines():
        if line.startswith("Table "):
            in_table = line.strip() == "Table master4:"
            current_prefix = record = None
            continue
        if not in_table:
            continue
        match = re.match(r"^(\d+\.\d+\.\d+\.\d+/\d+)\s+", line)
        if match:
            current_prefix = str(ipaddress.ip_network(match.group(1)))
        if "[" in line and re.search(r"\]\s+\*?\s*\(\d+\)", line):
            record = {"prefix": current_prefix, "selected": bool(re.search(r"\]\s+\*\s*\(", line)), "path": None}
            records.append(record)
        elif record is not None and "BGP.as_path:" in line:
            value = line.split("BGP.as_path:", 1)[1].strip()
            if not re.fullmatch(r"\d+(?:\s+\d+)*", value):
                raise ValueError(f"Unsupported AS path: {value!r}")
            record["path"] = [int(n) for n in value.split()]
    selected = [r for r in records if r["prefix"] == prefix and r["selected"]]
    if not selected:
        if any(r["prefix"] == prefix for r in records):
            raise ValueError("Prefix exists but no selected route was parsed")
        return None
    if len(selected) != 1 or not selected[0]["path"]:
        raise ValueError("Selected route has missing or ambiguous BGP AS path")
    return selected[0]["path"]


def observe(prefix):
    result = subprocess.run(["docker", "exec", ROUTER, "birdc", "show", "route", "all"],
                            capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Docker/BIRD command failed")
    return selected_path(result.stdout, prefix)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Read one route and exit")
    args = parser.parse_args()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    previous = None
    print(f"Monitoring {ROUTER}; interval=1s; log={LOG}", flush=True)
    try:
        while True:
            started = time.monotonic()
            prefix, expected = next(iter(BASELINE.items()))
            event = {"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     "router": ROUTER, "prefix": prefix, "expected_origin": expected,
                     "observed_origin": None, "as_path": []}
            try:
                path = observe(prefix)
                if path is None:
                    event["status"] = "ROUTE_MISSING"
                else:
                    event["as_path"] = path
                    event["observed_origin"] = path[-1]
                    event["status"] = "NORMAL" if path[-1] == expected else "HIJACK_ALERT"
            except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
                event["status"] = "MONITOR_ERROR"
                event["error"] = str(exc)
            event["observed_at_unix"] = time.time()
            signature = (event["status"], tuple(event["as_path"]), event.get("error"))
            if signature != previous:
                message = json.dumps(event)
                with LOG.open("a", encoding="utf-8") as handle:
                    handle.write(message + "\n")
                print(message, flush=True)
                previous = signature
            if args.once:
                break
            time.sleep(max(0, 1.0 - (time.monotonic() - started)))
    except KeyboardInterrupt:
        print("\nMonitor stopped.", flush=True)


if __name__ == "__main__":
    main()
