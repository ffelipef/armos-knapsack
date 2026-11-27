"""Lê results.csv e gera tabelas e gráficos para a Seção 4 do artigo.

Uso: python analyze.py results            (pasta com results.csv)
Saídas na mesma pasta: summary.csv, analysis.md, fig_time_vs_n.png,
fig_ratio_boxplot.png, fig_ratio_vs_n.png
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress

folder = sys.argv[1] if len(sys.argv) > 1 else "results"
df = pd.read_csv(os.path.join(folder, "results.csv"))
algs = {"greedy": "guloso por razão", "modified": "guloso modificado",
        "scan": "varredura simples", "dp": "programação dinâmica"}

# ---- tabela-resumo por configuração
g = df.groupby(["kind", "gamma", "n"])
summary = g.agg(
    t_modified_med=("t_modified_us", "median"), t_modified_std=("t_modified_us", "std"),
    t_dp_med=("t_dp_us", "median"), t_dp_std=("t_dp_us", "std"),
    rho_mod_mean=("rho_modified", "mean"), rho_mod_min=("rho_modified", "min"),
    share_rho_090=("rho_modified", lambda s: (s >= 0.9).mean()),
).reset_index()
summary.to_csv(os.path.join(folder, "summary.csv"), index=False)

# ---- expoente empírico (inclinação em escala log-log) e ajuste dos modelos
lines = ["# Análise dos experimentos", ""]
lines += ["## Expoente empírico do tempo (regressão log-log da mediana por n)", "",
          "| algoritmo | expoente | R² | previsto |", "|---|---|---|---|"]
expected = {"greedy": "≈ 1 (n log n)", "modified": "≈ 1 (n log n)", "scan": "1 (n)",
            "dp": "≈ 2 (n·C com C ∝ n)"}
for k, label in algs.items():
    med = df.groupby("n")[f"t_{k}_us"].median()
    r = linregress(np.log(med.index.values), np.log(med.values))
    lines.append(f"| {label} | {r.slope:.2f} | {r.rvalue ** 2:.3f} | {expected[k]} |")

lines += ["", "## Ajuste dos modelos teóricos (t = a·x + b, x = modelo)", "",
          "| algoritmo | modelo x | a (µs por unidade) | b (µs) | R² |", "|---|---|---|---|---|"]
fits = {}


def fit(name, x, y):
    f = lambda x, a, b: a * x + b
    (a, b), _ = curve_fit(f, x, y)
    ss_res = float(np.sum((y - f(x, a, b)) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    fits[name] = (a, b)
    return a, b, 1 - ss_res / ss_tot if ss_tot else float("nan")


per_n = df.groupby("n").agg(t_mod=("t_modified_us", "median"), t_greedy=("t_greedy_us", "median"),
                            t_scan=("t_scan_us", "median"))
x_nlogn = per_n.index.values * np.log2(per_n.index.values)
for name, col in (("modified", "t_mod"), ("greedy", "t_greedy")):
    a, b, r2 = fit(name, x_nlogn, per_n[col].values)
    lines.append(f"| {algs[name]} | n·log₂n | {a:.4g} | {b:.4g} | {r2:.3f} |")
a, b, r2 = fit("scan", per_n.index.values.astype(float), per_n["t_scan"].values)
lines.append(f"| {algs['scan']} | n | {a:.4g} | {b:.4g} | {r2:.3f} |")
dp = df.assign(x=df["n"] * df["C"])
a, b, r2 = fit("dp", dp["x"].values.astype(float), dp["t_dp_us"].values)
lines.append(f"| {algs['dp']} | n·C | {a:.4g} | {b:.4g} | {r2:.3f} |")

# ---- razão de aproximação
lines += ["", "## Razão de aproximação ρ = SOL/OPT", "",
          "| tipo | algoritmo | média | mínimo | % de instâncias com ρ ≥ 0,9 |", "|---|---|---|---|---|"]
for kind, d in df.groupby("kind"):
    for k in ("greedy", "modified", "scan"):
        s = d[f"rho_{k}"]
        lines.append(f"| {kind} | {algs[k]} | {s.mean():.4f} | {s.min():.4f} | {100 * (s >= 0.9).mean():.1f}% |")
viol = int((~df["ok_half"].astype(bool)).sum())
lines += ["", f"Instâncias que violam a garantia de 1/2: **{viol}** de {len(df)}."]
open(os.path.join(folder, "analysis.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---- figura 1: tempo × n (log-log) com curvas ajustadas
fig, ax = plt.subplots(figsize=(7, 5))
for k, label in algs.items():
    q = df.groupby("n")[f"t_{k}_us"]
    med, lo, hi = q.median(), q.quantile(0.25), q.quantile(0.75)
    ax.errorbar(med.index, med.values, yerr=[med - lo, hi - med], marker="o", capsize=3, label=label)
n_axis = np.array(sorted(df["n"].unique()), dtype=float)
a, b = fits["modified"]
ax.plot(n_axis, a * n_axis * np.log2(n_axis) + b, "k--", lw=1, label="ajuste a·n·log₂n + b")
ax.axhline(16600, color="gray", ls=":", lw=1)
ax.text(n_axis[0], 16600 * 1.15, "quadro de 16,6 ms (60 FPS)", fontsize=8, color="gray")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("n (número de tarefas)"); ax.set_ylabel("tempo (µs), mediana e quartis")
ax.legend(fontsize=8, loc="lower right"); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(folder, "fig_time_vs_n.png"), dpi=200); plt.close(fig)

# ---- figura 2: boxplot de ρ por tipo
kinds = list(df["kind"].unique())
fig, axes = plt.subplots(1, len(kinds), figsize=(4 * len(kinds), 4), sharey=True, squeeze=False)
for ax, kind in zip(axes[0], kinds):
    d = df[df["kind"] == kind]
    ax.boxplot([d[f"rho_{k}"] for k in ("greedy", "modified", "scan")])
    ax.set_xticklabels(["guloso", "modif.", "varredura"])
    ax.axhline(0.5, color="r", ls="--", lw=1); ax.axhline(0.9, color="g", ls=":", lw=1)
    ax.set_title(kind)
axes[0][0].set_ylabel("ρ = SOL/OPT")
fig.tight_layout(); fig.savefig(os.path.join(folder, "fig_ratio_boxplot.png"), dpi=200); plt.close(fig)

# ---- figura 3: ρ médio e mínimo × n
fig, ax = plt.subplots(figsize=(7, 4))
for kind in kinds:
    d = df[df["kind"] == kind].groupby("n")["rho_modified"]
    line, = ax.plot(d.mean().index, d.mean().values, marker="o", label=f"{kind} (média)")
    ax.plot(d.min().index, d.min().values, ls="--", color=line.get_color(), label=f"{kind} (mínimo)")
ax.axhline(0.5, color="r", ls="--", lw=1)
ax.set_xscale("log"); ax.set_xlabel("n"); ax.set_ylabel("ρ do guloso modificado")
ax.legend(fontsize=7); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(folder, "fig_ratio_vs_n.png"), dpi=200); plt.close(fig)
print("Gerado em", folder)
