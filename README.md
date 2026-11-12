# GeoAI_Hackathon

Accessibility of Manhattan hospitals: what the map says is accessible versus what people can actually reach.

## Purpose

Quantify the gap between "accessible on the map" and "actually reachable". The study covers three hospitals on Manhattan island: Harlem Hospital, NYP/Columbia, and Mount Sinai Morningside. The analysis starts with subway and bus, then adds random elevator outages, and finally (still to do) curb ramps; see task t1 in `HANDOFF.md`.

Core questions: how many residents are covered when only ADA-accessible stations are used; how many are still covered when elevators fail at random; and which single elevator or station causes the largest loss when it goes out.

Project status, preliminary findings, known problems and the to-do list are in `HANDOFF.md`. Data checks and the working log are in `docs/checks_data.md`, `docs/checks_live.md` and `docs/checks_isochrone.md`. The final summary numbers are in `docs/final_summary.md` and `outputs/final_summary.csv`.

**All numbers are preliminary.** When quoting them, label them "preliminary" and do not quote exact areas.

## Study scope

- **Manhattan island only.** Residents are counted only in Manhattan census tracts; other boroughs are excluded. The isochrones themselves may cross rivers, but residents and areas are counted only inside Manhattan (see the clipping in script 56).
- The boundary is the official NYC Manhattan borough boundary (land only, rivers excluded). It includes Marble Hill. Roosevelt Island is inside the boundary but was never reached.
- **Three hospitals:** Harlem Hospital, NYP/Columbia, Mount Sinai Morningside.
- **30-minute isochrones**, averaged over five departure times from 07:30 to 08:30. The Monte Carlo uses the single time 08:00 only; the two time bases differ, so do not compare absolute values directly.
- **Direction:** both forward (leaving the hospital) and reverse (arriving at the hospital by 08:00) were computed; the final summary table uses reverse.
- **Four scenarios:** (1) anyone, subway only; (2) ADA subway stations only; (3) anyone, subway plus bus; (4) ADA subway stations plus bus (all buses and bus stops are treated as usable, which is an upper bound for the ADA group).
- **Residents:** ACS 2020–2024 residents with an ambulatory difficulty, allocated to the grid in proportion to tract area.

## Key assumptions (read "Known problems" in `HANDOFF.md` first)

- Elevator failures are independent; availability is the 12-month 24-hour average; an outage state does not change within the 30 minutes.
- Walking speed is 4.8 km/h; residents are spread uniformly inside each tract; curb ramps are not modelled.
- All buses are treated as accessible.
- 5 ADA stations have no elevator model and are treated as always available, which overstates coverage near them. For the 9 stations added later, the structure comes from the text descriptions in the MTA equipment list and has not been checked on site.
- 148 St is treated as "no elevator dependency", not verified on site.
- Ramp data were collected in 2017–2020 and have been rebuilt since; measured values cannot show ADA compliance by themselves.
- Times in the live data carry no time-zone marker, and the `ismaintenanceoutage` field is not usable.

## Preliminary results (from `docs/final_summary.md`; all preliminary)

ADA share of anyone (residents, reverse, five-time mean): with subway only, NYP about 75%, Harlem about 71%, Mount Sinai about 42%; with bus added, Harlem about 84%, NYP about 81%, Mount Sinai about 69%. The order of Harlem and NYP is not stable; Mount Sinai is the lowest.

Monte Carlo (scenario 4, 1000 draws, single time 08:00): the 5th percentile relative to the no-outage baseline is about 70% for NYP, about 90% for Harlem and about 94% for Mount Sinai. The largest single point of failure is NYP's 168 St (A/C): one outage loses about 43% of residents, and it depends on one elevator, EL139. Harlem's 135 St (2/3) loses about 32%.

## Folder layout

```
GeoAI/
├── README.md            this file
├── HANDOFF.md           project status, preliminary findings, known problems, to-do, rules
├── requirements.txt     third-party dependencies (see "Environment")
├── .gitignore           excludes raw/, data/cache/, archive/, zip files, files with keys, etc.
├── docs/                documentation
│   ├── checks_data.md       data checks (27 sections)
│   ├── checks_live.md       live-fetch checks (11 sections)
│   ├── checks_isochrone.md  isochrones and Monte Carlo log (31 sections)
│   └── final_summary.md     final summary table and how to read it
├── raw/                 raw downloaded data (not in the share package; see "Re-downloading raw data")
│                        14 sub-folders: borough_boundaries, census, elevator_availability,
│                        elevator_inventory, gtfs, gtfs_bus, live_equipment,
│                        mbpo_ramp_report, mta_amenities, mta_entrances, mta_stations,
│                        nyc_centerline, ped_ramp_locations, ramp_program_progress
├── data/
│   ├── clean/           cleaned, frozen tables (do not edit; create new files instead, see "Rules")
│   │                    station_table.csv, elevator_detail.csv,
│   │                    study_area_elevators.csv, elevators_assigned_by_coordinates.csv,
│   │                    station_model_fixes.csv, mc_station_model.csv,
│   │                    mc_elevator_station_map.csv
│   └── cache/           intermediate files written by the scripts (pickles etc.; regenerable, not shared)
│                        also data/cache/rebuilt/: rebuilt copies of the clean tables,
│                        which never overwrite data/clean/ directly
├── scripts/             all analysis scripts (51; see "Scripts and run order")
├── outputs/             maps (PNG) and summary tables (CSV)
├── live/                copies of the live fetcher: fetch script, launch-config template, station_status.py
└── archive/             backups and debugging material, not in the share package
                         checks_original.md, .pre_* backup files,
                         scripts_original_verbatim/ (verbatim copies of the 55 scripts),
                         scripts_debug/ (debugging scripts), scripts_superseded/ (superseded scripts),
                         refactor_paths.py, split_checks.py, verify_scripts.py
```

`raw/`, `data/cache/` and `archive/` are not part of this repository (see `.gitignore`).

## Environment

- Python 3.13 (the results were produced on 3.13.9).
- Only five third-party libraries are needed; everything else is the standard library:

```bash
pip install -r requirements.txt
```

`requirements.txt`: pandas 2.2.3, numpy 2.3.5, scipy 1.16.3, matplotlib 3.10.6, Pillow 12.0.0.

## How to run

Run from the project root (the folder above `scripts/`):

```bash
python scripts/01_download_raw.py --list   # first look at the raw-data list (optional)
python scripts/10_check_profile.py
python scripts/11_check_id_match.py
# ... continue in numeric order, see the table below
```

- Scripts run in numeric order. `lib_*.py` and `_paths.py` are not run directly; they are shared code loaded by other scripts through `exec` / `import`.
- All paths go through `scripts/_paths.py`: `R` = `raw/`, `O` = `data/clean/` (frozen tables) or `outputs/` (other outputs), `S` = `data/cache/`, `REB` = `data/cache/rebuilt/`. No absolute paths are hard-coded in the scripts.
- To run against a scratch copy (without touching the original project), set the environment variable `GEOAI_ROOT` to the root of that copy, for example `GEOAI_ROOT=/tmp/geoai-copy python scripts/54_....py`.
- Scripts 65 and 69 use multiprocessing and take about 5 minutes each; most other scripts finish within a minute.
- Some scripts were rebuilt from ad-hoc commands that were run at the time, and are not the exact scripts that were run then; this is stated in the file headers: `31_bus_windows.py`, `55_iso_time_average_summary.py`, `57_manhattan_clip_tables.py` and `66_mc_station_model_table.py`. `01_download_raw.py` and `81_add_pct_columns.py` are newly written.

### Scripts and run order

The "Main outputs" column lists only the main outputs; scripts marked "print only" write no files and show their results in the terminal.

| Script | What it does | Main inputs | Main outputs |
|---|---|---|---|
| `01_download_raw.py` | Downloads all 15 raw datasets (newly written, see "Re-downloading raw data") | source URLs | `raw/` (about 800 MB) |
| `10_check_profile.py` | Profiles the raw data: rows, columns, date ranges (prints) | the tables in `raw/` | print only |
| `11_check_id_match.py` | Checks that station / equipment IDs match across tables (prints) | the tables in `raw/` | print only |
| `12_check_station_id_zero_pad.py` | Checks that Station MRN agrees across tables once leading zeros are removed (prints) | availability table, equipment inventory, station table | print only |
| `13_ada_official_list_parse.py` | Parses the MTA website's accessible-stations page | `data/cache/mta_acc.html` | `data/cache/official_ada.csv` |
| `14_ada_official_list_match.py` | Matches the official accessible-station list to the station table by name and line (prints) | `official_ada.csv`, station table | print only |
| `15_search_148st.py` | Searches every table for 148 St / Harlem records (prints) | the tables in `raw/` | print only |
| `20_study_area_counts.py` | Defines the study area (north of 110 St plus 400 m around the three hospitals) and counts elevators and ramps inside it | the tables in `raw/` | print only |
| `21_study_area_line_fit.py` | Fits the 110 St boundary line from ramp corner points (prints) | ramp-location table | print only |
| `22_study_area_mbpo_stations.py` | Counts ramps and MBPO stations by hospital zone (prints) | ramp-location table, station table | print only |
| `23_station_table.py` | Builds the study-area station table and per-elevator detail | station table, equipment inventory, availability table | `data/clean/station_table.csv`, `elevator_detail.csv`, `study_area_elevators.csv`, `elevators_assigned_by_coordinates.csv` (via `data/cache/rebuilt/`) |
| `24_hospital_ada_stations.py` | ADA stations near the three hospitals (straight-line distance) | station table, entrances table | `outputs/hospital_ada_stations.csv` |
| `25_hospitals_map.py` | Map of the three hospitals and the study area | borough-boundary GeoJSON | `outputs/hospitals_map.png` |
| `30_street_graph.py` | Builds the walking network from NYC Street Centerline | `raw/nyc_centerline/` | `data/cache/graph.pkl` |
| `31_bus_windows.py` | Builds the bus-timetable windows (rebuilt, see file header) | `raw/gtfs_bus/` (Manhattan, Bronx, MTA Bus) | `data/cache/bus_8.pkl`, `bus_12.pkl`, `bus_avg.pkl`, `bus_rev.pkl`, `bus_rev5.pkl` |
| `40_iso_nyp_subway_run.py` | Forward 30-minute subway isochrone from NYP | street graph, subway GTFS | `data/cache/iso_res.pkl` |
| `41_iso_nyp_subway_area.py` | Area and resident statistics for the NYP subway isochrone | `iso_res.pkl` | `outputs/nyp_isochrone_summary.csv`, `data/cache/iso_masks.pkl` |
| `42_iso_nyp_subway_map.py` | Map of the NYP subway isochrone | `iso_res.pkl`, `iso_masks.pkl` | `outputs/nyp_isochrone_30min.png` |
| `43_iso_nyp_bus_run.py` | NYP subway plus bus: 08:00/12:00 × bus or not × ADA stations only | street graph, subway + bus GTFS | `data/cache/iso2_res.pkl` |
| `44_iso_nyp_bus_area.py` | Area and resident statistics for NYP subway plus bus | `iso2_res.pkl` | `outputs/nyp_isochrone_bus_summary.csv`, `data/cache/iso2_masks.pkl` |
| `45_iso_nyp_bus_map.py` | Four-scenario map for NYP subway plus bus | `iso2_masks.pkl`, summary table | `outputs/nyp_isochrone_bus_4scenarios.png` |
| `50_iso_hospitals_run.py` | Isochrones for the three hospitals: forward 08:00/12:00, reverse 08:00 | street graph, subway + bus GTFS | `data/cache/iso3_res.pkl` |
| `51_iso_hospitals_area.py` | Area and resident statistics for the three hospitals | `iso3_res.pkl` | `outputs/hospital_isochrone_summary.csv`, `data/cache/iso3_masks.pkl` |
| `52_iso_hospitals_map.py` | Four-scenario maps for the three hospitals | `iso3_masks.pkl`, summary table | `outputs/isochrone_harlem_4scenarios.png`, `isochrone_nyp_columbia_4scenarios.png`, `isochrone_mt_sinai_morningside_4scenarios.png` |
| `53_iso_reverse_validate.py` | Spot-check validation of the reverse isochrone (prints) | `iso3_res.pkl` | print only |
| `54_iso_time_average_runs.py` | Three hospitals × 4 scenarios × 5 departure times (07:30–08:30), forward | street graph, subway + bus GTFS | `outputs/hospital_isochrone_timeavg_runs.csv` |
| `55_iso_time_average_summary.py` | Mean / SD / min / max / coefficient of variation over the five times (rebuilt, see file header) | `hospital_isochrone_timeavg_runs.csv` | `outputs/hospital_isochrone_timeavg_summary.csv` |
| `56_manhattan_clip_runs.py` | Same as 54, but counting only residents and area inside Manhattan | street graph, subway + bus GTFS | `outputs/manhattan_clip_runs.csv` |
| `57_manhattan_clip_tables.py` | Before/after-clipping comparison, ADA share and bus gain (rebuilt, see file header) | `manhattan_clip_runs.csv` | `outputs/manhattan_clip_comparison.csv`, `manhattan_clip_ratios.csv` |
| `60_mc_first_run.py` | Scenario-4 Monte Carlo, first round: 1000 draws, random seed 20261111, single time 08:00 | elevator model, resident density grid | `outputs/mc_scenario4_summary.csv`, `mc_single_failure.csv`, `data/cache/mc_counts.pkl` |
| `61_mc_selfcheck.py` | Monte Carlo self-check: sampling frequency versus analytic probability (prints) | elevator model | print only |
| `62_mc_threshold_noise.py` | Sampling-noise check around the 90% coverage-probability threshold (prints) | `mc_counts.pkl`, `mc_scenario4_summary.csv` | print only |
| `63_mc_coverage_maps.py` | Monte Carlo coverage-probability maps | elevator model, the 1000 draws | `outputs/mc_scenario4_coverage_forward.png`, `mc_scenario4_coverage_reverse.png` |
| `64_mc_expanded_model_build.py` | Expands the elevator model from 10 to 59 stations (first validated on the original 10) | station table, equipment inventory, availability table | `data/cache/mc2_model.pkl` |
| `65_mc_expanded_run.py` | Monte Carlo with the expanded model: 1000 draws (multiprocessing, about 5 minutes) | `mc2_model.pkl` | `outputs/mc_manhattan_summary.csv`, `mc_manhattan_single_failure.csv` |
| `66_mc_station_model_table.py` | Exports the model as tables (rebuilt, see file header) | `mc2_model.pkl`, `mc3_model.pkl` | `data/cache/rebuilt/mc_station_model.csv`, `mc_elevator_station_map.csv` (another copy is already in `data/clean/`, used by script 80) |
| `67_mc_tables.py` | Turns the Monte Carlo results into tables (prints and writes tables) | `mc_manhattan_summary.csv` etc. | `data/cache/tbl_*.md` |
| `68_mc_station_fixes.py` | Corrects the elevator model: adds 9 stations and fixes 2 earlier models | `mc2_model.pkl`, availability table | `data/cache/mc3_model.pkl`, `data/clean/station_model_fixes.csv` |
| `69_mc_fixed_run.py` | Monte Carlo with the corrected model: 1000 draws (multiprocessing, about 5 minutes) | `mc3_model.pkl` | `outputs/mc_manhattan_summary_fixed.csv`, `mc_manhattan_single_failure_fixed.csv` |
| `70_mc_fix_compare.py` | Before/after comparison of the correction (prints) | summary tables before and after | print only |
| `80_final_summary.py` | Final summary: three hospitals × 4 scenarios plus Monte Carlo | clipping comparison tables, corrected MC tables, single-failure table | `outputs/final_summary.csv`, `docs/final_summary.md` |
| `81_add_pct_columns.py` | Adds two columns to the MC summary table: mean and 5th percentile as a percentage of each row's own baseline (baseline = same hospital, direction, departure time and scenario) | `mc_manhattan_summary_fixed.csv` | `outputs/mc_manhattan_summary_fixed_with_pct.csv` (the original file is untouched) |
| `_paths.py` | Path helper shared by all scripts (not run directly) | — | — |
| `lib_iso_core.py` | Shared code for subway isochrones (street network + subway GTFS) | — | used by 40–42, 44, 51 |
| `lib_iso2_core.py` | Shared code for subway-plus-bus isochrones | — | used by 43–45 |
| `lib_iso3_core.py` | Shared code for the three-hospital isochrones | — | used by 50–54 |
| `lib_iso4_grid.py` | 10 m grid and tract resident density | — | used by 54, 62 |
| `lib_clip_core.py` | Shared code for the Manhattan clipping | — | used by 56, 64, 65, 69 |
| `lib_mc_core.py` | Shared Monte Carlo code (10-station model) | — | used by 60–63 |
| `lib_mc2_model.py` | Builder for the expanded elevator model | — | used by 64–65, 68–69 |
| `lib_bus_load.py` | Bus GTFS loading | — | used by 31, 43, 50 |

## Re-downloading raw data

```bash
python scripts/01_download_raw.py --list    # list datasets, sizes and target paths
python scripts/01_download_raw.py --check   # only check that every URL answers, no download
python scripts/01_download_raw.py --only mta_stations,elevator_inventory
python scripts/01_download_raw.py           # everything, about 800 MB (mostly bus GTFS, about 560 MB)
```

The 15 datasets (`--list` shows all of them): elevator availability, elevator equipment inventory, subway station table, subway GTFS, bus GTFS (Manhattan, Bronx, Brooklyn, Queens, Staten Island, MTA Bus Company), pedestrian-ramp locations, ramp program progress, MBPO ramp report, borough boundaries, MTA live equipment and outage snapshots, subway entrances, subway station amenities, NYC street centerline, ACS 2020–2024 table B18105 plus the 2020 tract boundaries, and the MTA website's accessible-stations page (saved to `data/cache/`, not to `raw/`).

**Data that will not match the original exactly after a re-download:**

- `live_equipment`: an MTA live snapshot taken on 2026-11-11; it cannot be reproduced.
- Elevator availability, equipment inventory, station table, entrances, station amenities: rolling tables updated by the MTA.
- Subway / bus GTFS: the MTA replaces the files when a new timetable is published (the bus timetable used here is valid from 2026-10-12 to 2027-01-02).
- The MTA website's accessible-stations page: the version used was dated 2026-10-12.
- Borough / tract boundaries, street centerline, the ACS file and the ramp tables are static or change slowly, so a re-download should be essentially identical.

Alternatively, ask the team for the zip of `raw/` (about 183 MB; it is not in this repository) and unzip it into the project root to skip the download.

## Live fetching (`live/`)

- `live/fetch_live_outages.py`: queries the MTA live elevator/escalator outage endpoint every 10 minutes. Each successful fetch saves the raw response unchanged to `raw/live_outages/outages_<UTC time>.json` and appends one row to `live_log.csv` (UTC time, success flag, row count, error, New York time, device counts). Failures are logged and retried after 60 seconds; a 401/403 stops the script.
- `live/station_status.py`: computes station status from the live data. The live folder is set with the environment variable `GEOAI_LIVE_DIR` (default: `~/geoai-live`).
- `live/com.geoai.liveoutages.plist.template`: a macOS launchd configuration template. Replace `<PYTHON>`, `<LIVE_DIR>` and `<LOG_DIR>` with the real paths on your machine before using it.
- Do not touch the original `~/geoai-live`: the fetch process runs on the team lead's computer and a snapshot is shared on Saturday morning. Only copies and templates are kept in `live/`.
- An optional API key is read from the environment variable `MTA_API_KEY` (sent as the `x-api-key` header). Never write it into a file. No key has been needed so far.

## Rules for later work

- **Do not modify existing scripts or the files in `data/clean/`.** To change something, create a new file whose name starts with the task number, for example `t1_`.
- Write results in files such as `docs/checks_t1.md`, **without personal names**.
- Label every number "preliminary" and do not quote exact areas.
- Put new data and new intermediate files in `data/cache/` first; only tables that are confirmed frozen go into `data/clean/`.
- Do not put sensitive information (personal names, e-mail addresses, paths starting with `/Users/`, API keys, passwords, tokens) into files that will be shared.
- All written content in this repository (README, documents, comments, commit messages) is in English.

## Verification status

Each script was re-run in a scratch copy of the project after the paths were moved to `scripts/_paths.py`, and its outputs were compared with the original outputs (CSV values, PNG pixels, pickles); all matched, except that `80_final_summary.py` could not be checked because one input file was missing from the scratch copy at that moment. Scripts 01 and 81 are newly written and 31, 55, 57 and 66 were rebuilt, so they have no original output to compare against. The values in the CSV files and scripts are in English; text that the scripts write (table headers, review notes) was translated together with the code that reads it.

## Known problems

See "Known problems — read first" in `HANDOFF.md`: 5 stations have no elevator model; the 9 added stations have not been checked on site; several elevators at 161 St (B/D) have an availability of only about 50% for reasons not yet checked; the ramp data are old; the live data have no time-zone marker; and so on. Please read that section before starting t1–t6.
