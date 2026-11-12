"""NEW: adds mean_pct_of_own_baseline and p5_pct_of_own_baseline to the Monte Carlo summary (same code as the ad-hoc step 0).
Baseline = the row's own baseline (same hospital, direction, departure time, scenario, model, fill).
Input : outputs/mc_manhattan_summary_fixed.csv   Output: outputs/mc_manhattan_summary_fixed_with_pct.csv (the input file is not touched)"""
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py

import pandas as pd
M=pd.read_csv(O+"mc_manhattan_summary_fixed.csv")
M["mean_pct_of_own_baseline"]=(100*M["mean"]/M["baseline_res"]).round(2); M["p5_pct_of_own_baseline"]=(100*M["p5"]/M["baseline_res"]).round(2)
M.to_csv(O+"mc_manhattan_summary_fixed_with_pct.csv",index=False)
