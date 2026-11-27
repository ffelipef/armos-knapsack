"""Executa os experimentos e grava um CSV (uma linha por instância).

Exemplos:
  python run_experiments.py --quick                 # teste rápido
  python run_experiments.py                         # experimento completo do artigo
"""
import argparse
import csv
import gc
import json
import os
import platform
import subprocess
import sys
import time
import tracemalloc

import numpy as np

from algorithms import (dp_cells_updated, dp_exact, greedy_modified, greedy_ratio,
                        scan_arrival, sort_comparisons)
from generator import KINDS, make_instance, seed_for

ALGS = {"greedy": greedy_ratio, "modified": greedy_modified, "scan": scan_arrival, "dp": dp_exact}


def timed(fn, c, p, C):
    gc.disable()
    t0 = time.perf_counter_ns()
    value = fn(c, p, C)
    t1 = time.perf_counter_ns()
    gc.enable()
    return value, (t1 - t0) / 1000.0  # microssegundos


def peak_kib(fn, c, p, C):
    tracemalloc.start()
    fn(c, p, C)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024.0


def sysctl(name):
    try:
        return subprocess.check_output(["sysctl", "-n", name], text=True).strip()
    except Exception:
        return None


def env_info():
    info = {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "macos": platform.mac_ver()[0] or None,
        "cpu": sysctl("machdep.cpu.brand_string") or platform.processor() or None,
        "cpu_count": os.cpu_count(),
    }
    mem = sysctl("hw.memsize")
    if mem is None:
        try:
            mem = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except Exception:
            mem = None
    info["ram_gb"] = round(int(mem) / 2**30, 1) if mem else None
    return info


FIELDS = ["kind", "gamma", "n", "rep", "R", "C", "sum_c",
          "t_greedy_us", "t_modified_us", "t_scan_us", "t_dp_us",
          "v_greedy", "v_modified", "v_scan", "v_dp",
          "rho_greedy", "rho_modified", "rho_scan", "ok_half",
          "ops_dp_cells", "ops_sort_cmp", "mem_dp_kib", "mem_greedy_kib"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[50, 100, 500, 1000, 5000])
    ap.add_argument("--gammas", type=float, nargs="+", default=[0.25, 0.5, 0.75])
    ap.add_argument("--kinds", nargs="+", default=list(KINDS), choices=KINDS)
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--R", type=int, default=1000, help="custo máximo de um item")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="results")
    ap.add_argument("--quick", action="store_true", help="configuração pequena para testar")
    a = ap.parse_args()
    if a.quick:
        a.sizes, a.gammas, a.reps, a.R, a.out = [50, 100, 200, 400, 800], [0.5], 3, 200, "results_quick"

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "env.json"), "w") as f:
        json.dump({**env_info(), "args": vars(a)}, f, indent=2)

    path = os.path.join(a.out, "results.csv")
    total = len(a.kinds) * len(a.gammas) * len(a.sizes) * a.reps
    done = 0
    start = time.time()
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for kind in a.kinds:
            for gamma in a.gammas:
                for n in a.sizes:
                    # aquecimento dos algoritmos rápidos (não entra nos dados)
                    c, p, C = make_instance(kind, n, gamma, a.R, seed_for(a.seed, kind, n, gamma, -1))
                    for name in ("greedy", "modified", "scan"):
                        ALGS[name](c, p, C)
                    for rep in range(a.reps):
                        c, p, C = make_instance(kind, n, gamma, a.R, seed_for(a.seed, kind, n, gamma, rep))
                        row = {"kind": kind, "gamma": gamma, "n": n, "rep": rep, "R": a.R, "C": C, "sum_c": sum(c)}
                        vals = {}
                        for name, fn in ALGS.items():
                            vals[name], row[f"t_{name}_us"] = timed(fn, c, p, C)
                            row[f"v_{name}"] = vals[name]
                        opt = vals["dp"]
                        for name in ("greedy", "modified", "scan"):
                            row[f"rho_{name}"] = vals[name] / opt if opt > 0 else 1.0
                        row["ok_half"] = 2 * vals["modified"] >= opt
                        if not row["ok_half"]:
                            print("AVISO: garantia 1/2 violada em", row, file=sys.stderr)
                        if rep == 0:  # medidas auxiliares, fora da cronometragem
                            row["ops_dp_cells"] = dp_cells_updated(c, C)
                            row["ops_sort_cmp"] = sort_comparisons(c, p, C)
                            row["mem_dp_kib"] = round(peak_kib(dp_exact, c, p, C), 1)
                            row["mem_greedy_kib"] = round(peak_kib(greedy_modified, c, p, C), 1)
                        w.writerow(row)
                        f.flush()
                        done += 1
                    print(f"[{done}/{total}] {kind} gamma={gamma} n={n} ({time.time() - start:.0f}s)", flush=True)
    print("Resultados em", path)


if __name__ == "__main__":
    main()
