"""Central path helper. Every script imports its paths from here; no other file hard-codes a path.

Project layout (ROOT = the folder that contains this `scripts/` folder):
    raw/            downloaded source data (not shipped; see README for how to re-download)
    data/clean/     cleaned / frozen tables used as inputs by later work
    data/cache/     intermediate files written by the scripts (pickles etc.; regenerated, not shipped)
    outputs/        maps and summary tables
    scripts/        this folder

Environment variable GEOAI_ROOT overrides ROOT (used to run the scripts against a scratch copy of the tree).

Compatibility objects used by the scripts (they behave like the old absolute-path prefixes):
    R + "mta_stations/mta_stations.csv"   -> <ROOT>/raw/...
    O + "name.csv"                         -> <ROOT>/data/clean/name.csv if name is a frozen clean table, else <ROOT>/outputs/name
    S + "x.pkl"                            -> <ROOT>/data/cache/x.pkl
    S + "lib_or_script.py"                 -> <ROOT>/scripts/<new numbered file name>  (old names are mapped below)
    REB + "name.csv"                       -> <ROOT>/data/cache/rebuilt/name.csv  (rebuilt copies of clean tables; never overwrites data/clean)
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("GEOAI_ROOT", str(HERE.parent))).resolve()
RAW = ROOT / "raw"
CLEAN = ROOT / "data" / "clean"
CACHE = ROOT / "data" / "cache"
OUTPUTS = ROOT / "outputs"
SCRIPTS = HERE
LIVE = ROOT / "live"

# Tables that live in data/clean (frozen inputs). Everything else written to "O + name" goes to outputs/.
CLEAN_NAMES = {
    "station_table.csv", "elevator_detail.csv", "study_area_elevators.csv", "elevators_assigned_by_coordinates.csv",
    "station_model_fixes.csv", "mc_station_model.csv", "mc_elevator_station_map.csv",
}

# Old (working) script names -> numbered names in this folder. Used when one script reads another one's text.
RENAME = {
    "iso_core.py": "lib_iso_core.py", "iso2_core.py": "lib_iso2_core.py", "iso3_core.py": "lib_iso3_core.py",
    "iso4_grid.py": "lib_iso4_grid.py", "clip_core.py": "lib_clip_core.py", "mc_core.py": "lib_mc_core.py",
    "mc2_model.py": "lib_mc2_model.py", "bus_load.py": "lib_bus_load.py", "study.py": "20_study_area_counts.py",
}


class _Cache(str):
    def __new__(cls):
        return str.__new__(cls, str(CACHE) + "/")

    def __add__(self, name):
        name = str(name)
        if name.endswith(".py") and "/" not in name:
            return str(SCRIPTS / RENAME.get(name, name))
        return str(CACHE / name)


class _Out(str):
    def __new__(cls):
        return str.__new__(cls, str(OUTPUTS) + "/")

    def __add__(self, name):
        name = str(name)
        return str((CLEAN if name in CLEAN_NAMES else OUTPUTS) / name)


class _Rebuilt(str):
    def __new__(cls):
        return str.__new__(cls, str(CACHE / "rebuilt") + "/")

    def __add__(self, name):
        (CACHE / "rebuilt").mkdir(parents=True, exist_ok=True)
        return str(CACHE / "rebuilt" / str(name))


for _d in (CLEAN, CACHE, OUTPUTS):
    _d.mkdir(parents=True, exist_ok=True)

S = _Cache()
O = _Out()
R = str(RAW) + "/"
REB = _Rebuilt()
