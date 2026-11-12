# Final summary: ADA accessibility of three hospitals (Manhattan only)

**Scope and units.** Scope = the official NYC Manhattan borough boundary (land only, no river surface; includes Marble Hill; Roosevelt Island is inside the boundary but is never reached). **Residents** = ACS 2020–2024 residents with an ambulatory difficulty in Manhattan tracts (persons), allocated by tract area share. **Area** = km². **All directions are reverse**: origins from which the hospital is reached by 08:00 with a total travel time of at most 30 minutes. Scenarios: (1) anyone, subway; (2) ADA subway stations only; (3) anyone, subway plus bus; (4) ADA subway stations plus bus (all buses and bus stops are treated as usable). Walking speed 4.8 km/h; curb ramps are not modelled.

## 1. Residents by scenario (persons, reverse, mean over five arrive-by times 07:30–08:30; SD of the five times in parentheses)

| Hospital | (1) Anyone, subway | (2) ADA stations only | (3) Subway plus bus | (4) ADA stations plus bus |
|---|---|---|---|---|
| Harlem | 62,366 (SD 3,548) | 44,472 (3,585) | 65,860 (4,626) | 55,015 (2,945) |
| NYP/Columbia | 59,336 (SD 2,670) | 44,677 (4,409) | 64,248 (3,003) | 51,954 (4,998) |
| Mount Sinai | 57,017 (SD 2,976) | 23,699 (581) | 66,594 (4,286) | 45,598 (7,827) |

## 2. ADA group as a share of anyone (residents, reverse, five-time mean; area-based share in parentheses)

| Hospital | ADA share, subway only ((2) ÷ (1)) | With bus ((4) ÷ (3)) | Help from bus for the ADA group ((4) − (2), residents) |
|---|---|---|---|
| Harlem | **71%** (area 70%) | **84%** (area 80%) | +10,543 (+24%) |
| NYP/Columbia | **75%** (area 73%) | **81%** (area 77%) | +7,277 (+16%) |
| Mount Sinai | **42%** (area 41%) | **68%** (area 62%) | +21,899 (+92%) |

## 3. Monte Carlo: Manhattan residents in scenario (4) under random elevator outages (persons, reverse, **single time 08:00**, 1000 draws)

| Hospital | Baseline (no outage) | Mean | 5th percentile | Coverage probability ≥ 99% | Station whose outage loses most | Elevator whose outage loses most |
|---|---|---|---|---|---|---|
| Harlem | 55,665 | 54,740 (98.3%) | **50,357** (90%) | 39,908 (72%) | 135 St (2 3): −17,667 (32%) | EL180 (135 St (2 3)): −8,414 (15%, outage probability 2.8%) |
| NYP/Columbia | 58,458 | 56,787 (97.1%) | **40,815** (70%) | 29,980 (51%) | 168 St (A C): −25,089 (43%) | EL139 (168 St (A C)): −25,089 (43%, outage probability 2.6%) |
| Mount Sinai | 45,694 | 45,415 (99.4%) | **43,035** (94%) | 37,997 (83%) | 125 St (A C B D): −5,986 (13%) | EL142 (125 St (A C B D)): −5,986 (13%, outage probability 0.7%) |

"Coverage probability ≥ 99%" = residents in grid cells that are inside the isochrone in at least 990 of the 1000 draws. Baseline = all elevators working. This table uses the single time 08:00, so it is not on the same time basis as the five-time means in the first two tables (for example NYP scenario (4): 51,954 versus 58,458).

## 4. How to read it

- **ADA share:** with subway only, NYP 75% > Harlem 71% > Mount Sinai 42%; with bus added, Harlem 84% > NYP 81% > Mount Sinai 69%. **The gap between Harlem and NYP (3–4 percentage points) is smaller than the variation between departure times, so their order is not stable; Mount Sinai is clearly the lowest.**
- **Help from bus:** largest for Mount Sinai (+21,900 residents, +92%), then Harlem +10,542 (+24%), then NYP +7,277 (+16%).
- **Elevator-outage risk is concentrated in a few stations:** at NYP, one outage at 168 St (A/C) loses 43% of coverage (decided by elevator EL139); at Harlem, 135 St (2/3) loses 32%; at Mount Sinai, 125 St (A/C/B/D) loses 13%. 5th percentile: NYP keeps only 70%, Harlem 90%, Mount Sinai 94%.
- **The 14 stations that originally could not be given an elevator model:** 9 were added (72 St, 96 St, 49 St, 149 St-Hostos (2/5), 161 St-Yankee Stadium (4), Times Sq-42 St for 1/2/3, 7 and N/Q/R/W, and 59 St-Columbus Circle (1)), and 2 older models were corrected (161 St B/D and 59 St-Columbus Circle A/C/B/D). **5 still cannot be modelled:** Times Sq-42 St (S), 42 St-Port Authority (A/C/E), 51 St (6) and W 4 St-Wash Sq (A/C/E), because the platform-elevator connections are not clear from the data; and Harlem-148 St, which has no elevator in any dataset and is treated as "no elevator dependency" (not verified on site). With the added stations, the share of arrived-at ADA stations that can be perturbed rose from 67%–73% to 90%–100%.

**Main limitations:** elevator failures are independent; availability is the 12-month 24-hour average; an outage state does not change within 30 minutes; residents are spread uniformly inside each tract; all buses are treated as usable, which is an upper bound for the ADA group; the structure of the 9 added stations comes from the text descriptions in the MTA live equipment list, and 2 of the alternative paths (59 St-Columbus Circle) are inferred; the Monte Carlo covers only the single time 08:00. Details are in `final_summary.csv` and sections 57–60 of the original checks log (now in `docs/checks_isochrone.md`).
