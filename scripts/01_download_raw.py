"""NEW script (not the one actually used at the time: the data were first downloaded with curl commands during the analysis).
Downloads every raw dataset the project uses into raw/ (or --dest). Standard library only.

    python scripts/01_download_raw.py --list                      # show datasets, sizes, targets
    python scripts/01_download_raw.py --check                     # only check that every URL answers (no download)
    python scripts/01_download_raw.py --only mta_stations,elevator_inventory
    python scripts/01_download_raw.py                             # everything (about 800 MB, mostly bus GTFS)

Things a re-download CANNOT reproduce exactly (the sources change over time):
  * live_equipment   - snapshots of MTA live feeds (equipment list + current outages) taken on 2026-11-11
  * mta_entrances, mta_amenities, mta_stations, elevator_availability, elevator_inventory - rolling open-data tables, updated by the MTA
  * gtfs, gtfs_bus   - the MTA replaces the feed files when a new schedule is published (the bus feeds used here were valid 2026-10-12 .. 2027-01-02)
  * mta_official_list - the mta.info accessible-stations page (version dated 2026-10-12)
Static or slow-moving sources (NYC borough/tract boundaries, street centerline, ACS 2020-2024 file, ramp tables) should come back (nearly) identical.
"""
import argparse, os, sys, time, urllib.request, urllib.error, zipfile, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("GEOAI_ROOT", str(HERE.parent))).resolve()
UA = {"User-Agent": "geoai-download/1.0 (research project)"}
NYC, NYS = "data.cityofnewyork.us", "data.ny.gov"
csv = lambda dom, ident: f"https://{dom}/api/views/{ident}/rows.csv?accessType=DOWNLOAD"
S3 = "https://rrgtfsfeeds.s3.amazonaws.com/"
SODA = "https://data.cityofnewyork.us/resource/inkn-q76z.json?$select=the_geom,physicalid,rw_type,status,boroughcode,full_street_name,from_level_code,to_level_code&$order=physicalid&$limit=40000&$offset="
MTA_API = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/"
# name -> (description, approx MB, [(url, target path relative to ROOT)], [zip files to extract (relative to ROOT)])
DATA = {
 "elevator_availability": ("MTA NYCT subway elevator/escalator availability (data.ny.gov rc78-7x78)", 18, [(csv(NYS, "rc78-7x78"), "raw/elevator_availability/elevator_availability.csv")], []),
 "elevator_inventory": ("MTA subway elevator/escalator asset inventory (94fv-bak7)", 0.5, [(csv(NYS, "94fv-bak7"), "raw/elevator_inventory/elevator_inventory.csv")], []),
 "mta_stations": ("MTA subway stations (39hk-dx4f)", 0.1, [(csv(NYS, "39hk-dx4f"), "raw/mta_stations/mta_stations.csv")], []),
 "gtfs": ("MTA subway GTFS (static)", 6, [(S3 + "gtfs_subway.zip", "raw/gtfs/gtfs_subway.zip")], ["raw/gtfs/gtfs_subway.zip=raw/gtfs/unz"]),
 "ped_ramp_locations": ("DOT Pedestrian Ramp Locations (ufzp-rrqu)", 42, [(csv(NYC, "ufzp-rrqu"), "raw/ped_ramp_locations/ped_ramp_locations.csv")], []),
 "ramp_program_progress": ("DOT Pedestrian Ramp - Program Progress (e7gc-ub6z)", 23, [(csv(NYC, "e7gc-ub6z"), "raw/ramp_program_progress/ramp_program_progress.csv")], []),
 "mbpo_ramp_report": ("MBPO Pedestrian Ramp Report (8kic-uvpz)", 0.03, [(csv(NYC, "8kic-uvpz"), "raw/mbpo_ramp_report/mbpo_ramp_report.csv")], []),
 "borough_boundaries": ("NYC borough boundaries, clipped to shoreline (gthc-hcne), GeoJSON", 3, [(f"https://{NYC}/api/geospatial/gthc-hcne?method=export&format=GeoJSON", "raw/borough_boundaries/boroughs.geojson")], []),
 "live_equipment": ("MTA live feeds: equipment list and current outages (no key needed at the time of writing)", 0.8,
                    [(MTA_API + "nyct%2Fnyct_ene_equipments.json", "raw/live_equipment/equipments.json"), (MTA_API + "nyct%2Fnyct_ene.json", "raw/live_equipment/outages.json")], []),
 "mta_entrances": ("MTA subway entrances and exits (i9wp-a4ja)", 0.3, [(csv(NYS, "i9wp-a4ja"), "raw/mta_entrances/entrances.csv")], []),
 "mta_amenities": ("MTA subway station amenities (6yjv-fk7g)", 10, [(csv(NYS, "6yjv-fk7g"), "raw/mta_amenities/amenities.csv")], []),
 "gtfs_bus": ("MTA bus GTFS: Manhattan, Bronx, Brooklyn, Queens, Staten Island, MTA Bus Company", 560,
              [(S3 + f"{n}.zip", f"raw/gtfs_bus/{n}.zip") for n in ("gtfs_m", "gtfs_bx", "gtfs_busco", "gtfs_b", "gtfs_q", "gtfs_si")],
              [f"raw/gtfs_bus/{n}.zip=raw/gtfs_bus/{n}" for n in ("gtfs_m", "gtfs_bx", "gtfs_busco", "gtfs_b", "gtfs_q", "gtfs_si")]),
 "nyc_centerline": ("NYC Street Centerline (CSCL, inkn-q76z), 4 JSON pages of 40,000 rows", 40, [(SODA + str(o), f"raw/nyc_centerline/cscl_{o}.json") for o in (0, 40000, 80000, 120000)], []),
 "census": ("ACS 2020-2024 5-year table B18105 (summary file, 74 MB) + NYC 2020 census tracts clipped to shoreline (63ge-mke6)", 82,
            [("https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b18105.dat", "raw/census/acsdt5y2024-b18105.dat"),
             (f"https://{NYC}/api/geospatial/63ge-mke6?method=export&format=GeoJSON", "raw/census/nyc_tracts_2020.geojson")], []),
 "mta_official_list": ("mta.info accessible-stations page (parsed by 13_ada_official_list_parse.py); saved to data/cache, not raw/", 0.2,
                       [("https://www.mta.info/accessibility/stations", "data/cache/mta_acc.html")], []),
}


def fetch(url, dest, tries=3):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            tmp.replace(dest)
            return dest.stat().st_size
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"download failed: {url}: {last}")


def check(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            return f"HTTP {r.status}, content-length {r.headers.get('Content-Length', '?')}"
    except Exception as e:  # report, do not raise
        return f"FAILED: {e}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", help="comma-separated dataset names")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true", help="only test that the URLs answer")
    ap.add_argument("--force", action="store_true", help="download even if the target file exists")
    a = ap.parse_args()
    names = [n.strip() for n in a.only.split(",")] if a.only else list(DATA)
    bad = [n for n in names if n not in DATA]
    if bad:
        sys.exit(f"unknown dataset(s): {bad}; use --list")
    if a.list:
        for n in names:
            d = DATA[n]
            print(f"{n:24s} ~{d[1]:>6} MB  {d[0]}")
            for u, p in d[2]:
                print(f"{'':26s}{p}  <-  {u[:100]}")
        return
    failed = []
    for n in names:
        desc, mb, files, zips = DATA[n]
        for url, rel in files:
            tgt = ROOT / rel
            if a.check:
                msg = check(url); print(f"[check] {n}: {rel}: {msg}")
                if msg.startswith("FAILED"):
                    failed.append(f"{n}:{rel}")
                continue
            if tgt.exists() and not a.force:
                print(f"[skip ] {n}: {rel} exists"); continue
            print(f"[get  ] {n}: {rel} ...", flush=True)
            try:
                print(f"         {fetch(url, tgt) / 1e6:.1f} MB")
            except RuntimeError as e:
                print("         FAILED:", e); failed.append(f"{n}:{rel}")
        for z in ([] if a.check else zips):
            src, out = (ROOT / p for p in z.split("="))
            if src.exists() and (a.force or not out.exists()):
                with zipfile.ZipFile(src) as zf:
                    zf.extractall(out)
                print(f"[unzip] {src.name} -> {out.relative_to(ROOT)}")
    if failed:
        print("\nFAILED items:", *failed, sep="\n  "); sys.exit(1)
    print("\ndone")


if __name__ == "__main__":
    main()
