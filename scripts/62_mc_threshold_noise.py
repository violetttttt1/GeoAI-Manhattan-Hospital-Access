import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
from _paths import S, R, O, REB, ROOT   # all paths come from scripts/_paths.py
exec(open((S+"iso3_core.py")).read().split("HOSP=")[0])
exec(open((S+"iso4_grid.py")).read())
D=pickle.load(open(S+"mc_counts.pkl","rb")); DC=DENS[TRID]; M=pd.read_csv((O+"mc_scenario4_summary.csv")); M=M[M.fill=="mean"]
print("residents whose estimated coverage probability lies in [88%,92%] (sampling-noise band around the 90% line), and in [93%,97%]:")
for (h,dn),(C_,crop) in D["counts"].items():
    # counts grid is cropped to crop0 of baseline
    d=DC; b=M[(M.hospital==h)&(M.direction==dn)].baseline_residents.iloc[0]
    band=lambda lo,hi: float(d[(C_>=lo)&(C_<=hi)].sum())
    print(f"{h[:24]:24s} {dn:7s} baseline {b:8.0f} | [88,92]%: {band(880,920):7.0f} ({100*band(880,920)/b:4.1f}%) | [93,97]%: {band(930,970):7.0f} | exactly in 90-95 band: {band(900,949):7.0f}")
print("max standard error of an estimated probability with 1000 draws: %.2f pts"%(100*np.sqrt(0.25/1000)))
