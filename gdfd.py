import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# === データ読み込み ===
path = Path("/mnt/data/adafg.xlsx")
df = pd.read_excel(path, sheet_name="PK1&2")

col_c1 = "中央 Recorded Tmp（℃）"
col_c2 = "間口 Recorded Tmp（℃）"
col_air = "Air tmp（℃）"
col_d1 = "中央 Diff"
col_d2 = "間口 Diff"

# === タイムスタンプ列（30分間隔） ===
start = pd.Timestamp("2025-08-28 10:30:00")
dt_index = start + pd.to_timedelta(np.arange(len(df)), unit="m") * 30
df["Timestamp_fixed"] = dt_index

# === 数値変換 ===
for c in [col_c1, col_c2, col_air, col_d1, col_d2]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df_raw = df.set_index("Timestamp_fixed")

# === 大気温補間 ===
df_interp = df_raw.copy()
df_interp[col_air] = df_interp[col_air].interpolate(method='time', limit_direction='both')
df_interp[col_d1] = df_interp[col_c1] - df_interp[col_air]
df_interp[col_d2] = df_interp[col_c2] - df_interp[col_air]

# === プロット ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# 上段：温度
ax1.plot(df_interp.index, df_interp[col_air], label="Ambient (Interpolated)", linestyle="--", color="tab:blue")
ax1.plot(df_interp.index, df_interp[col_c1], label="Container 1 (Measured)", color="tab:orange")
ax1.plot(df_interp.index, df_interp[col_c2], label="Container 2 (Measured)", color="tab:green")
ax1.set_ylabel("Temperature (°C)")
ax1.set_title("Container vs Ambient Temperature (Daily gridlines, weekly date labels)")
ax1.legend(loc="upper right")
ax1.grid(True)

# 下段：差分（棒グラフ）
bar_width = 0.02
ax2.bar(df_interp.index, df_interp[col_d1], width=bar_width, label="Gap 1 (C1 - Air)", color="tab:red", alpha=0.6)
ax2.bar(df_interp.index, df_interp[col_d2], width=bar_width, label="Gap 2 (C2 - Air)", color="tab:pink", alpha=0.6)
ax2.set_ylabel("Δ Temp (°C)")
ax2.set_title("Temperature Gap (Measured - Interpolated Ambient)")
ax2.legend(loc="upper right")
ax2.grid(True)

# === 横軸設定 ===
# 1日ごとの補助線
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter(''))  # Majorは線だけ

# 1週間ごとの日付表示
ax2.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))
ax2.xaxis.set_minor_formatter(mdates.DateFormatter('%Y/%m/%d'))

# ラベル縦書き
plt.setp(ax2.get_xticklabels(minor=True), rotation=90, ha='center', fontsize=7)

# 1日ごとの補助線
ax2.grid(True, which='major', axis='x', linestyle=':', color='gray', alpha=0.5)

# === 保存 ===
plt.tight_layout()
out_path = "/mnt/data/container_temp_gap_bar_interp_daily_grid_weekly_labels.png"
plt.savefig(out_path, dpi=150)
plt.show()

print("✅ グラフ保存完了:", out_path)
