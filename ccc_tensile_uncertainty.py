"""
Tensile data analysis and uncertainty for a carbon-carbon composite (CCC).

Source data: my MSc thesis, Table 1 (room-temperature tensile test, 3 specimens)
and Table 2 (one hot-tensile test at 250 C).

Limits: only 3 specimens, so the t-distribution is used and no bootstrap.
The measurement uncertainties below are ASSUMED typical values. Replace them
with the real instrument specifications.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

DATA_FILE = Path(__file__).parent / "data" / "tensile_specimens.csv"
OUT_DIR = Path(__file__).parent / "results"

FEM_PREDICTION_MPA = 90.65          # from my MATLAB 1D FEM project
HOT_TENSILE_UTS_MPA = 108.0         # thesis Table 2, single specimen
HOT_TENSILE_TEMP_C = 250            # thesis Table 2

# ASSUMED measurement uncertainties (1 standard deviation). Edit these.
U_DIMENSION_MM = 0.01               # caliper / micrometer resolution
U_LOAD_FRACTION = 0.01              # load cell accuracy, 1 % of reading
N_MONTE_CARLO = 100_000
RNG_SEED = 42


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_FILE)

    # 1. Recompute area and strength from the raw measurements
    df["area_calc_mm2"] = df["gauge_width_mm"] * df["gauge_thickness_mm"]
    df["uts_calc_MPa"] = df["ultimate_load_kN"] * 1000.0 / df["area_calc_mm2"]
    df["area_diff_mm2"] = df["area_calc_mm2"] - df["area_reported_mm2"]
    df["uts_diff_MPa"] = df["uts_calc_MPa"] - df["uts_reported_MPa"]

    print("\n1) Recalculated vs reported values")
    print(df.round(2).to_string(index=False))

    # 2. Scatter between specimens
    uts = df["uts_calc_MPa"].to_numpy()
    n = len(uts)
    mean = uts.mean()
    sd = uts.std(ddof=1)
    sem = sd / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, df=n - 1)
    ci_low, ci_high = mean - t_crit * sem, mean + t_crit * sem

    print("\n2) Specimen-to-specimen scatter (n = %d)" % n)
    print(f"   mean UTS            : {mean:.2f} MPa")
    print(f"   standard deviation  : {sd:.2f} MPa  (CV = {100 * sd / mean:.1f} %)")
    print(f"   95 % CI of the mean : {ci_low:.1f} to {ci_high:.1f} MPa (t = {t_crit:.2f})")

    # 3. Monte Carlo propagation of measurement uncertainty
    rng = np.random.default_rng(RNG_SEED)
    mc_sd = []
    for _, row in df.iterrows():
        w = rng.normal(row.gauge_width_mm, U_DIMENSION_MM, N_MONTE_CARLO)
        t = rng.normal(row.gauge_thickness_mm, U_DIMENSION_MM, N_MONTE_CARLO)
        p = rng.normal(row.ultimate_load_kN, U_LOAD_FRACTION * row.ultimate_load_kN,
                       N_MONTE_CARLO)
        mc_sd.append((p * 1000.0 / (w * t)).std())
    mc_sd = np.array(mc_sd)

    print("\n3) Measurement uncertainty per specimen (Monte Carlo, assumed inputs)")
    for sid, u in zip(df["sample_id"], mc_sd):
        print(f"   {sid}: +/- {u:.2f} MPa (1 sigma)")
    print(f"   typical measurement uncertainty : {mc_sd.mean():.2f} MPa")
    print(f"   specimen-to-specimen scatter    : {sd:.2f} MPa")
    print(f"   -> scatter is about {sd / mc_sd.mean():.0f}x larger than measurement error,")
    print("      so material variability dominates, not the measurement.")

    # 4. FEM vs experiment
    diff = FEM_PREDICTION_MPA - mean
    inside_ci = ci_low <= FEM_PREDICTION_MPA <= ci_high
    print("\n4) FEM vs experiment")
    print(f"   FEM prediction      : {FEM_PREDICTION_MPA:.2f} MPa")
    print(f"   experimental mean   : {mean:.2f} MPa")
    print(f"   difference          : {diff:+.2f} MPa ({100 * diff / mean:+.2f} %)")
    print(f"   inside 95 % CI?     : {inside_ci}")

    # 5. Plot
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(n)
    ax.errorbar(x, uts, yerr=mc_sd, fmt="o", capsize=4, color="#1f4e79",
                label="Specimens (+/- assumed measurement uncertainty)")
    ax.axhspan(ci_low, ci_high, color="#1f4e79", alpha=0.12,
               label=f"95 % CI of mean ({ci_low:.0f}-{ci_high:.0f} MPa)")
    ax.axhline(mean, color="#1f4e79", lw=1.2, label=f"Experimental mean {mean:.1f} MPa")
    ax.axhline(FEM_PREDICTION_MPA, color="#c0392b", ls="--", lw=1.5,
               label=f"1D FEM prediction {FEM_PREDICTION_MPA:.2f} MPa")
    ax.scatter([n], [HOT_TENSILE_UTS_MPA], marker="s", color="#7f8c8d", zorder=3,
               label=f"Hot tensile, {HOT_TENSILE_TEMP_C} C (single specimen)")
    ax.set_xticks(list(x) + [n])
    ax.set_xticklabels(list(df["sample_id"]) + ["Hot"])
    ax.set_ylabel("Ultimate tensile strength (MPa)")
    ax.set_title("CCC tensile strength: experiment, scatter and FEM")
    ax.set_ylim(70, 120)
    ax.legend(fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "tensile_uncertainty.png", dpi=200)

    df.round(3).to_csv(OUT_DIR / "tensile_recalculated.csv", index=False)
    print(f"\nSaved results to: {OUT_DIR}")


if __name__ == "__main__":
    main()
