"""
SBO Project - Event Tree Automation
EMINE - Regulations & Safety
"""

import paramiko
import os
import posixpath
import time

# ==============================================================================
# CONFIGURATION
# ==============================================================================

HOSTNAME = '10.5.18.62'
USERNAME = 'Ovella'
PASSWORD = 'Napoli2026'
PORT     = 3322

BASE_CASE_FILE = 'ss3_base'
STRIP_NAME     = 'strip_base'

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER  = os.path.join(BASE_DIR, 'Input')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'Output', 'EventTree')

# ==============================================================================
# EVENT TREE CASES
# (small_leak, large_leak, tdp, batteries, ac_recovery)
# ==============================================================================

EVENT_TREE_CASES = {
    'ET01_all':                         (True,  True,  True,  True,  True ),
    'ET02_noAC':                        (True,  True,  True,  True,  False),
    'ET03_noBat':                       (True,  True,  True,  False, True ),
    'ET04_noBat_noAC':                  (True,  True,  True,  False, False),
    'ET05_noTDP':                       (True,  True,  False, True,  True ),
    'ET06_noTDP_noAC':                  (True,  True,  False, True,  False),
    'ET07_noTDP_noBat_noAC':            (True,  True,  False, False, False),
    'ET08_noLeak':                      (False, False, True,  True,  True ),
    'ET09_noLeak_noAC':                 (False, False, True,  True,  False),
    'ET10_noLeak_noBat_noAC':           (False, False, True,  False, False),
    'ET11_noLeak_noTDP_noAC':           (False, False, False, True,  False),
    'ET12_noLeak_noTDP_noBat_noAC':     (False, False, False, False, False),
}

# ==============================================================================
# TRIP STRINGS  — must match ss3_base.i exactly (copy-paste from file)
# ==============================================================================

TRIP_ORIGINALS = {
    'small_leak':   '770           458           and           454                     n',
    'large_leak_a': '771           454           and           456             n',
    'large_leak_b': '772           454           and           457             n',
    'tdp':          '755          750      and      -491                      n',
    'batteries':    '491   time         0 lt    timeof        515 18000.0   n * availability of the system',
    'ac':           '453   time         0 ge      timeof       452 43200.0       l * AC power recovery 12h after SBO',
}

TRIP_DISABLED = {
    'small_leak':   '770           611           and           611                     n * small leak DISABLED',
    'large_leak_a': '771           611           and           611             n * large leak DISABLED',
    'large_leak_b': '772           611           and           611             n * large leak DISABLED',
    'tdp':          '755          611      and      611                       n * TDP DISABLED',
    'batteries':   '491   time         0 gt      null          0   1.0e9   n * Bat DISABLED',
    'ac':           '453   time         0 gt      null          0   1.0e9   l * AC recovery DISABLED',
}

# ==============================================================================
# HELPERS
# ==============================================================================

def banner(text):
    print(f'\n{"="*60}')
    print(f'  {text}')
    print(f'{"="*60}')

def exec_wait(client, cmd, label=''):
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    err = stderr.read().decode().strip()
    if exit_status != 0 and err:
        print(f'    WARNING ({label}): {err[:200]}')
    return exit_status


def exec_nowait(client, cmd):
    """Fire-and-forget remote command (for background RELAP launch)."""
    client.exec_command(cmd)


def wait_for_relap(sftp, remote_work_dir, case_name, timeout=1800, poll=15):
    """
    Poll the .o file size until it stops growing → RELAP finished.
    Returns True if finished, False if timeout.
    """
    remote_o = posixpath.join(remote_work_dir, f'{case_name}.o')
    print(f'    Polling {case_name}.o', end='', flush=True)
    prev_size = -1
    stable_count = 0
    elapsed = 0
    while elapsed < timeout:
        try:
            size = sftp.stat(remote_o).st_size
            if size > 0 and size == prev_size:
                stable_count += 1
                if stable_count >= 3:
                    print(f' ✓ done ({size//1024} KB, {elapsed}s)')
                    return True
            else:
                stable_count = 0
            prev_size = size
        except IOError:
            pass  # file not yet created
        print('.', end='', flush=True)
        time.sleep(poll)
        elapsed += poll
    print(' TIMEOUT')
    return False


def generate_case_input(base_content, case_name, small_leak, large_leak, tdp, batteries, ac):
    """Generate modified input with disabled systems and verify replacements."""
    content = base_content
    changes = []
    # In generate_case_input, dopo gli altri replace:
    if case_name in ['ET02_noAC', 'ET09_noLeak_noAC']:
        content = content.replace(
            '201  50000.0    1.0e-7   0.1   3    50     50000  50000',
            '201  259200.0   1.0e-7   0.1   3    50     50000  259200'
        )

    def replace(key):
        nonlocal content
        orig = TRIP_ORIGINALS[key]
        repl = TRIP_DISABLED[key]
        if orig in content:
            content = content.replace(orig, repl)
            changes.append(f'  ✓ disabled: {key}')
        else:
            changes.append(f'  ✗ NOT FOUND: {key}  ← check spacing in TRIP_ORIGINALS')

    if not small_leak:
        replace('small_leak')
    if not large_leak:
        replace('large_leak_a')
        replace('large_leak_b')
    if not tdp:
        replace('tdp')
    if not batteries:
        replace('batteries')
    if not ac:
        replace('ac')

    header = f'* EVENT TREE CASE: {case_name}\n'
    return header + content, changes


def check_core_damage(dat_file):
    """Parse strip .dat to find if PCT >= 1700 K (core damage)."""
    CD_THRESHOLD   = 1477.0   # K — PCT regulatory limit (core damage)
    RELAP_STOP     = 1700.0   # K — RELAP trip 455 (simulation stop)
    if not os.path.exists(dat_file):
        return 'NO DATA'
    try:
        with open(dat_file, 'r') as f:
            lines = f.readlines()
        if not lines:
            return 'EMPTY'

        header = lines[0].split()
        httemp_idx = [i for i, c in enumerate(header) if 'httemp' in c.lower()]
        if not httemp_idx:
            return 'NO HTTEMP'

        max_t = 0.0
        for line in lines[1:]:
            parts = line.split()
            if len(parts) <= max(httemp_idx):
                continue
            try:
                t = float(parts[0])
                for idx in httemp_idx:
                    temp = float(parts[idx])
                    if temp > max_t:
                        max_t = temp
                    if temp >= RELAP_STOP:
                        return f'CD_SEVERE @ {t:.0f}s (T={temp:.0f}K)'
                    if temp >= CD_THRESHOLD:
                        return f'CD @ {t:.0f}s (T={temp:.0f}K)'
            except ValueError:
                continue
        return f'SUCCESS (max T={max_t:.0f}K)'
    except Exception as e:
        return f'ERROR: {e}'


# ==============================================================================
# MAIN
# ==============================================================================

def run_event_tree():

    banner('EVENT TREE RUNNER — SBO Project')

    # Load base case
    base_path = os.path.join(INPUT_FOLDER, f'{BASE_CASE_FILE}.i')
    if not os.path.exists(base_path):
        print(f'  ✗ Base case not found: {base_path}')
        return
    with open(base_path, 'r') as f:
        base_content = f.read()
    print(f'  ✓ Base case loaded ({len(base_content)//1024} KB)')

    # --- Verify trip strings exist in base ---
    banner('VERIFYING TRIP STRINGS IN BASE CASE')
    all_found = True
    for key, orig in TRIP_ORIGINALS.items():
        if orig in base_content:
            print(f'  ✓ Found: {key}')
        else:
            print(f'  ✗ MISSING: {key}')
            print(f'    Expected: "{orig}"')
            all_found = False
    if not all_found:
        print('\n  Fix TRIP_ORIGINALS strings before running. Aborting.')
        return

    # --- Generate input files ---
    banner('GENERATING INPUT FILES')
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    case_files = {}

    for case_name, (small, large, tdp, bat, ac) in EVENT_TREE_CASES.items():
        content, changes = generate_case_input(base_content, case_name,
                                               small, large, tdp, bat, ac)
        filepath = os.path.join(INPUT_FOLDER, f'{case_name}.i')
        with open(filepath, 'w') as f:
            f.write(content)
        case_files[case_name] = filepath
        n_disabled = sum(1 for c in changes if '✓' in c)
        print(f'  {case_name:<38} ({n_disabled} systems disabled)')
        for ch in changes:
            print(f'    {ch}')

    # --- Connect ---
    banner('CONNECTING TO SERVER')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, port=PORT, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        remote_dir = sftp.normalize('.')
        print(f'  ✓ Connected: {remote_dir}')
    except Exception as e:
        print(f'  ✗ {e}')
        return

    # Upload strip file once
    local_strip = os.path.join(INPUT_FOLDER, f'{STRIP_NAME}.i')
    if os.path.exists(local_strip):
        sftp.put(local_strip, posixpath.join(remote_dir, f'{STRIP_NAME}.i'))
        print(f'  ✓ Strip file uploaded')

    # Upload restart.r (needed by all cases as initial condition)
    local_restart = os.path.join(INPUT_FOLDER, 'restart.r')
    if os.path.exists(local_restart):
        size_mb = os.path.getsize(local_restart) / 1e6
        print(f'  Uploading restart.r ({size_mb:.1f} MB)...', end='', flush=True)
        sftp.put(local_restart, posixpath.join(remote_dir, 'restart.r'))
        print(' ✓')
    else:
        print('  ✗ restart.r NOT FOUND in Input/ — aborting')
        sftp.close()
        client.close()
        return

    results = {}

    for i, (case_name, (small, large, tdp, bat, ac)) in enumerate(EVENT_TREE_CASES.items()):

        banner(f'CASE {i+1}/{len(EVENT_TREE_CASES)}: {case_name}')
        print(f'  leak={small} lgLeak={large} TDP={tdp} bat={bat} AC={ac}')

        # Upload input
        sftp.put(case_files[case_name],
                 posixpath.join(remote_dir, f'{case_name}.i'))
        print(f'  ✓ Uploaded {case_name}.i')

        # Delete old .o if exists (avoid reading stale file)
        try:
            sftp.remove(posixpath.join(remote_dir, f'{case_name}.o'))
        except IOError:
            pass

        # Run RELAP — blocks until relap1.sh returns (same as run_SBO.py)
        cmd_run = f'cd {remote_dir} && relap1.sh {case_name} run'
        t0 = time.time()
        status = exec_wait(client, cmd_run, label='RELAP')
        elapsed = int(time.time() - t0)

        if status != 0:
            print(f'  ✗ RELAP failed after {elapsed//60}m {elapsed%60}s')
            results[case_name] = 'FAILED'
            continue

        print(f'  ✓ Completed in {elapsed//60}m {elapsed%60}s')

        # Extract strip (case-specific name to avoid overwrite)
        # Step 1: extract (blocking)
        # Corretto: RELAP scrive sempre su restart.r
        cmd_extract = f'cd {remote_dir} && extract.sh {STRIP_NAME} restart'
        exec_wait(client, cmd_extract, label='extract')
        time.sleep(3)

        # Rinomina strip_base_restart.dat → ET01_all_strip.dat
        cmd_mv = f'mv {remote_dir}/{STRIP_NAME}_restart.dat {remote_dir}/{case_name}_strip.dat'
        exec_wait(client, cmd_mv, label='mv')

        # Download
        for remote_name, local_name in [
            (f'{case_name}.o',         f'{case_name}.o'),
            (f'{case_name}_strip.dat', f'{case_name}_strip.dat'),
        ]:
            rpath = posixpath.join(remote_dir, remote_name)
            lpath = os.path.join(OUTPUT_FOLDER, local_name)
            try:
                sftp.get(rpath, lpath)
                print(f'  ✓ {local_name} ({os.path.getsize(lpath)//1024} KB)')
            except Exception as e:
                print(f'  ~ {remote_name}: {e}')

        # Assess outcome
        outcome = check_core_damage(os.path.join(OUTPUT_FOLDER, f'{case_name}_strip.dat'))
        results[case_name] = outcome
        print(f'  >>> {outcome}')

    sftp.close()
    client.close()

    # --- Summary ---
    banner('EVENT TREE SUMMARY')
    print(f'{"Case":<40} {"Lk":>3} {"LgLk":>4} {"TDP":>4} {"Bat":>4} {"AC":>4}  {"Outcome"}')
    print('-' * 80)
    s = lambda x: 'Y' if x else 'N'
    for case_name, (small, large, tdp, bat, ac) in EVENT_TREE_CASES.items():
        outcome = results.get(case_name, 'NOT RUN')
        print(f'{case_name:<40} {s(small):>3} {s(large):>4} {s(tdp):>4} {s(bat):>4} {s(ac):>4}  {outcome}')

    summary_path = os.path.join(OUTPUT_FOLDER, 'event_tree_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('EVENT TREE RESULTS\n' + '='*80 + '\n')
        f.write(f'{"Case":<40} {"Lk":>3} {"LgLk":>4} {"TDP":>4} {"Bat":>4} {"AC":>4}  Outcome\n')
        f.write('-'*80 + '\n')
        for case_name, (small, large, tdp, bat, ac) in EVENT_TREE_CASES.items():
            outcome = results.get(case_name, 'NOT RUN')
            f.write(f'{case_name:<40} {s(small):>3} {s(large):>4} {s(tdp):>4} {s(bat):>4} {s(ac):>4}  {outcome}\n')

    print(f'\n  Summary: {summary_path}')


if __name__ == '__main__':
    run_event_tree()