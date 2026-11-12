# Project status

## Goal
Quantify the gap between "accessible on the map" and "actually reachable" for three hospitals on Manhattan island (Harlem Hospital, NYP/Columbia, Mount Sinai Morningside): first subway and bus, then elevator failures, finally curb ramps. The study is limited to Manhattan island, and residents are counted only in Manhattan tracts.

## Done
- 7 datasets downloaded and health-checked (`docs/checks_data.md`).
- Study-area station table and per-elevator detail. Elevator models were added for 9 more stations; 54 stations can now be modelled and 5 cannot. 148 St is treated as "no elevator dependency", not verified on site.
- 30-minute isochrones for each of the three hospitals in 4 scenarios: anyone and ADA-stations-only, each with and without bus. Forward and reverse, averaged over five departure times; residents are ACS residents with an ambulatory difficulty.
- Monte Carlo of elevator failures (scenario 4, 1000 draws, covering 90% to 100% of the ADA stations in Manhattan) and the single-point-failure ranking.
- Live elevator-outage fetching (runs on the team lead's computer; a snapshot is shared on Saturday morning).

## Preliminary findings (reverse, Manhattan residents; all preliminary, do not quote exact values)
- ADA group as a share of anyone, subway only: NYP about 75%, Harlem about 71%, Mount Sinai about 42%. With bus added: Harlem about 84%, NYP about 81%, Mount Sinai about 69%. The order of Harlem and NYP is not stable; Mount Sinai is the lowest.
- Monte Carlo, worst 5% of days relative to the own baseline: NYP about 70%, Harlem about 90%, Mount Sinai about 94%.
- Single-point dependence: at NYP, one outage at 168 St (A/C) loses about 43% of residents and depends on one elevator, EL139. At Harlem, 135 St (2/3) loses about 32%.
- Note: resident counts use the mean of five departure times, while the Monte Carlo uses only 08:00. The time bases differ, so do not compare absolute values directly.

## Known problems — read first
- A few elevators in the study area have no record in the availability table; the two fill values are used, and for now this does not change the results.
- 5 ADA stations have no elevator model and are treated as always available, which overstates coverage near them. For the 9 stations added later, the structure comes from the text descriptions in the MTA equipment list and has not been checked on site.
- Several elevators at 161 St (B/D) have an availability of only about 50%; the reason has not been checked.
- Ramp data were collected in 2017 to 2020 and have been rebuilt since. Measured values cannot show ADA compliance by themselves. The MBPO validation sample is small.
- Times in the live data carry no time-zone marker, and the `ismaintenanceoutage` field is not usable.
- Assumptions: elevator failures are independent; 24-hour average availability; walking speed 4.8 km/h; all buses treated as accessible; residents spread uniformly inside each tract.

## To do
- t1: Ramp walking network. Start with 400 m around NYP, using three states ("passable when measured", "not passable", "modified since") and running a strict and a lenient version.
- t2: Priority ranking. Turn the single-point-failure ranking into "expected benefit of improving one elevator's availability", then add ramps.
- t3: XGBoost elevator-failure prediction, split by time and compared with the historical average.
- t4: Live-data comparison. Use the snapshots to test the station probabilities and the independence assumption, and build the Saturday "right now" layer.
- t5: Field check of 20 to 30 ramps, plus the elevator structures at 181 St, 175 St and 148 St.
- t6: Pitch and slides.

## Rules
- Do not modify existing scripts or the files in `data/clean`. To change something, create a new file whose name starts with the task number, for example `t1_`.
- Write results in files such as `docs/checks_t1.md`, without personal names.
- Label every number "preliminary" and do not quote exact areas.
