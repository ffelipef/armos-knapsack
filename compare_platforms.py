"""Compara duas execuções (por exemplo, macOS e Android) e gera tabela e gráficos.

Uso: python compare_platforms.py results_mac/results.csv results_android/results.csv \
        --names macOS Android --out comparacao
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("a_csv"); ap.add_argument("b_csv")
ap.add_argument("--names", nargs=2, default=["A", "B"])
ap.add_argument("--out", default="comparacao")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
A, B = (pd.read_csv(args.a_csv), pd.read_csv(args.b_csv))
na, nb = args.names
algs = {"greedy": "guloso por razão", "modified": "guloso modificado",
        "scan": "varredura simples", "dp": "programação dinâmica"}
key = ["kind", "gamma", "n", "rep"]
J = A.merge(B, on=key, suffixes=("_a", "_b"))

# instâncias e valores idênticos?
same = {c: bool((J[c + "_a"] == J[c + "_b"]).all()) for c in ["C", "v_greedy", "v_modified", "v_scan", "v_dp"]}

rows = []
for n, g in J.groupby("n"):
    for k in algs:
        ta, tb = g[f"t_{k}_us_a"].median(), g[f"t_{k}_us_b"].median()
        rows.append({"n": n, "algoritmo": algs[k], f"mediana_{na}_us": ta, f"mediana_{nb}_us": tb, f"razao_{nb}/{na}": tb / ta})
tab = pd.DataFrame(rows)
tab.to_csv(os.path.join(args.out, "comparacao.csv"), index=False)
with open(os.path.join(args.out, "comparacao.md"), "w", encoding="utf-8") as f:
    f.write(f"Valores idênticos entre as plataformas: {same}\n\n")
    f.write(tab.round(2).to_markdown(index=False) if hasattr(tab, "to_markdown") else tab.round(2).to_string(index=False))

# figura: tempo × n, cor = algoritmo, traço = plataforma
fig, ax = plt.subplots(figsize=(7.5, 5))
colors = dict(zip(algs, ["tab:blue", "tab:orange", "tab:green", "tab:red"]))
for k, label in algs.items():
    for D, name, ls, mk in ((A, na, "-", "o"), (B, nb, "--", "s")):
        med = D.groupby("n")[f"t_{k}_us"].median()
        ax.plot(med.index, med.values, ls=ls, marker=mk, color=colors[k], label=f"{label} ({name})")
ax.axhline(16600, color="gray", ls=":", lw=1)
ax.text(52, 16600 * 1.2, "quadro de 16,6 ms (60 FPS)", fontsize=8, color="gray")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("n (número de tarefas)"); ax.set_ylabel("tempo mediano (µs)")
ax.legend(fontsize=7, ncol=2, loc="upper left"); ax.grid(True, which="both", alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig_comparacao_tempo.png"), dpi=200); plt.close(fig)

# figura: razão B/A por algoritmo
fig, ax = plt.subplots(figsize=(7, 4.2))
for k, label in algs.items():
    r = tab[tab["algoritmo"] == label]
    ax.plot(r["n"], r[f"razao_{nb}/{na}"], marker="o", color=colors[k], label=label)
ax.axhline(1, color="k", lw=0.8)
ax.set_xscale("log"); ax.set_xlabel("n"); ax.set_ylabel(f"tempo {nb} ÷ tempo {na}")
ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(args.out, "fig_razao_plataformas.png"), dpi=200); plt.close(fig)
print("Gerado em", args.out, same)
