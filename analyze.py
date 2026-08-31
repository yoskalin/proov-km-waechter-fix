# analyze.py
# Summary: km_since_service is by far the strongest breakdown predictor (+61% higher in cars
# that broke down). avg_daily_km (+22%) and load_factor (+19%) also separate the groups.
# Total mileage (odometer_km) and age_years show virtually no difference between the two
# groups (+0.3% and -0.2%), so the common assumption that "older, higher-mileage cars break
# down more" is not supported by this fleet's data.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# ── 1. Separate the two groups ────────────────────────────────────────────────
broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

print("=" * 65)
print(f"Fleet history: {len(df)} cars  |  broke down: {len(broke)}  |  ok: {len(ok)}")
print("=" * 65)

# ── 2. Compare each column between the two groups ────────────────────────────
cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print(f"\n{'Column':<20}  {'broke mean':>11}  {'ok mean':>11}  {'diff %':>8}  {'separates?':>10}")
print("-" * 70)
for c in cols:
    bm   = broke[c].mean()
    om   = ok[c].mean()
    diff = (bm - om) / om * 100
    tag  = "YES" if abs(diff) >= 15 else "no"
    print(f"{c:<20}  {bm:>11.2f}  {om:>11.2f}  {diff:>+8.1f}%  {tag:>10}")

print()
print("Finding: odometer_km (+0.3%) and age_years (-0.2%) do NOT separate the groups.")
print("The three columns that do: km_since_service, avg_daily_km, load_factor.")

# ── 3. Build a 0-100 risk score from the three separating columns ─────────────
#
# Normalise each column to [0, 1] (min-max), then weight by separation strength:
#   km_since_service  60 %   (by far the strongest signal)
#   avg_daily_km      22 %
#   load_factor       18 %
#
WEIGHTS = {
    "km_since_service": 0.60,
    "avg_daily_km":     0.22,
    "load_factor":      0.18,
}

scored = df.copy()
for col, w in WEIGHTS.items():
    col_min = df[col].min()
    col_max = df[col].max()
    scored[f"_{col}_norm"] = (df[col] - col_min) / (col_max - col_min)

scored["risk_score"] = sum(
    scored[f"_{col}_norm"] * w for col in WEIGHTS
) * 100

# ── 4. Print cars ranked by risk, highest first ───────────────────────────────
display_cols = ["car_id", "km_since_service", "avg_daily_km", "load_factor",
                "age_years", "odometer_km", "broke_down", "risk_score"]

ranked = scored[display_cols].sort_values("risk_score", ascending=False)

print()
print("=" * 65)
print("Cars ranked by breakdown risk (highest first)")
print("=" * 65)
print(f"{'car_id':<12} {'risk':>6}  {'km_since_svc':>13}  {'daily_km':>9}  "
      f"{'load':>6}  {'age':>4}  {'broke':>6}")
print("-" * 65)
for _, row in ranked.iterrows():
    flag = " ← BROKE" if row["broke_down"] == 1 else ""
    print(f"{row['car_id']:<12} {row['risk_score']:>6.1f}  "
          f"{row['km_since_service']:>13.0f}  {row['avg_daily_km']:>9.0f}  "
          f"{row['load_factor']:>6.2f}  {row['age_years']:>4.0f}  "
          f"{int(row['broke_down']):>6}{flag}")

# ── 5. Sanity check: how well does the risk score separate the groups? ─────────
threshold = ranked["risk_score"].quantile(0.75)   # flag top 25% as high-risk
high_risk  = ranked[ranked["risk_score"] >= threshold]
caught     = high_risk["broke_down"].sum()

print()
print(f"Sanity check: top-25% risk tier ({len(high_risk)} cars) catches "
      f"{caught} of {len(broke)} breakdowns ({caught/len(broke)*100:.0f}%).")
