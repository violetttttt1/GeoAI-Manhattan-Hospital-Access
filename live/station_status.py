#!/usr/bin/env python3
"""Per-snapshot station availability for the 10 study-area ADA stations.

For every raw snapshot in ~/geoai-live/raw/live_outages/outages_*.json that is not yet in
station_status_timeseries.csv, append one row per station:

  - an elevator is "out" if the snapshot has a row for it with isupcomingoutage == "N"
    (upcoming outages are ignored)
  - station_table.csv `access_paths` gives the structure: "PN: A+B | C+D; PS: ..."
    "+" = in series (all needed), "|" = alternative paths (any one is enough),
    each direction (PN/PS) must have at least one fully working path
  - a station with elevator_dependency starting with "no" (Harlem-148 St, no elevator needed,
    per MTA facilities data, not verified on site) gets available = 1 regardless of outages
  - a station with no access_paths and no such flag gets available = "" (cannot tell)
  - recovery_overdue: set to "estimated return time has passed" when the snapshot is later than the
    estimatedreturntoservice of an elevator that is out (latest estimate among its current rows).
    Informational only, availability is NOT changed. The feed's times have no timezone; they are
    read as New York local time (unverified).

Re-run any time; already-written snapshots are skipped, existing rows are never rewritten.
"""
import csv
import glob
import json
import re
from datetime import datetime, timezone
import os
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                                   # project root (this file lives in <ROOT>/live/)
# Folder written by fetch_live_outages.py; set GEOAI_LIVE_DIR to wherever you run the fetcher (default: ~/geoai-live)
LIVE_DIR = Path(os.environ.get("GEOAI_LIVE_DIR", str(Path.home() / "geoai-live")))
SNAP_DIR = LIVE_DIR / "raw" / "live_outages"
STATION_TABLE = ROOT / "data" / "clean" / "station_table.csv"
OUT = ROOT / "outputs" / "station_status_timeseries.csv"
NYC = ZoneInfo("America/New_York")
HEADER = ["snapshot_utc", "snapshot_nyc", "station_id", "gtfs_stop_id", "station_name", "routes",
          "elevator_dependency", "available", "blocked_directions", "elevators_out",
          "recovery_overdue", "overdue_elevators"]
OVERDUE = "estimated return time has passed"


def parse_paths(text):
    """'PN: A+B | C+D; PS: A+B' -> {'PN': [['A','B'],['C','D']], 'PS': [['A','B']]}"""
    out = {}
    for part in filter(None, (p.strip() for p in text.split(";"))):
        direction, paths = part.split(":", 1)
        out[direction.strip()] = [[e.strip() for e in p.split("+")] for p in paths.split("|")]
    return out


def load_stations():
    with open(STATION_TABLE, encoding="utf-8-sig") as f:
        return [{**r, "paths": parse_paths(r["access_paths"])} for r in csv.DictReader(f)]


def snapshot_time(path):
    s = re.search(r"outages_(\d{8}T\d{6})Z", path.name).group(1)
    return datetime.strptime(s, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


def done_snapshots():
    if not OUT.exists():
        return set()
    with open(OUT, newline="") as f:
        return {r["snapshot_utc"] for r in csv.DictReader(f)}


def current_outages(data):
    """{equipment: latest estimatedreturntoservice (naive datetime or None)} for isupcomingoutage == N"""
    out = {}
    for r in data:
        if r.get("isupcomingoutage") != "N":
            continue
        try:
            est = datetime.strptime(r["estimatedreturntoservice"], "%m/%d/%Y %I:%M:%S %p")
        except (KeyError, ValueError):
            est = None
        prev = out.get(r["equipment"], "unset")
        if prev == "unset" or (est and (prev is None or est > prev)):
            out[r["equipment"]] = est
    return out


def overdue_elevators(elevators_out, current, t):
    now_local = t.astimezone(NYC).replace(tzinfo=None)
    return [e for e in elevators_out if current.get(e) and now_local > current[e]]


def station_status(st, out_now):
    paths = st["paths"]
    members = sorted({e for ps in paths.values() for p in ps for e in p})
    elevators_out = [e for e in members if e in out_now]
    if st.get("elevator_dependency", "").startswith("no"):
        return 1, "", elevators_out
    if not paths:
        return "", "", elevators_out
    blocked = [d for d, ps in paths.items() if not any(all(e not in out_now for e in p) for p in ps)]
    return int(not blocked), ";".join(blocked), elevators_out


def main():
    stations = load_stations()
    seen = done_snapshots()
    new_file = not OUT.exists() or OUT.stat().st_size == 0
    added = 0
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(HEADER)
        for path in sorted(SNAP_DIR.glob("outages_*.json")):
            t = snapshot_time(path)
            key = t.isoformat(timespec="seconds")
            if key in seen:
                continue
            data = json.loads(path.read_bytes())
            current = current_outages(data)
            out_now = set(current)
            for st in stations:
                avail, blocked, el_out = station_status(st, out_now)
                late = overdue_elevators(el_out, current, t)
                w.writerow([key, t.astimezone(NYC).isoformat(timespec="seconds"),
                            st["station_id"], st["gtfs_stop_id"], st["station_name"], st["routes"],
                            st["elevator_dependency"], avail, blocked, ";".join(el_out),
                            OVERDUE if late else "", ";".join(late)])
            added += 1
    print(f"added {added} snapshot(s) -> {OUT.name}")


if __name__ == "__main__":
    main()
