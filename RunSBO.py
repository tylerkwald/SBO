"""
SBO Project - Automated RELAP5 Runner
EMINE - Regulations & Safety

Usage:
    python run_SBO.py

What it does:
    0. Generates strip file from STRIP_VARIABLES dict
    1. Uploads input files to the server
    2. Runs RELAP5
    3. Extracts strip data
    4. Downloads results
    5. Generates all plots automatically

Place this script in: SBO/
"""

import paramiko
import os
import posixpath
import time
import subprocess
import sys

# ==============================================================================
# CONFIGURATION — edit these
# ==============================================================================

# Server credentials
HOSTNAME = '10.5.18.62'
USERNAME = 'Ovella'
PASSWORD = 'Napoli2026'   # <-- change this
PORT     = 3322                      # <-- check if it's 22 or 3322

# Case name (without extension)
CASE_NAME  = 'ss3_base'
STRIP_NAME = 'strip_base'

# Local folder structure (relative to this script location)
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER  = os.path.join(BASE_DIR, 'Input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'Output')
GRAPHS_FOLDER = os.path.join(BASE_DIR, 'Graphs')

# ==============================================================================
# STRIP VARIABLES — add/remove variables here, no need to edit the .i file
# Format: 'keyword component': 'description'
# ==============================================================================

STRIP_VARIABLES = {
    # --- Levels ---
    'cntrlvar 21':       'core level',
    'cntrlvar 22':       'upper plenum level',
    'cntrlvar 23':       'downcomer level',
    'cntrlvar 150':      'pressurizer level',
    'cntrlvar 176':      'SG intact DC level',
    'cntrlvar 276':      'SG broken DC level',
    # --- Power ---
    'rktpow 0':          'core power',
    'cntrlvar 833':      'PZR heaters power',
    # --- RCP ---
    'pmpvel 113':        'RCP intact angular velocity',
    'pmpvel 209':        'RCP broken angular velocity',
    # --- Clad temperatures (axial nodes 1-12, surface point 17) ---
    'httemp 336000117':  'clad surface node 1 (bottom)',
    'httemp 336000217':  'clad surface node 2',
    'httemp 336000317':  'clad surface node 3',
    'httemp 336000417':  'clad surface node 4',
    'httemp 336000517':  'clad surface node 5',
    'httemp 336000617':  'clad surface node 6',
    'httemp 336000717':  'clad surface node 7',
    'httemp 336000817':  'clad surface node 8',
    'httemp 336000917':  'clad surface node 9',
    'httemp 336001017':  'clad surface node 10',
    'httemp 336001117':  'clad surface node 11',
    'httemp 336001217':  'clad surface node 12 (top)',
    # --- Pressures ---
    'p 150010000':       'primary pressure (pressurizer)',
    'p 180010000':       'secondary pressure intact SG',
    'p 280010000':       'secondary pressure broken SG',
    # --- Temperatures ---
    'tempf 330010000':   'core inlet temperature',
    'tempf 340010000':   'core outlet temperature',
    'tempg 330010000':   'core outlet vapor temperature (CET)',
    'tempf 100010000':   'hot leg intact',
    'tempf 270060000':   'hot leg broken',
    'tempf 114010000':   'cold leg intact',
    'tempf 210010000':   'cold leg broken',
    # --- Primary mass flows ---
    'mflowj 100010000':  'intact loop flow (3 loops)',
    'mflowj 200010000':  'broken loop flow (1 loop)',
    # --- Feedwater and AFW ---
    'mflowj 181000000':  'intact main feedwater',
    'mflowj 281000000':  'broken main feedwater',
    'mflowj 183000000':  'intact AFW motor-driven',
    'mflowj 283000000':  'broken AFW motor-driven',
    'mflowj 473000000':  'intact TDP (uncontrolled)',
    'mflowj 475000000':  'broken TDP (uncontrolled)',
    # --- RCP seal leaks ---
    'mflowj 506000000':  'intact small RCP seal leak',
    'mflowj 507000000':  'broken small RCP seal leak',
    'mflowj 508000000':  'intact large RCP seal leak',
    'mflowj 509000000':  'broken large RCP seal leak',
    # --- PZR and SG relief/safety valves ---
    'mflowj 155000000':  'PZR safety valve',
    'mflowj 157000000':  'PZR relief valve (PORV)',
    'mflowj 187000000':  'SG intact relief valve',
    'mflowj 287000000':  'SG broken relief valve',
    # --- ECCS (active after AC recovery at 12h) ---
    'mflowj 196000000':  'intact LPSI',
    'mflowj 198000000':  'intact HPSI',
    'mflowj 296000000':  'broken LPSI',
    'mflowj 298000000':  'broken HPSI',
    # --- Accumulators ---
    'acvliq 190':        'intact accumulator liquid volume',
    'acvliq 290':        'broken accumulator liquid volume',
    # --- Integral mass flows ---
    'cntrlvar 500':      'integral PZR valves mass flow',
    'cntrlvar 502':      'integral ECCS mass flow',
    'cntrlvar 504':      'integral RCP seal leak mass flow',
}

# ==============================================================================
# HELPERS
# ==============================================================================

def banner(text):
    print(f'\n{"="*60}')
    print(f'  {text}')
    print(f'{"="*60}')


def exec_wait(client, cmd, label=''):
    """Execute remote command and wait for completion."""
    print(f'  Running: {cmd}')
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    err = stderr.read().decode().strip()
    if exit_status != 0 and err:
        print(f'  WARNING ({label}): {err[:300]}')
    return exit_status


def generate_strip_file():
    """Generate strip .i file automatically from STRIP_VARIABLES."""
    strip_path = os.path.join(INPUT_FOLDER, f'{STRIP_NAME}.i')
    os.makedirs(INPUT_FOLDER, exist_ok=True)

    lines = [
        f'= {STRIP_NAME}',
        '0000100 strip fmtout',
        '101  run',
        '103  0',
        '*' + '-' * 55,
        f'* Auto-generated strip file — {len(STRIP_VARIABLES)} variables',
        '*' + '-' * 55,
    ]
    for i, (var, comment) in enumerate(STRIP_VARIABLES.items(), start=1001):
        lines.append(f'{i:<6} {var:<30} * {comment}')
    lines.append('.')

    with open(strip_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f'  ✓ Generated: {strip_path}')
    print(f'  ✓ Variables: {len(STRIP_VARIABLES)}')
    return strip_path


# ==============================================================================
# MAIN
# ==============================================================================

def run_simulation():

    # --- 0. Generate strip file ---
    banner('0. GENERATING STRIP FILE')
    generate_strip_file()

    # --- 1. Check local files ---
    banner('1. CHECKING LOCAL FILES')
    local_input = os.path.join(INPUT_FOLDER, f'{CASE_NAME}.i')
    local_strip = os.path.join(INPUT_FOLDER, f'{STRIP_NAME}.i')

    all_ok = True
    for f, label in [(local_input, 'Input file'), (local_strip, 'Strip file')]:
        if os.path.exists(f):
            size_kb = os.path.getsize(f) / 1024
            print(f'  ✓ {label}: {os.path.basename(f)} ({size_kb:.0f} KB)')
        else:
            print(f'  ✗ {label} NOT FOUND: {f}')
            all_ok = False
    if not all_ok:
        print('  Aborting.')
        return

    # --- 2. Connect to server ---
    banner('2. CONNECTING TO SERVER')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(HOSTNAME, port=PORT, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        print(f'  ✓ Connected to {USERNAME}@{HOSTNAME}:{PORT}')
    except Exception as e:
        print(f'  ✗ Connection failed: {e}')
        return

    try:
        # Use home directory directly (no subfolder)
        remote_work_dir = sftp.normalize('.')
        print(f'  Remote working dir: {remote_work_dir}')

        # --- 3. Upload input files ---
        banner('3. UPLOADING INPUT FILES')
        remote_input = posixpath.join(remote_work_dir, f'{CASE_NAME}.i')
        remote_strip = posixpath.join(remote_work_dir, f'{STRIP_NAME}.i')

        print(f'  Uploading {CASE_NAME}.i ...')
        sftp.put(local_input, remote_input)
        print(f'  ✓ Done')

        print(f'  Uploading {STRIP_NAME}.i ...')
        sftp.put(local_strip, remote_strip)
        print(f'  ✓ Done')

        # --- 4. Run RELAP5 ---
        banner('4. RUNNING RELAP5')
        cmd_run = f'cd {remote_work_dir} && relap1.sh {CASE_NAME} run'
        print(f'  Starting simulation (this may take several minutes)...')
        start_time = time.time()

        status = exec_wait(client, cmd_run, label='RELAP run')
        elapsed = time.time() - start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        if status != 0:
            print(f'  ✗ RELAP failed after {mins}m {secs}s — downloading .o for inspection')
            try:
                remote_out = posixpath.join(remote_work_dir, f'{CASE_NAME}.o')
                local_out  = os.path.join(OUTPUT_FOLDER, f'{CASE_NAME}.o')
                os.makedirs(OUTPUT_FOLDER, exist_ok=True)
                sftp.get(remote_out, local_out)
                print(f'  Downloaded {CASE_NAME}.o → check for errors')
            except Exception:
                pass
            return
        else:
            print(f'  ✓ RELAP completed in {mins}m {secs}s')

        # --- 5. Extract strip data ---
        banner('5. EXTRACTING STRIP DATA')
        cmd_extract = f'cd {remote_work_dir} && extract.sh {STRIP_NAME} restart'
        status = exec_wait(client, cmd_extract, label='extract')
        if status == 0:
            print(f'  ✓ Extraction complete')
        else:
            print(f'  ✗ Extraction may have failed — attempting download anyway')
        time.sleep(2)

        # --- 6. Download results ---
        banner('6. DOWNLOADING RESULTS')
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        files_to_download = [
            (f'{CASE_NAME}.o',               f'{CASE_NAME}.o',          'Output log',  False),
            (f'{STRIP_NAME}_restart.dat', 'strip_base_restart.dat',  'Strip data',  True),
        ]

        data_downloaded = False
        for remote_name, local_name, label, required in files_to_download:
            remote_path = posixpath.join(remote_work_dir, remote_name)
            local_path  = os.path.join(OUTPUT_FOLDER, local_name)
            try:
                sftp.get(remote_path, local_path)
                size_kb = os.path.getsize(local_path) / 1024
                print(f'  ✓ {label}: {local_name} ({size_kb:.0f} KB)')
                if required:
                    data_downloaded = True
            except Exception:
                marker = '✗' if required else '~'
                print(f'  {marker} {label} not found: {remote_name}')

    except Exception as e:
        print(f'\n  CRITICAL ERROR: {e}')
        import traceback
        traceback.print_exc()
        return

    finally:
        try:
            sftp.close()
            client.close()
            print('\n  Connection closed.')
        except Exception:
            pass

    # --- 7. Generate plots ---
    if not data_downloaded:
        print('\n  Skipping plots — data file not downloaded.')
        return

    banner('7. GENERATING PLOTS')

    if not os.path.exists(GRAPHS_FOLDER):
        print(f'  Graph Codes folder not found: {GRAPHS_FOLDER}')
        print('  Skipping plots.')
        return

    py_scripts = sorted([f for f in os.listdir(GRAPHS_FOLDER) if f.endswith('.py')])

    if not py_scripts:
        print('  No Python scripts found in Graph Codes/')
        return

    print(f'  Found {len(py_scripts)} script(s): {", ".join(py_scripts)}')
    print()

    for script in py_scripts:
        script_path = os.path.join(GRAPHS_FOLDER, script)
        print(f'  Running {script} ... ', end='', flush=True)
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode == 0:
                n_saved = result.stdout.count('Saved:')
                print(f'✓  ({n_saved} plots saved)')
            else:
                print('✗')
                print(f'    Error:\n{result.stderr[:400]}')
        except subprocess.TimeoutExpired:
            print('✗  (timeout after 180s)')
        except Exception as e:
            print(f'✗  ({e})')

    # --- Done ---
    banner('DONE')
    print(f'  Output files : {OUTPUT_FOLDER}')
    print(f'  Plots        : {os.path.join(BASE_DIR, "Pictures")}')
    print()


if __name__ == '__main__':
    run_simulation()
