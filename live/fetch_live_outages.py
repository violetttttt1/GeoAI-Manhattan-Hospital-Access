#!/usr/bin/env python3
"""Poll the MTA elevator/escalator current-outages feed every 10 minutes.

Per successful poll:
  - raw response bytes saved untouched to raw/live_outages/outages_<UTC time>.json
  - one row appended to live_log.csv (UTC time, success, row count, error, NYC time,
    device-level counts)
Failures are logged (csv + stderr) and retried after 60 s.
The equipment list is fetched once (skipped if an equipment_*.json already exists).

Optional key: export MTA_API_KEY=... (sent as x-api-key). Not needed so far.
A 401/403 stops the script instead of retrying.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/"
OUTAGES_URL = BASE + "nyct%2Fnyct_ene.json"
EQUIPMENT_URL = BASE + "nyct%2Fnyct_ene_equipments.json"

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw" / "live_outages"
LOG_CSV = ROOT / "live_log.csv"
INTERVAL = 600
RETRY_DELAY = 60
TIMEOUT = 30


NYC = ZoneInfo("America/New_York")
HEADER = ["fetched_at_utc", "success", "outage_count", "error",
          "fetched_at_nyc", "current_outage_devices", "current_nonmaint_devices",
          "distinct_devices"]


def outage_stats(data):
    """Device-level counts (deduplicated by `equipment`).

    current  = devices with at least one row isupcomingoutage == "N"
    nonmaint = devices with at least one such current row also ismaintenanceoutage == "N"
    distinct = all devices in the list (current + upcoming)
    """
    current = {r["equipment"] for r in data if r.get("isupcomingoutage") == "N"}
    nonmaint = {r["equipment"] for r in data
                if r.get("isupcomingoutage") == "N" and r.get("ismaintenanceoutage") == "N"}
    distinct = {r["equipment"] for r in data}
    return len(current), len(nonmaint), len(distinct)


class AuthRequired(Exception):
    pass


def now():
    return datetime.now(timezone.utc)


def stamp(t):
    return t.strftime("%Y%m%dT%H%M%SZ")


def fetch(url):
    headers = {"User-Agent": "geoai-live-outages/1.0"}
    key = os.environ.get("MTA_API_KEY")
    if key:
        headers["x-api-key"] = key
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise AuthRequired(f"HTTP {e.code} from {url}")
        raise


def save_raw(prefix, t, body):
    """Write bytes verbatim; never overwrite an existing file."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    while True:
        suffix = f"_{n}" if n else ""
        path = RAW_DIR / f"{prefix}_{stamp(t)}{suffix}.json"
        try:
            with open(path, "xb") as f:
                f.write(body)
            return path
        except FileExistsError:
            n += 1


def log_row(t, ok, count, error, stats=None):
    new = not LOG_CSV.exists() or LOG_CSV.stat().st_size == 0
    with open(LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow([t.isoformat(timespec="seconds"), int(ok), count if ok else "", error,
                    t.astimezone(NYC).isoformat(timespec="seconds"),
                    *(stats if ok and stats else ["", "", ""])])


def poll_outages():
    t = now()
    try:
        body = fetch(OUTAGES_URL)
        save_raw("outages", t, body)
        data = json.loads(body)
        if not isinstance(data, list):
            raise ValueError(f"expected JSON list, got {type(data).__name__}")
    except AuthRequired:
        raise
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        log_row(t, False, None, err)
        print(f"[{t.isoformat(timespec='seconds')}] FAIL {err}", file=sys.stderr, flush=True)
        return False
    stats = outage_stats(data)
    log_row(t, True, len(data), "", stats)
    print(f"[{t.isoformat(timespec='seconds')}] ok, {len(data)} rows, "
          f"{stats[0]} current / {stats[1]} non-maint / {stats[2]} distinct devices", flush=True)
    return True


def fetch_equipment_once():
    if any(RAW_DIR.glob("equipment_*.json")):
        return
    t = now()
    try:
        path = save_raw("equipment", t, fetch(EQUIPMENT_URL))
        print(f"[{t.isoformat(timespec='seconds')}] equipment saved: {path.name}", flush=True)
    except AuthRequired:
        raise
    except Exception as e:
        print(f"[{t.isoformat(timespec='seconds')}] equipment FAIL {type(e).__name__}: {e}",
              file=sys.stderr, flush=True)


def main():
    try:
        fetch_equipment_once()
        while True:
            ok = poll_outages()
            time.sleep(INTERVAL if ok else RETRY_DELAY)
    except AuthRequired as e:
        t = now()
        log_row(t, False, None, f"AUTH REQUIRED: {e}")
        print(f"STOPPED: {e}. The endpoint now needs a key; set MTA_API_KEY and restart.",
              file=sys.stderr, flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
