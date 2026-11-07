"""
versao2.py - A4, Versão 2: produtor/consumidor COM semáforos.

Ponderada CC08 - "Do pipeline ao deadlock" (pulseira Tato)
Autor: Bernardo Laurindo Gonzaga  (D1 = 8, D2 = 3, N = 6)

Solução clássica do buffer limitado com três semáforos:
  * vazio  (começa em N): conta posições livres; o produtor espera nele.
  * cheio  (começa em 0): conta posições ocupadas; o consumidor espera nele.
  * mutex  (começa em 1): exclusão mútua no acesso ao buffer e aos índices.

Ordem correta: o produtor faz wait(vazio) e SÓ DEPOIS wait(mutex); o
consumidor faz wait(cheio) e só depois wait(mutex). O time.sleep(0) da
versão 1 continua dentro da região crítica, para mostrar que agora a
interrupção nesse ponto não causa estrago.

Uso:
    python versao2.py        # 3 execuções
    python versao2.py 5      # 5 execuções
"""

import threading
import time

from comum import N, TOTAL_AMOSTRAS, TIMEOUT_TRAVAMENTO, agora, contabilizar, rodar_varias, Resultado


def executar() -> Resultado:
    """Roda uma execução completa da versão com semáforos na ordem correta.

    Parâmetros:
        Nenhum (usa N, TOTAL_AMOSTRAS e TIMEOUT_TRAVAMENTO de comum.py).

    Retorno:
        `Resultado` com consumidas, perdidas, duplicadas e se travou.

    Funcionamento:
        Cria buffer, semáforos e threads; o consumidor usa acquire com
        timeout para detectar travamento (1 s sem receber nada).
    """
    buffer = [None] * N
    vazio = threading.Semaphore(N)
    cheio = threading.Semaphore(0)
    mutex = threading.Semaphore(1)
    estado = {"ocupadas": 0, "produzidas": 0, "travou": False}
    recebidas = []

    def produtor() -> None:
        """Thread do sensor: escreve TOTAL_AMOSTRAS amostras no buffer.

        Parâmetros: nenhum (usa buffer, semáforos e estado da função de fora).
        Retorno: None.
        Funcionamento: para cada amostra faz P(vazio), P(mutex), escreve,
        V(mutex) e V(cheio).
        """
        entrada = 0
        for amostra in range(TOTAL_AMOSTRAS):
            vazio.acquire()                         # P(vazio): espera posição livre
            mutex.acquire()                         # P(mutex): entra na região crítica
            buffer[entrada] = amostra
            entrada = (entrada + 1) % N
            tmp = estado["ocupadas"]
            time.sleep(0)                           # interrupção agora é inofensiva
            estado["ocupadas"] = tmp + 1
            mutex.release()                         # V(mutex)
            cheio.release()                         # V(cheio): avisa que há amostra
            estado["produzidas"] += 1

    def consumidor() -> None:
        """Thread do motor: lê TOTAL_AMOSTRAS amostras do buffer.

        Parâmetros: nenhum (usa buffer, semáforos, estado e recebidas da função de fora).
        Retorno: None. As amostras lidas vão para a lista `recebidas`.
        Funcionamento: para cada amostra faz P(cheio), P(mutex), lê, V(mutex)
        e V(vazio). Se algum P esperar mais de TIMEOUT_TRAVAMENTO segundos,
        marca travamento e encerra.
        """
        saida = 0
        for _ in range(TOTAL_AMOSTRAS):
            if not cheio.acquire(timeout=TIMEOUT_TRAVAMENTO):   # P(cheio)
                estado["travou"] = True
                return
            if not mutex.acquire(timeout=TIMEOUT_TRAVAMENTO):   # P(mutex)
                estado["travou"] = True
                return
            recebidas.append(buffer[saida])
            saida = (saida + 1) % N
            tmp = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = tmp - 1
            mutex.release()                         # V(mutex)
            vazio.release()                         # V(vazio): libera a posição

    inicio = agora()
    tp = threading.Thread(target=produtor, name="sensor", daemon=True)
    tc = threading.Thread(target=consumidor, name="motor", daemon=True)
    tp.start(); tc.start()
    tc.join()
    tp.join(timeout=TIMEOUT_TRAVAMENTO)
    return contabilizar(recebidas, estado["produzidas"], estado["travou"], agora() - inicio)


if __name__ == "__main__":
    rodar_varias("Versão 2 - com semáforos vazio/cheio/mutex", executar)
