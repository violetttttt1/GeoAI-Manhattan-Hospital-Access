# Data, study-area and elevator-model checks (checks_data)

Covers: health checks of the 7 datasets, study-area counts, the station table and elevator model (series/parallel, fill values), the 148 St search, comparison with the equipment list, and the modelling repair of 14 stations. Section numbers are renumbered inside this file; the original file is kept in `archive/checks_original.md`, and a table at the end maps new to old section numbers. All numbers are preliminary.

---

*(Original chapter: data health check, checks.md)*

Check date: 2026-11-11. Only completeness and key-matching checks were done; no analysis. The raw files are under `raw/`, one directory per dataset.

## 1. Dataset overview

| Dataset | Source / ID | Local files | Rows | Latest date |
|---|---|---|---|---|
| Elevator availability | data.ny.gov `rc78-7x78` | `raw/elevator_availability/` | 83,776 | Month = 2026-09-01 (from 2015-01, 141 months) |
| Elevator asset inventory | data.ny.gov `94fv-bak7` | `raw/elevator_inventory/` | 759 | no observation date; maximum `Latest Installation Date` is 2026-10-24 |
| MTA stations | data.ny.gov `39hk-dx4f` | `raw/mta_stations/` | 496 | no date column |
| GTFS (subway) | rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip | `raw/gtfs/` | stops 1,488 / trips 20,310 / routes 29 / transfers 613 / calendar 3 | calendar valid 2026-11-01 to 2027-05-15 |
| DOT Pedestrian Ramp Locations | data.cityofnewyork.us `ufzp-rrqu` | `raw/ped_ramp_locations/` | 217,679 | maximum `GeoCyclora` 2020-01-29 (range 2017-03-27 to 2020-01-29); Socrata metadata updated 2022-05-09 |
| Pedestrian Ramp – Program Progress | data.cityofnewyork.us `e7gc-ub6z` | `raw/ramp_program_progress/` | 187,749 | maximum `Construction_End_Date` 2026-10-26 (only 60,510 rows non-empty, earliest 2003-03-22) |
| MBPO Pedestrian Ramp Report | data.cityofnewyork.us `8kic-uvpz` | `raw/mbpo_ramp_report/` | 277 | no date column; Socrata metadata updated 2021-08-10 |

Note: row counts are the actual rows of the downloaded CSV and agree with Socrata `count(*)` (except GTFS, which has no such endpoint).

## 2. Column names

**Elevator availability (23 columns)**: Month, Borough, Equipment Type, Equipment Code, Managed By, Total Outages, Scheduled Outages, Unscheduled Outages, Entrapments, Time Since Major Improvement, AM Peak Availability, AM Peak Hours Available, AM Peak Total Hours, PM Peak Availability, PM Peak Hours Available, PM Peak Total Hours, 24-Hour Availability, 24-Hour Hours Available, 24-Hour Total Hours, Station Name, Station MRN, Station Complex Name, Station Complex MRN

**Elevator asset inventory (44 columns)**: Equipment Code, Elevator or Escalator, Asset Class, Station MRN, Station Name, Station Description, Station Complex MRN, Station Complex Description, Subway Line, Borough, X Coordinate, Y Coordinate, Original Installation Date, Latest Installation Date, Service Status Code, Service Status, Service Life, NYCT Owned, Maintained By, Installer, Revenue Machine, ADA Compliant, Street Access, Exposed to Weather, Escalator Rise, Elevator Rise, Elevator Capacity, Elevator Loading Class, Elevator Number of Landings, Escalator Number of Steps, Escalator Step Width, Elevator Direction Serviced, Elevator Order, Elevator Mezzanine 1 Access, Elevator Mezzanine 2 Access, Elevator Platform Access, Notes, Redundant Elevator, Redundant Elevator Street Access, Redundant Elevator Mezzanine Access, Redundant Elevator Access Between Mezzanines, Redundant Elevator Platform Access, Alternative Route, Georeference

**MTA stations (19 columns)**: GTFS Stop ID, Station ID, Complex ID, Division, Line, Stop Name, Borough, CBD, Daytime Routes, Structure, GTFS Latitude, GTFS Longitude, North Direction Label, South Direction Label, ADA, ADA Northbound, ADA Southbound, ADA Notes, Georeference

**GTFS**
- stops: stop_id, stop_name, stop_lat, stop_lon, location_type, parent_station
- trips: route_id, trip_id, service_id, trip_headsign, direction_id, shape_id
- routes: route_id, agency_id, route_short_name, route_long_name, route_desc, route_type, route_url, route_color, route_text_color, route_sort_order
- calendar: service_id, monday…sunday, start_date, end_date
- transfers: from_stop_id, to_stop_id, transfer_type, min_transfer_time
- also agency / calendar_dates / feed_info / shapes / stop_times, whose rows were not counted this time

**Ramp Locations (24 columns)**: the_geom, CornerID, RampID, Ramp_OnStreet, GeoCyclora, Borough, StName1, StName2, CURB_REVEAL, RAMP_RUNNING_SLOPE_TOTAL, DWS_CONDITIONS, GUTTER_SLOPE, LND_WIDTH, LND_LENGTH, LND_CROSS_SLOPE, COUNTER_SLOPE, RAMP_WIDTH, RAMP_RIGHT_FLARE, RAMP_LEFT_FLARE, RAMP_LENGTH, RAMP_CROSS_SLOPE, PONDING, OBSTACLES_RAMP, OBSTACLES_LANDING

**Program Progress (9 columns)**: the_geom, OBJECTID, CornerID, Street_Name1, Street_Name2, Borough, Construction_Type, Construction_End_Date, Construction_Status_Value

**MBPO Ramp Report (24 columns)**: Station, Street 1, Street 2, Curb Cut, Center Cut, No Curb Cut, Ramp ID (No Id means a part of center cut), Compliant, Slope (1":12" or less), Slope Non-Comp, Ramp Width (36" or more), Width Non-Comp, Lip or Bump (1/4" or less), Lip Non-Comp, Crumbling Concrete?, Crumbling Non-Comp, Led to Pot Hole?, Pot Hole Non-Comp, Detectable warnings?, Warnings Non-Comp, Object barriers ?, Objects Non-Comp, Barriers above?, Ramp looks relatively "new"?

## 3. Match rate of elevator numbers (Equipment Code)

The availability table and the asset inventory both contain elevators and escalators; below they are filtered to `Equipment Type` / `Elevator or Escalator` = Elevator.

| Check | Result |
|---|---|
| Distinct elevator numbers in the availability table | 419 |
| Elevator numbers in the inventory | 482 (no duplicates) |
| Availability → inventory match rate | **419 / 419 = 100%** |
| Inventory → availability match rate | **419 / 482 = 86.9%** |
| The 419 elevators of the latest month (2026-09) → inventory | 100% |
| Intersection of elevators + escalators combined (701 in availability, 759 in inventory) | 696 |

**The 63 elevators in the inventory but not in the availability table:**
- Status: 53 Installed-Functioning-In Service, 5 Installed-Non Functioning-Out of Service, 4 Installed-Functioning-Out of Service, 1 Removed
- 23 have empty Station MRN / Complex MRN
- Ownership: 22 not NYCT-owned; maintained by NYCT 38, Private Contractor 14, LIRR 8, Third-Party 3
- 22 of them have numbers ending in `X`
- The reason has not been checked. From ownership and maintainer, some are suspected not to belong to the NYCT subway operating statistics; to be confirmed

**Note on the number format:** numbers can carry an `X` suffix (such as `EL200X`); 73 elevators in the inventory have an X, and 6,236 rows of the availability table do. If the X is stripped before comparing, the intersection actually drops from 419 to 417, which shows the X is part of the number, so **do not strip it**.

## 4. Match rate of station / complex keys

| Check | Result |
|---|---|
| Availability Complex MRN → MTA stations `Complex ID` | 152 / 152 = 100% |
| Inventory Complex MRN → MTA stations `Complex ID` | 158 / 158 = 100% |
| Same elevator number: Complex MRN agrees between the two tables | 100% (419 elevators) |
| Same elevator number: Station MRN agrees between the two tables (raw strings) | 84.2% (66 disagree) |
| Same, **after removing leading zeros** | **100%** |
| Station MRN (leading zeros removed) → MTA stations `Station ID` | availability 185/185, inventory 191/191 |
| MTA stations `GTFS Stop ID` → GTFS stops | 100% (496 = the 496 parent stations in GTFS) |
| Inventory Station MRN → MTA stations `GTFS Stop ID` | 49 / 191 (the two are different numbering schemes and cannot be joined directly) |

**Key finding:** 91 rows of the inventory's Station MRN have a leading zero (`012`), while the availability and station tables do not (`12`). A direct string join would miss about 16% of the elevators. Normalize before joining, for example with `lstrip("0")`.

Of the 496 rows of the station table, 166 have `ADA=1`. Of these, 155 are in complexes that have elevators in the inventory and 11 are not (reason not checked).

## 5. Match rate of the ramp tables

| Check | Result |
|---|---|
| Ramp Locations: RampID | 217,679 values, all unique, no empty values |
| Ramp Locations: CornerID | 134,127 distinct values, 83,552 repeated rows (several ramps per corner, as expected) |
| Program Progress: CornerID | 187,749 values, all unique |
| Ramp Locations CornerID → Program Progress | 134,108 / 134,127 = 99.99% |
| CornerIDs in Program Progress covered by Ramp Locations | 134,108 / 187,749 = 71.4% (the other corners have no 2017–2020 survey record) |
| MBPO Ramp ID → Ramp Locations `RampID` | 198 / 199 = 99.5% |
| MBPO Ramp ID → `CornerID` of either table | 0 (different numbering schemes; RampID must be used, not CornerID) |

## 6. Other things to watch

1. **The inventory's coordinate column labels are swapped:** `X Coordinate` holds 40.53–40.90 (latitude) and `Y Coordinate` holds -74.x (longitude). Swap them before use, or use `Georeference` instead.
2. **Elevators and ramps share no key:** there is no direct ID link between the two groups of data; they can only be related by location (station coordinates ↔ ramp `the_geom`).
3. **Ramp Locations is old:** the data were actually collected in 2017–2020, and the metadata was last updated in 2022-05. Program Progress is still being updated as of 2026-11. The two have different time bases.
4. **Status distribution in Program Progress:** Planned Construction 61,183; Constructed 55,120; Not Required 25,411; Not Assigned 25,204; Complex Planned 16,288; Complex Constructed 4,543. Only 32% of `Construction_End_Date` is non-empty.
5. **The MBPO report has only 277 rows:** it is a local sample (around subway stations), not a citywide survey, and the rows without a Ramp ID are parts of a Center Cut.
6. **The GTFS calendar is the currently valid timetable,** which is not on the same time dimension as the historical monthly availability data.

## 7. Not done

- Share of missing values, outliers or duplicate records inside each table were not checked (beyond what is mentioned above)
- The specific reasons for the 63 unmatched elevators in section 3 were not checked
- No statistical analysis was done

---

*(Original chapter: Round 2 checks, gaps and compliance inside the study area)*

Counting checks only; no modelling or inference.

## 8. Study-area definition (shared by all counts below)

Study area = **Manhattan north of 110 St** ∪ **400 m around each of the three hospitals**, with the requirement that the data's Borough field is Manhattan.

| Item | Method |
|---|---|
| 110 St boundary line | A straight line was fitted to the coordinates of 81 corners at 110 St / Central Park North in the ramp table (bearing -29°, residual standard deviation 8 m); everything north of the line counts as "north". At first the line joining the 1 and 6 line 110 St stations was used, but the 2/3 line 110 St station is 104 m off that line, so the ramp-fitted line was used instead. The two lines differ by 46 ramps and by nothing for elevators |
| Ramps on the boundary | Ramps at the corners on both sides of 110 St itself: the north side counts, the south side does not |
| Hospital coordinates | Geocoded by address with OpenStreetMap Nominatim: Harlem Hospital (506 Lenox Ave) 40.8147, -73.9393; NYP/Columbia Irving Medical Center (622 W 168th St) 40.8410, -73.9407; Mount Sinai Morningside (1111 Amsterdam Ave) 40.8052, -73.9614 |
| 400 m | A **single coordinate point** per hospital, 400 m straight-line distance. The real campus is a cluster of buildings, Columbia's campus in particular is large, and a buffer around building outlines would give a larger area and slightly higher counts |
| Effect of the hospital buffer | All three hospitals are north of 110 St, so the buffer adds only a little south of Mount Sinai Morningside (113 St): elevators +0, ramps +10, MBPO +0 |

## 9. Of the study-area elevators, how many have no record in the availability table

Elevator = `Elevator or Escalator = Elevator` in the asset inventory; coordinates are the inventory's X/Y (swapped and treated as latitude/longitude).

| Indicator | Value |
|---|---|
| Manhattan elevators in the inventory | 221 |
| Elevators in the study area | **48** |
| of which have a record in the availability table (any month) | 37 |
| **of which have no record at all** | **11 (22.9%)** |
| of which have no record in the latest month (2026-09) | 11 (the same set, not just the latest month missing) |

Composition of the 11 elevators without records:
- **6** (EL147, EL150, EL151, EL152, EL153, EL155): the inventory has no station name or Station MRN for them; status In Service, NYCT-owned and maintained. All 6 study-area elevators lacking a station number are here, so the missing station information in the inventory may be what prevents the link; the reason has not been checked
- **3** (EL166X, EL167X, EL169X): 137 St-City College station, maintained by a Private Contractor, not NYCT-owned, status Installed-Functioning-Out of Service
- **EL520**: 137 St-City College station, maintained by a Third-Party Contractor
- **EL156**: Dyckman St station, NYCT-maintained, In Service

Elevators within 400 m of a hospital: Harlem Hospital 2, NYP/Columbia 7, Mount Sinai Morningside 0; all are included in the 48 above, and the missing-record status of these 9 was not split out. The elevator nearest the 110 St line is 1.15 km away, so the boundary definition has no effect on the elevator results.

Details are in [study_area_elevators.csv](../data/clean/study_area_elevators.csv).

## 10. Of the study-area ramps, how many have a completion date in Program Progress

Ramp = one row of Ramp Locations (one ramp), joined to Program Progress by `CornerID` (CornerID is unique in Progress, so the join creates no duplicate rows). The completion date in Progress is at corner level, so several ramps on one corner share one date.

| Indicator | Ramps | Share of study-area ramps |
|---|---|---|
| Study-area ramps | **6,647** (on 3,874 corners) | 100% |
| No matching corner in Progress | 1 | |
| **With a completion date** | **2,011** | 30.3% |
| of which completed **on or after 1 February 2020** | **1,429** | 21.5% (71.1% of those with a date) |
| of which completed in January 2020 | 58 | |
| of which completed before January 2020 | 524 | |

"After January 2020" is computed here as ≥ 2020-02-01 (January excluded). Including January it would be 1,487. Using the Ramp Locations collection cut-off of 2020-01-29 as the boundary, it is 1,437.

Counted by corner: of the 3,874 corners, 1,150 have a completion date, of which 818 are from 2020-02 on.

Completion dates by year (ramps): 2014–2016 total 20; 2017 71; 2018 214; 2019 219; 2020 448; 2021 121; 2022 102; 2023 69; 2024 413; 2025 91; 2026 243.

Things to note:
- Of the 2,011 ramps with a completion date, the status is Constructed for 1,834 and Complex Constructed for 116, but **61** have the status Complex Planned Construction (35), Planned Construction (25) or Not Assigned (1); that is, a date does not always mean "built"
- Ramp Locations was collected in 2017–2020, so for ramps completed from 2020-02 on, the measured data describe the state **before** completion
- Counted from the Progress side, the study area has 4,766 corners (3,874 of them in Ramp Locations and another 892 with no survey record), of which 1,250 have a completion date and 907 are from 2020-02 on

## 11. MBPO report: rows that can be judged for compliance, compliant rows, rows in the study area

"Can be judged" = `Compliant` is true or false. "Compliant" = `Compliant = true`.

| Indicator | Rows |
|---|---|
| Total MBPO rows | 277 |
| **Can be judged** | **248** |
| of which **compliant (true)** | **14** (5.6% of those that can be judged) |
| of which non-compliant (false) | 234 |
| Cannot be judged (Compliant empty) | 29 |

All 29 rows that cannot be judged are rows with Center Cut = YES and no Ramp ID, where the Compliant column is empty.

**Rows in the study area:**

| Definition | Study-area rows | Can be judged | Compliant |
|---|---|---|---|
| **Joined to ramp coordinates by Ramp ID** | **48** | 48 | **3** |
| By station name (125 St, 135 St, 168 St, 175 St, 207 St, Dyckman St) | 53 | 50 | 3 |

- Of the 277 rows, 199 have a Ramp ID, and 198 of those can be joined to Ramp Locations coordinates (1 ID cannot be found). The other 78 rows have no Ramp ID and cannot be located by coordinates
- The two definitions differ by 5 rows: 3 rows at 135 St and 1 row at 168 St have no Ramp ID (counted by station name), and 1 more row at 168 St has a Ramp ID joined to a ramp at 40.55°N (on Staten Island), which **looks like a mistyped ID**; it is excluded by the coordinate definition and included by the station-name definition
- The 3 compliant rows in the study area: 2 at 207 St station and 1 at Dyckman St station
- The other 22 stations (including 4 stations with no Ramp ID at all: 66 St-Lincoln Center, 72 St Broadway, Chambers St and Roosevelt Island) are by station name all south of 110 St and not in the study area

## 12. ADA station counts of the MTA station table (by borough), compared with the MTA website

**Station table (`39hk-dx4f`, updated 2026-11-11)**, one row per station per line, 496 rows:

| Borough | ADA=1 (fully accessible) | ADA=2 (one direction only) | Total ADA rows | ADA=0 |
|---|---|---|---|---|
| Manhattan (M) | 65 | 5 | 70 | 83 |
| Brooklyn (Bk) | 44 | 2 | 46 | 123 |
| Queens (Q) | 28 | 1 | 29 | 54 |
| Bronx (Bx) | 23 | 0 | 23 | 47 |
| Staten Island (SI) | 6 | 0 | 6 | 15 |
| **Total** | **166** | **8** | **174** | **322** |

**MTA website (mta.info/accessibility/stations, page marked Updated Oct 12, 2026)**, the "Quick Reference Station List", parsed from the page HTML:

| Borough | Website entries | of which one direction only | De-duplicated by name | Station table de-duplicated by Complex ID |
|---|---|---|---|---|
| Manhattan | 58 | 5 | 50 | 50 |
| Brooklyn | 39 | 2 | 36 | 38 |
| Queens | 26 | 1 | 26 | 25 |
| Bronx | 21 | 0 | 21 | 21 |
| Staten Island Railway | 6 | 0 | 6 | 6 |
| **Total** | **150** | **8** | **139** | **140** |

**Conclusions:**
1. **The raw numbers do not match, but the reason is a different counting unit.** The website has 150 "station name + line" entries, and the station table has 174 station-line rows. The website merges several lines of the same station into one entry (for example one for Times Sq-42 St against 4 rows in the station table)
2. **A one-by-one check found no contradiction in accessibility status:** every website entry can be found as an ADA row in the station table, and all 174 ADA rows of the station table map to website entries. Three entries (Times Sq-42 St, West 4 St-Washington Sq, Park Place) needed manual matching because the station names are abbreviated differently (the station table has Times Sq / W 4 St-Wash Sq / Park Pl)
3. **One-direction accessibility agrees exactly:** the website's 8 "uptown only / downtown only / one direction" entries (Manhattan 28 St, 49 St, 50 St, 86 St, Spring St; Brooklyn Hoyt St, Wilson Av; Queens Court Sq-23 St) match the 8 ADA=2 rows of the station table, with the same directions
4. **Cases that differ by line also agree:** the website says that at Union Sq only L/N/Q/R/W are accessible and 4/5/6 are not; at Canal St only the 6; at 168 St only A/C. The corresponding station-table rows are 1/1/0, 1/0 and 1/0
5. **Reverse check:** for entries the website says are accessible, no corresponding line is marked ADA=0 in the station table. The one hint is Pelham Pkwy, which is really two different stations (the website means the White Plains Rd line 2/5; the Dyre Av line 5 Pelham Pkwy was never accessible), so it is not a difference
6. **Small differences remain under the de-duplicated counts:** Brooklyn 38 in the station table versus 36 on the website, Queens 25 versus 26. I did not trace each one; the complexes may be merged differently. Every entry has a matching row, so no station is missing
7. The note "rush hours only" for Rockaway Park-Beach 116 St on the website refers to the S line running only at rush hours; it is not an accessibility status, and the station table has ADA=1 for that station, so there is no difference

**Limitations:** the website list was parsed by me from the page HTML and is not an official data download; the website page date (2026-10-12) is a month earlier than the station table (2026-11-11). The website covers only the subway and the Staten Island Railway.

## 13. Files produced in this round

- [study_area_elevators.csv](../data/clean/study_area_elevators.csv): detail of the 48 elevators in the study area

---

*(Original chapter: Round 3, study-area ADA station table)*

## 14. Output of this round

| File | Content |
|---|---|
| [station_table.csv](../data/clean/station_table.csv) | **Main table**, one row per study-area ADA station, 10 rows and 30 columns |
| [elevator_detail.csv](../data/clean/elevator_detail.csv) | Per-elevator detail (the 48 study-area elevators + the elevators linked to them), including 12-month 24-hour / AM peak / PM peak availability, number of outages, whether the elevator enters the probability model and why |
| [elevators_assigned_by_coordinates.csv](../data/clean/elevators_assigned_by_coordinates.csv) | Result of assigning the 6 elevators without station information to stations by coordinates, **for you to check** |
| [hospitals_map.png](../outputs/hospitals_map.png) | The three hospital coordinates with their 400 m circles, the 110 St boundary line, the study area and the 10 ADA stations |

The folder also contains `fetch_live_outages.py`, `live_fetch.out` and `live_log.csv`, which I did not create and did not touch.

## 15. Which stations go in the table

The study area contains 35 station rows, of which **10** are ADA stations (ADA=1 or 2); all are ADA=1 with both `ADA Northbound` and `ADA Southbound` equal to 1, and none is one-direction only. Two hospitals have one station inside their 400 m circle (168 St A/C in the NYP/Columbia circle and 135 St 2/3 in the Harlem Hospital circle), but both stations were already north of 110 St, so the hospital buffer added no station. Mount Sinai Morningside has no ADA station inside its circle.

Stations in the table: Inwood-207 St (A), Dyckman St (1), 181 St (A), 175 St (A), 168 St (A C), Harlem-148 St (3), 137 St-City College (1), 135 St (2 3), 125 St (A C B D), 125 St (4 5 6).

## 16. How elevators are assigned to stations

- **Key:** the asset inventory's `Station MRN` (leading zeros removed) = the station table's `Station ID`. Section 4 verified that these two numbers agree.
- **27** elevators map to these 10 stations, **of which 23 enter the probability model**.
- Distance check: the elevator in the model farthest from its station's coordinates is 212 m away (EL517/EL518 at 181 St), median 73 m. The only ones over 400 m are EL166X/167X/169X at 137 St (446 m), and these three are not in the model (see section 19).
- Station names in the inventory agree with the station table (for example `125ST-8AV-A/B/C/D` ↔ 125 St A C B D).

### The 6 elevators without station information (please check)

Nearest station by coordinates (using the station table's GTFS coordinates, straight-line distance). Details are in `elevators_assigned_by_coordinates.csv`.

| Elevator | Inventory note | Nearest station (distance) | Second nearest | Nearest ADA station (distance) |
|---|---|---|---|---|
| EL147 | Relay Building A | 207 St, 1 line (202 m) | Inwood-207 St A (473 m) | Inwood-207 St (473 m) |
| EL150 | Passenger Elevator At 207Th Street Yard | 215 St, 1 line (213 m) | Inwood-207 St A (320 m) | Inwood-207 St (320 m) |
| EL151 | Freight Elevator At 207Th Street Yard | 215 St, 1 line (233 m) | Inwood-207 St A (576 m) | Inwood-207 St (576 m) |
| EL152 | Freight Elevator At 207Th Street Yard | 215 St, 1 line (144 m) | Inwood-207 St A (388 m) | Inwood-207 St (388 m) |
| EL153 | Freight Elevator At 207Th Street Yard | 215 St, 1 line (156 m) | Inwood-207 St A (356 m) | Inwood-207 St (356 m) |
| EL155 | Freight Elevator At 207Th Street Yard | 215 St, 1 line (265 m) | Inwood-207 St A (378 m) | Inwood-207 St (378 m) |

**Three points for you to note:**
1. Assigned to the nearest station, the 6 elevators fall on 215 St (5) and 207 St (1), two **non-ADA stations on the 1 line**, which are not in the ADA station table, so they do not appear in any row of station_table.csv.
2. The distances are 144–576 m, while the median distance from an in-station elevator to its station in the same table is 73 m. Judging from the notes, they are **freight/passenger elevators of the 207 St yard and a relay building**, not in-station paths. I think that even if they were forced onto the nearest ADA station (Inwood-207 St), they should not be included in that station's accessibility-path probability.
3. These 6 also have no record in the availability table. So I did not put them into any station's probability calculation, and only mentioned them in the `review_note` of the Inwood-207 St row. If you want them included, tell me which station they belong to and whether to treat them as series or parallel.

## 17. Availability definition

| Item | Method |
|---|---|
| Time window | Last 12 months: 2025-10 to 2026-09 (the latest month in the data is 2026-09) |
| Mean availability | Hour-weighted: sum of `24-Hour Hours Available` in the window ÷ sum of `24-Hour Total Hours`. Months with `Total Hours = 0` (215 rows) are not used |
| Unscheduled outages | Sum of `Unscheduled Outages` in the window |
| Other fields kept | AM peak and PM peak availability and total outages are in elevator_detail.csv but do not enter the probability calculation |
| Completeness | Of the 419 elevators with data in the window, 397 have all 12 months. Among the elevators in the model, EL519 (137 St) has only 5 months and EL144 (125 St A/C/B/D) only 9 months; this is noted in `review_note`, and their outage counts also cover only those months |

## 18. Elevators without availability records: no 100% fill

- For an elevator with no availability record at all, `elevator_avail_status` is **unknown**, and the availability and outage-count columns also say `unknown`; it is neither 1 nor 0.
- The whole-station probability comes in two versions, **filling only elevators without a record**; elevators with a record always use their own measured value:
  - `station_prob_mean_fill`: filled with the study-area mean **0.9787** (the simple mean of the 12-month availability of the 37 study-area elevators that have a record)
  - `station_prob_low_fill`: filled with a low value **0.9636** (the 10th percentile of the same 37 elevators)
- Reference distribution: for the 37 elevators with a record the minimum is 0.9490 and the median is 0.9807. If you want a more pessimistic value (such as the minimum), just say so.
- **The fill affects only one station:** among the 23 elevators in the model, only EL520 (137 St southbound) has no record. So the two columns differ only at 137 St (0.9502 vs 0.9356) and are the same for the other stations.
- These two fills are scenario assumptions, not estimates. An elevator without a record may differ systematically from those with a record (for example, maintained by a private contractor or not NYCT-owned), and a fill value cannot reflect that.

## 19. How series and parallel are computed

**Source of the structure:** each elevator in the asset inventory has these fields: whether it reaches the street (`Street Access`), whether it reaches mezzanine 1/2 (`Elevator Mezzanine 1/2 Access`), whether it reaches the platform (`Elevator Platform Access`), and the direction served (`Elevator Direction Serviced`: Both/Northbound/Southbound). I treated each elevator as an "edge" connecting the floors it stops at, and built a connectivity graph "street → mezzanine → northbound/southbound platform".

**Whole-station availability probability** = the probability that one can get from the street entrance to the platforms of **all ADA directions**. Because all 10 stations are ADA in both directions, both the northbound and southbound platforms must be reachable. Elevators are independent, and the on/off states of the elevators are enumerated exactly (at most 5 elevators per station), so series (required), parallel (any one is enough) and shared elevators (such as EL139 at 168 St, which is on both the northbound and the southbound path) are all handled correctly with no double counting.

**Structure and result for each station** (the paths are listed in the `access_paths` column of station_table.csv; `+` means series and `|` means parallel):

| Station | Path structure | Probability (mean fill / low fill) | Note |
|---|---|---|---|
| Inwood-207 St (A) | EL148 → EL149 in series | 0.9748 / 0.9748 | |
| Dyckman St (1) | southbound EL178; northbound EL178 + EL179 in series | 0.9695 / 0.9695 | EL156 not included (see below) |
| 181 St (A) | one of EL117, 118, 119 → northbound EL517 / southbound EL518 | 0.9847 / 0.9847 | entrance is inferred (see below) |
| 175 St (A) | EL123 → EL124 in series | 0.9868 / 0.9868 | |
| 168 St (A C) | EL139 → northbound EL140 / southbound EL141 | 0.9470 / 0.9470 | all three in series (EL139 shared), lowest of this batch |
| Harlem-148 St (3) | — | **empty (cannot be computed)** | no elevator in the inventory |
| 137 St-City College (1) | northbound EL519, southbound EL520, both must work | 0.9502 / 0.9356 | EL520 has no record, EL519 only 5 months of data |
| 135 St (2 3) | northbound EL180, southbound EL181, both must work | 0.9580 / 0.9580 | |
| 125 St (A C B D) | EL142 → northbound EL144 / southbound EL143 | 0.9662 / 0.9662 | EL144 has only 9 months of data |
| 125 St (4 5 6) | EL125 → EL126 in series | 0.9526 / 0.9526 | |

**Limitations of these results:**
1. **Independence assumption:** elevator failures are assumed to be unrelated. Elevators in the same station may be hit by the same event (power cut, construction, the same contractor), so the real whole-station probability may be overestimated.
2. **24-hour basis:** availability is an all-day average that includes scheduled outages, and it is not the same as availability during commuting hours.
3. **Elevators only:** fare gates, ramps, platform gaps and other accessibility links are not considered, nor are alternative routes (`Alternative Route` in the inventory is a text description and is not quantified).
4. **Availability ≠ the user's experience:** the probability is that of "the whole station being reachable at a random moment", not "the probability that one trip succeeds".

## 20. Points for you to review

There are 6 stations with `needs_review = yes` in the table, for these reasons:

| Station | Issue | What I did |
|---|---|---|
| **Harlem-148 St** | No elevator in the asset inventory maps to this station, and there is no inventory elevator within 500 m. This is a data gap, not "no elevator" | Probability left empty, no fill |
| **181 St (A)** | No elevator in the inventory reaches the street. The notes show that EL117–119 go "from the upper mezzanine to the lower mezzanine", and the upper mezzanine is at the street entrance at 184 St & Ft Washington Av | The entrance was set to mezzanine 2 (M2, the upper mezzanine); this is an inference, not given directly by the inventory |
| **Dyckman St (1)** | EL156 is linked to the station, but its note is "Freight Elevator At Dyckman Street/ Sub. Station" (a substation freight elevator) and it has no landing fields | Not included in the probability |
| **137 St-City College** | EL166X, EL167X and EL169X are linked to the station; their status is Out of Service, maintained by a private contractor, with no landing fields, and their coordinates are 446 m from the station | Not included in the probability; EL520 has no availability record and uses the fill value |
| **Inwood-207 St (A)** | 6 yard elevators are nearest to it (see section 16) | Not included in the probability |
| **125 St (A C B D)** | EL144 has only 9 months of data in the window | Computed as usual, with a note only |

## 21. Map

[hospitals_map.png](../outputs/hospitals_map.png): orange is Manhattan land north of 110 St (including Randalls Island and Marble Hill, which belong to Manhattan administratively), the dashed line is the fitted 110 St line, the red crosses are the three hospitals, the circles are the 400 m ranges, and the green triangles are the 10 ADA stations. The base-map boundary comes from the NYC Open Data Borough Boundaries (downloaded to `raw/borough_boundaries/`). The circles of all three hospitals are fully visible on the map, and the circle of Mount Sinai Morningside crosses the 110 St line.

**One thing seen on the map:** Randalls Island is also counted as "Manhattan north of 110 St" in the study area. There is currently no ADA station on that island, so it has no effect on this round's tables.

---

*(Original chapter: Round 4, 148 St elevator search, ADA stations near the hospitals, NYP/Columbia 30-minute isochrone)*

## 22. Elevators at 148 St (Harlem-148 St): not found in any data

In the station table this station has `Station ID = 436`, GTFS stop `301`, line 3, ADA=1. I searched every dataset with these keys plus the text "148 / Harlem".

| Data | Search scope | Result |
|---|---|---|
| Asset inventory (759 rows) | Full text of 44 columns including station name, Station MRN and Complex MRN | **No elevator.** 0 rows have a Station MRN or Complex MRN equal to 436, and the station names contain no 148 St / Harlem |
| Availability table (83,776 rows) | Station name, complex name, equipment number, Station MRN, Complex MRN | **None.** 0 rows. The other stations on the line (135 St, 3 Av-149 St and 9 other LWP stations) all have rows |
| Live equipment list (707 devices: 430 elevators + 277 escalators) | Station name, GTFS stop ID (301), MRN (436), Complex ID (436), service description, adjacent ADA stations | **None.** `elevatorsgtfsstopid=301`, `elevatormrn=436` and `stationcomplexid=436` all give 0 rows |
| Live current-outage list (182 entries) | Station name, equipment, service description | **None** |
| Station amenities dataset (71,290 rows, 2026-05 to 2026-10) | Station MRN 436 | The station has fare gates, countdown clocks, help points, OMNY vending machines and **1 ADA accessible fare gate each for entry and exit**, but the number of `ELEVATOR`-type amenities is **0** (in the same period 135 St 2/3 has 2 and Dyckman St has 3) |
| Station entrances dataset (2,120 rows) | Station ID 436 | Only **1 entrance, of type Station House**, and none of type Elevator (the entrances of 135 St 2/3 include 2 of type Elevator) |
| Search by coordinates (done in Round 3) | Inventory elevators within 500 m of the station | 0 |

**Where the text mentions 148 St (not as an elevator of 148 St):** in the inventory and the live list, the "alternative route" text of EL180/EL181 at 135 St says that when the elevator is out one can take the 3 line uptown to Harlem-148 St and transfer to a downtown 3 train back to 135 St. This shows that the MTA treats 148 St as a station that accessible passengers can use, but it has not registered any elevator for it. Also, in the live list the "next ADA station to the north" of the 135 St elevators lists only the 2 line's `434, 2` (3 Av-149 St), not the 3 line's 148 St.

**What can be concluded:** no 148 St elevator was found, consistently across all sources. Together with "has ADA fare gates, only one station-house entrance, and no Elevator-type amenity", the data are **consistent with** "the station can be entered without steps and without an elevator", but I cannot prove this from the data alone and have not checked on site. If the station does use an elevator to reach the platform, then all these datasets omit it.

Newly downloaded files: `raw/live_equipment/` (`equipments.json`, `outages.json`, from the MTA public endpoint `api-endpoint.mta.info/Dataservice/mtagtfsfeeds/`, downloaded 2026-11-11), `raw/mta_entrances/` (`i9wp-a4ja`), `raw/mta_amenities/` (`6yjv-fk7g`). Your live polling program now sits in `<LIVE_DIR>/`; I read only its directory listing and the start of the script, to confirm the endpoint address, and changed nothing and used none of its data; the live list was downloaded again by me.

## 23. ADA stations within 400 m of the three hospitals, and the nearest ADA station

ADA station = ADA of 1 or 2 in the station table, 174 citywide (not limited to the study area). Distance is the straight-line distance from the hospital point to the station's GTFS coordinates. In parentheses is the straight-line distance to the station's nearest entrance (entrances dataset). Details are in [hospital_ada_stations.csv](../outputs/hospital_ada_stations.csv).

| Hospital | ADA stations within 400 m | Nearest ADA station and straight-line distance |
|---|---|---|
| Harlem Hospital | **1**: 135 St (2 3), 136 m (entrance 118 m) | 135 St (2 3), 136 m. Second nearest Harlem-148 St (3), 1,047 m |
| NYP/Columbia Irving Medical Center | **1**: 168 St (A C), 100 m (entrance 110 m) | 168 St (A C), 100 m. Second nearest 175 St (A), 718 m |
| Mount Sinai Morningside | **0** | 125 St (A C B D), **1,003 m** (entrance 935 m). Second nearest 96 St (1 2 3), 1,559 m |

Additional notes:
- Within 400 m of NYP/Columbia there is also a non-ADA station, 168 St-Washington Hts (1 line, connected through non-ADA elevators to the A/C station, see the note in section 16)
- The only subway station within 400 m of Mount Sinai Morningside is 116 St-Columbia University (1 line), which is **not an ADA station**
- Single-point assumption: only one point is used per hospital, but the real campus is larger, so the "within 400 m" result is sensitive to the hospital's land boundary. The Columbia campus in particular is large, and measuring from the campus edge might bring more stations inside

---

*(Original chapter: Round 6, ADA check of the equipment list and the station-status time series)*

## 24. The ADA field in the equipment list (`nyct_ene_equipments.json`)

38 of the 48 study-area elevators can be found in the equipment list (the other 10 are not in the list, see section 23). The `ADA` field of these 38: **23 are Y and 15 are N**.

**The 15 elevators with ADA = N** (ADA = N in the list, and `ADA Compliant` in the asset inventory is also NO, so the two agree):

| Station (name in the list, line) | Elevators |
|---|---|
| 181 St (1 line) | EL107, EL108, EL109, EL110 ("mezzanine to bridge") |
| 168 St-Washington Hts (1 line) | EL111, EL112, EL113, EL114 ("transfer mezzanine to overpass for 1 train") |
| 190 St (A line) | EL115, EL116, EL120 |
| 191 St (1 line) | EL103, EL104, EL105, EL106 |

**Whether they are counted in the `station_table` probability: none of them.** In `elevator_detail.csv` the `in_probability_model` of these 15 is False, for the reason "station not in ADA station table": their stations (181 St, 168 St and 191 St on the 1 line, and 190 St) are not themselves ADA stations and are not among the 10 stations of station_table.

**In the other direction:** the `access_paths` of station_table contain 23 elevators in total, and **all can be found in the equipment list with ADA = Y**, so no elevator with ADA = N is mixed into the probability. These 23 are exactly the 23 with ADA=Y among the 38 above.

Note the same names for different stations: **181 St (A line)** in station_table and **181 St (1 line)** in the table above are two different stations; do not mix them up.

## 25. 181 St (A) entrance inference compared with the inventory: consistent, but still an inference

The earlier inference: EL117–119 connect the "upper mezzanine" and the "lower mezzanine", the street entrance joins the upper mezzanine, and EL517/518 connect the mezzanine to the platform. The comparison:

| Evidence | Content | Consistent? |
|---|---|---|
| Equipment-list `serving` | EL117/118/119: Upper mezzanine (**184 St & Ft Washington Av**) to lower mezzanine, both directions; EL517: Mezzanine to platform for Inwood-207 St-bound; EL518: Mezzanine to platform for Downtown and Brooklyn-bound | Consistent: the location of the upper mezzanine is written as a street intersection, EL117–119 are between the upper and lower levels, and only EL517/518 reach the platform |
| Equipment-list `redundant` | EL117/118/119 = 1, EL517/518 = 0 | Consistent: the three in parallel can replace one another, and each of the two platform elevators is unique |
| Equipment-list `alternativeroute` | EL117–119: "Use an adjacent elevator."; for EL517/518 the alternative route says to take a train to an adjacent station and transfer, when on the platform | Consistent |
| Asset-inventory fields | EL117–119: Street Access = NO, Mezzanine 1 = +, Mezzanine 2 = +, Platform = -; EL517/518: Street = NO, Mezz 1 = +, Platform = + | Consistent: EL117–119 connect the two mezzanine levels, EL517/518 connect the lower mezzanine and the platform, and no elevator is marked "street" |
| Coordinates (inventory X/Y after swapping) | EL117–119 at about 40.8528°N, 136–153 m north of the station point; EL517/518 at 40.8498°N, 212 m south of the station point | Consistent: 184 St is north of 181 St, so the upper-mezzanine elevators are in the north and the platform elevators in the south |

**What the inventory does not confirm directly:** neither the equipment list nor the asset inventory marks any elevator as a "street entrance", so the step "street into the upper mezzanine" is still derived from "184 St & Ft Washington Av" in `serving` and is not given by a field. `nextadanorth` / `nextadasouth` are empty for these elevators and do not help. Conclusion: **nothing contradicts the inference, but this point counts only as "consistent with the inventory", not "confirmed by the inventory".**

---

*(Original chapter: Round 7, Harlem-148 St flag and "estimated return time has passed")*

## 26. Harlem-148 St marked "no elevator dependency"

- `station_table.csv` gets a new column `elevator_dependency`: "no elevator dependency (not verified on site)" for Harlem-148 St and "yes" for the other 9 stations.
- Both `station_prob_mean_fill` and `station_prob_low_fill` of Harlem-148 St are changed to **1** (they were empty). `fill_mean_used` and `fill_low_used` keep their values; they are study-area-wide fill references and have no practical effect on this station.
- `review_note` states the basis: in the MTA station-amenities dataset the station has ADA accessible fare gates (1 for entry and 1 for exit) but the number of `ELEVATOR`-type amenities is 0, the station-entrances dataset lists only 1 Station House entrance, and no elevator for this station appears in the asset inventory, the availability table or the live equipment list (see the section "Elevators at 148 St: not found in any data" above). **This is only an inference from data and has not been checked on site**; if the station actually uses an elevator to reach the platform, the 1 for this station is optimistic. `needs_review` stays "yes".
- In `station_status_timeseries.csv` the `available` of Harlem-148 St is now **1** (it was empty), and the `elevator_dependency` column is marked the same way, so it is not affected by elevator outages.
- The original files were backed up: `station_table.pre_harlem.csv`, `station_status_timeseries.pre_v2.csv`. Because columns were added, the time series was regenerated from all 6 snapshots; apart from Harlem-148 St and the new columns, the content is the same as the old version.

---

*(Original chapter: Round 11, the 14 stations that could not be modelled, Monte Carlo after the repair, final summary)*

Before writing I confirmed again that checks.md had not changed since the last chapter was appended (1503 lines). Append only; section numbers continue from the previous chapter, starting at **57**.

| File | Content |
|---|---|
| [final_summary.csv](../outputs/final_summary.csv) | Final summary table, one row per hospital, with the unit, direction and time basis in the column names |
| [final_summary.md](final_summary.md) | One-page note |
| [station_model_fixes.csv](../data/clean/station_model_fixes.csv) | Investigation and handling record of 16 stations (14 that could not be modelled + 2 that were corrected): the earlier status and reason, the handling, and the paths before and after the repair |
| [mc_manhattan_summary_fixed.csv](../outputs/mc_manhattan_summary_fixed.csv), [mc_manhattan_single_failure_fixed.csv](../outputs/mc_manhattan_single_failure_fixed.csv) | Monte Carlo summary and single-point failures after the repair (the old results `mc_manhattan_*.csv` are kept, not overwritten) |

## 27. Why those 14 stations could not get an elevator model, and which could be repaired

**The causes fall into two kinds:** for 6 stations the asset inventory has **no elevator under the station's name**; 8 stations have elevators, but the fields are incomplete (no direction served, or no mezzanine-to-platform link), so the "street – mezzanine – platform" path cannot be built.

**What I used to repair them:** the MTA live equipment list (`nyct_ene_equipments.json`, downloaded 2026-11-11 in the chapter "148 St elevator search", in `raw/live_equipment/`). For each elevator it gives the service description (`serving`, `shortdescription`), the lines served (`linesservedbyelevator`) and the stations it belongs to (`elevatorsgtfsstopid`; one elevator can belong to several stops). **Criterion:** if the description is enough to determine which levels the elevator connects (street / mezzanine / platform of which direction) and the elevator's stop ID matches the target station, it is added; if the description is missing or vague, it is not. Direction mapping: uptown = northbound platform (PN), downtown = southbound platform (PS). This mapping agrees with the GTFS convention on the trunk lines 1/2/3, 2/5, 4, B/D and N/Q/R/W; I did not check it line by line.

| Station (line) | Borough | Why it could not be modelled | What was found in the data | Handling | Paths used (elevator numbers; + series, \| parallel) |
|---|---|---|---|---|---|
| 72 St (1/2/3) | Manhattan | Elevators have a street flag but no direction served | Live list: EL239 "Street to Northbound platform", EL240 "Street to Southbound platform" | **Added** | Northbound EL239; southbound EL240 |
| 96 St (1/2/3) | Manhattan | Same | EL146 "Street to uptown platform", EL145 "Street to downtown platform" | **Added** | Northbound EL146; southbound EL145 |
| 49 St (N/R/W) | Manhattan | 1 elevator without direction | EL268X "Street to uptown platform"; the station has ADA = 2, uptown only | **Added** | Northbound only, EL268X |
| 149 St-Hostos (2/5) | Bronx | No elevator under this station name in the inventory | The elevators are registered under the 4 line station of the same complex (Station MRN 390); the live list shows EL100–EL102 serving both stops 222 and 415 and lines 2/4/5 | **Added** | Northbound EL100+EL101; southbound EL100+EL102 |
| 161 St-Yankee Stadium (4) | Bronx | No elevator under this station name in the inventory | The elevators are registered under the B/D station (MRN 219); EL131 street to mezzanine, EL132 mezzanine to northbound 4 platform, EL133 mezzanine to southbound 4 platform | **Added** | Northbound EL131+EL132; southbound EL131+EL133 |
| Times Sq-42 St (1/2/3) | Manhattan | Elevator fields lack direction | Within the complex: EL231X (42 St & 7 Av) and EL619 (43 St & Broadway) are both "street to mezzanine, serving all lines in both directions"; EL233 mezzanine to uptown 1/2/3, EL232 mezzanine to downtown 1/2/3 and 7 | **Added** | Northbound (EL231X \| EL619)+EL233; southbound (EL231X \| EL619)+EL232 |
| Times Sq-42 St (7) | Manhattan | Only escalators under this station name in the inventory | EL232 to the 7 line platform | **Added** (assuming the 7 line platform shares EL232 for both directions) | Both directions (EL231X \| EL619)+EL232 |
| Times Sq-42 St (N/Q/R/W) | Manhattan | Mezzanine-to-platform path missing | EL230 mezzanine to uptown N/Q/R/W, EL229 mezzanine to downtown N/Q/R/W | **Added** | Northbound (EL231X \| EL619)+EL230; southbound (EL231X \| EL619)+EL229 |
| 59 St-Columbus Circle (1) | Manhattan | No elevator under this station name in the inventory | The elevators are registered under the A/C/B/D station (MRN 161). EL280 street to uptown 1 platform, EL276X street to mezzanine, EL278 mezzanine to uptown A/B/C/D, EL279 connects the uptown 1 platform and the uptown A/B/C/D platform, EL277 and EL622 mezzanine to the downtown platform | **Added** (1 alternative path is inferred) | Northbound EL280 \| EL276X+EL278+EL279 (the latter inferred); southbound EL276X+EL277 \| EL276X+EL622 |
| **Corrected: 161 St (B/D)** | Bronx | Already modelled, but EL132 and EL133 had been mixed in | These two serve the **4 line** and had been taken as parallel backups of the B/D platform elevators | **Corrected** | Northbound EL131+EL135; southbound EL131+EL134 (EL132 and EL133 had been added as alternatives) |
| **Corrected: 59 St-Columbus Circle (A/C/B/D)** | Manhattan | Already modelled, but the street entrance EL276X had not entered the model because of a missing field | The platform elevators EL278, EL279 and EL280 had been treated as independent backups of each other, which was optimistic | **Corrected** | Northbound EL276X+EL278 \| EL279+EL280 (the latter inferred); southbound EL276X+EL277 \| EL276X+EL622 |
| Times Sq-42 St (S) | Manhattan | No elevator under this station name in the inventory | The live list has only the entrance elevators shared by the complex (the line list includes S), and no elevator to the S platform | **Cannot be added** | The elevator connection to the S platform is not stated in the data (it may need no elevator, but the data do not say) |
| 42 St-Port Authority (A/C/E) | Manhattan | The inventory elevators have no usable platform fields | EL291X street to intermediate level, EL290X level to mezzanine, EL288X/EL289X bus terminal to mezzanine, all "A/C/E both directions" | **Cannot be added** | No elevator is described from mezzanine to the A/C/E platforms, so the street-to-platform chain is incomplete |
| 51 St (6) | Manhattan | Mezzanine-to-platform path missing | The descriptions are of the underground passage between the uptown and downtown 6 platforms (EL201, EL202) and street to mezzanine (EL203X) | **Cannot be added** | How the mezzanine reaches each 6 platform is not clear; the passage description is vague |
| W 4 St-Wash Sq (A/C/E) | Manhattan | Street-entrance-to-platform fields missing | EL334/EL335 connect the A/C/E platform with the transfer mezzanine and B/D/F/M; EL333 "street to upper platform level" | **Cannot be added** | It is vague which level of A/C/E platform the street elevator reaches |
| Harlem-148 St (3) | Manhattan | No elevator in the inventory | No elevator in the asset inventory, availability table, live equipment list, station-amenities dataset or entrances dataset (chapter "148 St search") | **Cannot be added, and there is nothing to add** | Keeps the earlier flag: "no elevator dependency" (**not verified on site**) |

**Result: 9 added, 2 old models corrected, 5 cannot be added.** The number of stations that can get an elevator model rose from 45 to **54**, and the number of elevators from 128 to **132**. The elevators without availability records are still **EL132, EL133 and EL520** (handled with the two fills, mean fill 0.9787 and low fill 0.9636). After the repair, every newly used elevator was checked: by the stop IDs in the live list it does belong to the corresponding station.

**Share of arrived-at ADA stations that can be perturbed** (scenario 4, ADA station records reached within 30 minutes):

| Hospital / direction | ADA stations reached | Perturbed | Share (before) | of which Manhattan stations | Perturbed | Share (before) |
|---|---|---|---|---|---|---|
| Harlem reverse | 40 | 36 | **90%** (70%) | 26 | 22 | 85% (62%) |
| Harlem forward | 40 | 37 | **92%** (70%) | 32 | 29 | 91% (69%) |
| NYP/Columbia reverse | 39 | 35 | **90%** (72%) | 32 | 28 | 88% (72%) |
| NYP/Columbia forward | 22 | 20 | **91%** (73%) | 17 | 15 | 88% (71%) |
| Mount Sinai reverse | 15 | 14 | **93%** (67%) | 13 | 12 | 92% (69%) |
| Mount Sinai forward | 10 | 10 | **100%** (70%) | 9 | 9 | 100% (67%) |

---

## Appendix: old and new section numbers

| New section | Original chapter | Original section | Title |
|---|---|---|---|
| 1 | Data health check, checks.md | 1 | Dataset overview |
| 2 | Data health check, checks.md | 2 | Column names |
| 3 | Data health check, checks.md | 3 | Match rate of elevator numbers (Equipment Code) |
| 4 | Data health check, checks.md | 4 | Match rate of station / complex keys |
| 5 | Data health check, checks.md | 5 | Match rate of the ramp tables |
| 6 | Data health check, checks.md | 6 | Other things to watch |
| 7 | Data health check, checks.md | 7 | Not done |
| 8 | Round 2 checks: gaps and compliance inside the study area | 8 | Study-area definition (shared by all counts below) |
| 9 | Round 2 checks: gaps and compliance inside the study area | 9 | Of the study-area elevators, how many have no record in the availability table |
| 10 | Round 2 checks: gaps and compliance inside the study area | 10 | Of the study-area ramps, how many have a completion date in Program Progress |
| 11 | Round 2 checks: gaps and compliance inside the study area | 11 | MBPO report: rows that can be judged for compliance, compliant rows, rows in the study area |
| 12 | Round 2 checks: gaps and compliance inside the study area | 12 | ADA station counts of the MTA station table (by borough), compared with the MTA website |
| 13 | Round 2 checks: gaps and compliance inside the study area | 13 | Files produced in this round |
| 14 | Round 3: study-area ADA station table | 14 | Output of this round |
| 15 | Round 3: study-area ADA station table | 15 | Which stations go in the table |
| 16 | Round 3: study-area ADA station table | 16 | How elevators are assigned to stations |
| 17 | Round 3: study-area ADA station table | 17 | Availability definition |
| 18 | Round 3: study-area ADA station table | 18 | Elevators without availability records: no 100% fill |
| 19 | Round 3: study-area ADA station table | 19 | How series and parallel are computed |
| 20 | Round 3: study-area ADA station table | 20 | Points for you to review |
| 21 | Round 3: study-area ADA station table | 21 | Map |
| 22 | Round 4: 148 St elevator search, ADA stations near hospitals, NYP/Columbia 30-minute isochrone | 22 | Elevators at 148 St (Harlem-148 St): not found in any data |
| 23 | Round 4: 148 St elevator search, ADA stations near hospitals, NYP/Columbia 30-minute isochrone | 23 | ADA stations within 400 m of the three hospitals, and the nearest ADA station |
| 24 | Round 6: ADA check of the equipment list and the station-status time series | 30 | The ADA field in the equipment list (`nyct_ene_equipments.json`) |
| 25 | Round 6: ADA check of the equipment list and the station-status time series | 31 | 181 St (A) entrance inference compared with the inventory: consistent, but still an inference |
| 26 | Round 7: Harlem-148 St flag and "estimated return time has passed" | 34 | Harlem-148 St marked "no elevator dependency" |
| 27 | Round 11: the 14 stations that could not be modelled, Monte Carlo after the repair, final summary | 57 | Why those 14 stations could not get an elevator model, and which could be repaired |
