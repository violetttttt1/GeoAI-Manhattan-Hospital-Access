# Live outage data checks (checks_live)

Covers: checks of the live outage fetching, the log fields, the station-status time series, and the estimated return-to-service times. The fetcher is in `live/`. Section numbers are renumbered inside this file; the original file is kept in `archive/checks_original.md`, and a table at the end maps new to old section numbers. All numbers are preliminary.

---

*(Original chapter: Round 4, live outage data check)*

Checks only, no analysis. The collection script and data now live in `~/geoai-live/` (script, `live_log.csv`, `raw/live_outages/`), not in this folder, because launchd cannot read `~/Desktop`. `LIVE_OUTAGES_MOVED.txt` in this folder explains this. The statement in section 14 of docs/checks_data.md that `fetch_live_outages.py` and the related files were not created by me is now out of date: they were created later and moved away.

Endpoints: `nyct%2Fnyct_ene.json` (current outages) and `nyct%2Fnyct_ene_equipments.json` (equipment list); neither needs a key (a request without a key returns 200).

## 1. Fields in the latest snapshot

File: `outages_20261111T192728Z.json` (fetched 2026-11-11 19:27:28 UTC), a JSON array with **182 rows** and 12 fields per row; every field has a value in all 182 rows:

| Field | Meaning (inferred from the values) |
|---|---|
| station | station name |
| borough | borough (**an empty string in every row** of this snapshot) |
| trainno | line |
| equipment | equipment number (such as EL124), the same scheme as `Equipment Code` in the study-area file |
| equipmenttype | EL (elevator) 158 rows / ES (escalator) 24 rows |
| serving | description of the floors the equipment connects |
| ADA | Y/N |
| outagedate | start of the outage, string `MM/DD/YYYY hh:mm:ss AM/PM` |
| estimatedreturntoservice | estimated return to service, same format |
| reason | reason (for example Planned Work, Inspection, Maintenance, Under Investigation) |
| isupcomingoutage | Y/N |
| ismaintenanceoutage | Y/N |

Example (first row):

```json
{"station": "175 St", "borough": "", "trainno": "A", "equipment": "EL124",
 "equipmenttype": "EL", "serving": "Mezzanine to platform for service in both directions.",
 "ADA": "Y", "outagedate": "12/16/2026 10:00:00 PM",
 "estimatedreturntoservice": "12/17/2026 06:00:00 AM", "reason": "Planned Work",
 "isupcomingoutage": "Y", "ismaintenanceoutage": "N"}
```

**Three things to note:**
1. **182 rows are not 182 devices.** One device can have several rows (EL123 has two, EL786 has three, and so on); there are only **132 distinct equipment numbers** (108 of them elevators).
2. **`isupcomingoutage = Y` in 140 rows and N in only 42 rows.** Y means a scheduled outage that has not started yet (for example the start time in the example above is 2026-12-16, later than the fetch time). So `outage_count` in `live_log.csv` (= number of array rows, 182) **includes future planned outages** and does not equal "how many devices are down right now". I did not make this clear when I earlier reported "179 outages". `ismaintenanceoutage` is N in all 182 rows.
3. The time fields are strings without a time zone; the time zone has not been verified (probably New York local time).

## 2. Matching live data to `study_area_elevators.csv` by equipment number

The study area has 48 elevators with the column `Equipment Code`; in the live data the column is `equipment` (in the equipment list it is `equipmentno`). Numbers are compared directly, without stripping any X suffix.

| Check | Result |
|---|---|
| Study-area elevators found in the equipment list (707 devices: 430 elevators + 277 escalators) | **38 / 48 = 79.2%** |
| The 37 study-area elevators that **have** an availability record, to the equipment list | 37 / 37 = 100% |
| Equipment numbers in live outages (132 across all 5 snapshots), to the equipment list | 132 / 132 = 100% |
| 48 study-area elevators, to the latest snapshot (appearing in the outage / scheduled-outage list) | **8 / 48 = 16.7%** (EL123, EL124, EL142, EL143, EL144, EL179, EL517, EL518) |
| 132 devices in the latest snapshot, to the study area | 8 / 132 = 6.1% |

"Match rate" can be read two ways, and both are listed above: **whether the numbering scheme lines up** (equipment list 79.2%; the 10 missing ones are 10 of the 11 listed separately below); and **whether study-area elevators appear in the outage list** (8). The second number only reflects who is on the outage list; it is not a matching failure.

Of the 8, in the latest snapshot only **EL123 (175 St) is N (currently out, Under Investigation)**; all the others are Y (scheduled outages). This is only a cross-check; nothing more was read into it.

## 3. The 11 study-area elevators without availability records: are they in the live data?

The 11: EL147, EL150, EL151, EL152, EL153, EL155, EL156, EL166X, EL167X, EL169X, EL520 (section 9 of docs/checks_data.md).

| Elevator | In the equipment list (`equipments.json`) | Appears in live outages (5 snapshots) |
|---|---|---|
| EL147, EL150, EL151, EL152, EL153, EL155 | no | no |
| EL156 | no | no |
| EL166X, EL167X, EL169X | no | no |
| EL520 | **yes** | no |

Conclusion: **none of the 11 ever appeared in the live outage data** (0 of 5 snapshots). Only EL520 can be found in the equipment list.

Do not read "did not appear" as "has no failures": the outage endpoint lists only devices that are out or about to be, so not appearing only means they were not listed in these 5 snapshots. Also, 10 of these 11 are not in the MTA equipment list at all, so the MTA live system may not monitor them; the reason has not been checked. EL520 is in the list but has no historical availability and did not appear among the outages.

## 4. Number of snapshots and gaps

Time range: 2026-11-11 19:06:17 to 19:27:28 UTC (at the time of the check).

| Item | Value |
|---|---|
| Outage snapshot files | **5** |
| Rows in `live_log.csv` | 5, all success = 1, no failure records |
| Equipment-list files | 1 (19:06:12, fetched only once) |
| File count versus log rows | consistent |

Interval between consecutive fetches (seconds):

| Time (UTC) | Interval | Note |
|---|---|---|
| 19:06:17 → 19:09:33 | 196 | while the first, manually started process was running |
| 19:09:33 → 19:15:56 | 383 | I stopped the process, tried launchd, then restarted the process |
| 19:15:56 → 19:17:26 | 90 | process switch during the move; interval shorter than 10 minutes |
| 19:17:26 → 19:27:28 | 602 | launchd running normally at the 10-minute cadence |

- **No gaps**: no interval is longer than 10 minutes (600 seconds); the longest is 602 seconds (including request time).
- **The first 3 intervals are shorter than 10 minutes** because the process was restarted several times while debugging; nothing was missed, the cadence was just uneven. Since 19:17:26 it has been a steady one fetch every 10 minutes.
- This covers only 21 minutes, which is not enough to show long-term stability, and behaviour across sleep, network loss and reboots has not been verified.

---

*(Original chapter: Round 5, log columns and a small live-data check)*

Snapshot: `outages_20261111T193539Z.json` (2026-11-11 19:35:39 UTC, 14:35:39 New York time).

## 5. New columns in `live_log.csv`

Location `~/geoai-live/live_log.csv`. The original 4 columns keep their order; the new columns are added at the end:

| Column | Meaning |
|---|---|
| `fetched_at_nyc` | fetch time in New York time (with offset, such as `2026-11-11T14:35:39-05:00`) |
| `current_outage_devices` | devices currently out: `isupcomingoutage = N`, de-duplicated by `equipment` |
| `current_nonmaint_devices` | of these, the number of **non-maintenance** devices: the same row has both `isupcomingoutage = N` and `ismaintenanceoutage = N`, de-duplicated by device |
| `distinct_devices` | all distinct devices in the list (currently out + scheduled) |

- For fetches that failed, the three device-count columns are left empty.
- The old 5 rows were back-filled from the raw files saved at the time; the old log was backed up as `~/geoai-live/live_log.pre_v2.csv`. `outage_count` did not change from before to after the back-fill.
- Latest row (19:35:39): 182 rows, 42 currently out, 42 non-maintenance, 132 distinct devices.
- **`current_nonmaint_devices` is currently always equal to `current_outage_devices`**: `ismaintenanceoutage` is N in every snapshot fetched so far, including rows whose `reason` says "Maintenance" (such as EL144, EL517, EL518). So the field does not seem to distinguish maintenance from other outages; whether it has another meaning has not been checked.
- The script was changed and launchd was restarted (new process), so every later fetch writes the new columns automatically.

## 6. The 8 study-area elevators in the list

8 devices and 14 rows in total (one device can have several outage records). Station and line come from `station` and `trainno` in the live data. Times are the raw strings; the time zone has not been verified.

| Device | Station | Scheduled (isupcomingoutage) | Maintenance (ismaintenanceoutage) | Reason | Start | Estimated return |
|---|---|---|---|---|---|---|
| EL123 | 175 St (A) | **N (currently out)** | N | Under Investigation | 11/11/2026 01:27 PM | 11/11/2026 09:00 PM |
| EL123 | 175 St (A) | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL124 | 175 St (A) | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL142 | 125 St (A/C/B/D) | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL143 | 125 St (A/C/B/D) | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL144 | 125 St (A/C/B/D) | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL179 | Dyckman St (1) | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL179 | Dyckman St (1) | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |
| EL517 | 181 St (A) | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL517 | 181 St (A) | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL517 | 181 St (A) | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |
| EL518 | 181 St (A) | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL518 | 181 St (A) | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL518 | 181 St (A) | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |

Of the 14 rows only the first (EL123) is currently out; the other 13 are scheduled outages.

## 7. Of the devices currently out, how many have ADA = Y

| Item | Count |
|---|---|
| Devices currently out (`isupcomingoutage = N`, de-duplicated) | 42 |
| of which `ADA = Y` | **18** |
| of which `ADA = N` | 24 |

Split further: **all 18 with ADA = Y are elevators (EL) and all 24 with ADA = N are escalators (ES)**, so the two fields correspond exactly. For each device the ADA value is the same in all of its currently-out rows; no device is both Y and N.

## 8. Time zone of the log timestamps

- **`fetched_at_utc` is UTC.** The script produces it with `datetime.now(timezone.utc)`, and the value carries the suffix `+00:00`; the time in the raw file name comes from the same instant, with the suffix `Z`.
- Check: UTC 19:35:39 corresponds to New York 14:35:39, offset -05:00, which fits US Eastern Standard Time (daylight saving time ended on 1 November in 2026).
- The new `fetched_at_nyc` is converted with the system's `America/New_York` time-zone data, so daylight saving time is handled automatically.
- This only shows that **our own recorded fetch time** is UTC. `outagedate` and `estimatedreturntoservice` returned by the endpoint carry no time-zone marker; whether they are New York local time has not been verified.

---

*(Original chapter: Round 6, ADA check of the equipment list and the station-status time series)*

## 9. Station-status time series: `station_status.py` and `station_status_timeseries.csv`

- Script: [station_status.py](../live/station_status.py). It reads all snapshots under `~/geoai-live/raw/live_outages/` and `station_table.csv`, and writes [station_status_timeseries.csv](../outputs/station_status_timeseries.csv).
- To re-run: `python3 station_status.py`. It appends only snapshots not yet in the output (judged by `snapshot_utc`) and never rewrites existing rows; running it twice in a row appends 0 snapshots the second time (verified).
- Columns: `snapshot_utc, snapshot_nyc, station_id, gtfs_stop_id, station_name, routes, available, blocked_directions, elevators_out`.
- **Rules:**
  - An elevator is "out" if the snapshot has a row whose `equipment` matches and `isupcomingoutage = N`. Scheduled outages (Y) do not count.
  - In a station's `access_paths`, `+` means in series (all must work) and `|` means in parallel (any one working is enough). A station counts as available (`available = 1`) only if both directions `PN` and `PS` have at least one fully working path. `blocked_directions` says which direction is blocked.
  - `elevators_out` lists only elevators on that station's paths.
  - Harlem-148 St has no elevator data; `available` is left empty, meaning it cannot be judged: neither available nor unavailable.
- Currently 6 snapshots × 10 stations = 60 rows. **In every snapshot only 175 St is unavailable (0), always because of EL123.** Harlem-148 St is empty throughout, and the other 8 stations are all 1.
- Limitations:
  - This only says whether the MTA's current outage list contains the elevator. Causes outside the list (for example a device that is not monitored or is not in the inventory) are invisible.
  - `estimatedreturntoservice` is not used to decide whether the return time has passed; if the snapshot still lists the elevator, it counts as out.
  - The EL519/EL520 paths at 137 St use the structure in station_table; EL166X, EL167X and EL169X are not on the paths.
  - No probabilities were computed and nothing was modelled.

## 10. Is 175 St available right now

**Not available.** The latest snapshot is `outages_20261111T193539Z.json` (UTC 19:35:39, New York 14:35:39). In `station_status_timeseries.csv` the 175 St row has `available = 0`, `blocked_directions = PN;PS`, `elevators_out = EL123`.

- The structure of 175 St is EL123 → EL124 **in series** (`PN: EL123+EL124; PS: EL123+EL124`), with no parallel alternative elevator. EL123 is out, so neither direction can be used.
- In the inventory, EL123's `serving` is "177 St & Fort Washington Ave (NE corner) to mezzanine", i.e. the one from street to mezzanine.
- This outage: started 11/11/2026 01:27 PM, estimated return 11/11/2026 09:00 PM, reason Under Investigation, `isupcomingoutage = N`. The time strings have no time zone; whether they are New York local time has not been verified. If they are, it was about 14:40 New York time, so roughly 6 hours 20 minutes remain. The estimated return time is only an MTA estimate, not a guarantee.
- EL124 itself is not out right now; it has only a scheduled outage (Y) on 12/16.
- 175 St was unavailable in all 6 snapshots, so this is a lasting state, not a one-off.

---

*(Original chapter: Round 7, Harlem-148 St flag and "estimated return time has passed")*

## 11. New `recovery_overdue` column

Two new columns in the time series: `recovery_overdue` (value "estimated return time has passed", or empty) and `overdue_elevators` (which elevators).

- Rule: for an elevator on a station's paths that is **currently out**, flag it if the snapshot time is later than its `estimatedreturntoservice`. If an elevator has several current outage records, the latest estimated return time is used.
- **`available` is not changed.** The flag is only a hint; availability still depends only on `isupcomingoutage = N`.
- The times in the endpoint have no time zone. I read them as New York local time, which is **not verified**.
- In the 6 snapshots no row is flagged: EL123's estimated return is 11/11 21:00 and all snapshots are earlier.
- The logic was tested with made-up data: with EL123's estimated return at 21:00 New York time, a snapshot at 20:59 is not flagged, one at 21:01 is flagged, and `available` is still 0.
- The script `station_status.py` was updated at the same time; re-run it when new snapshots arrive.

---

## Appendix: old and new section numbers

| New section | Original chapter | Original section | Title |
|---|---|---|---|
| 1 | Round 4: live outage data check | 22 | Fields in the latest snapshot |
| 2 | Round 4: live outage data check | 23 | Matching live data to `study_area_elevators.csv` by equipment number |
| 3 | Round 4: live outage data check | 24 | The 11 study-area elevators without availability records: are they in the live data |
| 4 | Round 4: live outage data check | 25 | Number of snapshots and gaps |
| 5 | Round 5: log columns and a small live-data check | 26 | New columns in `live_log.csv` |
| 6 | Round 5: log columns and a small live-data check | 27 | The 8 study-area elevators in the list |
| 7 | Round 5: log columns and a small live-data check | 28 | Of the devices currently out, how many have ADA = Y |
| 8 | Round 5: log columns and a small live-data check | 29 | Time zone of the log timestamps |
| 9 | Round 6: ADA check of the equipment list and the station-status time series | 32 | Station-status time series: `station_status.py` and `station_status_timeseries.csv` |
| 10 | Round 6: ADA check of the equipment list and the station-status time series | 33 | Is 175 St available right now |
| 11 | Round 7: Harlem-148 St flag and "estimated return time has passed" | 35 | New `recovery_overdue` column |
