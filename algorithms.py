"""Algoritmos da mochila 0-1 usados no artigo.

Todas as funções recebem custos c, importâncias p (listas de inteiros) e a
capacidade C, e devolvem o valor da solução (soma das importâncias escolhidas).
Os gulosos e a varredura são Python puro; a programação dinâmica é vetorizada
com numpy (uma operação vetorial por item), o que mantém o tempo O(n·C).
"""
from functools import cmp_to_key

import numpy as np


def _greedy_core(c, p, C):
    """Descarta itens com c_i > C, ordena por p_i/c_i decrescente e insere até o
    primeiro item que não cabe (item de quebra). Devolve (soma gulosa, p_max)."""
    idx = []
    p_max = 0
    for i in range(len(c)):
        if c[i] <= C:
            idx.append(i)
            if p[i] > p_max:
                p_max = p[i]
    idx.sort(key=lambda i: p[i] / c[i], reverse=True)
    total_c = 0
    total_p = 0
    for i in idx:
        if total_c + c[i] > C:
            break
        total_c += c[i]
        total_p += p[i]
    return total_p, p_max


def greedy_ratio(c, p, C):
    """Guloso por razão. Tempo O(n log n)."""
    return _greedy_core(c, p, C)[0]


def greedy_modified(c, p, C):
    """Guloso modificado: melhor entre a soma gulosa e o maior item isolado
    que cabe. 1/2-aproximação (Teorema 2 do artigo). Tempo O(n log n)."""
    greedy_sum, p_max = _greedy_core(c, p, C)
    return max(greedy_sum, p_max)


def scan_arrival(c, p, C):
    """Linha de base: varre os itens na ordem de chegada e insere o que couber."""
    total_c = 0
    total_p = 0
    for i in range(len(c)):
        if total_c + c[i] <= C:
            total_c += c[i]
            total_p += p[i]
    return total_p


def dp_exact(c, p, C):
    """Programação dinâmica exata, só o valor ótimo. Tempo O(n·C), espaço O(C)."""
    dp = np.zeros(C + 1, dtype=np.int64)
    for ci, pi in zip(c, p):
        if ci <= C:
            # a soma à direita é calculada por inteiro antes da escrita (0-1)
            np.maximum(dp[ci:], dp[:C + 1 - ci] + pi, out=dp[ci:])
    return int(dp[C])


def dp_cells_updated(c, C):
    """Número de células atualizadas pela programação dinâmica."""
    return sum(C + 1 - ci for ci in c if ci <= C)


def sort_comparisons(c, p, C):
    """Conta as comparações da ordenação do guloso (execução à parte, fora da
    medição de tempo). Compara razões por multiplicação cruzada."""
    count = 0

    def cmp(i, j):
        nonlocal count
        count += 1
        a = p[i] * c[j]
        b = p[j] * c[i]
        return (b > a) - (b < a)

    idx = [i for i in range(len(c)) if c[i] <= C]
    idx.sort(key=cmp_to_key(cmp))
    return count
