# Alocação gulosa de orçamento de quadro entre Android e desktop

Código e experimentos do artigo da disciplina Análise e Projeto de Algoritmos (CESUPA),
ligado ao projeto ARMOS. O problema é modelado como mochila 0-1: a cada quadro, o ambiente
Android reserva sua parcela do orçamento e o desktop recebe a sobra, que deve ser preenchida
com as tarefas de maior importância total.

Projeto **ARMOS:** https://github.com/ffelipef/armos/

## O que há aqui

| Arquivo | Função |
|---|---|
| `algorithms.py` | guloso por razão, guloso modificado (1/2-aproximação), varredura simples e programação dinâmica exata |
| `generator.py` | gerador de instâncias sintéticas (não correlacionadas, fracamente e fortemente correlacionadas) |
| `run_experiments.py` | roda os experimentos e grava `results/results.csv` e `results/env.json` |
| `analyze.py` | gera `summary.csv`, `analysis.md` e os três gráficos |
| `compare_platforms.py` | compara duas execuções (por exemplo macOS e Android): tabela de razões e gráficos |
| `test_algorithms.py` | testes de corretude (confronto com força bruta e garantia de 1/2) |

## Instalação

Requer Python 3.9 ou superior (testado em 3.9.6 e 3.12.15).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como reproduzir

```bash
python -m unittest                  # 1. testes de corretude
python run_experiments.py --quick   # 2. teste rápido (segundos)
python run_experiments.py           # 3. experimento completo do artigo
python analyze.py results           # 4. tabelas e gráficos
# 5. comparar duas plataformas:
python compare_platforms.py results_mac/results.csv results_android/results.csv --names macOS Android --out comparacao
```

O experimento completo usa n ∈ {50, 100, 500, 1000, 5000}, γ ∈ {0,25; 0,5; 0,75}, os três
tipos de instância e 10 repetições por configuração. A programação dinâmica é a parte
lenta (custo O(n·C)); com n = 5000 cada execução leva segundos. Deixe a máquina ligada na
tomada, com os outros aplicativos fechados, e não use o computador durante a execução.

Opções: `--sizes`, `--gammas`, `--kinds`, `--reps`, `--R` (custo máximo de um item, padrão 1000),
`--seed` (padrão 42) e `--out` (pasta de saída).

## Modelo das instâncias

- Custo: c_i ~ U[1, R].
- Não correlacionada: p_i ~ U[1, R].
- Fracamente correlacionada: p_i ~ U[c_i − R/10, c_i + R/10], com mínimo 1.
- Fortemente correlacionada: p_i = c_i + R/10.
- Capacidade: C = ⌊γ · Σ c_i⌋.
- A semente de cada instância é determinística (semente base, tipo, n, γ e repetição), então
  os resultados são reproduzíveis.

## Medidas

- **Tempo:** `time.perf_counter_ns` em uma chamada por instância, com o coletor de lixo
  desligado e um aquecimento dos algoritmos rápidos antes de cada configuração.
  Os gulosos e a varredura são Python puro; a programação dinâmica é vetorizada com numpy.
- **Razão de aproximação:** ρ = SOL/OPT, com OPT dado pela programação dinâmica.
- **Operações elementares e memória:** medidas na repetição 0 de cada configuração, fora da
  cronometragem (células atualizadas pela PD, comparações da ordenação, pico de memória via `tracemalloc`).
- **Ambiente:** `env.json` registra o processador, a RAM, o sistema e as versões. Copie esses
  dados para a seção de metodologia.

## Limites

Os experimentos rodam sobre o sistema operacional da máquina (por exemplo, macOS), não sobre o
kernel Linux compartilhado do ARMOS. Eles medem os algoritmos, e não o comportamento do
escalonador real.

## Licença

Esta especificação arquitetural e suas implementações de PoC são licenciadas sob a GNU GPLv3. As disposições de copyleft garantem que qualquer integração ou modificação derivada feita por terceiros ou fornecedores da indústria deva permanecer inteiramente de código aberto, preservando o acesso colaborativo da comunidade de desenvolvedores.
