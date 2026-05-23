"""
SBO Project - Event Tree Post-Processing
EMINE - Regulations & Safety

Plots Peak Cladding Temperature for all event tree cases.
Reads all *_strip.dat from Output/EventTree/
Saves plot to Pictures/EventTree/

Place this script in: SBO/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR   = os.path.join(BASE_DIR, 'Output', 'EventTree')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'Pictures', 'EventTree')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SBO_TIME      = 1000.0   # s — SBO initiation (t=0 on x-axis)
CD_THRESHOLD  = 1477.0   # K — 1204°C, 10 CFR 50.46 PCT limit
RELAP_STOP    = 1700.0   # K — trip 455

# Cases known to go CD (for color coding)
CD_CASES = {
    'ET02_noAC', 'ET04_noBat_noAC', 'ET05_noAFW',
    'ET07_noSL_noAC', 'ET09_noSL_noBat_noAC',
    'ET11_noLeak_noAC', 'ET13_noLeak_noBat_noAC', 'ET15_noAFW_noAC',
}

# ==============================================================================
# STYLE
# ==============================================================================

try:
    plt.style.use('seaborn-v0_8-whitegrid')
except Exception:
    plt.style.use('bmh')

# Color palette: reds for CD, blues/greens for SAFE
CD_COLORS = [
    '#d62728', '#ff7f0e', '#9467bd',
    '#8c564b', '#e377c2', '#bcbd22',
    '#17becf', '#7f7f7f',
]
SAFE_COLORS = [
    '#1f77b4', '#2ca02c', '#17becf',
    '#aec7e8', '#98df8a', '#c5b0d5', '#c49c94',
]

# ==============================================================================
# LOAD DATA
# ==============================================================================

print('Loading strip files...')

cases = {}
dat_files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('_strip.dat')])

if not dat_files:
    print(f'  No *_strip.dat files found in {INPUT_DIR}')
    exit(1)

for fname in dat_files:
    case_name = fname.replace('_strip.dat', '')
    fpath = os.path.join(INPUT_DIR, fname)
    try:
        df = pd.read_csv(fpath, sep=r'\s+')
        httemp_cols = [c for c in df.columns if 'httemp' in c.lower()]
        if not httemp_cols or 'time-0' not in df.columns:
            print(f'  ✗ Skipping {fname} — missing columns')
            continue
        df['max_clad'] = df[httemp_cols].max(axis=1)
        df['t_sbo'] = (df['time-0'] - SBO_TIME) / 3600  # hours after SBO
        # Keep only transient (t >= SBO)
        df = df[df['time-0'] >= SBO_TIME].copy()
        if len(df) < 2:
            print(f'  ✗ Skipping {fname} — too few data points')
            continue
        cases[case_name] = df
        max_t = df['t_sbo'].max()
        max_T = df['max_clad'].max()
        print(f'  ✓ {case_name:<40} {max_t:.1f}h, max T={max_T:.0f}K')
    except Exception as e:
        print(f'  ✗ Error loading {fname}: {e}')

if not cases:
    print('No data loaded. Exiting.')
    exit(1)

print(f'\n  Loaded {len(cases)} cases.')

# ==============================================================================
# PLOT — ALL CASES TOGETHER
# ==============================================================================

fig, ax = plt.subplots(figsize=(14, 7), dpi=150)

cd_iter   = iter(CD_COLORS)
safe_iter = iter(SAFE_COLORS)

for case_name, df in sorted(cases.items()):
    is_cd = any(cd in case_name for cd in CD_CASES) or case_name in CD_CASES
    is_cd_by_data = df['max_clad'].max() >= CD_THRESHOLD

    if is_cd or is_cd_by_data:
        color = next(cd_iter, '#d62728')
        lw    = 1.8
        ls    = '-'
        zorder = 3
    else:
        color = next(safe_iter, '#1f77b4')
        lw    = 1.4
        ls    = '--'
        zorder = 2

    # Clean label
    label = case_name.replace('ET', 'ET').replace('_', ' ')

    ax.plot(df['t_sbo'], df['max_clad'],
            color=color, linewidth=lw, linestyle=ls,
            label=label, zorder=zorder, alpha=0.9)

# CD threshold line
ax.axhline(y=CD_THRESHOLD, color='black', linestyle='--', linewidth=1.8,
           zorder=5, label=f'PCT limit: {CD_THRESHOLD:.0f} K (1204°C)')

# RELAP stop line (lighter)
ax.axhline(y=RELAP_STOP, color='gray', linestyle=':', linewidth=1.2,
           zorder=4, label=f'RELAP stop: {RELAP_STOP:.0f} K')

# Shaded CD zone
ax.axhspan(CD_THRESHOLD, RELAP_STOP + 50,
           alpha=0.06, color='red', zorder=1)

# Formatting
ax.set_xlabel('Time after SBO [h]', fontsize=13)
ax.set_ylabel('Peak Cladding Temperature [K]', fontsize=13)
ax.set_title('Event Tree Analysis — Peak Cladding Temperature\nZion NPP Station Blackout (SBO)',
             fontsize=14, fontweight='bold', pad=12)

# Secondary y-axis in °C
ax2 = ax.secondary_yaxis('right',
    functions=(lambda K: K - 273.15, lambda C: C + 273.15))
ax2.set_ylabel('Temperature [°C]', fontsize=12)
ax2.tick_params(labelsize=10)

ax.tick_params(axis='both', labelsize=11)
ax.set_xlim(left=0)
ax.set_ylim(bottom=200)

ax.grid(which='major', linestyle='-',  linewidth=0.6, color='darkgray', alpha=0.5)
ax.grid(which='minor', linestyle=':', linewidth=0.3, color='gray',     alpha=0.3)
ax.minorticks_on()

# Legend — split CD/SAFE
legend = ax.legend(loc='upper left', fontsize=8.5,
                   frameon=True, framealpha=0.92,
                   fancybox=True, shadow=True,
                   ncol=2, columnspacing=1.0,
                   handlelength=2.0)

# Annotation for CD region
ax.annotate('Core Damage Region\n(PCT > 1204°C)',
            xy=(ax.get_xlim()[1] * 0.98, CD_THRESHOLD + 30),
            ha='right', va='bottom', fontsize=9,
            color='darkred', style='italic')

fig.tight_layout()
out_path = os.path.join(OUTPUT_DIR, 'EventTree_PCT_all_cases.pdf')
fig.savefig(out_path, bbox_inches='tight')
print(f'\n  ✓ Saved: {out_path}')
plt.close(fig)

# ==============================================================================
# PLOT — CD CASES ONLY (zoomed)
# ==============================================================================

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
cd_iter = iter(CD_COLORS)

for case_name, df in sorted(cases.items()):
    is_cd = df['max_clad'].max() >= CD_THRESHOLD
    if not is_cd:
        continue
    color = next(cd_iter, '#d62728')
    label = case_name.replace('_', ' ')
    ax.plot(df['t_sbo'], df['max_clad'],
            color=color, linewidth=2.0, label=label)

ax.axhline(y=CD_THRESHOLD, color='black', linestyle='--', linewidth=1.8,
           label=f'PCT limit: {CD_THRESHOLD:.0f} K (1204°C)')
ax.axhline(y=RELAP_STOP, color='gray', linestyle=':', linewidth=1.2,
           label=f'RELAP stop: {RELAP_STOP:.0f} K')
ax.axhspan(CD_THRESHOLD, RELAP_STOP + 50, alpha=0.07, color='red')

ax.set_xlabel('Time after SBO [h]', fontsize=13)
ax.set_ylabel('Peak Cladding Temperature [K]', fontsize=13)
ax.set_title('Event Tree — Core Damage Sequences\nPeak Cladding Temperature',
             fontsize=14, fontweight='bold', pad=12)

ax2 = ax.secondary_yaxis('right',
    functions=(lambda K: K - 273.15, lambda C: C + 273.15))
ax2.set_ylabel('Temperature [°C]', fontsize=12)
ax2.tick_params(labelsize=10)

ax.tick_params(axis='both', labelsize=11)
ax.set_xlim(left=0)
ax.set_ylim(bottom=500)
ax.grid(which='major', linestyle='-',  linewidth=0.6, color='darkgray', alpha=0.5)
ax.grid(which='minor', linestyle=':', linewidth=0.3, color='gray',     alpha=0.3)
ax.minorticks_on()
ax.legend(loc='upper left', fontsize=9, frameon=True,
          framealpha=0.92, fancybox=True, shadow=True)

fig.tight_layout()
out_path = os.path.join(OUTPUT_DIR, 'EventTree_PCT_CD_only.pdf')
fig.savefig(out_path, bbox_inches='tight')
print(f'  ✓ Saved: {out_path}')
plt.close(fig)

print('\nDone.')