#!/usr/bin/env python3
# judge.py
import argparse
import subprocess
import os
import sys
import difflib
import shlex
import time
import resource
import glob
import json
import yaml


def normalize_output(text: str) -> str:
    """
    Normalize output text for comparison by:
    1. Stripping leading/trailing whitespace
    2. Removing trailing spaces from each line
    3. Removing empty lines
    4. Ensuring consistent line endings
    """
    if not text:
        return ""

    # Strip overall and process each line
    lines = text.strip().split('\n')
    # Remove trailing spaces from each line and filter out empty lines
    normalized_lines = [line.rstrip() for line in lines if line.strip()]

    return '\n'.join(normalized_lines)


def set_limits(mem_mb, time_ms):
    # POSIX-only. For Windows, skip memory limit or use Job Objects.
    try:
        if mem_mb and os.name == 'posix':
            # Set memory limit more carefully for macOS compatibility
            resource.setrlimit(resource.RLIMIT_AS,
                               (mem_mb*1024*1024, mem_mb*1024*1024))
    except (OSError, ValueError):
        # If memory limit setting fails, continue without it
        # This can happen on macOS or other systems with restrictions
        pass
    # We rely on subprocess timeout for time limit.


def run_with_limits(exec_path, in_path, out_path, time_ms, mem_mb):
    with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:
        start = time.time()
        try:
            subprocess.run(
                [exec_path],
                stdin=fin, stdout=fout, stderr=subprocess.PIPE,
                preexec_fn=(lambda: set_limits(mem_mb, time_ms)
                            ) if os.name == 'posix' else None,
                timeout=time_ms/1000.0, check=False
            )
        except subprocess.TimeoutExpired:
            return 'TLE', None, time.time()-start
    return 'OK', None, time.time()-start


def diff_check(ans_path, out_path):
    try:
        with open(ans_path, 'r', encoding='utf-8') as fa, open(out_path, 'r', encoding='utf-8') as fo:
            # Use consistent normalization function
            expected = normalize_output(fa.read())
            actual = normalize_output(fo.read())

            return 'AC' if expected == actual else 'WA'
    except Exception:
        return 'JE'  # Judge Error if files can't be read


def float_check(ans_path, out_path, tol):
    import math
    try:
        A = open(ans_path).read().split()
        B = open(out_path).read().split()
        if len(A) != len(B):
            return 'WA'
        for x, y in zip(A, B):
            try:
                if abs(float(x) - float(y)) > tol:
                    return 'WA'
            except:
                return 'WA'
        return 'AC'
    except Exception:
        return 'JE'


def spj_check(spj_exec, in_path, out_path, ans_path):
    # SPJ convention: return code 0 = AC, 1 = WA, 2 = PE; others = JE
    try:
        p = subprocess.run([spj_exec, in_path, out_path, ans_path])
        if p.returncode == 0:
            return 'AC'
        if p.returncode == 1:
            return 'WA'
        if p.returncode == 2:
            return 'PE'
        return 'JE'
    except Exception:
        return 'JE'


def main():
    ap = argparse.ArgumentParser(description='Codeforces-style judge')
    ap.add_argument('problem_dir', help='Path to problem directory')
    ap.add_argument('solution_cpp', help='Path to C++ solution file')
    args = ap.parse_args()

    # Load toolchain configuration
    try:
        meta = json.loads(open('judge/toolchain.json').read())
    except Exception as e:
        print(f'Error loading toolchain.json: {e}')
        sys.exit(1)

    # Load problem configuration
    prob_config_path = os.path.join(args.problem_dir, 'problem.yaml')
    if not os.path.exists(prob_config_path):
        print(f'Error: problem.yaml not found in {args.problem_dir}')
        sys.exit(1)

    try:
        y = yaml.safe_load(open(prob_config_path))
    except Exception as e:
        print(f'Error loading problem.yaml: {e}')
        sys.exit(1)

    # Compile the solution
    exe = os.path.join(args.problem_dir, 'solution')
    compile_cmd = meta['compile'].replace(
        '{src}', args.solution_cpp).replace('{out}', exe)
    print(f'Compiling: {compile_cmd}')

    c = subprocess.run(shlex.split(compile_cmd),
                       capture_output=True, text=True)
    if c.returncode != 0:
        print('CE (Compilation Error)')
        if c.stderr:
            print('Compilation errors:')
            print(c.stderr)
        sys.exit(1)

    print(f'Running tests for problem: {y.get("title", "Unknown")}')
    print(f'Time limit: {y.get("time_limit_ms", 1000)}ms')
    print(f'Memory limit: {y.get("memory_limit_mb", 256)}MB')
    print(f'Checker: {y.get("checker", "diff")}')
    print('-' * 50)

    verdicts = []

    # Run tests for each bucket (pretests, system)
    for bucket in ['pretests', 'system']:
        in_dir = os.path.join(args.problem_dir, 'tests', bucket)
        if not os.path.isdir(in_dir):
            print(f'Skipping {bucket} (directory not found)')
            continue

        test_files = sorted(glob.glob(os.path.join(in_dir, '*.in')))
        if not test_files:
            print(f'No test files found in {bucket}')
            continue

        print(f'\n[{bucket.upper()}]')

        for ip in test_files:
            base = os.path.splitext(os.path.basename(ip))[0]
            apath = os.path.join(in_dir, base + '.ans')
            opath = os.path.join(in_dir, base + '.out')

            # Check if answer file exists
            if not os.path.exists(apath):
                print(f'  {base}: JE (missing .ans file)')
                verdicts.append((bucket, base, 'JE', '0ms'))
                continue

            # Run the solution
            status, _, elapsed = run_with_limits(
                exe, ip, opath,
                y.get('time_limit_ms', 1000),
                y.get('memory_limit_mb', 256)
            )

            if status != 'OK':
                print(f'  {base}: {status} ({elapsed*1000:.0f}ms)')
                verdicts.append(
                    (bucket, base, status, f'{elapsed*1000:.0f}ms'))
                continue

            # Check the output
            chk = y.get('checker', 'diff')
            if chk == 'diff':
                res = diff_check(apath, opath)
            elif chk == 'float':
                res = float_check(apath, opath, y.get('float_abs_tol', 1e-6))
            elif chk == 'spj':
                spj_exec_path = y.get('spj_exec', '')
                if not spj_exec_path or not os.path.exists(spj_exec_path):
                    res = 'JE'
                else:
                    res = spj_check(spj_exec_path, ip, opath, apath)
            else:
                res = 'JE'

            print(f'  {base}: {res} ({elapsed*1000:.0f}ms)')
            verdicts.append((bucket, base, res, f'{elapsed*1000:.0f}ms'))

    # Summary
    print('\n' + '=' * 50)
    print('SUMMARY:')
    ok = True
    for b, base, res, t in verdicts:
        print(f'[{b}] {base}: {res} ({t})')
        if res not in ('AC',):
            ok = False

    if ok:
        print('\nAll tests passed! ✅')
    else:
        print('\nSome tests failed! ❌')

    # Clean up executable
    if os.path.exists(exe):
        os.remove(exe)

    sys.exit(0 if ok else 2)


if __name__ == '__main__':
    main()
