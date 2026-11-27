"""Gerador de instâncias sintéticas (três perfis de correlação)."""
import numpy as np

KINDS = ("uncorrelated", "weak", "strong")


def seed_for(base_seed, kind, n, gamma, rep):
    """Semente determinística por configuração e repetição (rep = -1 é o aquecimento)."""
    return np.random.SeedSequence([base_seed, KINDS.index(kind), n, round(gamma * 1000), rep + 1])


def make_instance(kind, n, gamma, R, seed):
    """Devolve (c, p, C).

    c_i ~ U[1, R]. Importância p_i:
      uncorrelated: U[1, R], independente de c_i
      weak:         U[c_i - R/10, c_i + R/10], com mínimo 1
      strong:       c_i + R/10
    Capacidade: C = floor(gamma * soma(c_i)).
    """
    rng = np.random.default_rng(seed)
    c = rng.integers(1, R + 1, size=n)
    d = max(1, R // 10)
    if kind == "uncorrelated":
        p = rng.integers(1, R + 1, size=n)
    elif kind == "weak":
        p = np.maximum(1, rng.integers(c - d, c + d + 1))
    elif kind == "strong":
        p = c + d
    else:
        raise ValueError(f"tipo desconhecido: {kind}")
    C = max(1, int(gamma * int(c.sum())))
    return c.tolist(), p.tolist(), C
