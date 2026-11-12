# Isochrones, residents, Monte Carlo and final summary (checks_isochrone)

Covers: the NYP isochrone, buses, the three hospitals, reverse direction and time averaging, the Manhattan clipping, the Monte Carlo, and the final summary. Section numbers are renumbered inside this file; the original file is kept in `archive/checks_original.md`, and a table at the end maps new to old section numbers. All numbers are preliminary.

---

*(Original chapter: Round 4, 148 St elevator search, ADA stations near the hospitals, NYP/Columbia 30-minute isochrone)*

## 1. NYP/Columbia 30-minute isochrone

Map: [nyp_isochrone_30min.png](../outputs/nyp_isochrone_30min.png); values: [nyp_isochrone_summary.csv](../outputs/nyp_isochrone_summary.csv).

### Results

> **Correction (see section 5 of docs/checks_live.md):** the "anyone" area of 30.75 km² in this section is too small; after the fix it is 30.95 km², because of a bug in the code of the previous round. The 17.58 km² for "ADA only" is not affected. The ratio is still about 57%.

| Scenario (weekday 08:00 departure, 100 m buffer) | Area covered | Reachable street length | Station records / station groups reached |
|---|---|---|---|
| **Anyone (all subway stations)** | **30.75 km²** | 450.7 km | 61 / 55 |
| **ADA stations only** | **17.58 km²** (57% of anyone) | 246.8 km | 14 / 11 |
| Walking only (no subway) | 7.99 km² | 134.0 km | 0 |

Sensitivity (area in km², anyone / ADA only):

| Condition | Anyone | ADA only | ADA as share of anyone |
|---|---|---|---|
| 08:00, 100 m buffer (baseline) | 30.75 | 17.58 | 57% |
| 08:00, 50 m buffer | 25.80 | 14.37 | 56% |
| 12:00, 100 m buffer | 37.24 | 19.15 | 51% |
| 12:00, 50 m buffer | 31.77 | 15.84 | 50% |

How to read it:
- The area difference at the 08:00 baseline is 13.17 km² (30.75 − 17.58). With 12:00 or a 50 m buffer, the ADA share of anyone stays between 50% and 57%, so the order of magnitude, "ADA-only stations give somewhere between about half and four-tenths less", is fairly stable
- On the map, the places that ADA-only travellers cannot reach are mainly: a large area south of 125 St along the west-side 1 line, and several areas in the northern Bronx and east of the Harlem River. The reason is that most stations on these routes are not ADA stations (for example 168 St-Washington Hts on the 1 line is not). This is what the map shows; I did not attribute it station by station
- ADA-only travellers on the A express reach 125 St (15.0 minutes), 59 St-Columbus Circle (23.5 minutes) and 42 St-Port Authority (26.5 minutes); near Times Sq and 72 St they are already close to 30 minutes, so little walking time is left, which is why the blue area at the southern end is small
- "Station records" are counted by GTFS parent stop, so one station group can have several records. Stations reached after more than 30 minutes are not counted

### Assumptions and method used

**Departure and time**
- Origin: the single coordinate point of NYP/CUIMC (40.8410, -73.9407, i.e. 622 W 168th St), snapped to the nearest street node; the snapping distance of 58 m is counted as walking time
- Departure time: weekday 08:00, **this single departure time only**, with no averaging over several times. Subway headways affect the result; the 12:00 area is 21% larger than at 08:00, which shows some sensitivity to the departure time
- Total time 30 minutes = walk from the origin + waiting + riding + transfers + walk after getting off

**Transit (GTFS)**
- MTA `gtfs_subway.zip`, weekday (`Weekday`) service, 8,498 trips and 207 running patterns. The timetable is valid from 2026-11-01 to 2027-05-15
- It is the **scheduled timetable**; real-time delays, outages and temporary re-routing are not considered
- **Subway and Staten Island Railway only.** No buses (such as M3, Bx7), no LIRR, Metro-North or ferries
- Transfers use only GTFS `transfers.txt`: in-station transfers of 180 seconds (463 records) and between-station transfers (150 records, such as Times Sq with 42 St-Port Authority). There are **no** street-level walking transfers (getting off and walking to another, unconnected station to board again)
- RAPTOR earliest-arrival algorithm, at most 7 rounds (6 transfers)
- Waiting: wait for the next train on arrival at the station, with no extra time to enter the station and no vertical movement time for fare gates, stairs or elevators; station locations use the GTFS parent-stop coordinates. Both groups are therefore slightly optimistic

**People using ADA stations only**
- They may board, alight and transfer only at ADA stations. At ADA=1 stations all platforms are usable; at ADA=2 (one direction only) stations only the accessible-direction platform is usable, judged from `ADA Northbound/Southbound` of the station table. 340 of the 992 platforms are usable
- They may ride through non-ADA stations (without getting off)
- GTFS transfers between two ADA stations are **also assumed accessible by default**, without checking each one
- **Elevator failures are not considered.** Usability is "the station is marked ADA, so it is usable"; the whole-station availability probability of Round 3 is not used (no modelling, as you asked)
- The walking part uses the same street network as for anyone, with no distinction between steps and curb ramps

**Walking network**
- Source: NYC Open Data Street Centerline (CSCL, `inkn-q76z`, 122,331 segments), downloaded to `raw/nyc_centerline/`
- OpenStreetMap Overpass was tried first, but fetching a 1.5 × 1.7 km block took 77 seconds, so covering the whole isochrone extent was not practical; CSCL was used instead
- Kept: streets, bridges (bridges whose names contain highway-like words such as PKWY, EXPY, HWY, DR are excluded), footpaths, alleys, step streets (258 segments), boardwalks. Excluded: highways, tunnels, driveways, ramps, ferries, streets under construction
- Extent: latitude 40.60–40.93, longitude -74.06 to -73.78; only segments entirely inside the extent are kept. 86,873 segments; the largest connected component holds 91.3% of the nodes and is the only one used (about 7,720 km)
- Walking speed 4.8 km/h (1.33 m/s) by segment length, with no gradient or crossing waits
- **No sidewalks, curb ramps or crossing signals.** Street centerlines stand in for sidewalks. Only some paths inside parks are included, which affects the areas around Fort Tryon, Highbridge and other parks
- Step streets are walkable for both groups. Strictly, wheelchair users cannot use steps, but you asked to leave ramps out for now, so I kept the network the same for both groups and let only the subway part differ
- Each segment is positioned by a straight line from start to end; the real length uses the length of the original polyline

**Area calculation**
- Reached streets (including segments reached halfway) are sampled every 5 m and dropped into a 10 m grid; land cells within ≤ 100 m of a reached street count as covered (50 m as a sensitivity check)
- The NYC borough boundary is used to remove water, so river surface is not counted
- Area is sensitive to the buffer width (100 m versus 50 m differs by about 5–6 km²), so **the relative difference between the two groups is more reliable than the absolute area**
- The dashed line on the map is the coverage of pure walking

### Checks done
1. **Plausible times:** 168 St to 125 St (A express) takes 15.0 minutes in total (including 2.4 minutes of walking, waiting and riding), 59 St-Columbus Circle 23.5 minutes, 42 St-Port Authority 26.5 minutes, consistent in order of magnitude with the real A express timetable
2. **Subset relation:** arrival times for ADA-only are never earlier than for anyone at any street node (0 violating nodes), so the blue area must lie entirely inside the orange area
3. **Station-count definition:** a counting error was fixed: after adding transfer times, some stations had arrival times over 30 minutes and were excluded. It has no effect on the area (street walking starts only from stations reached within ≤ 30 minutes)
4. Pure walking of 8.0 km² corresponds to a network distance of about 2.4 km, which is a reasonable order of magnitude around 168 St (hills and the riverbank limit the extent)

### Limitations
- A single origin, a single departure time and a scheduled timetable; no real-time data
- No buses; in the real world accessible travellers use buses a lot, so "ADA subway stations only" underestimates the real reachable range
- The street network contains no ramps and no curb-ramp information; the ramp data (Ramp Locations / Program Progress) are left for later
- The ADA flag comes from the station table and was not checked against elevator availability or actual paths
- Station entry and exit time is not included; both groups are optimistic, and for the ADA group elevator waits and longer accessible paths would make the gap larger

## 2. New files in this round

| File | Content |
|---|---|
| [nyp_isochrone_30min.png](../outputs/nyp_isochrone_30min.png) | Two-layer isochrone map |
| [nyp_isochrone_summary.csv](../outputs/nyp_isochrone_summary.csv) | Area, street length and station counts per scenario |
| [hospital_ada_stations.csv](../outputs/hospital_ada_stations.csv) | ADA stations within 400 m of the three hospitals and the nearest ADA station |
| `raw/live_equipment/`, `raw/mta_entrances/`, `raw/mta_amenities/`, `raw/nyc_centerline/` | Raw data downloaded in this round |

---

*(Original chapter: Round 5, adding buses (NYP/Columbia isochrone))*

Map: [nyp_isochrone_bus_4scenarios.png](../outputs/nyp_isochrone_bus_4scenarios.png); values: [nyp_isochrone_bus_summary.csv](../outputs/nyp_isochrone_bus_summary.csv). Apart from adding buses, the settings are the same as in section 1 (origin, 08:00 departure, 30 minutes, 4.8 km/h, CSCL street network, 100 m buffer, no ramps).

## 3. Results

Weekday 08:00 departure, 100 m buffer (baseline):

| Scenario | Area covered | Share of (1) | Subway station records reached | Bus stops used as walking origins |
|---|---|---|---|---|
| (1) Anyone, subway only | **30.95 km²** | 100% | 61 | 0 |
| (2) ADA subway stations only | **17.59 km²** | 57% | 14 | 0 |
| (3) Anyone, subway + bus | **36.51 km²** | 118% | 76 | 1,170 |
| (4) ADA subway stations only, plus bus | **23.79 km²** | 77% | 22 | 759 |

**Relative ratio between the two groups** (ADA group ÷ anyone):

| Comparison | 08:00 (100 m) | 08:00 (50 m) | 12:00 (100 m) | 12:00 (50 m) |
|---|---|---|---|---|
| Subway only: (2) ÷ (1) | **57%** | 55% | 51% | 50% |
| Subway + bus: (4) ÷ (3) | **65%** | 64% | 57% | 55% |

**Gain from adding buses:**

| | 08:00 | 12:00 |
|---|---|---|
| Anyone: (3) − (1) | +5.56 km² (+18%) | +3.35 km² (+9%) |
| ADA group: (4) − (2) | +6.20 km² (+35%) | +3.79 km² (+20%) |

Also at 08:00: (4) ÷ (2) = 135%, (3) ÷ (2) = 208%; at 12:00 the area of (4) (22.96 km²) is actually smaller than at 08:00 (23.79 km²), while (3) at 12:00 (40.65 km²) is larger than at 08:00.

How to read it:
1. **Buses narrow the gap between the two groups but do not remove it.** At 08:00 the ADA group's share of anyone rises from 57% to 65%, and the absolute gap falls from 13.4 km² to 12.7 km². At 12:00 the share goes from 51% to 57%.
2. **Buses help the ADA group more in relative terms** (+35% versus +18%), because they have fewer subway options and buses fill the gap.
3. **The added area falls mainly in the Bronx.** Split by borough (08:00, km²):

| Scenario | Manhattan | Bronx | of which Manhattan north / south of 110 St |
|---|---|---|---|
| (1) | 22.53 | 8.43 | 14.88 / 7.66 |
| (2) | 15.18 | 2.42 | 13.03 / 2.15 |
| (3) | 23.75 | 12.78 | 15.65 / 8.09 |
| (4) | 17.54 | 6.26 | 14.96 / 2.58 |

   Of the 5.56 km² that anyone gains from buses, the Bronx accounts for 4.35 and Manhattan for 1.22. Of the 6.20 km² the ADA group gains, the Bronx accounts for 3.84 and Manhattan for 2.36 (of which 1.93 north of 110 St). Neither Brooklyn nor Queens is reached within 30 minutes.
4. The two starkest contrasts near the study area: south of 110 St in Manhattan the ADA group has only 2.15 km² (anyone 7.66), and only 2.58 km² after adding buses. Buses help the ADA group mainly in Manhattan north of 110 St and in the Bronx.
5. **Sensitivity:** the ratio changes with the departure time and the buffer width, but in the same direction, within about 50%–65%. The 12:00 result is lower, possibly because there are fewer buses at midday (at 08:00 there are 1,170 bus stops used as walking origins and at 12:00 1,254, not much different, so different transfer combinations are more likely); I did not check the reason one by one.

### Correction to the previous round's result

On re-verification I found **a bug in the previous round's code**: when the "arrival times at stations" are used as the starting points of street walking, and several stations snap to the same street node, I used assignment and kept the last value written, not the earliest arrival. As a result, 3 street nodes in the "anyone" scenario (each with 2 reached stations) took the later time, by up to 180 seconds.

- Verification: the old way of writing reproduces the previous round's result exactly, and the difference disappears after taking the minimum. Everything in the previous round other than buses (RAPTOR itself, the station arrival times) is identical.
- Effect: the "anyone" area 30.75 → **30.95 km²** (+0.20, of which 0.12 comes from the bug and 0.08 from alignment differences caused by the changed extent of this round's grid); ADA group 17.58 → **17.59 km²** (not affected, because there are no coinciding nodes); the ratio 57.2% → **56.8%**, so the conclusion is unchanged.
- The sensitivity numbers in section 1 (12:00 at 37.24 / 19.15, the 50 m buffer) have the same small deviation. This section was fully recomputed with the corrected code, so please use section 3.

## 4. Bus data: which feeds are used, and whether data for other boroughs is needed

MTA bus GTFS is split by "the borough the route belongs to", with download addresses like `https://rrgtfsfeeds.s3.amazonaws.com/gtfs_<borough>.zip`. They are downloaded to `raw/gtfs_bus/`.

| Feed | Status | Note |
|---|---|---|
| `gtfs_m` Manhattan | **Used** | 19 routes stop in Manhattan north of 110 St: M1, M2, M3, M4, M5, M7, M10, M11, M15, M15+, M35, M60+, M98, M101, M102, M103, M104, M116, M125 |
| `gtfs_bx` Bronx | **Used (required for upper Manhattan)** | 15 routes stop in upper Manhattan: Bx3, Bx6, Bx6+, Bx7, Bx9, Bx11, Bx12, Bx12+, Bx13, Bx19, Bx20, Bx33, Bx35, Bx36, and **M100**. M100 has an M name but is in the Bronx feed, so downloading only the Manhattan feed would miss it. These Bx routes are also the corridor to the Bronx, which is the main source of the bus gain in this map |
| `gtfs_busco` MTA Bus Company | **Used** | 9 BxM express routes stop in upper Manhattan (10 stops in total), with very little effect |
| `gtfs_b` Brooklyn | Not needed | Not a single stop in the extent covering upper Manhattan and the west side of the Bronx |
| `gtfs_q` Queens | Not needed | Same, 0 stops |
| `gtfs_si` Staten Island | Not needed | Same, 0 stops |

The three unneeded feeds were also downloaded (to verify that they have no stops). All feeds are valid from 2026-10-12 to 2027-01-02.

**Key point:** bus routes in upper Manhattan **do need data from other boroughs**, at least the Bronx feed, so downloading only the Manhattan feed is not enough.

## 5. Assumptions used

**Bus timetable**
- **Service date: 2026-11-18 (Wednesday).** Today (11 November) is Veterans Day and every feed has holiday adjustments, so today was not used. The services valid on that day were resolved from `calendar.txt` and `calendar_dates.txt`: 5 services for Manhattan, 4 for the Bronx and 8 for Bus Company. The day is a school day, so services marked `SDon` are included
- The subway feed keeps the previous round's `Weekday` service (the feed is valid 2026-11-01 to 2027-05-15, different from the bus feeds' validity, so the two do not correspond to exactly the same date, but both are regular weekday service)
- Trips in the window: only trips running between 08:00 and 08:30 are kept (760 for Manhattan, 909 for the Bronx, 1,255 for Bus Company), giving 405 running patterns and 6,220 bus stops
- **Scheduled timetable; no real-time or traffic conditions**; boarding/alighting restrictions (`pickup_type`/`drop_off_type`) are handled: a stop that does not allow boarding cannot be boarded at, and one that does not allow alighting cannot be alighted at
- BxM express routes are treated as ordinary routes, without restrictions other than the express fare or stopping rules; off-board payment for Select Bus Service is not considered either
- Bus stop numbers carry a feed prefix; when one physical stop appears in several feeds it is treated as different stops, with a 0-second walking transfer

**Transfers and walking**
- **Street-level walking transfers were added between bus and bus and between bus and subway**, up to 5 minutes (300 seconds, by street-network distance at 4.8 km/h), 67,716 pairs in total; **transfers between subway stations stay as before**, using only GTFS `transfers.txt`. This keeps scenarios (1) and (2) comparable with the previous round, but it creates an asymmetry: there are no street-level walking transfers between subway stations, while there are for those involving buses
- Bus stops are mostly in the middle of a block, so bus stops snap to the nearest **segment** (by the nearest point on the segment, with the distances to both ends counted); subway stations still snap to the nearest **node** as in the previous round, to keep scenarios (1) and (2) comparable. The two conventions coexist. Of the 6,220 bus stops, 360 (5.8%) are more than 150 m from the street network and cannot be walked to; at 08:00 none of these 360 is reached within 30 minutes, so there is no effect on the results
- Origin to bus stop: walking on the street network, the same as to subway stations
- Waiting: wait for the next bus on arrival, with no extra time to enter, cross streets or buy a ticket

**ADA group and buses**
- **All buses and all bus stops are treated as usable by the ADA group.** This is an assumption made at your request (bus stops do not require curb ramps; ramps are not considered for now), and it is an upper bound: in reality not every stop has an accessible curb, bus pad and sidewalk. MTA buses themselves are accessible, but accessibility around the stops was not checked
- The subway part keeps the previous round's restriction: boarding, alighting and transferring only at ADA stations (all platforms at ADA=1; the accessible-direction platform at ADA=2), and riding through non-ADA stations is allowed. Walking transfers between ADA subway stations and bus stops are treated as ordinary transfers, with no extra restriction
- Elevator failures, and steps and curb ramps on street walking, are not considered

**Other settings kept:** origin, 30 minutes, walking at 4.8 km/h, the street network (CSCL), the 100 m buffer, the 10 m grid, the removal of water surface; the dashed line on the map is the pure-walking range.

## 6. Problems met

1. **Downloading only the Manhattan feed is not enough.** See section 4: M100 is in the Bronx feed, and the Bx routes are the corridor into the Bronx.
2. **Today's date is not suitable as the baseline.** It is Veterans Day and the feeds adjust that day, so 11-18 was used instead.
3. **Boarding/alighting restrictions of buses were missed at first.** The first version of the parser read only the stop times and not `pickup_type` / `drop_off_type`. The check found that about 6% of the stops of the Bus Company express routes do not allow boarding and 6% do not allow alighting (only 0.1%–0.2% in the Manhattan and Bronx feeds). After adding them and re-running, **the 08:00 result is completely unchanged**, and 12:00 differs by only a few stops (bus stops 1,258 → 1,254), so there is no effect on the conclusion.
4. **A bug in the previous round was found and corrected** (see "Correction" in section 3).
5. **Bus stops falling outside the street network.** Downloading OSM in blocks was too slow, so the street network uses CSCL, limited to latitude 40.60–40.93 and longitude -74.06 to -73.78. 360 bus stops are outside the extent or too far from a street; at 08:00 none of them is reached, so nothing was truncated. But I did not check this separately for 12:00.
6. **Not done:** a bus-only scenario (without subway), averaging over several departure times, bus reliability and crowding, and whether the actual transfer paths are accessible (elevators, slopes).
7. **Plausibility checks:** (a) the implied straight-line average speed to the bus stops reached is at most 6.4 m/s (23 km/h, including walking and waiting), with no "teleporting"; (b) all bus stops reached snap to the street network (0 truncated); (c) buses make 15 subway stations that were unreachable within 30 minutes reachable (such as 125 St, 135 St, 145 St, 116 St, Fordham Rd, Kingsbridge Rd, 3 Av-149 St), and another 36 platforms are reached earlier.

## 7. New files in this round

| File | Content |
|---|---|
| [nyp_isochrone_bus_4scenarios.png](../outputs/nyp_isochrone_bus_4scenarios.png) | Map of the four scenarios side by side, with area and share in each panel title; in (3) and (4) the light colour is the range without buses and the dark colour is the part added by buses |
| [nyp_isochrone_bus_summary.csv](../outputs/nyp_isochrone_bus_summary.csv) | Area for each scenario, two departure times and two buffers, plus the previous round's results (marked superseded) for comparison |
| `raw/gtfs_bus/` | Zips and unzipped contents of the six bus feeds |

---

*(Original chapter: Round 8, four-scenario isochrones for the three hospitals, land area, ACS residents and direction check)*

**About section numbers:** before writing I read this whole file. At that time the file had two workstreams that each used the numbering "Round 4 / Round 5" and sections 22–30 (the live outage data check and the isochrones), so section numbers were duplicated. I only appended and changed no existing content; this chapter started from section **36**, and references go by title instead of ambiguous numbers such as "section 1" or "section 3".

## 8. Output of this chapter

| File | Content |
|---|---|
| [isochrone_harlem_4scenarios.png](../outputs/isochrone_harlem_4scenarios.png) | Four-scenario map for Harlem Hospital |
| [isochrone_nyp_columbia_4scenarios.png](../outputs/isochrone_nyp_columbia_4scenarios.png) | Four-scenario map for NYP/Columbia (CUIMC) |
| [isochrone_mt_sinai_morningside_4scenarios.png](../outputs/isochrone_mt_sinai_morningside_4scenarios.png) | Four-scenario map for Mount Sinai Morningside |
| [hospital_isochrone_summary.csv](../outputs/hospital_isochrone_summary.csv) | Summary table, 102 rows: 3 hospitals × 4 time/direction settings × 4 scenarios (plus pure walking) × 2 buffers. Columns include land area, area including water, areas in Manhattan / Bronx / Brooklyn / Queens / Staten Island, reachable street length, numbers of subway and bus stops, residents with an ambulatory difficulty and their 90% margin of error, and the population base |
| `raw/census/` | `acsdt5y2024-b18105.dat` (ACS summary file) and `nyc_tracts_2020.geojson` (NYC 2020 census-tract boundaries, clipped to the shoreline) |

The definitions of the four scenarios, the bus data, the walking network and the area algorithm are exactly the same as in the chapter "Adding buses (NYP/Columbia isochrone)" ((1) anyone, subway; (2) ADA subway stations only; (3) anyone, subway + bus; (4) ADA subway stations only, plus bus; all buses and bus stops are treated as usable; 08:00 departure; 30 minutes; 4.8 km/h; CSCL streets; 100 m buffer; no ramps; no elevator failures). This chapter does not repeat those assumptions.

**Regression check:** after the code was restructured, the same code was used to recompute the four 08:00 scenarios for NYP/Columbia, and **the arrival time at every street node agrees point by point with the previous chapter's result** (4/4). The area difference is within 0.02 km² (for example scenario (1) 30.95 → 30.93), caused by a different alignment of the raster grid.

## 9. Results of the four scenarios for the three hospitals

Weekday 08:00 departure, 100 m buffer, **land only**. "Other boroughs" is **always the Bronx** in every scenario: no scenario reaches Brooklyn, Queens or Staten Island (all 51 scenarios are 0).

| Hospital / scenario | Land area km² | Manhattan | Bronx | Share of (1) | Subway station records / bus stops used as walking origins | Residents with ambulatory difficulty (±90% margin) |
|---|---|---|---|---|---|---|
| **Harlem Hospital** (1) | 41.03 | 27.86 | 13.16 | 100% | 103 / 0 | 102,539 (±3,516) |
| (2) | 28.92 | 20.19 | 8.73 | 70% | 38 / 0 | 70,857 (±2,917) |
| (3) | 46.80 | 31.96 | 14.84 | 114% | 119 / 1,464 | 111,358 (±3,714) |
| (4) | 33.98 | 22.79 | 11.19 | 83% | 40 / 1,067 | 83,580 (±3,181) |
| Walking only | 11.49 | 8.12 | 3.37 | | | 32,739 (±1,866) |
| **NYP/Columbia** (1) | 30.93 | 22.51 | 8.43 | 100% | 61 / 0 | 74,067 (±3,045) |
| (2) | 17.58 | 15.16 | 2.41 | 57% | 14 / 0 | 44,402 (±2,310) |
| (3) | 36.51 | 23.73 | 12.78 | 118% | 76 / 1,170 | 87,954 (±3,287) |
| (4) | 23.80 | 17.53 | 6.28 | 77% | 22 / 759 | 61,970 (±2,753) |
| Walking only | 7.98 | 6.48 | 1.50 | | | 25,017 (±1,801) |
| **Mount Sinai Morningside** (1) | 25.17 | 23.77 | 1.40 | 100% | 70 / 0 | 60,600 (±2,798) |
| (2) | 10.05 | 9.72 | 0.33 | 40% | 9 / 0 | 23,531 (±1,587) |
| (3) | 27.05 | 25.52 | 1.52 | 107% | 74 / 904 | 64,585 (±2,867) |
| (4) | 14.30 | 13.97 | 0.33 | 57% | 10 / 497 | 32,406 (±1,903) |
| Walking only | 9.03 | 9.03 | 0 | | | 21,611 (±1,547) |

**Relative ratios (08:00, 100 m)**, with the corresponding ratios for residents with an ambulatory difficulty in parentheses:

| Hospital | ADA group ÷ anyone, subway only (2) ÷ (1) | With buses (4) ÷ (3) | Buses for anyone (3) ÷ (1) | Buses for the ADA group (4) ÷ (2) |
|---|---|---|---|---|
| Harlem Hospital | 70% (69%) | 73% (75%) | 114% (109%) | 117% |
| NYP/Columbia | 57% (60%) | 65% (70%) | 118% (119%) | 135% |
| Mount Sinai Morningside | 40% (39%) | 53% (50%) | 107% (107%) | 142% |

Area gain from buses (km², 08:00): anyone Harlem +5.78 (+14%), NYP +5.58 (+18%), Mount Sinai +1.87 (+7%); ADA group Harlem +5.06 (+17%), NYP +6.23 (+35%), Mount Sinai +4.25 (+42%). In residents with an ambulatory difficulty: anyone +8,819 / +13,887 / +3,985, ADA group +12,723 / +17,568 / +8,875.

How to read it:
1. **ADA accessibility differs a lot between the three hospitals, in a fixed order: Harlem (70%) > NYP/Columbia (57%) > Mount Sinai Morningside (40%).** This order does not change under any of the later time and direction settings (see section 13).
2. **Mount Sinai Morningside's (2) is almost just its walking range:** its 10.05 km² for (2) is only 1.0 km² more than the pure-walking 9.03 km². The reason can be seen from the earlier checks: there is no ADA station within 400 m, and the nearest ADA station (125 St A/C/B/D) is 1,003 m away.
3. **Buses help the ADA group more in relative terms, and more for hospitals that lack ADA stations** (Mount Sinai +42%, NYP +35%, Harlem +17%). Buses fill the gap caused by sparse ADA subway stations, but after that the ADA group is still below anyone (53%–73%).
4. All the area outside Manhattan is in the Bronx. The Bronx weighs more in the Harlem–NYP difference (Harlem's (2) Bronx area is 66% of (1), and the Manhattan part is 72%).

## 10. Area: land only, split into Manhattan and other boroughs

- Method: the NYC borough boundary (NYC Open Data Borough Boundaries, clipped to the shoreline) is rasterized to a 10 m grid, and each cell is labelled with its borough. Only the intersection of the isochrone's buffer with land counts as area; river surface and cells belonging to no borough do not count.
- Water removed: in the 12 scenarios at 08:00 and 100 m, the area of the buffer including water is 0.17–1.37 km² larger than the land area, i.e. 1.6%–5.3% of the buffer is water. `hospital_isochrone_summary.csv` gives both `area_incl_water_km2` and `area_land_km2` for comparison.
- Manhattan area includes Randalls Island and Marble Hill (they belong to Manhattan in the borough boundary).
- The area is the land within the buffer radius, not "the area people can walk to": a 100 m buffer also counts parks, courtyards and so on between streets. Comparing relative differences is more reliable than absolute areas, but see section 13: the relative values themselves also change with time and direction.
- The latest check for all scenarios: the isochrones are at least 2.8 km (to the north) from the boundary of the street-network extent (latitude 40.60–40.93, longitude -74.06 to -73.78), and none of the 51 scenarios comes close to the boundary, so none is cut off by the network extent.

## 11. Residents: ACS ambulatory-difficulty population, allocated by area share

**Indicator:** the sum of the 10 "with an ambulatory difficulty" cells (5 age groups for each sex) in ACS table B18105 (sex × age × ambulatory difficulty, for the civilian non-institutionalized population aged 5 and over). It excludes children under 5 and people living in institutions (nursing homes, prisons and so on).

**Data source and download:** the 2020–2024 5-year ACS, **from the Census summary-file download, not the API**. The Census data API now returns "Missing Key" (an API key is required), and I did not register a key for you. The summary file is a public direct download: `https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b18105.dat`, 74,139,777 bytes; the download timed out once midway and was completed by resuming, and the final size matches what the server declares. The 5 counties of New York City have 2,327 tracts in total, with 604,930 people "with an ambulatory difficulty" citywide, which is 7.6% of the 7,946,933 non-institutionalized population aged 5 and over, a plausible order of magnitude.

**Census-tract boundaries:** NYC Department of City Planning 2020 Census Tracts (`63ge-mke6`, shoreline-clipped version, 2,325 polygons). **The version including water areas** (`imfq-nf3j`) **cannot be used**, because with area-share allocation the water surface would dilute the denominator. All 2,325 polygons can be matched to ACS rows by `geoid`; ACS has 2 more rows without polygons (presumably pure-water tracts, not verified).

**Allocation method:** each tract's residents × (the share of the isochrone's land area inside that tract), with the share computed on the 10 m raster. That is, residents are assumed to be spread uniformly over the land inside each tract.
- For tracts cut by my raster extent (the raster covers only the area of the isochrone): the denominator of the share uses the polygon's vector area, otherwise the share would be overestimated. This correction changes the counts by less than 1% (for example NYP (1) 74,658 → 74,067).
- Ratio of raster area to vector area: for tracts that fall completely inside the grid the median is 0.998, and the 5th to 95th percentile is 0.974–1.035.
- Land area in the isochrones that belongs to no tract: 0.

**Margin of error:** the ± in the table is the 90% margin of error, computed roughly as "each tract's ACS margin of error times its allocation share, tracts independent, square root of the sum of squares". **It reflects only the ACS sampling error and not the error from the "uniform distribution" assumption**, so the real uncertainty is larger than in the table. The ACS error at tract level is large to begin with.

**Limitations of this indicator:**
- It counts people who live inside the circle, not patients or staff going to the hospital, and not people who need an elevator or wheelchair. "Ambulatory difficulty" is self-reported and much broader than "wheelchair use"
- The circle is **from the hospital outward**, while "can residents get to the hospital" corresponds to the "arrival" direction; see the reverse result in section 13
- Uniform allocation by area is inaccurate in parks, large institutions, and near high-density apartment buildings

**Share for reference:** in (1) at 08:00, residents with an ambulatory difficulty are 9.2% (Harlem), 8.9% (NYP) and 8.4% (Mount Sinai) of the population base, all above the citywide 7.6%; in the pure-walking circles 10.8%, 10.1% and 8.3%.

## 12. Relative ratios of residents

The (2) ÷ (1) and (4) ÷ (3) ratios of residents with an ambulatory difficulty are close to the area ratios (in parentheses in section 9): Harlem 69% / 75%, NYP 60% / 70%, Mount Sinai 39% / 50%. The differences (NYP area 57% versus residents 60%) show that residents are slightly denser in the areas covered by ADA stations, but the difference is within the margin of error and is not interpreted further.

## 13. Direction check: computing "arrive by 08:00" in reverse

**Question:** the forward direction (30 minutes from the hospital) answers "where can one go from the hospital"; what matters more for patients and staff is "where can people reach the hospital by 08:00 from". I computed the latter with a time-reversed search and compared it with the forward one.

**Method:** the times of all trips are negated and the stop order reversed, and the same RAPTOR is run from the hospital; the boarding/alighting restrictions are swapped (the original "alighting allowed" becomes "boarding allowed" in reverse), the transfer table is reversed, and the ADA-station restriction is unchanged. Given "arrive by 08:00", each street node gets a "latest departure time" L, and the door-to-door duration = 08:00 − L; the **nodes with a duration ≤ 30 minutes** form the reverse isochrone. Buses use the trips running 07:30–08:00.

**Validation (important):** for each of NYP and Mount Sinai, 3 cases (subway, subway + bus, ADA subway + bus), 25 random nodes each, 150 in total. With each node as a forward origin, **leaving at time L always arrives at the hospital by 08:00 (150/150, maximum deviation 0 seconds)**; **leaving 90 seconds later misses it in all cases (150/150)**. This shows that the reverse search is a correct "latest departure".
- The first validation failed: I rounded L up, and L fell exactly on a train departure time, so being less than 1 second late missed that train and required the next one (about 5 minutes later), which looked like "arriving 5 minutes late". **This was a problem in how the test was written** (it should round down), not a model error, and everything passed after the change. It was confirmed to be the cause by checking station by station.

**Comparison of areas under the three settings** (km², land, 100 m). "Forward 07:30" is the control: it uses the same time window as the reverse (07:30–08:00), to separate "direction" from "time of day":

| Hospital / scenario | Forward 08:00 | Forward 07:30 | **Reverse (arrive by 08:00)** | Reverse vs forward 08:00 | Reverse vs forward 07:30 |
|---|---|---|---|---|---|
| Harlem (1) | 41.03 | 49.68 | **48.71** | +19% | −2% |
| (2) | 28.92 | 34.42 | **35.22** | +22% | +2% |
| (3) | 46.80 | 55.10 | **52.03** | +11% | −6% |
| (4) | 33.98 | 43.02 | **42.25** | +24% | −2% |
| NYP (1) | 30.93 | 35.03 | **38.16** | +23% | +9% |
| (2) | 17.58 | 18.95 | **24.09** | +37% | +27% |
| (3) | 36.51 | 38.41 | **47.48** | +30% | +24% |
| (4) | 23.80 | 27.19 | **30.27** | +27% | +11% |
| Mount Sinai (1) | 25.17 | 22.45 | **26.88** | +7% | +20% |
| (2) | 10.05 | 10.69 | **10.36** | +3% | −3% |
| (3) | 27.05 | 27.82 | **31.71** | +17% | +14% |
| (4) | 14.30 | 15.62 | **17.82** | +25% | +14% |

**Shape overlap (intersection over union, IoU, where 1 is a perfect overlap):** forward 08:00 against reverse 0.62–0.87; forward 07:30 against reverse 0.67–0.92. The highest overlap is Harlem's (1) (0.92); the lowest is the ADA group with buses (4) (0.62–0.68).

**Residents in reverse (with ambulatory difficulty, persons):** Harlem (1) 122,630 (2) 92,515 (3) 130,196 (4) 109,534; NYP (1) 84,452 (2) 56,203 (3) 108,843 (4) 73,560; Mount Sinai (1) 61,053 (2) 24,003 (3) 72,532 (4) 46,125.

**How the ratios change with the setting** (area (2) ÷ (1) / (4) ÷ (3)):

| Hospital | Forward 08:00 | Forward 12:00 | Forward 07:30 | Reverse |
|---|---|---|---|---|
| Harlem | 70% / 73% | 71% / 73% | 69% / 78% | 72% / 81% |
| NYP/Columbia | 57% / 65% | 51% / 56% | 54% / 71% | 63% / 64% |
| Mount Sinai | 40% / 53% | 41% / 48% | 48% / 56% | 39% / 56% |

**Conclusions:**
1. **The absolute area is sensitive to both "what time" and "which direction", and cannot be taken as an exact number.** Reverse is 3%–37% larger than forward 08:00, and almost always larger. Forward 07:30 also differs from 08:00 by −11% to +27% (for example Harlem (1) 41.0 → 49.7, Harlem (4) 34.0 → 43.0). For these three hospitals the uncertainty of a single-departure-time isochrone area is roughly ±10%–25%.
2. **When the time windows are aligned (forward 07:30 against reverse), Harlem is almost the same (−6% to +2%), while NYP and Mount Sinai still differ (up to +27%).** So it is not only a matter of "what time"; the direction itself also matters, especially for the ADA group (NYP (2) +27%).
3. **The order of the ADA ÷ anyone ratio across the three hospitals is stable:** in the 8 combinations in the table above (4 settings × 2 definitions), Harlem > NYP/Columbia > Mount Sinai holds in all. This is the most robust conclusion of this chapter. The specific ratio values swing by 5–20 percentage points with the setting (for example NYP (2) ÷ (1) from 51% to 63%).
4. **After adding buses, the ADA group's share rises in all 12 combinations** (4 settings × 3 hospitals), except that for NYP in reverse it is almost flat (63% → 64%). This agrees with the forward 08:00 conclusion.
5. **If the question is "who can get to the hospital", the reverse numbers should be used**, because they target arrival. The reverse area and resident counts are both larger than forward, with similar ratios.

**Possible explanations for the differences (not checked one by one):** forward counts the time spent "waiting for the first train at the origin" within the 30 minutes, and depends exactly on the phase between the 08:00 moment and the timetable; reverse is as if the passenger could pick the departure time, with the slack of arriving early at the hospital end counted in the duration. Both affect sparse services (the few lines the ADA group mainly depends on) more, so the direction difference is more visible for the ADA group. I did not separate and quantify these two factors. **A more robust approach (not done):** average over several departure times every few minutes between 07:30 and 08:30, or take the "maximum reachable", to remove the effect of timetable phase.

## 14. Problems met and limitations

1. **The Census API needs a key.** It returns "Missing Key". I did not register one and used the public summary file instead. The 74 MB download timed out midway and was complete after resuming.
2. **Duplicated section numbers.** See the start of this chapter. I did not change the chapters written by others.
3. **The first validation of the reverse search failed.** The cause was the rounding direction in the test, see section 13. Fixed and passing.
4. **Denominator for edge tracts.** See section 11; the effect after the fix is below 1%.
5. **Only the Manhattan, Bronx and MTA Bus Company bus feeds were loaded.** Buses in Brooklyn, Queens and Staten Island were not loaded; since none of the 51 scenarios reaches those three boroughs, there is no effect on this chapter's results. They would need to be added if longer times or a larger area are used later.
6. **A single origin, a single departure time (plus 12:00 and 07:30 as controls) and a scheduled timetable; no real-time data.** The effect of a single time on the results is in section 13.
7. **The bus assumption for the ADA group is still an upper bound:** all buses and bus stops are treated as usable.
8. **Not done:** averaging over several departure times, a bus-only scenario, a 12:00 version of the reverse search, allocating residents to the building level (using Census blocks or building outlines would be more accurate than "uniform within a tract"), and using the actual home locations of patients or staff as trip origins.
9. **Hospitals are still single coordinate points.** The real campus has some extent; the NYP/Columbia campus is large, and the origin is a single point at 622 W 168th St, so another point (such as another building) would change the results slightly; no sensitivity check was done.

---

*(Original chapter: Round 9, residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo)*

Before writing I confirmed again that checks.md had not changed since the last chapter was appended (987 lines). This chapter is append-only; section numbers start from **43**, continuing the previous chapter (Round 8, sections 36–42). References to other chapters still go by title.

## 15. Output of this chapter

| File | Content |
|---|---|
| [hospital_isochrone_timeavg_summary.csv](../outputs/hospital_isochrone_timeavg_summary.csv) | Second item: for each hospital × 4 scenarios, the mean, standard deviation, minimum, maximum and coefficient of variation over the 5 departure times (area and residents, with the Manhattan/Bronx split) |
| [hospital_isochrone_timeavg_runs.csv](../outputs/hospital_isochrone_timeavg_runs.csv) | Raw results of the 60 individual runs behind the above |
| [mc_scenario4_summary.csv](../outputs/mc_scenario4_summary.csv) | Third item: Monte Carlo summary, 12 rows (3 hospitals × reverse/forward × 2 fills). Columns include baseline residents, the mean / standard deviation / 5th percentile / minimum of the 1000 draws, residents and area at each coverage-probability level (with the Manhattan/Bronx split) |
| [mc_single_failure.csv](../outputs/mc_single_failure.csv) | Residents lost when a single station or a single elevator fails on its own |
| [mc_scenario4_coverage_reverse.png](../outputs/mc_scenario4_coverage_reverse.png), [mc_scenario4_coverage_forward.png](../outputs/mc_scenario4_coverage_forward.png) | Coverage-probability maps (the 3 hospitals side by side) |

The first item needs no new file: the reverse resident counts were already computed in `hospital_isochrone_summary.csv` (`mode = rev0800`) and are organized into a table below.

## 16. Residents on the reverse basis (arriving at the hospital), split into Manhattan and the Bronx

Reverse = origins from which the hospital is reached by 08:00 with a total duration ≤ 30 minutes (method and validation in the "Direction check" section of the previous chapter). Residents = ACS 2020–2024 B18105 residents "with an ambulatory difficulty", allocated by tract area share. **Manhattan / Bronx is split by the county of the tract** (New York County / Bronx County). The previous chapter established that in all scenarios the areas in Brooklyn, Queens and Staten Island are 0 apart from Manhattan and the Bronx, so "other boroughs" means the Bronx. The two parts differ from the total by at most 1 person, due to rounding.

| Hospital / scenario (arrive by 08:00, 100 m) | Total residents (±90% margin) | Manhattan | Bronx | Bronx share |
|---|---|---|---|---|
| **Harlem Hospital** (1) anyone, subway | 122,630 (±3,809) | 62,299 | 60,331 | 49% |
| (2) ADA subway stations only | 92,515 (±3,254) | 45,187 | 47,327 | 51% |
| (3) subway + bus | 130,196 (±3,927) | 65,163 | 65,032 | 50% |
| (4) ADA subway + bus | 109,534 (±3,603) | 55,598 | 53,936 | 49% |
| **NYP/Columbia** (1) | 84,452 (±3,303) | 59,911 | 24,541 | 29% |
| (2) | 56,203 (±2,655) | 47,151 | 9,052 | 16% |
| (3) | 108,843 (±3,658) | 68,502 | 40,341 | 37% |
| (4) | 73,560 (±3,025) | 58,365 | 15,195 | 21% |
| **Mount Sinai Morningside** (1) | 61,053 (±2,839) | 59,827 | 1,226 | 2% |
| (2) | 24,003 (±1,661) | 24,003 | 0 | 0% |
| (3) | 72,532 (±3,037) | 68,035 | 4,498 | 6% |
| (4) | 46,125 (±2,322) | 45,660 | 466 | 1% |

**ADA group ÷ anyone (residents):** subway only (2) ÷ (1) = Harlem 75%, NYP 67%, Mount Sinai 39%; with buses (4) ÷ (3) = 84%, 68%, 64%. The order is still Harlem > NYP > Mount Sinai.

**Compared with forward 08:00:** the reverse resident counts are larger (Harlem (1) 122,630 vs 102,539, NYP (1) 84,452 vs 74,067, Mount Sinai (1) 61,053 vs 60,600), and the Bronx share is also higher (Harlem (1) 49% vs 40%). The reasons are in the previous chapter (reverse and forward treat "waiting for the first train" differently, plus a different time window) and are not repeated here.

The numbers in this section come from the previous chapter's raster (a smaller extent). The new full-extent raster of this chapter recomputes the same 08:00 forward results with an area difference ≤ 0.018 km² and a resident difference ≤ 148 persons (0.13%), so the two rasters can be used interchangeably.

## 17. Averaging over several departure times: area, residents and variation between times

**Method:** for each hospital and each scenario, depart from the hospital at **07:30, 07:45, 08:00, 08:15 and 08:30** (forward, 30 minutes each), 3 × 4 × 5 = 60 runs. Bus trips are those running between 07:30 and 09:00 (about 4,800 trips); the subway uses all-day trips. Other settings are unchanged. The "mean" in the tables is the **average of the area (or residents) of the 5 times**, not the area of the 5 overlaid circles. SD is the sample standard deviation (n = 5) and CV = SD ÷ mean.

**Area (km², land, 100 m):**

| Hospital / scenario | Mean | SD | Min – max | CV |
|---|---|---|---|---|
| Harlem (1) | **47.30** | 4.71 | 41.01 – 53.62 | 10.0% |
| (2) | 32.30 | 3.61 | 28.52 – 36.97 | 11.2% |
| (3) | 53.76 | 5.52 | 46.79 – 61.90 | 10.3% |
| (4) | 39.06 | 4.62 | 33.97 – 44.27 | 11.8% |
| NYP (1) | **35.98** | 5.73 | 30.20 – 43.01 | 15.9% |
| (2) | 20.37 | 4.40 | 15.81 – 26.83 | 21.6% |
| (3) | 41.04 | 6.79 | 33.77 – 48.48 | 16.5% |
| (4) | 26.46 | 4.15 | 20.95 – 31.41 | 15.7% |
| Mount Sinai (1) | **25.48** | 2.86 | 22.44 – 30.10 | 11.2% |
| (2) | 10.65 | 0.36 | 10.05 – 11.04 | 3.4% |
| (3) | 27.97 | 2.76 | 25.61 – 32.70 | 9.9% |
| (4) | 14.20 | 0.84 | 13.64 – 15.62 | 5.9% |

**Residents with an ambulatory difficulty (persons):**

| Hospital / scenario | Mean | SD | Min – max | CV |
|---|---|---|---|---|
| Harlem (1) | **117,224** | 10,437 | 102,496 – 129,716 | 8.9% |
| (2) | 80,771 | 10,787 | 67,993 – 91,240 | 13.4% |
| (3) | 125,550 | 10,870 | 111,276 – 139,990 | 8.7% |
| (4) | 95,541 | 10,868 | 83,579 – 106,319 | 11.4% |
| NYP (1) | **86,072** | 12,113 | 74,215 – 99,965 | 14.1% |
| (2) | 49,875 | 8,943 | 40,316 – 62,074 | 17.9% |
| (3) | 98,538 | 13,766 | 85,059 – 114,177 | 14.0% |
| (4) | 68,418 | 9,493 | 55,516 – 77,389 | 13.9% |
| Mount Sinai (1) | **57,022** | 5,872 | 49,989 – 64,727 | 10.3% |
| (2) | 25,212 | 1,067 | 23,585 – 26,288 | 4.2% |
| (3) | 62,558 | 5,356 | 56,475 – 70,091 | 8.6% |
| (4) | 33,096 | 1,663 | 31,699 – 35,855 | 5.0% |

**Raw values at each time** (area km² / residents in thousands, in the order 07:30, 07:45, 08:00, 08:15, 08:30):

| Hospital / scenario | 07:30 | 07:45 | 08:00 | 08:15 | 08:30 |
|---|---|---|---|---|---|
| Harlem (1) | 49.7 / 123.7 | 45.6 / 112.7 | 41.0 / 102.5 | 53.6 / 129.7 | 46.6 / 117.4 |
| (2) | 34.4 / 91.2 | 28.5 / 68.0 | 28.9 / 70.9 | 37.0 / 90.2 | 32.7 / 83.5 |
| (3) | 55.1 / 130.2 | 51.5 / 119.4 | 46.8 / 111.3 | 61.9 / 140.0 | 53.5 / 126.9 |
| (4) | 43.0 / 106.3 | 35.0 / 84.2 | 34.0 / 83.6 | 44.3 / 103.3 | 39.1 / 100.3 |
| NYP (1) | 35.0 / 84.5 | 30.2 / 74.6 | 30.9 / 74.2 | 40.7 / 97.0 | 43.0 / 100.0 |
| (2) | 19.0 / 46.4 | 15.8 / 40.3 | 17.6 / 44.5 | 22.6 / 56.1 | 26.8 / 62.1 |
| (3) | 38.4 / 93.1 | 33.8 / 85.1 | 36.5 / 88.0 | 48.5 / 114.2 | 48.0 / 112.4 |
| (4) | 27.2 / 70.6 | 21.0 / 55.5 | 23.8 / 62.0 | 29.0 / 77.4 | 31.4 / 76.6 |
| Mount Sinai (1) | 22.4 / 50.0 | 30.1 / 64.7 | 25.2 / 60.7 | 24.1 / 53.1 | 25.6 / 56.6 |
| (2) | 10.7 / 25.9 | 10.6 / 24.8 | 10.1 / 23.6 | 10.8 / 25.5 | 11.0 / 26.3 |
| (3) | 27.8 / 63.0 | 32.7 / 70.1 | 27.1 / 64.7 | 25.6 / 56.5 | 26.7 / 58.5 |
| (4) | 15.6 / 35.9 | 13.7 / 33.4 | 14.3 / 32.5 | 13.7 / 32.1 | 13.6 / 31.7 |

**Relative ratios after averaging (mean ÷ mean):** area: Harlem (2)÷(1) 68%, (4)÷(3) 73%; NYP 57%, 64%; Mount Sinai 42%, 51%. Residents: Harlem 69%, 76%; NYP 58%, 69%; Mount Sinai 44%, 53%. The range of the ratio across individual times: Harlem (2)÷(1) 63%–71%, (4)÷(3) 68%–78%; NYP 52%–62%, 60%–71%; Mount Sinai 35%–48%, 42%–56%. The gain from buses (mean (3)÷(1) / (4)÷(2)): Harlem 114% / 121%, NYP 114% / 130%, Mount Sinai 110% / 133%.

**Conclusions:**
1. **The variation between times is large:** the CV of area and residents is mostly 9%–22% (only Mount Sinai's two ADA scenarios are at 3%–6%). Apart from Mount Sinai's two ADA scenarios (maximum 10%–15% above minimum), for the same hospital and scenario the maximum is 28%–70% above the minimum (for example NYP (2) 15.8 → 26.8 km², 70% higher).
2. **The single time 08:00 is on the low side:** the 08:00 area of Harlem and NYP is 10%–14% below the 5-time mean, while Mount Sinai differs by only −6% to +1%. The absolute areas given at the single point 08:00 in the previous two chapters are **10%–14% below the 5-time mean** for Harlem and NYP; to report a representative absolute area, the multi-time mean should be used rather than a single point.
3. **Source of the variation (conjecture, not checked one by one):** the departure phase of subways and buses. The walk from the origin to the nearest station is only 2–3 minutes, and the waiting time falls between 0 and 5 minutes, changing with the departure time and eating directly into a part of the 30 minutes. NYP's ADA group depends on a few lines, so it varies the most.
4. **Relative ratios are more stable than absolute areas, but still swing** (see the ranges above). The order of (2)÷(1) across the three hospitals on the means is Harlem 68% > NYP 57% > Mount Sinai 42%, and it also holds at every individual time (Harlem's lowest 63% is above NYP's highest 62%, and NYP's lowest 52% is above Mount Sinai's highest 48%). The ranges of (4)÷(3) overlap, so it cannot be said that every time keeps this order.
5. There are only 5 times, 15 minutes apart, a very small sample that may also be synchronized with the headways. SD is a rough guide to magnitude only.

**Regression:** the 08:00 column compared with the previous chapter gives an area difference ≤ 0.018 km² and a resident difference ≤ 148 persons.

## 18. Monte Carlo: coverage probability of scenario (4) under random elevator outages

### What was done

| Item | Method |
|---|---|
| Scenario | Only scenario (4) (ADA subway plus bus, all buses and bus stops usable). You did not specify a direction, so I **did both**: reverse (arrive by 08:00, the main result, consistent with the residents basis of section 16) and forward (depart at 08:00). A recomputation takes only about 0.2–0.3 seconds each, so no compromise was needed |
| Elevator model | `access_paths` of `station_table.csv` (which elevators are in series or parallel, to the northbound and southbound platforms) and `avail_24h_12m` of `elevator_detail.csv` (12-month 24-hour availability). 10 stations and 23 elevators in total |
| Sampling | Each draw takes an **independent** Bernoulli for each of the 23 elevators: probability of being out = 1 − availability. **1000 draws** in total with a fixed random seed (20261111); the three hospitals, two directions and two fills use the **same random numbers** |
| How a draw affects the isochrone | If a station has no fully working elevator path to the platform of a direction, that platform at that station cannot be boarded, alighted or transferred at by ADA passengers (riding through is still possible). The isochrone is then **fully recomputed** (RAPTOR + street walking + rasterization + resident allocation) |
| Harlem-148 St | Marked as in Round 7: no elevator dependency, never blocked |
| Elevators without availability | Only **EL520** (137 St southbound). Handled with the two earlier scenarios: **mean fill 0.9787** (outage probability 2.13%) and **low fill 0.9636** (3.64%). Both fills were run |
| "Probability that each resident is covered" | Residents are uniformly spread inside a tract, so for each 10 m cell I count "how many of the 1000 draws it is inside the isochrone" and multiply by the cell's residents. Residents with coverage probability ≥ 90% = the sum of residents in those cells |
| Baseline | All elevators working (that is, scenario (4) of the previous chapter; the resident counts differ slightly because of grid alignment: for example NYP reverse 73,669 vs 73,560) |

### Self-checks

1. **Sampling frequency vs analytic probability** (20,000 draws, the frequency of each station being "not fully usable in both directions" against 1 − whole-station probability in `station_table`): Inwood-207 St 2.29% vs 2.52%, Dyckman 3.22% vs 3.05%, 181 St 1.64% vs 1.53%, 175 St 1.26% vs 1.32%, 168 St 5.10% vs 5.30%, 137 St 4.82% vs 4.98%, 135 St 4.17% vs 4.20%, 125 St A/C/B/D 3.42% vs 3.38%, 125 St 4/5/6 4.80% vs 4.74%, Harlem-148 St 0 vs 0. All differences are within sampling error.
2. **The de-duplication used for speed is exact:** among the platforms blocked in a draw, only those "used in the baseline" can change the result. De-duplication is done on this part only (so each hospital and direction needs only 22–48 independent recomputations instead of 1000). For 25 randomly chosen outage draws, **the de-duplicated recomputation agrees point by point with the full recomputation (25/25)**.
3. In every scenario, the "expected number of covered residents computed from the per-cell coverage probabilities" equals "the mean of the 1000 individual results" (difference 3×10⁻¹¹), and no cell is covered outside the baseline (outages only reduce coverage).
4. **In 282 of the 1000 draws (28.2%) at least one station is not fully usable** (290 with the low fill). Number of draws in which each station is blocked: Inwood-207 St 25, Dyckman 32, 181 St 29, 175 St 13, 168 St 46, 137 St 47, 135 St 34, 125 St A/C/B/D 43, 125 St 4/5/6 57, Harlem-148 St 0.

### Results

**Scenario (4) residents (with ambulatory difficulty, persons).** Under the two fills, these resident statistics (mean, percentiles, residents at each coverage-probability level, number of draws with loss) are **exactly identical** (difference 0), so only one set is listed. The two differ only in the number of draws with "at least one station not fully usable" (282 vs 290) and in the number of independent recomputations:

| Hospital / direction | Baseline (no outage) | Mean of 1000 | SD | 5th percentile | Min | **Coverage probability ≥ 90%** | ≥ 95% | ≥ 99% | = 100% | Draws with loss |
|---|---|---|---|---|---|---|---|---|---|---|
| Harlem reverse | 109,561 | 108,980 | 4,221 | 109,526 | 64,435 | **109,561 (100.0%)** | 109,553 (100.0%) | 101,104 (92.3%) | 55,609 (50.8%) | 115 |
| Harlem forward | 83,579 | 83,085 | 2,586 | 83,427 | 68,676 | **83,579 (100.0%)** | 83,427 (99.8%) | 69,319 (82.9%) | 54,568 (65.3%) | 93 |
| NYP reverse | 73,669 | 71,755 | 6,510 | 52,487 | 39,859 | **72,887 (98.9%)** | 54,962 (74.6%) | 37,384 (50.7%) | 37,384 (50.7%) | 171 |
| NYP forward | 61,961 | 61,028 | 3,138 | 53,439 | 43,565 | **61,961 (100.0%)** | 48,890 (78.9%) | 42,308 (68.3%) | 42,155 (68.0%) | 140 |
| Mount Sinai reverse | 46,169 | 45,890 | 916 | 43,510 | 40,183 | **46,169 (100.0%)** | 42,704 (92.5%) | 39,378 (85.3%) | 39,378 (85.3%) | 150 |
| Mount Sinai forward | 32,480 | 32,455 | 117 | 32,289 | 31,763 | **32,480 (100.0%)** | 32,289 (99.4%) | 31,763 (97.8%) | 31,763 (97.8%) | 77 |

In parentheses is the share of the baseline. "Draws with loss" = the number of the 1000 draws in which residents are below the baseline.

**Residents with coverage ≥ 90% split by Manhattan / Bronx** (baseline in parentheses):

| Hospital / direction | Manhattan | Bronx |
|---|---|---|
| Harlem reverse | 55,665 (55,665) | 53,896 (53,896) |
| Harlem forward | 49,365 (49,365) | 34,214 (34,214) |
| NYP reverse | 57,922 (58,458) | 14,965 (15,212) |
| NYP forward | 45,260 (45,260) | 16,700 (16,701) |
| Mount Sinai reverse | 45,694 (45,694) | 475 (475) |
| Mount Sinai forward | 31,986 (31,986) | 494 (494) |

By area: the area with coverage probability ≥ 90% is almost the same as the baseline (Harlem reverse 42.2 km², NYP reverse 29.9 km² against a baseline of 30.3 km², Mount Sinai reverse 17.8 km²); the area with 100% coverage is much smaller (Harlem reverse 18.9 km², NYP reverse 12.2 km², Mount Sinai reverse 15.2 km²).

### How to read it

1. **The residents with "coverage probability ≥ 90%" almost equal the baseline (98.9%–100%).** But this is mainly caused by a **loose threshold**: every perturbed station has a whole-station availability probability of 94.7%–98.7%, all above 90%. Only for NYP reverse do 782 residents (1.1%) fall into the 88%–92% noise band (the standard error of a probability estimated from 1000 draws is at most 1.6 percentage points); in the other scenarios the band holds 0, so the ≥ 90% results are not affected by sampling noise.
2. **Once the threshold is raised, differences appear quickly:** at ≥ 95%, NYP reverse drops to 74.6% and Mount Sinai reverse to 92.5%; at ≥ 99%, NYP reverse 50.7%, Harlem reverse 92.3%, Mount Sinai reverse 85.3%. NYP reverse has 17,925 residents in the 90%–95% band, concentrated around 168 St and 125 St (the orange-red areas on the map). If the decision concerns "almost certainly able to get there", look at ≥ 95% or ≥ 99% rather than ≥ 90%.
3. **The mean loss is small but the tail is large:** the mean of the 1000 draws is below the baseline by 0.5% (Harlem reverse), 2.6% (NYP reverse), 0.6% (Mount Sinai reverse); forward 0.6%, 1.5%, 0.1%. But the worst few draws lose a lot: Harlem reverse minimum 64,435 (59% of the baseline), NYP reverse minimum 39,859 (54%). This is because a few stations carry most of the coverage (next point).
4. **Which stations are single points:** the residents lost when one station is shut down in both directions on its own (reverse):
   - Harlem: **135 St (2/3) loses 57,613 persons, 53% of the baseline**; the other stations have almost no effect (6 of 9 stations have no effect at all)
   - NYP: **168 St (A/C) loses 32,898 (45%)**, 125 St (A/C/B/D) 21,182 (29%), Inwood-207 St 6,543 (9%), 125 St 4/5/6 782 (1%)
   - Mount Sinai: 125 St (A/C/B/D) 5,986 (13%), 168 St 2,659 (6%), 175 St 889 (2%), 125 St 4/5/6 805 (2%), 181 St 300 (1%)
   - Forward: Harlem 135 St −28,859 (35%); NYP 168 St −17,416 (28%), Inwood-207 St −8,521 (14%), 125 St A/C/B/D −6,778 (11%); Mount Sinai's largest, 125 St A/C/B/D, is only −718 (2%)

   Elevators ranked by expected loss (probability of being out on its own × loss when out on its own), reverse: Harlem: EL181 (outage probability 1.4%, loss when out on its own 45,126, expected 641), EL180 (2.8%, 8,414, 238); NYP: EL139 (2.6%, 32,898, 852), EL140 (1.8%, 27,229, 483), EL144 (1.6%, 21,182, 335), EL142 (0.7%, 21,182, 156); Mount Sinai: EL139 (69), EL143 (53), EL142 (44), EL141 (27). Of the 23 elevators only 5–12 have any loss.
5. **The two fills make no difference.** The outage probability of EL520 (137 St) changes from 2.13% to 3.64% and all statistics are identical: 137 St is on no hospital's best ADA path, so its state does not affect the result. (The number of independent recomputations occasionally differs by 1, such as NYP reverse 45 vs 46, because 137 St is in a different state in those draws, but this has no effect on the resident counts.)

### Limitations (please pay particular attention to item 1)

1. **Only the 10 study-area stations in station_table were perturbed; the other ADA stations are treated as always available.** The isochrones use far more ADA stations than these 10: the share of perturbed stations among the ADA stations reached is: reverse Harlem 6/40, NYP 9/39, Mount Sinai 7/15; forward Harlem 6/40, NYP 10/22, Mount Sinai 4/10 (Harlem-148 St is counted too, but it is never blocked). So the large "P = 100%" areas in southern Manhattan and the Bronx are there because the stations depended on there were not perturbed, **not because they are truly always available**; coverage probability is **overestimated**, and the ≥ 90% resident counts are too high. The inventory and the availability table cover the whole city's elevators, so in principle the same method could model all 174 ADA stations; you asked to use station_table, so I did not.
2. **Elevators are independent:** elevators in one station may go out together (power cut, construction, the same contractor), and the independence assumption underestimates the probability of large losses.
3. **Availability is a 24-hour, 12-month average** (including scheduled outages and nights), and the real availability in the morning peak may differ (`elevator_detail.csv` has the AM-peak availability, which was not used). EL519 has only 5 months and EL144 only 9 months of data.
4. **The outage state does not change for the whole 30 minutes,** with no recovery or new failure along the way; there are also no alternative routes (such as detours beyond "use an adjacent elevator"), apart from the parallel relations encoded in the path graph itself.
5. **Only the ADA group is affected** (scenario (4)); anyone is not affected by elevators. The baseline is "all elevators working", consistent with the earlier scenario (4), but does not represent a typical day.
6. **Residents are allocated as "uniform inside a tract",** so in cells with high coverage probability the number of residents may not match reality; the residents counted are people living there, not patients who actually travel.
7. 1000 draws: the estimation error of a coverage probability is up to about 1.6 percentage points; tail events (5th percentile, minimum) are less stable still.

## 19. Problems met in this chapter

1. **No direction was specified.** The Monte Carlo was done in both directions, and the main result is the reverse one.
2. **Two small bugs in the script** (both found and fixed before results were produced, with no effect on the final numbers): the resident density was first taken per tract instead of per cell, causing an index error; the saved coverage counts were for the whole grid instead of the clipped one, which raised an error in the threshold-noise test.
3. **`item` has the same name as a pandas method,** which raised an error when printing the single-station and single-elevator rankings; dictionary lookup was used instead.
4. **Concern that the de-duplication speed-up could be bypassed:** see self-check 2 in section 18; verified to be exact.
5. **Not done:** modelling all 174 ADA stations (see limitation 1), non-independent elevator failures (common cause), using AM-peak availability, the Monte Carlo at several departure times (only 08:00 was done), and the outage effect on scenarios (1), (2) and (3) (they do not depend on elevators).

---

*(Original chapter: Round 10, clipping to Manhattan, expanded elevator Monte Carlo)*

Before writing I read checks.md again: it was still 1178 lines (unchanged since the last chapter was appended). This chapter is append-only, and section numbers continue from the previous chapter, starting at **48**. This chapter was appended in two steps: sections 20–23 are "clipping to Manhattan" (your points 1 and 2), followed by the Monte Carlo (points 3–5). References to other chapters still go by title.

## 20. Method and output of this chapter

- **What clipping means:** isochrones are still computed on the **whole street network** (travel is not restricted to Manhattan; for example one can take a bus through the Bronx and come back), and after computing, the coverage is **clipped to the Manhattan borough**, so area and residents count only Manhattan. Residents count only **Manhattan tracts** (New York County, FIPS 36061).
- **Both directions, single time and multi-time:** for each hospital and scenario, I ran the single time 08:00 forward (depart at 08:00) and reverse (arrive by 08:00), and the mean of five times (forward: depart at 07:30, 07:45, 08:00, 08:15, 08:30; reverse: these five arrival deadlines). That is 3 hospitals × 4 scenarios × 2 directions × 5 times = 120 runs, plus 3 pure-walking runs. Reverse bus trips are those running 07:00–08:30.
- **Regression:** the "before clipping" numbers were computed by the same program on the same raster and agree **point by point** with the 60 forward results of the previous two chapters (area difference 0.0000 km², resident difference 0).

| File | Content |
|---|---|
| [manhattan_clip_runs.csv](../outputs/manhattan_clip_runs.csv) | Results of the 120 runs + 3 pure-walking runs: area and residents before and after clipping, and the contribution of Marble Hill, Roosevelt Island, Randalls/Wards Island and other parts |
| [manhattan_clip_comparison.csv](../outputs/manhattan_clip_comparison.csv) | For each hospital, scenario and 4 settings (forward/reverse × single/mean), the before and after clipping comparison |
| [manhattan_clip_ratios.csv](../outputs/manhattan_clip_ratios.csv) | The ratios ((2) ÷ (1), (4) ÷ (3), (4) ÷ (2), (3) ÷ (1)) and the gain from buses, before and after clipping |

## 21. Extent of Manhattan: official boundary, water removed; Marble Hill and Roosevelt Island

**Boundary:** NYC Open Data Borough Boundaries (`gthc-hcne`, clipped to the shoreline, land only), borough = Manhattan. It consists of 36 polygons with a total (vector) area of 58.79 km². **River surface is not included**, so "removing water" is guaranteed by the boundary itself; the isochrone's 100 m street buffer is intersected first with land and then with Manhattan. The rasterized Manhattan land area is 59.18 km², 0.7% more than the vector area, which is an edge effect of the 10 m raster.

| Part | Area km² | Counted? | Times reached in the 120 runs | Largest area reached | Most residents |
|---|---|---|---|---|---|
| Main island | 54.62 | yes | all | | |
| **Marble Hill** | 0.30 | **yes** | 52 | 0.296 km² | 1,413 |
| **Roosevelt Island** | 0.58 | **yes** | **0** | 0 | 0 |
| Randalls/Wards Island | 2.17 | yes | 49 | 1.53 km² | 109 |
| Governors Island | 0.71 | yes | 0 | 0 | 0 |
| Other small islands (Liberty, Ellis, around the Battery) | 0.41 | yes | 0 | 0 | 0 |

**Answers to your questions:**
- **Marble Hill is counted.** It is a separate piece of the official Manhattan boundary (0.304 km²), geographically attached to the Bronx mainland but administratively part of Manhattan, and its census tracts are in New York County. It is reached only in the NYP/Columbia and Mount Sinai scenarios (none of Harlem's scenarios). For NYP scenario (1) (08:00) it contributes 0.30 km² and about 1,412 residents, 2.4%–2.6% of the Manhattan residents; for Mount Sinai (1) 0.7%–1.4%. **What happens if it is excluded:** I also computed a version excluding Marble Hill; the changes in the (2)÷(1) and (4)÷(3) ratios are all within 1 percentage point and the judgement on the order does not change, so this chapter does not exclude it.
- **Roosevelt Island is counted, but no scenario reaches it.** The island has 176 street nodes (all in the connected street network), and the Roosevelt Island station is an ADA station, but it cannot be reached within 30 minutes from or to any of the three hospitals, so it contributes nothing to the numbers. This is a result, not missing data.
- Randalls/Wards Island: counted; the largest area when reached is 1.53 km², but the most residents are only 109, so its contribution to the resident counts is small.

**Consistency:** the Manhattan boundary and the "tracts of New York County" almost completely coincide: the area inside the boundary whose tract is not in New York County is only 0.010 km², and the reverse is 0, so "area clipped to the Manhattan boundary" and "residents counted only in Manhattan tracts" are self-consistent. After clipping, the resident count equals `amb_manhattan` of the previous two chapters (identical run by run).

## 22. Before and after clipping

"Before clipping" = all the land covered by the whole network and the residents of all tracts (the basis of the previous two chapters, including the Bronx); "after clipping" = Manhattan only. Area in km² (land, 100 m buffer), residents = ACS residents with an ambulatory difficulty. "Share of (1)" is the scenario's share of scenario (1) (anyone, subway) under the same setting. The SD in the mean tables is the standard deviation of the area over the five times (after clipping).

**Forward, single time 08:00**

| Hospital / scenario | Area before → after (km²) | Share of (1) | Residents before → after (persons) | Share of (1) |
|---|---|---|---|---|
| **Harlem** (1) | 41.01 → **27.84** | 100% → 100% | 102,496 → **61,324** | 100% → 100% |
| (2) | 28.92 → **20.19** | 71% → 73% | 70,938 → **43,627** | 69% → 71% |
| (3) | 46.79 → **31.96** | 114% → 115% | 111,276 → **66,685** | 109% → 109% |
| (4) | 33.97 → **22.79** | 83% → 82% | 83,579 → **49,365** | 82% → 80% |
| **NYP/Columbia** (1) | 30.95 → **22.52** | 100% → 100% | 74,215 → **54,408** | 100% → 100% |
| (2) | 17.59 → **15.18** | 57% → 67% | 44,483 → **38,321** | 60% → 70% |
| (3) | 36.50 → **23.74** | 118% → 105% | 87,996 → **57,366** | 119% → 105% |
| (4) | 23.79 → **17.53** | 77% → 78% | 61,961 → **45,260** | 83% → 83% |
| **Mount Sinai** (1) | 25.19 → **23.78** | 100% → 100% | 60,701 → **56,502** | 100% → 100% |
| (2) | 10.05 → **9.72** | 40% → 41% | 23,585 → **23,091** | 39% → 41% |
| (3) | 27.06 → **25.53** | 107% → 107% | 64,683 → **60,341** | 107% → 107% |
| (4) | 14.30 → **13.97** | 57% → 59% | 32,480 → **31,986** | 54% → 57% |

**Reverse, arrive by 08:00 (single time)**

| Hospital / scenario | Area before → after (km²) | Share of (1) | Residents before → after (persons) | Share of (1) |
|---|---|---|---|---|
| **Harlem** (1) | 48.73 → **27.58** | 100% → 100% | 122,625 → **62,362** | 100% → 100% |
| (2) | 35.20 → **19.45** | 72% → 71% | 92,555 → **45,271** | 75% → 73% |
| (3) | 52.07 → **28.54** | 107% → 103% | 130,214 → **65,237** | 106% → 105% |
| (4) | 42.25 → **23.41** | 87% → 85% | 109,561 → **55,665** | 89% → 89% |
| **NYP/Columbia** (1) | 38.16 → **27.47** | 100% → 100% | 84,585 → **59,993** | 100% → 100% |
| (2) | 24.10 → **20.85** | 63% → 76% | 56,327 → **47,256** | 67% → 79% |
| (3) | 47.47 → **30.52** | 124% → 111% | 108,925 → **68,578** | 129% → 114% |
| (4) | 30.28 → **24.72** | 79% → 90% | 73,669 → **58,458** | 87% → 97% |
| **Mount Sinai** (1) | 26.88 → **26.21** | 100% → 100% | 61,102 → **59,878** | 100% → 100% |
| (2) | 10.36 → **10.36** | 39% → 40% | 24,067 → **24,067** | 39% → 40% |
| (3) | 31.72 → **29.62** | 118% → 113% | 72,595 → **68,085** | 119% → 114% |
| (4) | 17.82 → **17.54** | 66% → 67% | 46,169 → **45,694** | 76% → 76% |

**Forward, mean of five departure times**

| Hospital / scenario | Area before → after (km²) | Share of (1) | Residents before → after (persons) | Share of (1) |
|---|---|---|---|---|
| **Harlem** (1) | 47.30 → **29.99** (SD 2.6) | 100% → 100% | 117,224 → **66,409** | 100% → 100% |
| (2) | 32.30 → **20.01** (SD 1.3) | 68% → 67% | 80,771 → **43,493** | 69% → 65% |
| (3) | 53.76 → **33.09** (SD 2.4) | 114% → 110% | 125,550 → **69,649** | 107% → 105% |
| (4) | 39.06 → **23.41** (SD 1.2) | 83% → 78% | 95,541 → **51,279** | 82% → 77% |
| **NYP/Columbia** (1) | 35.98 → **24.60** (SD 3.2) | 100% → 100% | 86,072 → **57,243** | 100% → 100% |
| (2) | 20.37 → **17.45** (SD 3.4) | 57% → 71% | 49,875 → **41,880** | 58% → 73% |
| (3) | 41.04 → **25.71** (SD 3.6) | 114% → 105% | 98,538 → **59,911** | 114% → 105% |
| (4) | 26.46 → **19.68** (SD 3.4) | 74% → 80% | 68,418 → **48,626** | 79% → 85% |
| **Mount Sinai** (1) | 25.48 → **24.71** (SD 2.5) | 100% → 100% | 57,022 → **55,297** | 100% → 100% |
| (2) | 10.65 → **10.44** (SD 0.4) | 42% → 42% | 25,212 → **24,920** | 44% → 45% |
| (3) | 27.97 → **26.78** (SD 2.2) | 110% → 108% | 62,558 → **59,715** | 110% → 108% |
| (4) | 14.20 → **13.98** (SD 0.9) | 56% → 57% | 33,096 → **32,797** | 58% → 59% |

**Reverse, mean of five arrival deadlines (07:30–08:30)**

| Hospital / scenario | Area before → after (km²) | Share of (1) | Residents before → after (persons) | Share of (1) |
|---|---|---|---|---|
| **Harlem** (1) | 45.97 → **27.13** (SD 2.5) | 100% → 100% | 118,347 → **62,366** | 100% → 100% |
| (2) | 32.71 → **19.09** (SD 2.4) | 71% → 70% | 86,404 → **44,472** | 73% → 71% |
| (3) | 50.16 → **29.08** (SD 4.0) | 109% → 107% | 126,390 → **65,860** | 107% → 106% |
| (4) | 39.68 → **23.22** (SD 2.2) | 86% → 86% | 104,251 → **55,015** | 88% → 88% |
| **NYP/Columbia** (1) | 36.94 → **26.27** (SD 2.3) | 100% → 100% | 84,321 → **59,336** | 100% → 100% |
| (2) | 21.89 → **19.12** (SD 2.9) | 59% → 73% | 52,250 → **44,677** | 62% → 75% |
| (3) | 44.53 → **28.16** (SD 2.4) | 121% → 107% | 104,207 → **64,248** | 124% → 108% |
| (4) | 28.11 → **21.64** (SD 3.1) | 76% → 82% | 70,638 → **51,954** | 84% → 88% |
| **Mount Sinai** (1) | 25.68 → **25.01** (SD 1.6) | 100% → 100% | 58,460 → **57,017** | 100% → 100% |
| (2) | 10.22 → **10.15** (SD 0.3) | 40% → 41% | 23,810 → **23,699** | 41% → 42% |
| (3) | 32.17 → **29.16** (SD 2.0) | 125% → 117% | 74,651 → **66,594** | 128% → 117% |
| (4) | 19.14 → **18.22** (SD 3.1) | 75% → 73% | 47,794 → **45,598** | 82% → 80% |

Pure-walking range (no vehicles): Harlem 11.49 → **8.12** km², 32,796 → **24,256** residents; NYP/Columbia 7.98 → **6.48** km², 24,992 → **20,588**; Mount Sinai 9.03 → **9.03**, 21,675 → **21,675** (Mount Sinai's walking circle is entirely in Manhattan).

**Where the loss is largest (forward 08:00, share cut off):** Harlem area (1) 32%, (2) 30%, (3) 32%, (4) 33% (residents about 40%); NYP (1) 27%, (2) 14%, (3) 35%, (4) 26%; Mount Sinai (1) 6%, (2) 3%, (3) 6%, (4) 2%. In reverse, Harlem loses 43%–45% (residents 49%–51%).

## 23. What changed after removing the other boroughs: two main points

### (a) ADA group as a share of anyone: the order of the three hospitals changed

Ratio = ADA group ÷ anyone ((2) ÷ (1) is subway only, (4) ÷ (3) is with buses). 4 settings × area/residents × 2 ratios = 16 combinations:

| Setting | Indicator | Harlem before→after | NYP/Columbia before→after | Mount Sinai before→after | Order (before clipping → after clipping) |
|---|---|---|---|---|---|
| Forward 08:00 single time | Area (2) ÷ (1) | 71% → **73%** | 57% → **67%** | 40% → **41%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |
| Forward 08:00 single time | Area (4) ÷ (3) | 73% → **71%** | 65% → **74%** | 53% → **55%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Forward 08:00 single time | Residents (2) ÷ (1) | 69% → **71%** | 60% → **70%** | 39% → **41%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |
| Forward 08:00 single time | Residents (4) ÷ (3) | 75% → **74%** | 70% → **79%** | 50% → **53%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, arrive by 08:00 (single time) | Area (2) ÷ (1) | 72% → **71%** | 63% → **76%** | 39% → **40%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, arrive by 08:00 (single time) | Area (4) ÷ (3) | 81% → **82%** | 64% → **81%** | 56% → **59%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |
| Reverse, arrive by 08:00 (single time) | Residents (2) ÷ (1) | 75% → **73%** | 67% → **79%** | 39% → **40%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, arrive by 08:00 (single time) | Residents (4) ÷ (3) | 84% → **85%** | 68% → **85%** | 64% → **67%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |
| Forward, mean of five departure times | Area (2) ÷ (1) | 68% → **67%** | 57% → **71%** | 42% → **42%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Forward, mean of five departure times | Area (4) ÷ (3) | 73% → **71%** | 64% → **77%** | 51% → **52%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Forward, mean of five departure times | Residents (2) ÷ (1) | 69% → **65%** | 58% → **73%** | 44% → **45%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Forward, mean of five departure times | Residents (4) ÷ (3) | 76% → **74%** | 69% → **81%** | 53% → **55%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Area (2) ÷ (1) | 71% → **70%** | 59% → **73%** | 40% → **41%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Area (4) ÷ (3) | 79% → **80%** | 63% → **77%** | 60% → **62%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Residents (2) ÷ (1) | 73% → **71%** | 62% → **75%** | 41% → **42%** | Harlem > NYP/Columbia > Mount → NYP/Columbia > Harlem > Mount **changed** |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Residents (4) ÷ (3) | 82% → **84%** | 68% → **81%** | 64% → **68%** | Harlem > NYP/Columbia > Mount → Harlem > NYP/Columbia > Mount |

**Conclusions:**
1. **Before clipping, Harlem ranks first in all 16 combinations,** ahead of NYP by 4.7–17.3 percentage points. **After clipping, Harlem ranks first in only 6, and NYP is higher in the other 10;** Harlem minus NYP lies between −7.7 and +5.1 percentage points. The conclusion of the previous chapter that "Harlem > NYP > Mount Sinai holds under all settings" **no longer holds within Manhattan** (see the "changed" marks).
2. **Mount Sinai is still last in every case (16/16):** its ratio is 40%–68%, while the lower of the other two is 65%–85% under the same setting, a large gap.
3. **Why the order of Harlem and NYP changed (the explanation comes from the area changes above, and is an inference):** clipping affects the two groups at Harlem in almost the same proportion (area loses about 30%–33% in both), so the ratio hardly moves. For NYP, anyone loses a lot (scenarios (1) and (3) lose 27%–36%) and the ADA group loses little (scenario (2) loses only 13%–14%): the large area that NYP's anyone group reaches to the north and east in the Bronx is something the ADA group could not reach anyway. Before clipping, NYP's ADA ratio is low largely because of the Bronx; looking at Manhattan only, the NYP ADA group does much better in relative terms ((2) ÷ (1) rises from 57% to 67%, and in reverse from 63% to 76%).
4. **So:** "Mount Sinai is lowest" is robust; "whether Harlem or NYP is higher" has **no stable order** within Manhattan (the difference is within ±8 percentage points, the same order of magnitude as the time-to-time variation within a single setting recorded in the previous chapter).

### (b) How much of the help from buses remains for the ADA group

Help from buses = (4) − (2) (the area or residents that the ADA group gains when buses are added to the ADA subway stations). In parentheses is the share kept after clipping.

| Setting | Indicator | Harlem before→after (kept) | NYP/Columbia before→after (kept) | Mount Sinai before→after (kept) |
|---|---|---|---|---|
| Forward 08:00 single time | Area km² | +5.05 → **+2.60** (51%) | +6.20 → **+2.35** (38%) | +4.25 → **+4.25** (100%) |
| Forward 08:00 single time | Residents | +12,641 → **+5,738** (45%) | +17,478 → **+6,940** (40%) | +8,895 → **+8,895** (100%) |
| Reverse, arrive by 08:00 (single time) | Area km² | +7.04 → **+3.96** (56%) | +6.18 → **+3.88** (63%) | +7.46 → **+7.17** (96%) |
| Reverse, arrive by 08:00 (single time) | Residents | +17,006 → **+10,394** (61%) | +17,342 → **+11,202** (65%) | +22,102 → **+21,628** (98%) |
| Forward, mean of five departure times | Area km² | +6.76 → **+3.40** (50%) | +6.10 → **+2.23** (37%) | +3.56 → **+3.55** (100%) |
| Forward, mean of five departure times | Residents | +14,770 → **+7,786** (53%) | +18,543 → **+6,746** (36%) | +7,883 → **+7,877** (100%) |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Area km² | +6.98 → **+4.13** (59%) | +6.22 → **+2.52** (40%) | +8.92 → **+8.07** (90%) |
| Reverse, mean of five arrival deadlines (07:30–08:30) | Residents | +17,847 → **+10,542** (59%) | +18,388 → **+7,277** (40%) | +23,984 → **+21,900** (91%) |

**Relative increase ((4) ÷ (2) − 1, area):** before clipping Harlem +17%–+21%, NYP +26%–+35%, Mount Sinai +33%–+87%; after clipping Harlem **+13%–+22%**, NYP **+13%–+19%**, Mount Sinai **+34%–+80%**.

**Conclusions:**
1. **Mount Sinai is almost unchanged:** the help from buses keeps 90%–100%, because its gain is almost entirely in Manhattan (conjecture: there are few ADA subway stations near it, and buses fill gaps inside Manhattan; not verified station by station), and its relative increase in area is still the largest (+34%–+80%).
2. **Harlem keeps about half (area 50%–59%, residents 45%–61%), NYP keeps 36%–65% (area 37%–63%).** That is, the previous chapter's finding that "buses help NYP's ADA group a lot (+35%)" had **about two thirds (62% in forward 08:00) coming from the Bronx**; for Harlem about half (49%) came from the Bronx. Looking at Manhattan only, the increases of both fall to +13%–+22%, similar to each other and far below Mount Sinai's +34%–+80%.
3. **This is still an upper bound:** all buses and bus stops are treated as usable by the ADA group, and curb ramps are not considered. Within Manhattan, the help from buses for the ADA groups of Harlem and NYP is about half of the original result, while for Mount Sinai it is almost fully kept.


### Second part of this chapter: Monte Carlo (your points 3–5)

Before writing I confirmed again that checks.md had not changed since sections 20–23 were appended. Section numbers continue.

| File | Content |
|---|---|
| [mc_manhattan_summary.csv](../outputs/mc_manhattan_summary.csv) | Monte Carlo summary, 30 rows: 6 "hospital × direction" × 5 variants (expanded model × 2 fills, availability = 1 check, original 10-station model × 2 fills). Includes baseline, mean, SD, 5th percentile, mean of the worst 5%, minimum, and residents and area at each threshold |
| [mc_manhattan_single_failure.csv](../outputs/mc_manhattan_single_failure.csv) | Manhattan residents lost when a single station or a single elevator is out on its own (1,038 rows) |
| [mc_station_model.csv](../data/clean/mc_station_model.csv) | Elevator model of the 59 ADA stations reached: whether it can be modelled, the reason if not, the elevators, the paths, and whether the entrance is inferred |

## 24. Monte Carlo set-up, and differences from the previous chapter

| Item | Previous chapter | This chapter |
|---|---|---|
| Perturbed stations | The 10 study-area stations in `station_table.csv` | **All ADA stations used in baseline scenario (4):** the union over three hospitals × both directions is **59**, of which **45 can be given an elevator model** (31 in Manhattan, 14 in the Bronx), with **128 elevators** in total |
| Source of elevator structure and availability | `access_paths` of station_table, availability of elevator_detail | The **asset inventory** entrance fields (street / mezzanine / platform, direction served) build the "street → mezzanine → northbound/southbound platform" connectivity graph, and the **availability table**'s 12-month 24-hour hour-weighted availability. The method is the same as in Round 3 |
| Residents and extent | All tracts | **Only Manhattan tracts, isochrones clipped to Manhattan** (sections 20–21) |
| Statistics reported | Thresholds 90%, 95%, 99% | Thresholds **90%, 95%, 97%, 99%, 100%**; **mean, 5th percentile, mean of the worst 5%, minimum** |
| Elevators without availability | EL520, two fills | 3 in total: **EL132, EL133, EL520**, **with the same two fills**: mean fill 0.9787, low fill 0.9636 |

Everything else is unchanged: only scenario (4) (ADA subway plus bus, all buses and bus stops usable); two directions (reverse = arrive by 08:00; forward = depart at 08:00); 1000 independent draws, each elevator out with probability 1 − availability; fixed seed 20261111, with all hospitals and directions sharing the same random numbers; when a platform direction at a station has no fully working elevator path in a draw, that direction at that station cannot be boarded, alighted or transferred at by ADA passengers (riding through is allowed); each draw **fully recomputes** the isochrone, then clips it to Manhattan and computes Manhattan residents. Residents are ACS residents with an ambulatory difficulty, spread uniformly inside tracts; "coverage probability" = the number of the 1000 draws in which a 10 m cell is inside the isochrone ÷ 1000, and "residents with coverage probability ≥ X%" = the sum of residents in those cells. Baseline = all elevators working.

**Construction and validation of the expanded model:**
- The generic builder was used to rebuild the original 10 stations, and the resulting `access_paths` agree with station_table **10/10 exactly**; for the 22 elevators with records in the original model, the recomputed 12-month availability differs from `elevator_detail.csv` by at most 3.3×10⁻¹⁶.
- Of the 59 stations, **45 can be modelled**; **14 cannot** and are treated as "never out" (an optimistic assumption, see sections 27–28): 6 have no elevator at all in the inventory (Harlem-148 St, the 7 and S lines of Times Sq-42 St, 59 St-Columbus Circle (1), 149 St-Hostos (2/5), 161 St-Yankee Stadium (4)), and 8 cannot get a path because the inventory's entrance fields are incomplete (72 St, 96 St, Times Sq-42 St 1/2/3 and N/Q/R/W, 42 St-Port Authority, 49 St, 51 St, W 4 St-Wash Sq).
- Among the 45 modelled stations, **8 have no street elevator**, and the entrance is inferred as "the outermost mezzanine" (the same approach as for 181 St (A)).
- One elevator in the inventory (EL281) is marked ADA Compliant = NO but is inside a modelled station; it was not excluded.

## 25. Results: Manhattan residents, scenario (4), expanded model

Residents (with ambulatory difficulty, persons), 1000 draws. In parentheses is the share of the baseline. **Under the two fills (EL132, EL133 and EL520 at the mean fill 0.9787 or the low fill 0.9636), all resident statistics are exactly identical (difference 0)**, so only one set is listed; they differ only in the number of draws with "at least one station blocked" (907 vs 909).

| Hospital / direction | Baseline (no outage) | Mean | SD | **5th percentile** | Mean of worst 5% | Min | ≥ 90% | ≥ 95% | ≥ 97% | ≥ 99% | = 100% | Draws with loss |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Harlem reverse | 55,665 | 55,091 (99.0%) | 1,813 | **50,357** (90%) | 48,383 (87%) | 46,839 (84%) | 55,665 (100.0%) | 51,849 (93.1%) | 42,290 (76.0%) | 41,499 (74.6%) | 41,123 (73.9%) | 206 |
| Harlem forward | 49,365 | 49,227 (99.7%) | 1,233 | **49,199** (100%) | 46,912 (95%) | 34,582 (70%) | 49,304 (99.9%) | 49,152 (99.6%) | 49,111 (99.5%) | 47,511 (96.2%) | 34,429 (69.7%) | 284 |
| NYP/Columbia reverse | 58,458 | 56,837 (97.2%) | 5,601 | **40,942** (70%) | 34,515 (59%) | 32,424 (55%) | 57,582 (98.5%) | 40,585 (69.4%) | 33,368 (57.1%) | 29,980 (51.3%) | 29,980 (51.3%) | 332 |
| NYP/Columbia forward | 45,260 | 44,653 (98.7%) | 2,112 | **38,701** (86%) | 36,141 (80%) | 34,564 (76%) | 45,206 (99.9%) | 37,614 (83.1%) | 34,564 (76.4%) | 32,328 (71.4%) | 32,174 (71.1%) | 205 |
| Mount Sinai reverse | 45,694 | 45,441 (99.4%) | 854 | **43,035** (94%) | 42,126 (92%) | 39,172 (86%) | 45,694 (100.0%) | 42,499 (93.0%) | 42,499 (93.0%) | 39,172 (85.7%) | 39,172 (85.7%) | 145 |
| Mount Sinai forward | 31,986 | 31,972 (100.0%) | 51 | **31,795** (99%) | 31,786 (99%) | 31,737 (99%) | 31,986 (100.0%) | 31,795 (99.4%) | 31,795 (99.4%) | 31,763 (99.3%) | 31,513 (98.5%) | 83 |

**Area (km²):**

| Hospital / direction | Draws with ≥1 station blocked | Draws with resident loss | Unique recomputations | Perturbed stations / elevators | Area ≥90% (km²) | Area ≥99% (km²) | Area =100% (km²) | Baseline area (km²) |
|---|---|---|---|---|---|---|---|---|
| Harlem reverse | 907 | 206 | 368 | 45 / 128 | 23.41 | 14.08 | 13.76 | 23.41 |
| Harlem forward | 907 | 284 | 335 | 45 / 128 | 22.77 | 20.76 | 11.71 | 22.79 |
| NYP/Columbia reverse | 907 | 332 | 298 | 45 / 128 | 24.05 | 9.68 | 9.68 | 24.72 |
| NYP/Columbia forward | 907 | 205 | 146 | 45 / 128 | 17.21 | 10.92 | 10.85 | 17.53 |
| Mount Sinai reverse | 907 | 145 | 47 | 45 / 128 | 17.54 | 15.08 | 15.08 | 17.54 |
| Mount Sinai forward | 907 | 83 | 33 | 45 / 128 | 13.97 | 13.82 | 13.66 | 13.97 |

How to read it:
1. **The mean loss is small:** 0.03%–2.8% below the baseline (Harlem reverse 1.0%, forward 0.3%; NYP reverse 2.8%, forward 1.3%; Mount Sinai reverse 0.6%, forward 0.03%). In the 1000 draws **907 (90.7%) have at least one modelled station blocked**, but only 83–332 actually reduce the Manhattan residents.
2. **The worst-5% level (5th percentile) differs a lot:** Mount Sinai forward 31,795 (99%) is almost unaffected; Harlem forward 49,199 (99.7%); Harlem reverse 50,357 (90%); Mount Sinai reverse 43,035 (94%); NYP forward 38,701 (86%); **NYP reverse 40,942 (70%)**, and the mean of the worst 5% of draws is only 59% of the baseline.
3. **Thresholds:** residents with ≥ 90% are 98.5%–100% of the baseline; **≥ 95%** drops to 69% (NYP reverse) – 99.6% (Harlem forward); **≥ 99%** drops to 51.3% (NYP reverse) – 99.3% (Mount Sinai forward). Residents covered at = 100% (in all 1000 draws): NYP reverse only 51.3%, Harlem reverse 73.9%, Mount Sinai reverse 85.7%, the rest 70%–99%. **The biggest change comes when the threshold goes from 90% to 95%:** the whole-station availability of the key stations is mostly 94%–98%, only slightly above the 90% line, so ≥ 90% is almost always met, while ≥ 95% starts to exclude residents who depend on these stations (this is how I read the numbers; I did not check the probability of each station one by one).
4. **Compared with the previous chapter (only 10 stations perturbed), the effect of the expansion is mainly on Harlem:**

| Hospital / direction | Baseline | 10-station: mean / P5 / ≥90% / ≥99% | Expanded: mean / P5 / ≥90% / ≥99% |
|---|---|---|---|
| Harlem reverse | 55,665 | 55,403 / 55,630 / 55,665 / 47,208 | 55,091 / 50,357 / 55,665 / 41,499 |
| Harlem forward | 49,365 | 49,238 / 49,213 / 49,365 / 49,212 | 49,227 / 49,199 / 49,304 / 47,511 |
| NYP/Columbia reverse | 58,458 | 57,038 / 40,946 / 57,922 / 29,980 | 56,837 / 40,942 / 57,582 / 29,980 |
| NYP/Columbia forward | 45,260 | 44,713 / 38,701 / 45,260 / 32,328 | 44,653 / 38,701 / 45,206 / 32,328 |
| Mount Sinai reverse | 45,694 | 45,431 / 43,035 / 45,694 / 39,172 | 45,441 / 43,035 / 45,694 / 39,172 |
| Mount Sinai forward | 31,986 | 31,974 / 31,795 / 31,986 / 31,763 | 31,972 / 31,795 / 31,986 / 31,763 |

   Harlem reverse's 5th percentile falls from 55,630 (99.9% of baseline) to 50,357 (90.5%), and ≥ 99% from 47,208 to 41,499; Harlem forward's ≥ 90% falls from 49,365 to 49,304. NYP and Mount Sinai are almost unchanged because their coverage depends mainly on the original 10 study-area stations (168 St, 125 St and so on). So the previous chapter's point that "perturbing only 10 stations overestimates the coverage probability" is **real and matters for Harlem, and has very little effect for NYP and Mount Sinai**.

## 26. Checks

**(1) Setting the availability of all perturbed elevators to 1 gives the unperturbed baseline (your point 4):** 1000 draws, **all 6 "hospital × direction" pass**: mean = baseline, SD of order 10⁻¹¹ (floating-point error), minimum = baseline, residents at coverage probability = 100% = baseline, only 1 configuration (the empty one), 0 draws with loss, 0 draws with a blocked station. EL132, EL133 and EL520, which have no availability record, are also set to 1.

| Hospital / direction | Baseline | Mean of 1000 | SD | Min | Residents ≥ 99% | Residents = 100% | Unique recomputations | Draws with loss | Draws with ≥1 station blocked | Pass |
|---|---|---|---|---|---|---|---|---|---|---|
| Harlem reverse | 55,665.06 | 55,665.06 | 1.5e-11 | 55,665.06 | 55,665.06 | 55,665.06 | 1 | 0 | 0 | yes |
| Harlem forward | 49,365.04 | 49,365.04 | 1.5e-11 | 49,365.04 | 49,365.04 | 49,365.04 | 1 | 0 | 0 | yes |
| NYP/Columbia reverse | 58,457.58 | 58,457.58 | 2.2e-11 | 58,457.58 | 58,457.58 | 58,457.58 | 1 | 0 | 0 | yes |
| NYP/Columbia forward | 45,260.08 | 45,260.08 | 7.3e-12 | 45,260.08 | 45,260.08 | 45,260.08 | 1 | 0 | 0 | yes |
| Mount Sinai reverse | 45,694.35 | 45,694.35 | 1.5e-11 | 45,694.35 | 45,694.35 | 45,694.35 | 1 | 0 | 0 | yes |
| Mount Sinai forward | 31,986.21 | 31,986.21 | 1.5e-11 | 31,986.21 | 31,986.21 | 31,986.21 | 1 | 0 | 0 | yes |

**(2) Engine regression:** the original 10-station model, with **no clipping and all tracts**, using the same random numbers as the previous chapter, reproduces the baseline, the mean of the 1000 draws and the 5th percentile **identically** to the previous chapter's `mc_scenario4_summary.csv` (6/6): for example Harlem reverse mean 108,979.6 vs 108,979.6, NYP reverse 5th percentile 52,487 vs 52,487. This shows that the expansion, the clipping and the parallel rewrite did not change the engine.
**(3) Expectation consistency:** in every scenario, the "expected residents computed from the per-cell coverage probabilities" equals "the mean of the 1000 individual results" (maximum difference 2×10⁻¹¹).
**(4) Two fills:** all resident statistics are identical (see section 25).
**(5) The de-duplication speed-up is exact:** it reuses the previous chapter's way of de-duplicating by "blocked platforms ∩ platforms reached in the baseline", which was verified there against the full recomputation on 25 random draws with point-by-point agreement; the identical results in (2) of this chapter confirm this from another angle.

## 27. Share of perturbed stations among the ADA stations in the isochrones; which station or elevator costs the most when it goes out (your point 5)

### Share

"ADA stations reached" = ADA station records (GTFS parent stops) reached within 30 minutes in baseline scenario (4); "perturbed" = stations that can be given an elevator model (those with elevator dependency).

| Hospital / direction | ADA stations reached | Perturbed | Share | of which in Manhattan | Perturbed | Share |
|---|---|---|---|---|---|---|
| Harlem reverse | 40 | 28 | **70%** | 26 | 16 | 62% |
| Harlem forward | 40 | 28 | **70%** | 32 | 22 | 69% |
| NYP/Columbia reverse | 39 | 28 | **72%** | 32 | 23 | 72% |
| NYP/Columbia forward | 22 | 16 | **73%** | 17 | 12 | 71% |
| Mount Sinai reverse | 15 | 10 | **67%** | 13 | 9 | 69% |
| Mount Sinai forward | 10 | 7 | **70%** | 9 | 6 | 67% |

**So 67%–73% of ADA stations are perturbed (the previous chapter had only 15%–47%), but about 30% are still not perturbed.** The stations not perturbed are concentrated in Midtown and the Upper West Side (72 St, 96 St, Times Sq, 42 St-Port Authority, 59 St-Columbus Circle, W 4 St and so on), and these stations are treated as never out.

### The station whose outage loses the most (out on its own, both directions, other stations normal)

Loss = baseline − Manhattan residents when that station is out.

| Hospital / direction | Baseline | Station whose outage loses most (loss, share of baseline) | Second | Third |
|---|---|---|---|---|
| Harlem reverse | 55,665 | 135 St (2 3) (17,667, 32%) | 86 St (4 5 6) (5,308, 10%) | 149 St-Hostos (4) (3,981, 7%) |
| Harlem forward | 49,365 | 135 St (2 3) (14,752, 30%) | 14 St (1 2 3) (889, 2%) | 34 St-Penn Station (1 2 3) (606, 1%) |
| NYP/Columbia reverse | 58,458 | 168 St (A C) (25,089, 43%) | 125 St (A C B D) (17,512, 30%) | 59 St-Columbus Circle (A C B D) (4,424, 8%) |
| NYP/Columbia forward | 45,260 | 168 St (A C) (10,696, 24%) | 125 St (A C B D) (6,559, 14%) | Inwood-207 St (A) (3,262, 7%) |
| Mount Sinai reverse | 45,694 | 125 St (A C B D) (5,986, 13%) | 168 St (A C) (2,659, 6%) | 59 St-Columbus Circle (A C B D) (952, 2%) |
| Mount Sinai forward | 31,986 | 66 St-Lincoln Center (1) (249, 1%) | 125 St (A C B D) (224, 1%) | 168 St (A C) (192, 1%) |

### A single elevator out on its own

| Hospital / direction | Elevator whose outage loses most (loss, share of baseline, outage probability) | Top three by "outage probability × loss" (expected loss) |
|---|---|---|
| Harlem reverse | EL180 (8,414, 15%, p=2.8%) | EL180 (238); EL273 (117); EL101 (105) |
| Harlem forward | EL181 (14,751, 30%, p=1.4%) | EL181 (210); EL618 (10); EL225 (6) |
| NYP/Columbia reverse | EL139 (25,089, 43%, p=2.6%) | EL139 (650); EL140 (418); EL144 (277) |
| NYP/Columbia forward | EL139 (10,696, 24%, p=2.6%) | EL139 (277); EL141 (86); EL143 (72) |
| Mount Sinai reverse | EL142 (5,986, 13%, p=0.7%) | EL139 (69); EL143 (53); EL142 (44) |
| Mount Sinai forward | EL238 (249, 1%, p=0.4%) | EL139 (5); EL140 (3); EL144 (3) |

Stations of the elevator numbers: EL139 / EL140 = 168 St (A/C); EL142 / EL143 / EL144 = 125 St (A/C/B/D); EL180 / EL181 = 135 St (2/3); EL273 = 86 St (4/5/6); **EL101 = 149 St-Hostos (4), in the Bronx**; EL618 = 34 St-Penn Station (1/2/3); EL225 = 34 St-Penn Station (A/C/E); EL238 = 66 St-Lincoln Center (1). Expected loss = outage probability on its own × loss when out on its own; this is a rough risk ranking of single elevators and does not account for several being out at the same time.

**Answers to your questions:**
- **The largest loss from one outage: 168 St (A/C) in NYP/Columbia reverse, losing 25,089 Manhattan residents, 43% of that scenario's baseline.** It is decided by one elevator, EL139 (street to mezzanine, outage probability 2.6%): the loss when EL139 is out is exactly the same as when the whole 168 St station is out. Second in NYP reverse is 125 St (A/C/B/D), losing 17,512 (30%); 168 St in NYP forward loses 10,696 (24%).
- **Harlem: 135 St (2/3) is a single point:** reverse loses 17,667 (32%) and forward 14,752 (30%), and its elevators EL180 (largest in reverse, 8,414, 15%) and EL181 (largest in forward, 14,751, 30%) are each the only platform elevator. Second and third for Harlem reverse are 86 St (4/5/6) (5,308, 10%) and **149 St-Hostos (4) in the Bronx** (3,981, 7%): stations in the Bronx also affect Manhattan residents, which is one of the reasons for extending the perturbation to all ADA stations used.
- **Mount Sinai:** the largest in reverse is 125 St (A/C/B/D), losing 5,986 (13%); **the largest single-station loss in forward is only 249 (1%)**, which shows its forward coverage hardly depends on elevators.
- **Number of sensitive stations:** of the 45 modelled stations, those whose outage loses residents: Harlem 12 (reverse and forward each), NYP reverse 15 / forward 8, Mount Sinai reverse 7 / forward 4. Of the 128 elevators, those whose outage on its own loses residents: Harlem 15, NYP reverse 22 / forward 11, Mount Sinai reverse 11 / forward 6.

## 28. Limitations, problems met, and the overall summary of this chapter

**Limitations:**
1. **14 ADA stations used (24% of the 59) still cannot be modelled and are treated as never out,** and they are concentrated in Midtown and the Upper West Side (plus W 4 St-Wash Sq and Harlem-148 St; the list is in section 24). This **overestimates** the coverage probability upstream and downstream of those stations, especially for residents travelling to and from Midtown in scenario (4). The reason is incomplete inventory fields (8) or no inventory record (6). To repair them, the direction served could be inferred from the `serving` text or the notes in the live equipment list, but that is an inference and I did not do it; Harlem-148 St keeps the earlier "no elevator dependency" flag.
2. **The elevator structure is derived from inventory fields:** the entrance of 8 of the 45 modelled stations is inferred; elevators for transfers between stations of the same complex are not modelled (GTFS transfers are treated as always available).
3. **Elevators are independent, availability is the 12-month 24-hour average, and the outage state does not change within 30 minutes;** the real morning-peak availability may differ, and the independence assumption underestimates the large losses when several elevators are out together.
4. **Only the single time 08:00 was done** (forward depart at 08:00, reverse arrive by 08:00). Section 17 shows that the area at a single time already varies by 10%–20%, and the Monte Carlo was not repeated for several times.
5. **Only the ADA group is affected by elevators,** the baseline is "all elevators working", which does not represent a typical day; buses are still assumed to be fully usable.
6. 1000 draws; the estimation error of a coverage probability is up to about 1.6 percentage points, and the tail (5th percentile, minimum) is less stable still.
7. Residents are uniformly spread inside tracts; where people live is not where patients come from.

**Problems met:**
- No direction was specified, so both were done.
- With parallel processes only some processes were busy (the two Harlem combinations were the slowest); total 233 seconds.

**Overall effect on the earlier conclusions (Monte Carlo part):**
- After extending the perturbation to all ADA stations used, **Harlem's tail risk becomes clearly larger** (reverse 5th percentile 99.9% → 90.5% of baseline), while NYP and Mount Sinai change very little.
- **The three hospitals' coverage is vulnerable to elevator outages to different degrees:** NYP reverse is the most vulnerable (5th percentile 70%, ≥ 99% only 51%), because the single station 168 St (A/C) carries 43% of the coverage; Mount Sinai forward is almost unaffected (5th percentile 99%).
- **The key points are a few stations:** 168 St (A/C), 125 St (A/C/B/D), 135 St (2/3). Adding redundancy or stronger maintenance for the elevators of these few stations would do more to make coverage reliable than improving the whole system broadly. This is how I read the data, not a recommended conclusion, and costs and site conditions were not considered.

---

*(Original chapter: Round 11, the 14 stations that could not be modelled, Monte Carlo after the repair, final summary)*

## 29. Monte Carlo re-run after the repair

The set-up is the same as in section 24 (scenario (4), Manhattan residents, 1000 draws, both directions); the only difference is that the elevator model is replaced with the repaired one (54 stations, 132 elevators).

**Before repair → after repair** (residents, persons):

| Hospital / direction | Baseline before→after | Mean before→after | 5th percentile before→after | ≥ 99% before→after | Worst-5% mean before→after | Draws with loss before→after |
|---|---|---|---|---|---|---|
| Harlem reverse | 55,665 → 55,665 | 55,091 → 54,740 | 50,357 → **50,357** | 41,499 → **39,908** | 48,383 → 47,331 | 206 → 284 |
| Harlem forward | 49,365 → 49,365 | 49,227 → 49,076 | 49,199 → **48,238** | 47,511 → **40,861** | 46,912 → 45,042 | 284 → 352 |
| NYP/Columbia reverse | 58,458 → 58,458 | 56,837 → 56,787 | 40,942 → **40,815** | 29,980 → **29,980** | 34,515 → 34,578 | 332 → 364 |
| NYP/Columbia forward | 45,260 → 45,260 | 44,653 → 44,578 | 38,701 → **38,701** | 32,328 → **32,296** | 36,141 → 36,213 | 205 → 280 |
| Mount Sinai reverse | 45,694 → 45,694 | 45,441 → 45,415 | 43,035 → **43,035** | 39,172 → **37,997** | 42,126 → 42,052 | 145 → 160 |
| Mount Sinai forward | 31,986 → 31,986 | 31,972 → 31,949 | 31,795 → **31,763** | 31,763 → **31,054** | 31,786 → 31,481 | 83 → 143 |

**Checks (all passed):**
1. **Setting the availability of all perturbed elevators to 1 gives the baseline:** for the repaired model all 6 "hospital × direction" pass (mean = baseline, maximum SD 2.2×10⁻¹¹, minimum = baseline, only 1 configuration, 0 draws with loss).
2. The results of the **original 10-station model** are **identical** to those of the previous run, which shows that the engine did not change and the change comes only from the elevator model.
3. Under the **two fills** (EL132, EL133, EL520), all resident statistics are identical (difference 0).

**How to read it:**
- **The baseline is unchanged, the tail is worse:** the baseline resident counts are exactly unchanged (the repair changes only outage behaviour, not coverage when everything works). The mean falls slightly (Harlem reverse 55,091 → 54,740); **residents with coverage probability ≥ 99% in Harlem forward fall from 47,511 to 40,861 (−14%)**, Harlem reverse 41,499 → 39,908, Mount Sinai reverse 39,172 → 37,997; NYP is almost unchanged. Harlem forward's 5th percentile goes 49,199 → 48,238.
- **In 982 of the 1000 draws at least one perturbed station is not fully usable** (907 before). The reasons: more stations are perturbed, and among the stations newly in the model there are elevators with very low availability (12-month 24-hour average): **EL131, EL134 and EL135 at 161 St (B/D) are only 49%, 53% and 47.5%**; EL130 76% and EL129 87.5% at 3 Av-149 St (2/5); EL228 83% and EL225 90% at 34 St-Penn Station (A/C/E). These low values come from the availability table itself, and I did not check the reason (possibly long-term closure or construction).
- **New key points:** Harlem's **96 St (1/2/3)** becomes the second-largest single point (reverse −6,471, 12% of baseline; forward −4,628, 9%); the second in Harlem reverse by "outage probability × loss" is EL100 of 149 St-Hostos (2/5) (outage probability 5.7%, expected loss 226). Mount Sinai forward's largest single-station loss changes from 249 at 66 St-Lincoln Center to 709 (2%) at 96 St (1/2/3).
- **The largest single-point failures are unchanged:** NYP reverse 168 St (A/C) −25,089 (43%); Harlem 135 St (2/3) reverse −17,667 (32%), forward −14,752 (30%); Mount Sinai reverse 125 St (A/C/B/D) −5,986 (13%).
- **Part of the old results affected by the corrections:** the old models of 161 St (B/D) and 59 St-Columbus Circle (A/C/B/D) were optimistic. The table above is the combined effect of all repairs; I did not separate the effect of these two corrections.

## 30. How to read the final summary table (final_summary.csv)

One row per hospital. **Column names carry the unit, direction and time basis directly:** `residents` (persons), `area_km2` (km²), `pct` (percent); `reverse` (reverse, arriving at the hospital); `5time_mean` (mean over the five arrival deadlines 07:30–08:30), `0800` (single time 08:00); `Manhattan` (Manhattan only).

| Column | Meaning |
|---|---|
| `S1…S4_residents_reverse_5time_mean_Manhattan` | Residents in scenarios 1–4, reverse, five-time mean |
| `S1…S4_residents_SD_over_5_times_reverse_Manhattan` | Standard deviation over the five times (residents) |
| `S1…S4_area_km2_reverse_5time_mean_Manhattan` | The same for area |
| `ADAshare_subway_S2_over_S1_…_pct_…`, `ADAshare_subway+bus_S4_over_S3_…_pct_…` | ADA group as a share of anyone: subway only, with buses; each in a residents and an area version |
| `MC_S4_baseline_no_outage / mean / P5 / coverage_prob_ge99pct / ge90pct_residents_reverse_0800_Manhattan` | Monte Carlo (scenario 4, 1000 draws, reverse, single time 08:00): baseline, mean, 5th percentile, residents with coverage probability ≥ 99% and ≥ 90% |
| `worst_single_station_outage…`, `worst_station_loss_residents_Manhattan`, `…_pct_of_MC_baseline` | The station whose outage loses most (reverse, 08:00), the residents lost and the share of the MC baseline |
| `worst_single_elevator_outage…`, `worst_elevator_loss_…`, `worst_elevator_outage_probability_pct` | The single elevator whose outage loses most, and its outage probability |

**A difference in basis to note:** the earlier resident and ratio columns use the **five-time mean**, while the Monte Carlo columns use the **single time 08:00**, because the Monte Carlo was run only at 08:00. They are not on the same time basis (for example NYP scenario (4): five-time mean 51,954, Monte Carlo 08:00 baseline 58,458).

## 31. Limitations and what was not done

1. **The structure of the 9 added stations comes from the text descriptions in the MTA live equipment list,** not from a site check. Two of the alternative paths at 59 St-Columbus Circle are inferred; the Times Sq 7 line assumes the two directions share EL232. If the real structure differs, the outage effect of these stations would change.
2. **5 stations are still not perturbed** (5/59, 8%): Times Sq-42 St (S), 42 St-Port Authority (A/C/E), 51 St (6) and W 4 St-Wash Sq (A/C/E) are treated as never out, so the coverage probability is overestimated; Harlem-148 St really has no elevator record.
3. The other limitations are the same as in section 28: independent elevators, 12-month 24-hour average availability, outage state unchanged within 30 minutes, residents uniform inside tracts, all buses treated as usable.
4. **Not done:** a site or other-source check of the added stations; repeating the Monte Carlo over the five times; separating the effect of the "2 corrected old models".

---

## Appendix: old and new section numbers

| New section | Original chapter | Original section | Title |
|---|---|---|---|
| 1 | Round 4: 148 St elevator search, ADA stations near hospitals, NYP/Columbia 30-minute isochrone | 24 | NYP/Columbia 30-minute isochrone |
| 2 | Round 4: 148 St elevator search, ADA stations near hospitals, NYP/Columbia 30-minute isochrone | 25 | New files in this round |
| 3 | Round 5: adding buses (NYP/Columbia isochrone) | 26 | Results |
| 4 | Round 5: adding buses (NYP/Columbia isochrone) | 27 | Bus data: which feeds are used, and whether data for other boroughs is needed |
| 5 | Round 5: adding buses (NYP/Columbia isochrone) | 28 | Assumptions used |
| 6 | Round 5: adding buses (NYP/Columbia isochrone) | 29 | Problems met |
| 7 | Round 5: adding buses (NYP/Columbia isochrone) | 30 | New files in this round |
| 8 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 36 | Output of this chapter |
| 9 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 37 | Results of the four scenarios for the three hospitals |
| 10 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 38 | Area: land only, split into Manhattan and other boroughs |
| 11 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 39 | Residents: ACS ambulatory-difficulty population, allocated by area share |
| 12 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 40 | Relative ratios of residents |
| 13 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 41 | Direction check: computing "arrive by 08:00" in reverse |
| 14 | Round 8: four-scenario isochrones for the three hospitals, land area, ACS residents and direction check | 42 | Problems met and limitations |
| 15 | Round 9: residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo | 43 | Output of this chapter |
| 16 | Round 9: residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo | 44 | Residents on the reverse basis (arriving at the hospital), split into Manhattan and the Bronx |
| 17 | Round 9: residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo | 45 | Averaging over several departure times: area, residents and variation between times |
| 18 | Round 9: residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo | 46 | Monte Carlo: coverage probability of scenario (4) under random elevator outages |
| 19 | Round 9: residents on the reverse basis, averaging over several departure times, elevator-outage Monte Carlo | 47 | Problems met in this chapter |
| 20 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 48 | Method and output of this chapter |
| 21 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 49 | Extent of Manhattan: official boundary, water removed; Marble Hill and Roosevelt Island |
| 22 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 50 | Before and after clipping |
| 23 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 51 | What changed after removing the other boroughs: two main points |
| 24 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 52 | Monte Carlo set-up, and differences from the previous chapter |
| 25 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 53 | Results: Manhattan residents, scenario (4), expanded model |
| 26 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 54 | Checks |
| 27 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 55 | Share of perturbed stations among the ADA stations in the isochrones; which station or elevator costs the most when it goes out |
| 28 | Round 10: clipping to Manhattan, expanded elevator Monte Carlo | 56 | Limitations, problems met, and the overall summary of this chapter |
| 29 | Round 11: the 14 stations that could not be modelled, Monte Carlo after the repair, final summary | 58 | Monte Carlo re-run after the repair |
| 30 | Round 11: the 14 stations that could not be modelled, Monte Carlo after the repair, final summary | 59 | How to read the final summary table (final_summary.csv) |
| 31 | Round 11: the 14 stations that could not be modelled, Monte Carlo after the repair, final summary | 60 | Limitations and what was not done |
