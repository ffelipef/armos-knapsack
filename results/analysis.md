# Análise dos experimentos

## Expoente empírico do tempo (regressão log-log da mediana por n)

| algoritmo | expoente | R² | previsto |
|---|---|---|---|
| guloso por razão | 1.02 | 1.000 | ≈ 1 (n log n) |
| guloso modificado | 1.04 | 0.999 | ≈ 1 (n log n) |
| varredura simples | 0.99 | 0.997 | 1 (n) |
| programação dinâmica | 1.97 | 1.000 | ≈ 2 (n·C com C ∝ n) |

## Ajuste dos modelos teóricos (t = a·x + b, x = modelo)

| algoritmo | modelo x | a (µs por unidade) | b (µs) | R² |
|---|---|---|---|---|
| guloso modificado | n·log₂n | 0.02368 | 8.593 | 1.000 |
| guloso por razão | n·log₂n | 0.02412 | 16.9 | 1.000 |
| varredura simples | n | 0.08448 | -5.402 | 0.999 |
| programação dinâmica | n·C | 0.0004794 | -9665 | 0.996 |

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
