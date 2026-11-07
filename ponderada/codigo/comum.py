"""
comum.py - Utilitários compartilhados pelas três versões da questão A4.

Ponderada CC08 - "Do pipeline ao deadlock" (pulseira Tato)
Autor: Bernardo Laurindo Gonzaga  (D1 = 8, D2 = 3, N = 6)

Este módulo concentra o que é igual nas três versões do produtor/consumidor:
  * os parâmetros do experimento (N, total de amostras, timeout de travamento);
  * a contabilização de amostras consumidas, perdidas e duplicadas;
  * o laço que executa uma versão várias vezes e imprime a tabela de resultados.

Cada versão (versao1.py, versao2.py, versao3.py) só precisa implementar a
função `executar()`, que roda UMA execução e devolve um objeto `Resultado`.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Callable, List

# --------------------------------------------------------------------------
# Parâmetros do experimento
# --------------------------------------------------------------------------
D1 = 8                      # letras de "Bernardo"
D2 = 3                      # último dígito de 23 (8 + 8 + 7)
N = 3 + (D2 % 5)            # tamanho do buffer circular = 6
TOTAL_AMOSTRAS = 20_000     # amostras geradas pelo produtor em cada execução
TIMEOUT_TRAVAMENTO = 1.0    # segundos sem receber nada => travamento
EXECUCOES_PADRAO = 3        # quantas vezes cada versão roda por padrão


@dataclass
class Resultado:
    """Resumo de uma execução do produtor/consumidor.

    Atributos:
        produzidas: quantas amostras o produtor conseguiu colocar no buffer.
        consumidas: quantas leituras o consumidor fez (conta repetições).
        perdidas:   amostras de 0..TOTAL_AMOSTRAS-1 que nunca chegaram ao
                    consumidor (sobrescritas no buffer ou nunca produzidas
                    por causa de travamento).
        duplicadas: leituras a mais de uma amostra que já tinha sido lida.
        travou:     True se o consumidor ficou TIMEOUT_TRAVAMENTO segundos
                    sem receber nada antes de terminar o trabalho.
        duracao:    tempo total da execução, em segundos.
    """

    produzidas: int
    consumidas: int
    perdidas: int
    duplicadas: int
    travou: bool
    duracao: float


def contabilizar(recebidas: List[int], produzidas: int, travou: bool,
                 duracao: float) -> Resultado:
    """Calcula consumidas, perdidas e duplicadas a partir do que o consumidor leu.

    Parâmetros:
        recebidas:  lista, na ordem de leitura, dos números de amostra que o
                    consumidor tirou do buffer.
        produzidas: quantas amostras o produtor chegou a escrever.
        travou:     se a execução foi encerrada por travamento.
        duracao:    tempo de execução em segundos.

    Retorno:
        Um `Resultado` preenchido.

    Funcionamento:
        Uma amostra é "duplicada" a cada vez que aparece de novo em
        `recebidas`; é "perdida" se o número dela (0..TOTAL_AMOSTRAS-1) não
        aparece nenhuma vez.
    """
    distintas = set(recebidas)
    consumidas = len(recebidas)
    duplicadas = consumidas - len(distintas)
    perdidas = TOTAL_AMOSTRAS - len(distintas & set(range(TOTAL_AMOSTRAS)))
    return Resultado(produzidas, consumidas, perdidas, duplicadas, travou, duracao)


def rodar_varias(nome: str, executar: Callable[[], Resultado]) -> None:
    """Executa uma versão várias vezes e imprime uma tabela de resultados.

    Parâmetros:
        nome:     título impresso no cabeçalho (ex.: "Versão 1 - sem sincronização").
        executar: função sem argumentos que roda uma execução e devolve `Resultado`.

    Retorno:
        Nada. O resultado vai para a saída padrão.

    Funcionamento:
        O número de execuções vem do primeiro argumento da linha de comando
        (padrão: 3). Cada execução é independente: as threads e o buffer são
        recriados dentro de `executar()`.
    """
    execucoes = int(sys.argv[1]) if len(sys.argv) > 1 else EXECUCOES_PADRAO
    print(f"=== {nome} ===")
    print(f"N = {N} posições | {TOTAL_AMOSTRAS} amostras | "
          f"timeout de travamento = {TIMEOUT_TRAVAMENTO:.0f} s | Python {sys.version.split()[0]}")
    print()
    cab = f"{'Exec':>4} | {'Produzidas':>10} | {'Consumidas':>10} | {'Perdidas':>8} | " \
          f"{'Duplicadas':>10} | {'Travou':>6} | {'Tempo (s)':>9}"
    print(cab)
    print("-" * len(cab))
    for i in range(1, execucoes + 1):
        r = executar()
        print(f"{i:>4} | {r.produzidas:>10} | {r.consumidas:>10} | {r.perdidas:>8} | "
              f"{r.duplicadas:>10} | {'SIM' if r.travou else 'não':>6} | {r.duracao:>9.2f}",
              flush=True)


def agora() -> float:
    """Retorna um relógio monotônico em segundos (atalho para time.monotonic)."""
    return time.monotonic()
