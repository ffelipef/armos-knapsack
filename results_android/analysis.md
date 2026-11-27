# Análise dos experimentos

## Expoente empírico do tempo (regressão log-log da mediana por n)

| algoritmo | expoente | R² | previsto |
|---|---|---|---|
| guloso por razão | 0.95 | 0.999 | ≈ 1 (n log n) |
| guloso modificado | 1.03 | 1.000 | ≈ 1 (n log n) |
| varredura simples | 0.96 | 0.999 | 1 (n) |
| programação dinâmica | 2.10 | 0.999 | ≈ 2 (n·C com C ∝ n) |

## Ajuste dos modelos teóricos (t = a·x + b, x = modelo)

| algoritmo | modelo x | a (µs por unidade) | b (µs) | R² |
|---|---|---|---|---|
| guloso modificado | n·log₂n | 0.04797 | 49.86 | 0.999 |
| guloso por razão | n·log₂n | 0.05135 | 59.21 | 0.999 |
| varredura simples | n | 0.1384 | 3.634 | 1.000 |
| programação dinâmica | n·C | 0.003114 | -3.023e+04 | 0.990 |

## Razão de aproximação ρ = SOL/OPT

| tipo | algoritmo | média | mínimo | % de instâncias com ρ ≥ 0,9 |
|---|---|---|---|---|
| strong | guloso por razão | 0.9929 | 0.9384 | 100.0% |
| strong | guloso modificado | 0.9929 | 0.9384 | 100.0% |
| strong | varredura simples | 0.9289 | 0.8097 | 70.0% |
| uncorrelated | guloso por razão | 0.9958 | 0.9451 | 100.0% |
| uncorrelated | guloso modificado | 0.9958 | 0.9451 | 100.0% |
| uncorrelated | varredura simples | 0.6395 | 0.3379 | 0.7% |
| weak | guloso por razão | 0.9880 | 0.8721 | 98.7% |
| weak | guloso modificado | 0.9880 | 0.8721 | 98.7% |
| weak | varredura simples | 0.9071 | 0.8257 | 65.3% |

Instâncias que violam a garantia de 1/2: **0** de 450.
