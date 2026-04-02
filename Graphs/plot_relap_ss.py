"""
plot_relap_ss.py
----------------
Parsing e plot dell'output RELAP5 per il caso SBO (ss3.o).
Produce 4 figure:
  1. Potenza reattore vs tempo (t = 0-2000 s)
  2. Temperatura cladding (httemp) vs tempo (t = 0-2000 s)
  3. Confronto valori steady-state calcolati vs valori attesi (Tabella 2 del PDF)
  4. Zoom sulla fase steady state (t = 0-1000 s)

Uso:
    python plot_relap_ss.py [percorso_file.o]
    (default: ss3.o nella stessa cartella dello script)
"""

import re
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch

# ─── Configurazione ────────────────────────────────────────────────────────────
FILE_PATH = sys.argv[1] if len(sys.argv) > 1 else "ss3.o"
OUT_DIR   = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

# Valori di riferimento della Tabella 2 (PDF)
TABLE2 = {
    "Power (MW)":                   3250.0,
    "Primary pressure hot leg (MPa)": 15.5,
    "Secondary pressure (MPa)":      6.7,
    "Pressurizer level (m)":         8.8,
    "Intact SG DC level (m)":        12.2,
    "Broken SG DC level (m)":        12.2,
    "Core outlet temperature (K)":   603.0,
    "Core inlet temperature (K)":    571.0,
    "Intact FW flow (kg/s)":         1325.0,
    "Broken FW flow (kg/s)":         459.0,
    "Intact loop flow (kg/s)":       12865.0,
    "Broken loop flow (kg/s)":       4351.0,
}

T_SBO = 1000.0   # SBO avviene a t=1000 s nel file

COLORS = {
    "main":  "#2563EB",
    "ref":   "#DC2626",
    "sbo":   "#F59E0B",
    "ok":    "#16A34A",
    "notok": "#DC2626",
    "bg":    "#F8FAFC",
}

# ─── Utilities ─────────────────────────────────────────────────────────────────

def float_e(s):
    """Converte una stringa RELAP (può usare la D di Fortran) in float."""
    return float(s.replace("D", "E").replace("d", "e"))


def read_file(path):
    with open(path, "r", errors="replace") as f:
        return f.readlines()


# ─── Parser minor edits ────────────────────────────────────────────────────────

def parse_minor_edits(lines):
    """
    Estrae le colonne (time, rktpow, httemp) dai blocchi di minor edit.
    Header:  "1 time        rktpow       httemp"
    Dati:    "   <time>    <rktpow>    <httemp>"
    """
    time_arr, power_arr, httemp_arr = [], [], []
    in_block  = False
    skip_head = 0

    for line in lines:
        if re.match(r"^1\s+time\s+rktpow\s+httemp", line):
            in_block  = True
            skip_head = 3
            continue

        if in_block:
            if skip_head > 0:
                skip_head -= 1
                continue
            # Fine blocco
            if re.match(r"^[01]\s", line) or re.match(r"^0[A-Za-z]", line):
                in_block = False
                continue
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) == 3:
                try:
                    time_arr.append(float_e(parts[0]))
                    power_arr.append(float_e(parts[1]))
                    httemp_arr.append(float_e(parts[2]))
                except ValueError:
                    pass

    return np.array(time_arr), np.array(power_arr), np.array(httemp_arr)


# ─── Parser major edit a t=0 ───────────────────────────────────────────────────

def find_major_edit_blocks(lines):
    """
    Restituisce una lista di (start_idx, end_idx, time) per ogni MAJOR EDIT.
    """
    starts = []
    for i, line in enumerate(lines):
        m = re.search(r"MAJOR EDIT.*time=\s*([\d.E+\-]+)\s*sec", line)
        if m:
            starts.append((i, float(m.group(1))))

    blocks = []
    for j, (i, t) in enumerate(starts):
        end = starts[j + 1][0] if j + 1 < len(starts) else len(lines)
        blocks.append((i, end, t))
    return blocks


def parse_steady_state(lines):
    """
    Estrae i valori steady-state dal MAJOR EDIT a t=0.
    """
    values = {}

    # Trova il blocco del major edit a t=0
    blocks = find_major_edit_blocks(lines)
    t0_blocks = [b for b in blocks if abs(b[2]) < 1.0]
    if not t0_blocks:
        print("ATTENZIONE: major edit a t=0 non trovato.")
        return values

    i0, i1, _ = t0_blocks[0]
    block = lines[i0:i1]

    # ── Potenza (riga "Total power" + riga dati successiva) ──────────────────
    for j, l in enumerate(block):
        if "Total power" in l:
            # Il dato è 1 o 2 righe dopo (a seconda se c'è la riga delle unità)
            for offset in (1, 2, 3):
                if j + offset >= len(block):
                    break
                m = re.search(r"^\s*([\d.E+\-]+)\s+[\d.E+\-]+\s+[\d.E+\-]+", block[j + offset])
                if m:
                    values["Power (MW)"] = float_e(m.group(1)) / 1e6
                    break
            break

    # Helper: match di una riga di volume  "  NNN-0NNNNN  <P>  <voidf>  ...  <tempf>  ..."
    # Formato: vol-no  pressure  voidf  voidg  voidgo  tempf  tempg  satt  uf  ug  flag
    def vol_row(vol_id, col):
        """Restituisce il valore nella colonna `col` (1-based, dopo vol_id)."""
        pattern = re.compile(
            r"^\s*" + re.escape(vol_id) + r"\s+" + r"([\d.E+\-]+)\s+" * col
        )
        for l in block:
            m = pattern.match(l)
            if m:
                return float_e(m.group(col))
        return None

    # ── Pressione primaria hot leg (vol 100-010000, col 1 = pressione) ───────
    p = vol_row("100-010000", 1)
    if p is not None:
        values["Primary pressure hot leg (MPa)"] = p / 1e6

    # ── Pressione secondaria (vol 180-010000 = steam dome SG intact) ─────────
    p2 = vol_row("180-010000", 1)
    if p2 is not None:
        values["Secondary pressure (MPa)"] = p2 / 1e6

    # ── Temperatura core outlet (vol 345-010000, col 5 = tempf) ──────────────
    t_out = vol_row("345-010000", 5)
    if t_out is not None:
        values["Core outlet temperature (K)"] = t_out

    # ── Temperatura core inlet (vol 330-010000, col 5 = tempf) ───────────────
    t_in = vol_row("330-010000", 5)
    if t_in is not None:
        values["Core inlet temperature (K)"] = t_in

    # ── Control variables ─────────────────────────────────────────────────────
    # Le control variable sono nel blocco "Control variable edit; at time= 0"
    # che è UNA SOLA riga marker, poi le coppie "N  name  type  value"
    cv_start = None
    for j, l in enumerate(block):
        if re.search(r"Control variable edit.*time=\s*0", l):
            cv_start = j
            break

    if cv_start is not None:
        cv_block = block[cv_start:]
        for l in cv_block:
            # Formato: "  150     pzrlvl       sum           8.85499  ..."
            m = re.search(r"\b150\b\s+\w+\s+\w+\s+([\d.E+\-]+)", l)
            if m:
                values["Pressurizer level (m)"] = float_e(m.group(1))
            m = re.search(r"\b176\b\s+\w+\s+\w+\s+([\d.E+\-]+)", l)
            if m:
                values["Intact SG DC level (m)"] = float_e(m.group(1))
            m = re.search(r"\b276\b\s+\w+\s+\w+\s+([\d.E+\-]+)", l)
            if m:
                values["Broken SG DC level (m)"] = float_e(m.group(1))

    # ── Portate: junctions (colonna mass flow = col 6 nella tabella Jun) ─────
    # Formato: " NNN-000000  from-vol   to-vol   liq.vel  vap.vel  massflow  ..."
    def jun_massflow(jun_id):
        pattern = re.compile(
            r"^\s*" + re.escape(jun_id) +
            r"\s+\S+\s+\S+\s+[\d.E+\-]+\s+[\d.E+\-]+\s+([\d.E+\-]+)"
        )
        for l in block:
            m = pattern.match(l)
            if m:
                return abs(float_e(m.group(1)))
        return None

    fw_i = jun_massflow("181-000000")
    if fw_i is not None:
        values["Intact FW flow (kg/s)"] = fw_i

    fw_b = jun_massflow("281-000000")
    if fw_b is not None:
        values["Broken FW flow (kg/s)"] = fw_b

    lp_i = jun_massflow("380-000000")
    if lp_i is not None:
        values["Intact loop flow (kg/s)"] = lp_i

    lp_b = jun_massflow("390-000000")
    if lp_b is not None:
        values["Broken loop flow (kg/s)"] = lp_b

    return values


# ─── Plot ──────────────────────────────────────────────────────────────────────

def make_plots(file_path, out_dir):
    print(f"Lettura file: {file_path}")
    lines = read_file(file_path)

    print("Parsing minor edits (time series)...")
    t, power, httemp = parse_minor_edits(lines)
    if len(t) == 0:
        print("ERRORE: nessun dato di time series trovato.")
        sys.exit(1)
    print(f"  Trovati {len(t)} punti  [{t[0]:.1f} – {t[-1]:.1f} s]")

    print("Parsing major edit (steady state a t=0)...")
    ss_vals = parse_steady_state(lines)
    print(f"  Estratte {len(ss_vals)}/{len(TABLE2)} variabili")
    for k in TABLE2:
        calc = ss_vals.get(k, float("nan"))
        ref  = TABLE2[k]
        err  = abs(calc - ref) / abs(ref) * 100 if not np.isnan(calc) and ref != 0 else float("nan")
        flag = "✓" if err <= 5 else "✗" if not np.isnan(err) else "?"
        print(f"  {flag}  {k:<40s}  calc={calc:>10.4g}  ref={ref:>10.4g}  err={err:>6.2f}%")

    # ── Stile ─────────────────────────────────────────────────────────────────
    plt.rcParams.update({
        "font.family":   "DejaVu Sans",
        "font.size":     11,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "axes.grid":     True,
        "grid.alpha":    0.35,
        "grid.linestyle": "--",
        "figure.facecolor": COLORS["bg"],
        "axes.facecolor":   COLORS["bg"],
    })

    # ══════════════════════════════════════════════════════════════════════════
    # FIG 1 – Potenza reattore vs tempo (0-2000 s)
    # ══════════════════════════════════════════════════════════════════════════
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    fig1.suptitle("RELAP5 – Reactor Power vs Time", fontweight="bold")

    ax1.plot(t, power / 1e6, color=COLORS["main"], lw=1.8, label="Calculated Power")
    ax1.axhline(TABLE2["Power (MW)"], color=COLORS["ref"], lw=1.4,
                ls="--", label=f"Reference Value (Table 2): {TABLE2['Power (MW)']:.0f} MW")
    ax1.axvline(T_SBO, color=COLORS["sbo"], lw=2, ls=":", label=f"SBO @ t = {T_SBO:.0f} s")
    ax1.axvspan(0, T_SBO, alpha=0.06, color=COLORS["ok"])
    ax1.text(T_SBO / 2, ax1.get_ylim()[0] + 50,
             "Steady state", ha="center", color=COLORS["ok"], fontsize=9, fontstyle="italic")
    ax1.annotate("SBO", xy=(T_SBO, power[t >= T_SBO][0] / 1e6 if any(t >= T_SBO) else 0),
                 xytext=(T_SBO + 40, 500),
                 color=COLORS["sbo"], fontsize=9, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=COLORS["sbo"], lw=1.2))

    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Power (MW)")
    ax1.legend(loc="upper right")
    ax1.set_xlim(t[0], t[-1])
    fig1.tight_layout()

    out1 = os.path.join(out_dir, "fig1_power.png")
    fig1.savefig(out1, dpi=150, bbox_inches="tight")
    print(f"\nSalvato: {out1}")

    # ══════════════════════════════════════════════════════════════════════════
    # FIG 2 – Temperatura cladding vs tempo (0-2000 s)
    # ══════════════════════════════════════════════════════════════════════════
    fig2, ax2 = plt.subplots(figsize=(12, 5))
    fig2.suptitle("RELAP5 – Cladding Temperature (node 336-000817) vs Time", fontweight="bold")

    ax2.plot(t, httemp, color="#7C3AED", lw=1.8, label="Calculated Cladding Temperature")
    ax2.axvline(T_SBO, color=COLORS["sbo"], lw=2, ls=":", label=f"SBO @ t = {T_SBO:.0f} s")
    ax2.axvspan(0, T_SBO, alpha=0.06, color=COLORS["ok"], label="Steady state")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel(" Cladding Temperature (K)")
    ax2.legend(loc="upper right")
    ax2.set_xlim(t[0], t[-1])
    fig2.tight_layout()

    out2 = os.path.join(out_dir, "fig2_httemp.png")
    fig2.savefig(out2, dpi=150, bbox_inches="tight")
    print(f"Salvato: {out2}")

    # ══════════════════════════════════════════════════════════════════════════
    # FIG 3 – Confronto Steady State vs Table 2 (barchart a gruppi)
    # ══════════════════════════════════════════════════════════════════════════
    groups = {
        "Potenza (MW)": [
            "Power (MW)"],
        "Pressioni (MPa)": [
            "Primary pressure hot leg (MPa)",
            "Secondary pressure (MPa)"],
        "Livelli (m)": [
            "Pressurizer level (m)",
            "Intact SG DC level (m)",
            "Broken SG DC level (m)"],
        "Temperature (K)": [
            "Core outlet temperature (K)",
            "Core inlet temperature (K)"],
        "Portate (kg/s)": [
            "Intact FW flow (kg/s)",
            "Broken FW flow (kg/s)",
            "Intact loop flow (kg/s)",
            "Broken loop flow (kg/s)"],
    }
    short_label = {
        "Power (MW)":                     "Power",
        "Primary pressure hot leg (MPa)": "P primary\nhot leg",
        "Secondary pressure (MPa)":       "P secondary",
        "Pressurizer level (m)":          "PZR level",
        "Intact SG DC level (m)":         "SG intact\nDC level",
        "Broken SG DC level (m)":         "SG broken\nDC level",
        "Core outlet temperature (K)":    "T core\noutlet",
        "Core inlet temperature (K)":     "T core\ninlet",
        "Intact FW flow (kg/s)":          "Intact FW",
        "Broken FW flow (kg/s)":          "Broken FW",
        "Intact loop flow (kg/s)":        "Intact\nloop",
        "Broken loop flow (kg/s)":        "Broken\nloop",
    }

    fig3 = plt.figure(figsize=(16, 10))
    fig3.suptitle(
        "RELAP5 – Confronto Steady State (t = 0 s) vs Valori Nominali (Table 2)",
        fontweight="bold", fontsize=14)

    gs = gridspec.GridSpec(2, 3, figure=fig3, hspace=0.60, wspace=0.45)
    layout = [gs[0, 0], gs[0, 1], gs[0, 2], gs[1, 0], gs[1, 1:3]]

    TOL = 5.0   # tolleranza errore %

    for ax_idx, (grp_name, keys) in enumerate(groups.items()):
        ax = fig3.add_subplot(layout[ax_idx])
        ax.set_title(grp_name, fontsize=11)

        x      = np.arange(len(keys))
        ref_v  = np.array([TABLE2[k] for k in keys])
        calc_v = np.array([ss_vals.get(k, np.nan) for k in keys])
        labels = [short_label[k] for k in keys]

        width = 0.35
        ax.bar(x - width / 2, ref_v, width,
               color=COLORS["ref"], alpha=0.65, label="Riferimento")

        for i, (rv, cv) in enumerate(zip(ref_v, calc_v)):
            if np.isnan(cv):
                ax.bar(x[i] + width / 2, 0, width,
                       color="gray", alpha=0.4, hatch="//")
                ax.text(x[i] + width / 2, rv * 0.05, "N/D",
                        ha="center", va="bottom", fontsize=8, color="gray")
                continue

            err_pct = abs(cv - rv) / abs(rv) * 100 if rv != 0 else 0
            color   = COLORS["ok"] if err_pct <= TOL else COLORS["notok"]
            ax.bar(x[i] + width / 2, cv, width, color=color, alpha=0.85)

            ymax = max(abs(rv), abs(cv))
            ax.text(x[i] + width / 2, max(rv, cv) + ymax * 0.03,
                    f"{err_pct:.1f}%", ha="center", va="bottom",
                    fontsize=8, color=color, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_xlim(-0.6, len(keys) - 0.4)

    legend_elements = [
        Patch(facecolor=COLORS["ref"],   alpha=0.65, label="Riferimento (Table 2)"),
        Patch(facecolor=COLORS["ok"],    alpha=0.85, label=f"RELAP5 – errore ≤ {TOL:.0f}%"),
        Patch(facecolor=COLORS["notok"], alpha=0.85, label=f"RELAP5 – errore > {TOL:.0f}%"),
        Patch(facecolor="gray",          alpha=0.40, hatch="//", label="Non disponibile"),
    ]
    fig3.legend(handles=legend_elements, loc="lower right",
                bbox_to_anchor=(0.99, 0.01), fontsize=10, framealpha=0.9)

    out3 = os.path.join(out_dir, "fig3_steadystate_compare.png")
    fig3.savefig(out3, dpi=150, bbox_inches="tight")
    print(f"Salvato: {out3}")

    # ══════════════════════════════════════════════════════════════════════════
    # FIG 4 – Zoom steady state (t = 0-1000 s): potenza + httemp affiancati
    # ══════════════════════════════════════════════════════════════════════════
    mask = t <= T_SBO

    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 5))
    fig4.suptitle("RELAP5 – Steady State Verification (t = 0 ÷ 1000 s)", fontweight="bold")

    # Potenza
    ax4a.plot(t[mask], power[mask] / 1e6, color=COLORS["main"], lw=2)
    ax4a.axhline(TABLE2["Power (MW)"], color=COLORS["ref"], lw=1.5, ls="--",
                 label=f"Reference Value: {TABLE2['Power (MW)']:.0f} MW")
    ax4a.set_xlabel("Time (s)")
    ax4a.set_ylabel("Power (MW)")
    ax4a.set_title("Reactor Thermal Power")
    ax4a.legend()
    ax4a.set_xlim(0, T_SBO)
    if mask.sum() > 0:
        ymid   = power[mask].mean() / 1e6
        ystd   = power[mask].std()  / 1e6 + 1
        ax4a.set_ylim(ymid - max(ystd * 3, ymid * 0.05),
                      ymid + max(ystd * 3, ymid * 0.05))

    # httemp
    ax4b.plot(t[mask], httemp[mask], color="#7C3AED", lw=2)
    ax4b.set_xlabel("Time (s)")
    ax4b.set_ylabel("T cladding (K)")
    ax4b.set_title("Cladding Temperature (node 336-000817)")
    ax4b.set_xlim(0, T_SBO)
    if mask.sum() > 0:
        ymid   = httemp[mask].mean()
        ystd   = httemp[mask].std() + 0.1
        ax4b.set_ylim(ymid - max(ystd * 3, ymid * 0.02),
                      ymid + max(ystd * 3, ymid * 0.02))

    fig4.tight_layout()
    out4 = os.path.join(out_dir, "fig4_ss_zoom.png")
    fig4.savefig(out4, dpi=150, bbox_inches="tight")
    print(f"Salvato: {out4}")

    print("\n✓ Tutti i plot salvati in:", out_dir)


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.isfile(FILE_PATH):
        print(f"ERRORE: file non trovato: {FILE_PATH}")
        sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)
    make_plots(FILE_PATH, OUT_DIR)
