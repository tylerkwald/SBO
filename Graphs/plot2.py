import re
import numpy as np
import matplotlib.pyplot as plt

# =========================
# PARAMETRI DA MODIFICARE
# =========================

file_path = "ss3.o"

# parole chiave delle variabili (adatta ai nomi nel tuo output)
variables = {
    "cntrlvar-021": "core power",
    "p_primary": "p",
    "p_secondary": "secondary pressure",
    "pzr_level": "cntrlvar-150",
    "httemp": "core outlet temp",
    "tempf": "core inlet temp",
    "pmpvel-113 ": "mflowj",
    "flow_broken": "pmpvel-209"
}

# =========================
# LETTURA FILE
# =========================

time = []
data = {key: [] for key in variables}

current_time = None

with open(file_path, "r", errors="ignore") as f:
    for line in f:
        
        # trova il tempo
        time_match = re.search(r"time\s*=\s*([\d\.E\+\-]+)", line, re.IGNORECASE)
        if time_match:
            current_time = float(time_match.group(1))
            time.append(current_time)
        
        # cerca variabili
        for key, keyword in variables.items():
            if keyword.lower() in line.lower():
                values = re.findall(r"[-+]?\d*\.\d+E[+-]?\d+|[-+]?\d+\.\d+|[-+]?\d+", line)
                if values:
                    data[key].append(float(values[-1]))

# =========================
# ALLINEAMENTO DATI
# =========================

min_len = min(len(time), *(len(v) for v in data.values()))

time = np.array(time[:min_len])

for key in data:
    data[key] = np.array(data[key][:min_len])

# =========================
# PLOT
# =========================

plt.figure(figsize=(12, 8))

for i, (key, values) in enumerate(data.items(), 1):
    plt.subplot(3, 3, i)
    plt.plot(time, values)
    plt.title(key)
    plt.xlabel("Time (s)")
    plt.ylabel(key)
    plt.grid()

plt.tight_layout()
plt.show()

# =========================
# CHECK STAZIONARIETA'
# =========================

print("\n=== CHECK STEADY STATE ===")

for key, values in data.items():
    if len(values) > 10:
        std = np.std(values[-10:])
        mean = np.mean(values[-10:])
        print(f"{key}: mean = {mean:.3e}, std = {std:.3e}")