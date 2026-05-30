"""
Motor Efficiency Model — fitted from 106 measured data points.
"""

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

# ── Motor parameters ─────────────────────────────────────────────────────────
GR       = 5
R_WHEEL  = 0.295        # m
PP       = 10
R_PHASE  = 0.0332       # Ω
LAMBDA_F = 0.012934     # Wb
MAX_PIN  = 720.0        # W  (VESC limit)
MAX_IDC  = 30.1         # A

# ── Dataset ───────────────────────────────────────────────────────────────────
raw = [
    (1,  0.6, 385, 24.19,  49.02, 2.24,  109.80, 22.0),
    (2,  0.6, 387, 24.32,  49.02, 2.28,  111.77, 21.8),
    (3,  0.6, 386, 24.25,  49.02, 2.25,  110.30, 22.0),
    (4,  0.7, 388, 28.44,  49.02, 2.31,  113.24, 25.1),
    (5,  0.7, 386, 28.30,  49.02, 2.32,  113.73, 24.9),
    (6,  0.8, 387, 32.42,  49.02, 2.37,  116.18, 27.9),
    (7,  0.9, 387, 36.48,  49.01, 2.50,  122.53, 29.8),
    (8,  1.0, 386, 40.42,  49.01, 2.63,  128.90, 31.4),
    (9,  1.1, 388, 44.70,  49.01, 2.72,  133.31, 33.5),
    (10, 1.3, 385, 52.41,  49.00, 2.79,  136.71, 38.3),
    (11, 1.4, 388, 56.89,  49.00, 2.94,  144.06, 39.5),
    (12, 1.6, 385, 64.51,  49.00, 3.11,  152.39, 42.3),
    (13, 1.8, 387, 72.95,  48.99, 3.29,  161.18, 45.3),
    (14, 1.9, 386, 76.80,  48.99, 3.47,  170.00, 45.2),
    (15, 2.1, 386, 84.89,  48.99, 3.60,  176.36, 48.1),
    (16, 2.3, 386, 92.97,  48.98, 3.86,  189.06, 49.2),
    (17, 2.4, 385, 96.76,  48.98, 3.95,  193.47, 50.0),
    (18, 2.8, 387, 113.48, 48.97, 4.10,  200.78, 56.5),
    (19, 2.9, 385, 116.92, 48.97, 4.50,  220.37, 53.1),
    (20, 3.2, 386, 129.35, 48.96, 4.63,  226.68, 57.1),
    (21, 3.4, 387, 137.79, 48.95, 4.95,  242.30, 56.9),
    (22, 3.6, 384, 144.77, 48.95, 5.08,  248.67, 58.2),
    (23, 4.3, 386, 173.82, 48.93, 5.60,  274.01, 63.4),
    (24, 4.4, 386, 177.86, 48.93, 5.86,  286.73, 62.0),
    (25, 5.1, 386, 206.16, 48.91, 6.33,  309.60, 66.6),
    (26, 5.4, 386, 218.28, 48.90, 6.85,  334.97, 65.2),
    (27, 5.7, 384, 229.22, 48.89, 7.01,  342.72, 66.9),
    (28, 6.4, 386, 258.71, 48.88, 7.50,  366.60, 70.6),
    (29, 6.4, 385, 258.04, 48.87, 7.85,  383.63, 67.3),
    (30, 7.2, 385, 290.29, 48.86, 8.33,  407.00, 71.3),
    (31, 7.7, 385, 310.45, 48.84, 8.84,  431.75, 71.9),
    (32, 8.0, 383, 320.87, 48.83, 9.22,  450.21, 71.3),
    (33, 8.8, 384, 353.88, 48.82, 9.70,  473.55, 74.7),
    (34, 8.9, 384, 357.90, 48.80, 10.08, 491.90, 72.8),
    (35, 9.7, 384, 390.07, 48.79, 10.56, 515.22, 75.7),
    (36, 10.3,384, 414.20, 48.78, 11.12, 542.43, 76.4),
    (37, 10.5,383, 421.14, 48.76, 11.60, 565.62, 74.5),
    (38, 11.5,383, 461.25, 48.75, 12.25, 597.19, 77.2),
    (39, 11.9,383, 477.30, 48.73, 12.77, 622.28, 76.7),
    (40, 12.5,381, 498.74, 48.72, 13.38, 651.87, 76.5),
    (41, 13.5,383, 541.47, 48.69, 14.04, 683.61, 79.2),
    (42, 13.8,381, 550.61, 48.68, 14.57, 709.27, 77.6),
    (43, 14.8,381, 590.51, 48.67, 15.33, 746.11, 79.1),
    (44, 15.7,382, 628.07, 48.66, 15.96, 776.61, 80.9),
    (45, 16.0,380, 636.72, 48.65, 16.66, 810.51, 78.6),
    (46, 17.0,380, 676.51, 48.63, 17.41, 846.65, 79.9),
    (47, 18.0,380, 716.31, 48.62, 18.16, 882.94, 81.1),
    (48, 18.4,378, 728.37, 48.61, 18.90, 918.73, 79.3),
    (49, 19.5,378, 771.91, 48.59, 19.71, 957.71, 80.6),
    (50, 20.6,378, 815.46, 48.57, 20.58, 999.57, 81.6),
    (51, 21.1,376, 830.83, 48.56, 21.31,1034.81, 80.3),
    (52, 22.2,376, 874.14, 48.54, 22.16,1075.65, 81.3),
    (53, 23.4,376, 921.39, 48.52, 23.05,1118.39, 82.4),
    (54, 24.2,374, 947.83, 48.49, 23.92,1159.88, 81.7),
    (55, 24.9,373, 972.64, 48.46, 24.75,1199.39, 81.1),
    (56, 26.3,374,1030.08, 48.44, 25.75,1247.33, 82.6),
    (57, 27.4,373,1070.29, 48.41, 26.71,1293.03, 82.8),
    (58, 28.1,371,1091.75, 48.39, 27.47,1329.27, 82.1),
    (59, 29.1,370,1127.55, 48.36, 28.47,1376.81, 81.9),
    (60, 30.2,370,1170.18, 48.33, 29.40,1420.90, 82.4),
    (61, 31.4,369,1213.38, 48.31, 30.10,1454.13, 83.4),
    (62, 32.2,354,1193.72, 48.31, 29.73,1436.26, 83.1),
    (63, 33.3,342,1192.65, 48.31, 29.73,1436.26, 83.0),
    (64, 34.3,331,1188.95, 48.31, 29.74,1436.74, 82.8),
    (65, 35.5,318,1182.22, 48.31, 29.77,1438.19, 82.2),
    (66, 36.7,308,1183.75, 48.31, 29.77,1438.19, 82.3),
    (67, 37.7,299,1180.47, 48.31, 29.78,1438.67, 82.1),
    (68, 38.7,290,1175.31, 48.31, 29.78,1438.67, 81.7),
    (69, 39.8,282,1175.37, 48.31, 29.77,1438.19, 81.7),
    (70, 41.0,273,1172.17, 48.31, 29.76,1437.71, 81.5),
    (71, 41.9,266,1167.18, 48.31, 29.76,1437.71, 81.2),
    (72, 42.8,258,1156.39, 48.31, 29.74,1436.74, 80.5),
    (73, 43.8,251,1151.30, 48.31, 29.73,1436.26, 80.2),
    (74, 45.1,243,1147.69, 48.31, 29.73,1436.26, 79.9),
    (75, 45.8,237,1136.73, 48.31, 29.73,1436.26, 79.1),
    (76, 47.5,231,1149.07, 48.31, 29.75,1437.22, 80.0),
    (77, 48.3,225,1138.08, 48.31, 29.77,1438.19, 79.1),
    (78, 49.4,218,1127.78, 48.31, 29.78,1438.67, 78.4),
    (79, 50.6,213,1128.68, 48.30, 29.78,1438.37, 78.5),
    (80, 51.9,207,1125.07, 48.31, 29.79,1439.16, 78.2),
    (81, 52.0,202,1100.01, 48.31, 29.78,1438.67, 76.5),
    (82, 53.8,197,1109.92, 48.31, 29.78,1438.67, 77.1),
    (83, 54.2,193,1095.47, 48.31, 29.77,1438.19, 76.2),
    (84, 55.9,187,1094.70, 48.31, 29.77,1438.19, 76.1),
    (85, 56.9,182,1084.49, 48.31, 29.77,1438.19, 75.4),
    (86, 57.7,178,1075.57, 48.31, 29.76,1437.71, 74.8),
    (87, 58.8,173,1065.28, 48.31, 29.75,1437.22, 74.1),
    (88, 59.9,169,1060.12, 48.31, 29.75,1437.22, 73.8),
    (89, 61.1,165,1055.77, 48.31, 29.74,1436.74, 73.5),
    (90, 61.7,160,1033.83, 48.31, 29.74,1436.74, 72.0),
    (91, 63.7,157,1047.32, 48.31, 29.74,1436.74, 72.9),
    (92, 64.4,153,1031.86, 48.31, 29.73,1436.26, 71.8),
    (93, 65.4,148,1013.64, 48.31, 29.72,1435.77, 70.6),
    (94, 66.0,145,1002.20, 48.31, 29.72,1435.77, 69.8),
    (95, 67.5,141, 996.70, 48.31, 29.72,1435.77, 69.4),
    (96, 68.4,137, 981.34, 48.31, 29.72,1435.77, 68.3),
    (97, 70.1,134, 983.71, 48.31, 29.71,1435.29, 68.5),
    (98, 70.6,130, 961.15, 48.31, 29.71,1435.29, 67.0),
    (99, 71.8,124, 932.37, 48.32, 29.31,1416.26, 65.8),
    (100,72.9,115, 877.95, 48.35, 28.19,1362.99, 64.4),
    (101,73.6,106, 817.01, 48.41, 27.07,1309.65, 62.4),
    (102,75.1, 97, 762.88, 48.41, 25.71,1244.62, 61.3),
    (103,75.8, 87, 690.61, 48.45, 24.60,1191.87, 57.9),
    (104,76.2, 68, 542.63, 48.51, 21.99,1066.74, 50.9),
    (105,76.7, 12,  96.39, 48.67, 11.94, 581.12, 16.6),
    (106,76.6,  0,   0.00, 48.87,  7.65, 373.86,  0.0),
]

cols = ['point','T_wheel_Nm','RPM_wheel','P_out_W','V_dc','I_dc_A','P_in_W','eta_pct']
df = pd.DataFrame(raw, columns=cols)

# Derived columns
df['omega_motor'] = df['RPM_wheel'] * GR * 2 * np.pi / 60.0
df['P_loss'] = df['P_in_W'] - df['P_out_W']
df['I2']     = df['I_dc_A'] ** 2

# ── STEP 1: Loss Model Fitting ────────────────────────────────────────────────
print("=" * 70)
print("STEP 1 — LOSS MODEL FITTING")
print("=" * 70)

# Zone 1: points 1-61 (index 0-60)
z1 = df.iloc[:61].copy()
z2 = df.iloc[61:98].copy()   # points 62-98

# Fit P_loss = R_eff * I² + P_iron_z1  (linear regression with intercept)
coeffs_z1 = np.polyfit(z1['I2'], z1['P_loss'], 1)
R_eff      = coeffs_z1[0]
P_iron_z1  = coeffs_z1[1]

omega_mean_z1 = z1['omega_motor'].mean()
k_iron1 = P_iron_z1 / omega_mean_z1

print(f"\nZone 1 regression (pts 1-61): P_loss = R_eff * I² + intercept")
print(f"  R_eff         = {R_eff:.6f}  Ω")
print(f"  P_iron_z1     = {P_iron_z1:.4f}  W  (intercept)")
print(f"  mean ω_motor  = {omega_mean_z1:.4f}  rad/s")
print(f"  k_iron1       = {k_iron1:.6f}  W·s/rad")

# Zone 2: fixed current ~29.7 A, varying speed (pts 62-98)
z2_Piron_res = z2['P_loss'] - R_eff * z2['I2']
# Fit through origin: k_iron2 = sum(ω·ΔP) / sum(ω²)
k_iron2 = np.dot(z2['omega_motor'], z2_Piron_res) / np.dot(z2['omega_motor'], z2['omega_motor'])

print(f"\nZone 2 regression (pts 62-98): P_iron_res = k_iron2 * ω (through origin)")
print(f"  k_iron2       = {k_iron2:.6f}  W·s/rad")

# Choose better k_iron (evaluate residuals on full dataset for both)
def model_Pin(df_, k):
    return df_['P_out_W'] + R_eff * df_['I2'] + k * df_['omega_motor']

err1 = np.abs((model_Pin(df, k_iron1) - df['P_in_W']) / df['P_in_W'] * 100).mean()
err2 = np.abs((model_Pin(df, k_iron2) - df['P_in_W']) / df['P_in_W'] * 100).mean()
print(f"\n  MAE P_in error with k_iron1: {err1:.3f} %")
print(f"  MAE P_in error with k_iron2: {err2:.3f} %")

k_iron = k_iron2 if err2 < err1 else k_iron1
chosen = "k_iron2" if err2 < err1 else "k_iron1"
print(f"\n  >>> Chosen: {chosen} = {k_iron:.6f}  W·s/rad")

# ── STEP 2: Verification ──────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 2 — VERIFICATION (all 106 points)")
print("=" * 70)

df['P_in_model'] = df['P_out_W'] + R_eff * df['I2'] + k_iron * df['omega_motor']
df['eta_model']  = df['P_out_W'] / df['P_in_model'] * 100
df['error_P_pct']= (df['P_in_model'] - df['P_in_W']) / df['P_in_W'] * 100
df['error_eta_pp']= df['eta_model'] - df['eta_pct']

mae_P   = df['error_P_pct'].abs().mean()
mae_eta = df['error_eta_pp'].abs().mean()

print(f"\n  MAE of P_in error   : {mae_P:.4f} %")
print(f"  MAE of eta error    : {mae_eta:.4f} pp")

worst5 = df.reindex(df['error_P_pct'].abs().nlargest(5).index)[
    ['point','T_wheel_Nm','RPM_wheel','P_in_W','P_in_model','error_P_pct','eta_pct','eta_model']
]
print(f"\n  Worst 5 points by |error_P_pct|:")
print(f"  {'Pt':>4} {'T_Nm':>6} {'RPM':>5} {'P_in_act':>10} {'P_in_mod':>10} {'err%':>8} {'eta_act':>8} {'eta_mod':>8}")
for _, r in worst5.iterrows():
    print(f"  {int(r['point']):>4} {r['T_wheel_Nm']:>6.1f} {int(r['RPM_wheel']):>5} "
          f"{r['P_in_W']:>10.2f} {r['P_in_model']:>10.2f} {r['error_P_pct']:>8.3f} "
          f"{r['eta_pct']:>8.1f} {r['eta_model']:>8.2f}")

# ── STEP 3: 2-D Lookup Table ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 3 — 2D LOOKUP TABLE")
print("=" * 70)

speeds_kmh  = [15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42.8]
torques_Nm  = list(range(1, 33))  # 1..32

# CubicSpline: T_wheel_Nm → I_dc_A from Zone 1
# Ensure unique, sorted torque values
z1_sorted = z1.drop_duplicates('T_wheel_Nm').sort_values('T_wheel_Nm')
cs_T_to_I = CubicSpline(z1_sorted['T_wheel_Nm'], z1_sorted['I_dc_A'],
                         bc_type='not-a-knot', extrapolate=True)
T_min_z1 = z1_sorted['T_wheel_Nm'].min()
T_max_z1 = z1_sorted['T_wheel_Nm'].max()

def get_Idc(T_Nm):
    """Cubic spline with clamped extrapolation."""
    T_clamped = np.clip(T_Nm, T_min_z1, T_max_z1)
    return float(cs_T_to_I(T_clamped))

eta_table   = pd.DataFrame(index=speeds_kmh, columns=torques_Nm, dtype=float)
Pin_table   = pd.DataFrame(index=speeds_kmh, columns=torques_Nm, dtype=float)
flags_table = pd.DataFrame(index=speeds_kmh, columns=torques_Nm, dtype=object)

for v in speeds_kmh:
    omega_wheel = v / 3.6 / R_WHEEL
    omega_motor_ = omega_wheel * GR
    for T in torques_Nm:
        P_out_ = T * omega_wheel
        I_dc_  = get_Idc(T)
        P_copper = R_eff * I_dc_ ** 2
        P_iron_  = k_iron * omega_motor_
        P_in_    = P_out_ + P_copper + P_iron_
        eta_     = P_out_ / P_in_ * 100 if P_in_ > 0 else 0.0

        eta_table.loc[v, T]   = round(eta_, 2)
        Pin_table.loc[v, T]   = round(P_in_, 2)

        flag_parts = []
        if P_in_ > MAX_PIN:
            flag_parts.append("OVER_VESC_LIMIT")
        if I_dc_ > MAX_IDC:
            flag_parts.append("OVER_PEAK_CURRENT")
        flags_table.loc[v, T] = "|".join(flag_parts)

eta_table.index.name  = 'speed_kmh'
Pin_table.index.name  = 'speed_kmh'
flags_table.index.name = 'speed_kmh'

print(f"\n  Lookup tables built: {len(speeds_kmh)} speeds × {len(torques_Nm)} torques = {len(speeds_kmh)*len(torques_Nm)} cells")

# Sample printout
print(f"\n  Eta% sample (T=5,10,15,20 Nm):")
print(f"  {'v(km/h)':>10} {'T=5':>8} {'T=10':>8} {'T=15':>8} {'T=20':>8}")
for v in speeds_kmh:
    print(f"  {v:>10.1f} {eta_table.loc[v,5]:>8.2f} {eta_table.loc[v,10]:>8.2f} "
          f"{eta_table.loc[v,15]:>8.2f} {eta_table.loc[v,20]:>8.2f}")

# ── STEP 4: Validate 5 specific points ───────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 4 — VALIDATION ON 5 SPECIFIC POINTS")
print("=" * 70)

validate_pts = [
    dict(pt=8,  T=1.0,  RPM=386, P_in_actual=128.90,  eta_actual=31.4),
    dict(pt=25, T=5.1,  RPM=386, P_in_actual=309.60,  eta_actual=66.6),
    dict(pt=44, T=15.7, RPM=382, P_in_actual=776.61,  eta_actual=80.9),
    dict(pt=61, T=31.4, RPM=369, P_in_actual=1454.13, eta_actual=83.4),
    dict(pt=72, T=42.8, RPM=258, P_in_actual=1436.74, eta_actual=80.5),
]

print(f"\n  {'Pt':>4} {'T_Nm':>6} {'RPM':>5} {'P_in_act':>10} {'P_in_mod':>10} {'err%':>8} "
      f"{'eta_act':>8} {'eta_mod':>8} {'eta_err_pp':>10}")
for vp in validate_pts:
    row = df[df['point'] == vp['pt']].iloc[0]
    pin_mod = row['P_in_model']
    eta_mod = row['eta_model']
    err_p   = (pin_mod - vp['P_in_actual']) / vp['P_in_actual'] * 100
    err_eta = eta_mod - vp['eta_actual']
    print(f"  {vp['pt']:>4} {vp['T']:>6.1f} {vp['RPM']:>5} "
          f"{vp['P_in_actual']:>10.2f} {pin_mod:>10.2f} {err_p:>8.3f} "
          f"{vp['eta_actual']:>8.1f} {eta_mod:>8.2f} {err_eta:>10.2f}")

# ── STEP 5: Save CSV outputs ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STEP 5 — SAVING CSV FILES")
print("=" * 70)

eta_table.to_csv('/home/user/flappy-boss/motor_eta_lookup.csv')
Pin_table.to_csv('/home/user/flappy-boss/motor_Pin_lookup.csv')
flags_table.to_csv('/home/user/flappy-boss/motor_flags_lookup.csv')
print("  Saved: motor_eta_lookup.csv")
print("  Saved: motor_Pin_lookup.csv")
print("  Saved: motor_flags_lookup.csv")

# Optimal torque per speed (max eta within VESC 720W limit)
opt_rows = []
for v in speeds_kmh:
    best_T   = None
    best_eta = -np.inf
    for T in torques_Nm:
        P_in_ = Pin_table.loc[v, T]
        if P_in_ <= MAX_PIN:
            eta_ = eta_table.loc[v, T]
            if eta_ > best_eta:
                best_eta = eta_
                best_T   = T
    label = str(best_T) if best_T is not None else "NO_VALID_POINT"
    opt_rows.append({'speed_kmh': v, 'optimal_torque_Nm': label,
                     'max_eta_pct': round(best_eta, 2) if best_T is not None else None})

opt_df = pd.DataFrame(opt_rows)
opt_df.to_csv('/home/user/flappy-boss/motor_optimal_torque.csv', index=False)
print("  Saved: motor_optimal_torque.csv")

print(f"\n  Optimal torque per speed (≤720 W VESC limit):")
print(f"  {'v(km/h)':>10} {'opt_T_Nm':>10} {'max_eta%':>10}")
for _, r in opt_df.iterrows():
    print(f"  {r['speed_kmh']:>10.1f} {str(r['optimal_torque_Nm']):>10} {str(r['max_eta_pct']):>10}")

# ── FULL SUMMARY ──────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FULL SUMMARY")
print("=" * 70)
print(f"""
Motor Parameters (given):
  Gear ratio GR          = {GR}
  Wheel radius R_wheel   = {R_WHEEL} m
  Pole pairs PP          = {PP}
  R_phase (given)        = {R_PHASE} Ω
  λf (given)             = {LAMBDA_F} Wb
  Max P_in (VESC limit)  = {MAX_PIN} W
  Max I_dc               = {MAX_IDC} A

Fitted Loss Model Parameters:
  R_eff  (effective resistance) = {R_eff:.6f}  Ω
    [fitted from Zone 1 linear regression of P_loss vs I²]
  k_iron (iron-loss coefficient) = {k_iron:.6f}  W·s/rad  ({chosen})
    [k_iron1 from Zone 1 intercept / mean ω = {k_iron1:.6f}]
    [k_iron2 from Zone 2 P_iron_res vs ω    = {k_iron2:.6f}]

  P_loss model: P_loss = {R_eff:.6f}×I² + {k_iron:.6f}×ω_motor

Verification (all 106 points):
  MAE of P_in error    = {mae_P:.4f} %
  MAE of eta error     = {mae_eta:.4f} percentage points

Validation — 5 specific points:
  Pt  8 (T=1.0  Nm, RPM=386): P_in_model={df.loc[df['point']==8,'P_in_model'].values[0]:.2f} W  (actual {128.90} W), eta_model={df.loc[df['point']==8,'eta_model'].values[0]:.2f}% (actual 31.4%)
  Pt 25 (T=5.1  Nm, RPM=386): P_in_model={df.loc[df['point']==25,'P_in_model'].values[0]:.2f} W  (actual {309.60} W), eta_model={df.loc[df['point']==25,'eta_model'].values[0]:.2f}% (actual 66.6%)
  Pt 44 (T=15.7 Nm, RPM=382): P_in_model={df.loc[df['point']==44,'P_in_model'].values[0]:.2f} W  (actual {776.61} W), eta_model={df.loc[df['point']==44,'eta_model'].values[0]:.2f}% (actual 80.9%)
  Pt 61 (T=31.4 Nm, RPM=369): P_in_model={df.loc[df['point']==61,'P_in_model'].values[0]:.2f} W  (actual {1454.13} W), eta_model={df.loc[df['point']==61,'eta_model'].values[0]:.2f}% (actual 83.4%)
  Pt 72 (T=42.8 Nm, RPM=258): P_in_model={df.loc[df['point']==72,'P_in_model'].values[0]:.2f} W  (actual {1436.74} W), eta_model={df.loc[df['point']==72,'eta_model'].values[0]:.2f}% (actual 80.5%)

Limitations:
  1. The loss model uses only two loss terms (copper + iron-proportional-to-ω).
     Additional losses such as eddy-current scaling with ω², stray-load losses,
     and mechanical (bearing/windage) losses are lumped into R_eff and k_iron.
  2. The CubicSpline torque→current mapping is fitted only on Zone 1 (pts 1-61,
     T_wheel 0.6–31.4 Nm).  Extrapolation outside this range is clamped and
     less accurate.
  3. Points 99-106 show significant efficiency drop (VESC current limiting /
     stall region) not captured by the linear loss model; those points show the
     highest model error.
  4. Temperature effects on R_eff are not modelled.
  5. V_dc sags slightly with load; the model uses the measured I_dc but does
     not explicitly track V_dc variation.

Output files saved:
  /home/user/flappy-boss/motor_eta_lookup.csv
  /home/user/flappy-boss/motor_Pin_lookup.csv
  /home/user/flappy-boss/motor_flags_lookup.csv
  /home/user/flappy-boss/motor_optimal_torque.csv
""")
