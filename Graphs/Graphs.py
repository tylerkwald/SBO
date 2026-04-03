"""
SBO Base Case - Post-Processing Script
Zion NPP - Station Blackout Analysis
EMINE - Regulations & Safety Project

Generates plots for:
  - Steady State verification (t < 1000 s)
  - SBO Base Case transient (t >= 1000 s)

Usage:
    python plot_SBO.py

File structure expected:
    SBO/
    ├── Graph Codes/   <- this script
    ├── Output/        <- strip_base_restart.dat
    └── Pictures/
        ├── Steady State/
        └── Base Case/
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================

DAT_FILE = '../Output/strip_base_restart.dat'
SBO_TIME = 1000.0    # s - SBO initiation time in RELAP problem time

OUT_SS   = '../Pictures/Steady State'
OUT_BC   = '../Pictures/Base Case'

# Create output directories
os.makedirs(OUT_SS, exist_ok=True)
os.makedirs(OUT_BC, exist_ok=True)

# ==============================================================================
# STYLE
# ==============================================================================

try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('bmh')

COLORS = {
    'primary':   '#1f4e79',
    'secondary': '#c00000',
    'intact':    '#1f4e79',
    'broken':    '#c00000',
    'green':     '#375623',
    'orange':    '#c55a11',
    'purple':    '#5c3292',
    'gray':      '#595959',
}

FIGSIZE   = (10, 5)
FIGSIZE_L = (10, 6)
DPI       = 150
LW        = 1.8
FS_TITLE  = 13
FS_LABEL  = 12
FS_TICK   = 11
FS_LEGEND = 10


def style_ax(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel, fontsize=FS_LABEL)
    ax.set_ylabel(ylabel, fontsize=FS_LABEL)
    ax.set_title(title, fontsize=FS_TITLE, fontweight='bold')
    ax.tick_params(axis='both', labelsize=FS_TICK)
    ax.grid(which='major', linestyle='-',  linewidth=0.7, color='darkgray', alpha=0.6)
    ax.grid(which='minor', linestyle=':', linewidth=0.4, color='gray',     alpha=0.3)
    ax.minorticks_on()
    legend = ax.legend(loc='best', fontsize=FS_LEGEND,
                       frameon=True, shadow=True, fancybox=True)
    legend.get_frame().set_alpha(0.9)


def add_sbo_line(ax, label=True):
    """Vertical line marking SBO initiation."""
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1.2,
               label='SBO initiation' if label else None)


def save(fig, folder, name):
    path = os.path.join(folder, name + '.pdf')
    fig.savefig(path, bbox_inches='tight')
    print(f'  Saved: {path}')
    plt.close(fig)


# ==============================================================================
# LOAD DATA
# ==============================================================================

print('Loading data...')
data = pd.read_csv(DAT_FILE, sep=r'\s+')

# Time relative to SBO (t=0 at SBO initiation)
data['t_sbo'] = data['time-0'] - SBO_TIME

# Split steady state and transient
ss = data[data['time-0'] <= SBO_TIME].copy()
bc = data[data['time-0'] >= SBO_TIME].copy()

print(f'  Steady state:  {len(ss)} points  ({ss["time-0"].min():.0f} - {ss["time-0"].max():.0f} s)')
print(f'  Base case:     {len(bc)} points  (0 - {bc["t_sbo"].max():.0f} s after SBO)')
print()

# ==============================================================================
# STEADY STATE PLOTS
# ==============================================================================

print('Generating Steady State plots...')

# --- SS1: Core Power ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['rktpow-0'] / 1e6,
        color=COLORS['primary'], linewidth=LW, label='Core power')
ax.axhline(y=3250, color=COLORS['secondary'], linestyle='--',
           linewidth=1.2, label='Target: 3250 MW')
style_ax(ax, 'Time [s]', 'Power [MW]', 'Steady State - Core Power')
ax.set_ylim(3200, 3300)
fig.tight_layout()
save(fig, OUT_SS, 'SS1_core_power')

# --- SS2: Primary Pressure ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['p-150010000'] / 1e6,
        color=COLORS['primary'], linewidth=LW, label='Primary pressure')
ax.axhline(y=15.5, color=COLORS['secondary'], linestyle='--',
           linewidth=1.2, label='Target: 15.5 MPa')
style_ax(ax, 'Time [s]', 'Pressure [MPa]', 'Steady State - Primary Pressure')
ax.set_ylim(15.0, 16.0)
fig.tight_layout()
save(fig, OUT_SS, 'SS2_primary_pressure')

# --- SS3: Secondary Pressure ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['p-180010000'] / 1e6,
        color=COLORS['intact'], linewidth=LW, label='Intact SG')
ax.plot(ss['time-0'], ss['p-280010000'] / 1e6,
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken SG')
ax.axhline(y=6.7, color=COLORS['gray'], linestyle=':',
           linewidth=1.2, label='Target: 6.7 MPa')
style_ax(ax, 'Time [s]', 'Pressure [MPa]', 'Steady State - Secondary Pressure')
ax.set_ylim(6.5, 7.0)
fig.tight_layout()
save(fig, OUT_SS, 'SS3_secondary_pressure')

# --- SS4: Pressurizer Level ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['cntrlvar-150'],
        color=COLORS['primary'], linewidth=LW, label='Pressurizer level')
ax.axhline(y=8.8, color=COLORS['secondary'], linestyle='--',
           linewidth=1.2, label='Target: 8.8 m')
style_ax(ax, 'Time [s]', 'Level [m]', 'Steady State - Pressurizer Level')
ax.set_ylim(8.0, 10.0)
fig.tight_layout()
save(fig, OUT_SS, 'SS4_pressurizer_level')

# --- SS5: SG Levels ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['cntrlvar-176'],
        color=COLORS['intact'], linewidth=LW, label='Intact SG DC level')
ax.plot(ss['time-0'], ss['cntrlvar-276'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken SG DC level')
ax.axhline(y=12.2, color=COLORS['gray'], linestyle=':',
           linewidth=1.2, label='Target: 12.2 m')
style_ax(ax, 'Time [s]', 'Level [m]', 'Steady State - Steam Generator DC Levels')
ax.set_ylim(11.5, 13.0)
fig.tight_layout()
save(fig, OUT_SS, 'SS5_SG_levels')

# --- SS6: Core Temperatures ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['tempf-330010000'],
        color=COLORS['intact'], linewidth=LW, label='Core inlet (cold leg)')
ax.plot(ss['time-0'], ss['tempf-340010000'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Core outlet (hot leg)')
ax.axhline(y=571, color=COLORS['intact'], linestyle=':', linewidth=1.0, label='Target inlet: 571 K')
ax.axhline(y=603, color=COLORS['broken'], linestyle=':', linewidth=1.0, label='Target outlet: 603 K')
style_ax(ax, 'Time [s]', 'Temperature [K]', 'Steady State - Core Inlet/Outlet Temperature')
fig.tight_layout()
save(fig, OUT_SS, 'SS6_core_temperatures')

# --- SS7: Primary Mass Flows ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['mflowj-100010000'],
        color=COLORS['intact'], linewidth=LW, label='Intact loop (3 loops)')
ax.plot(ss['time-0'], ss['mflowj-200010000'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken loop (1 loop)')
ax.axhline(y=12865, color=COLORS['intact'], linestyle=':', linewidth=1.0, label='Target intact: 12865 kg/s')
ax.axhline(y=4351, color=COLORS['broken'],  linestyle=':', linewidth=1.0, label='Target broken: 4351 kg/s')
style_ax(ax, 'Time [s]', 'Mass Flow [kg/s]', 'Steady State - Primary Loop Mass Flow')
fig.tight_layout()
save(fig, OUT_SS, 'SS7_primary_flow')

# --- SS8: Feedwater Flows ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(ss['time-0'], ss['mflowj-181000000'],
        color=COLORS['intact'], linewidth=LW, label='Intact SG feedwater')
ax.plot(ss['time-0'], ss['mflowj-281000000'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken SG feedwater')
ax.axhline(y=1325, color=COLORS['intact'], linestyle=':', linewidth=1.0, label='Target intact: 1325 kg/s')
ax.axhline(y=459,  color=COLORS['broken'],  linestyle=':', linewidth=1.0, label='Target broken: 459 kg/s')
style_ax(ax, 'Time [s]', 'Mass Flow [kg/s]', 'Steady State - Feedwater Mass Flow')
fig.tight_layout()
save(fig, OUT_SS, 'SS8_feedwater_flow')

print()

# ==============================================================================
# BASE CASE PLOTS
# Time axis: seconds after SBO (t_sbo = time-0 - 1000)
# ==============================================================================

print('Generating Base Case plots...')

t = bc['t_sbo']

# --- BC1: Core Power (decay heat) ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['rktpow-0'] / 1e6,
        color=COLORS['primary'], linewidth=LW, label='Core power (decay heat)')
ax.set_xlim(0, 200/3600)  
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Power [MW]',
         'Base Case - Core Decay Heat')
fig.tight_layout()
save(fig, OUT_BC, 'BC1_core_power')

# --- BC2: Primary Pressure ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['p-150010000'] / 1e6,
        color=COLORS['primary'], linewidth=LW, label='Primary pressure')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Pressure [MPa]',
         'Base Case - Primary Pressure')
fig.tight_layout()
save(fig, OUT_BC, 'BC2_primary_pressure')

# --- BC3: Secondary Pressure ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['p-180010000'] / 1e6,
        color=COLORS['intact'], linewidth=LW, label='Intact SG')
ax.plot(t / 3600, bc['p-280010000'] / 1e6,
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken SG')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Pressure [MPa]',
         'Base Case - Secondary Pressure (SG Cooldown)')
fig.tight_layout()
save(fig, OUT_BC, 'BC3_secondary_pressure')

# --- BC4: Pressurizer Level ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['cntrlvar-150'],
        color=COLORS['primary'], linewidth=LW, label='Pressurizer level')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Level [m]',
         'Base Case - Pressurizer Level')
fig.tight_layout()
save(fig, OUT_BC, 'BC4_pressurizer_level')

# --- BC5: SG Levels ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['cntrlvar-176'],
        color=COLORS['intact'], linewidth=LW, label='Intact SG DC level')
ax.plot(t / 3600, bc['cntrlvar-276'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken SG DC level')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Level [m]',
         'Base Case - Steam Generator DC Levels')
fig.tight_layout()
save(fig, OUT_BC, 'BC5_SG_levels')

# --- BC6: Core, Upper Plenum, Downcomer Levels ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['cntrlvar-21'],
        color=COLORS['primary'], linewidth=LW, label='Core level')
ax.plot(t / 3600, bc['cntrlvar-22'],
        color=COLORS['green'],   linewidth=LW, linestyle='--', label='Upper plenum level')
ax.plot(t / 3600, bc['cntrlvar-23'],
        color=COLORS['orange'],  linewidth=LW, linestyle=':', label='Downcomer level')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Level [m]',
         'Base Case - Primary System Levels')
fig.tight_layout()
save(fig, OUT_BC, 'BC6_primary_levels')

# --- BC7: RCP Velocities ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['pmpvel-113'],
        color=COLORS['intact'], linewidth=LW, label='Intact loop RCP')
ax.plot(t / 3600, bc['pmpvel-209'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken loop RCP')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Angular velocity [rad/s]',
         'Base Case - RCP Coast-Down')
# Zoom in first 30 minutes to show coast-down
ax2 = ax.inset_axes([0.35, 0.35, 0.60, 0.55])
mask = t / 3600 <= 0.5
ax2.plot(t[mask] / 3600, bc['pmpvel-113'][mask],
         color=COLORS['intact'], linewidth=LW)
ax2.plot(t[mask] / 3600, bc['pmpvel-209'][mask],
         color=COLORS['broken'], linewidth=LW, linestyle='--')
ax2.set_title('First 30 min', fontsize=9)
ax2.grid(True, alpha=0.4)
fig.tight_layout()
save(fig, OUT_BC, 'BC7_RCP_velocities')

# --- BC8: Primary Temperatures ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['tempf-100010000'],
        color=COLORS['primary'], linewidth=LW, label='Hot leg intact')
ax.plot(t / 3600, bc['tempf-270060000'],
        color=COLORS['broken'],  linewidth=LW, linestyle='--', label='Hot leg broken')
ax.plot(t / 3600, bc['tempf-114010000'],
        color=COLORS['green'],   linewidth=LW, linestyle=':', label='Cold leg intact')
ax.plot(t / 3600, bc['tempf-210010000'],
        color=COLORS['orange'],  linewidth=LW, linestyle='-.', label='Cold leg broken')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Temperature [K]',
         'Base Case - Primary Circuit Temperatures')
fig.tight_layout()
save(fig, OUT_BC, 'BC8_primary_temperatures')

# --- BC9: Clad Temperatures (axial profile evolution) ---
clad_cols = [c for c in data.columns if 'httemp-336' in c]
clad_labels = [f'Node {i+1}' for i in range(len(clad_cols))]
colors_clad = plt.cm.plasma(np.linspace(0.1, 0.9, len(clad_cols)))

fig, ax = plt.subplots(figsize=FIGSIZE_L, dpi=DPI)
for col, label, color in zip(clad_cols, clad_labels, colors_clad):
    ax.plot(t / 3600, bc[col], linewidth=1.2, label=label, color=color)
add_sbo_line(ax, label=False)
ax.axvline(x=0, color='black', linestyle='--', linewidth=1.2, label='SBO initiation')
style_ax(ax, 'Time after SBO [h]', 'Clad Temperature [K]',
         'Base Case - Clad Surface Temperatures (all axial nodes)')
ax.legend(loc='center right', fontsize=8, ncol=2)
fig.tight_layout()
save(fig, OUT_BC, 'BC9_clad_temperatures')

# --- BC10: Maximum Clad Temperature ---
bc_copy = bc.copy()
bc_copy['max_clad'] = bc_copy[clad_cols].max(axis=1)
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc_copy['max_clad'],
        color=COLORS['secondary'], linewidth=LW, label='Peak clad temperature')
ax.axhline(y=1477, color='black', linestyle='--', linewidth=1.2,
           label='PCT limit: 1477 K (1204°C)')
ax.axhline(y=923, color=COLORS['orange'], linestyle=':', linewidth=1.2,
           label='EOP trigger: 923 K (CET)')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Temperature [K]',
         'Base Case - Peak Clad Temperature')
fig.tight_layout()
save(fig, OUT_BC, 'BC10_peak_clad_temperature')

# --- BC11: AFW and TDP Mass Flows ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['mflowj-183000000'],
        color=COLORS['intact'],  linewidth=LW, label='AFW intact loop (motor-driven)')
ax.plot(t / 3600, bc['mflowj-283000000'],
        color=COLORS['broken'],  linewidth=LW, linestyle='--', label='AFW broken loop (motor-driven)')
ax.plot(t / 3600, bc['mflowj-473000000'],
        color=COLORS['green'],   linewidth=LW, linestyle=':', label='TDP intact loop')
ax.plot(t / 3600, bc['mflowj-475000000'],
        color=COLORS['orange'],  linewidth=LW, linestyle='-.', label='TDP broken loop')
# Mark 5h battery limit
ax.axvline(x=5.0, color='gray', linestyle=':', linewidth=1.2, label='Battery limit (5h)')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Mass Flow [kg/s]',
         'Base Case - Auxiliary Feedwater (AFW & TDP)')
fig.tight_layout()
save(fig, OUT_BC, 'BC11_AFW_TDP')

# --- BC12: RCP Seal Leaks ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['mflowj-506000000'],
        color=COLORS['intact'],  linewidth=LW, label='Small leak - intact (3 loops)')
ax.plot(t / 3600, bc['mflowj-507000000'],
        color=COLORS['broken'],  linewidth=LW, linestyle='--', label='Small leak - broken (1 loop)')
ax.plot(t / 3600, bc['mflowj-508000000'],
        color=COLORS['green'],   linewidth=LW, linestyle=':', label='Large leak - intact')
ax.plot(t / 3600, bc['mflowj-509000000'],
        color=COLORS['orange'],  linewidth=LW, linestyle='-.', label='Large leak - broken')
ax.axvline(x=600/3600, color='gray', linestyle=':', linewidth=1.2,
           label='Leak start (10 min)')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Mass Flow [kg/s]',
         'Base Case - RCP Seal Leaks')
fig.tight_layout()
save(fig, OUT_BC, 'BC12_RCP_seal_leaks')

# --- BC13: PZR and SG Relief/Safety Valves ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['mflowj-155000000'],
        color=COLORS['primary'],  linewidth=LW, label='PZR safety valve')
ax.plot(t / 3600, bc['mflowj-157000000'],
        color=COLORS['secondary'], linewidth=LW, linestyle='--', label='PZR relief valve (PORV)')
ax.plot(t / 3600, bc['mflowj-187000000'],
        color=COLORS['green'],    linewidth=LW, linestyle=':', label='SG intact relief')
ax.plot(t / 3600, bc['mflowj-287000000'],
        color=COLORS['orange'],   linewidth=LW, linestyle='-.', label='SG broken relief')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Mass Flow [kg/s]',
         'Base Case - Relief and Safety Valves')
fig.tight_layout()
save(fig, OUT_BC, 'BC13_relief_valves')

# --- BC14: Integral mass flows ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['cntrlvar-500'],
        color=COLORS['primary'],  linewidth=LW, label='Integral PZR valves flow')
ax.plot(t / 3600, bc['cntrlvar-504'],
        color=COLORS['secondary'], linewidth=LW, linestyle='--', label='Integral RCP seal leak')
ax.plot(t / 3600, bc['cntrlvar-502'],
        color=COLORS['green'],    linewidth=LW, linestyle=':', label='Integral ECCS flow')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Integrated Mass [kg]',
         'Base Case - Integral Mass Flows')
fig.tight_layout()
save(fig, OUT_BC, 'BC14_integral_mass_flows')

# --- BC15: Primary Flow (natural circulation) ---
fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
ax.plot(t / 3600, bc['mflowj-100010000'],
        color=COLORS['intact'], linewidth=LW, label='Intact loop (3 loops)')
ax.plot(t / 3600, bc['mflowj-200010000'],
        color=COLORS['broken'], linewidth=LW, linestyle='--', label='Broken loop (1 loop)')
add_sbo_line(ax)
style_ax(ax, 'Time after SBO [h]', 'Mass Flow [kg/s]',
         'Base Case - Primary Loop Flow (Natural Circulation)')
fig.tight_layout()
save(fig, OUT_BC, 'BC15_primary_flow')

# ==============================================================================
# STEADY STATE SUMMARY TABLE (printed to terminal)
# ==============================================================================

print()
print('=' * 65)
print('STEADY STATE VERIFICATION - TABLE 2 COMPARISON')
print('=' * 65)
ss_end = ss.iloc[-1]
targets = {
    'Core power [MW]':              (ss_end['rktpow-0'] / 1e6,    3250),
    'Primary pressure [MPa]':       (ss_end['p-150010000'] / 1e6, 15.5),
    'Secondary pressure [MPa]':     (ss_end['p-180010000'] / 1e6, 6.7),
    'Pressurizer level [m]':        (ss_end['cntrlvar-150'],      8.8),
    'SG intact DC level [m]':       (ss_end['cntrlvar-176'],      12.2),
    'SG broken DC level [m]':       (ss_end['cntrlvar-276'],      12.2),
    'Core outlet temp [K]':         (ss_end['tempf-340010000'],   603),
    'Core inlet temp [K]':          (ss_end['tempf-330010000'],   571),
    'Intact FW flow [kg/s]':        (ss_end['mflowj-181000000'],  1325),
    'Broken FW flow [kg/s]':        (ss_end['mflowj-281000000'],  459),
    'Intact loop flow [kg/s]':      (ss_end['mflowj-100010000'],  12865),
    'Broken loop flow [kg/s]':      (ss_end['mflowj-200010000'],  4351),
}
print(f"{'Parameter':<35} {'Target':>10} {'Simulated':>10} {'Error %':>8}")
print('-' * 65)
for param, (sim, tgt) in targets.items():
    err = abs(sim - tgt) / tgt * 100
    flag = '  ✓' if err < 3 else '  !'
    print(f"{param:<35} {tgt:>10.1f} {sim:>10.2f} {err:>7.2f}%{flag}")
print('=' * 65)
print()
print(f'All plots saved.')
print(f'  Steady State: {OUT_SS}')
print(f'  Base Case:    {OUT_BC}')
