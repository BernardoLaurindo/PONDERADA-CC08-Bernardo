"""
versao3.py - A4, Versão 3: semáforos com a ORDEM TROCADA no produtor.

Ponderada CC08 - "Do pipeline ao deadlock" (pulseira Tato)
Autor: Bernardo Laurindo Gonzaga  (D1 = 8, D2 = 3, N = 6)

Igual à versão 2, exceto que o produtor faz wait(mutex) ANTES de
wait(vazio). Quando o buffer enche, o produtor dorme em `vazio` segurando o
`mutex`; o consumidor, que é o único que poderia liberar `vazio`, fica
bloqueado em `mutex`. Cada um espera pelo outro: deadlock.

O consumidor usa acquire com timeout de 1 s para detectar o travamento e
encerrar; a thread do produtor é daemon e fica presa até o fim do programa
(exatamente o que aconteceria na pulseira, só que lá não haveria timeout).

Uso:
    python versao3.py        # 3 execuções
    python versao3.py 5      # 5 execuções
"""

import threading
import time

from comum import N, TOTAL_AMOSTRAS, TIMEOUT_TRAVAMENTO, agora, contabilizar, rodar_varias, Resultado


def executar() -> Resultado:
    """Roda uma execução completa da versão com a ordem dos semáforos trocada.

    Parâmetros:
        Nenhum (usa N, TOTAL_AMOSTRAS e TIMEOUT_TRAVAMENTO de comum.py).

    Retorno:
        `Resultado` com consumidas, perdidas, duplicadas e se travou.

    Funcionamento:
        Mesma estrutura da versão 2; só o produtor muda a ordem dos P().
    """
    buffer = [None] * N
    vazio = threading.Semaphore(N)
    cheio = threading.Semaphore(0)
    mutex = threading.Semaphore(1)
    estado = {"ocupadas": 0, "produzidas": 0, "travou": False}
    recebidas = []

    def produtor() -> None:
        """Thread do sensor com a ordem errada dos semáforos.

        Parâmetros: nenhum (usa buffer, semáforos e estado da função de fora).
        Retorno: None (na prática fica bloqueada para sempre quando o buffer enche).
        Funcionamento: para cada amostra faz P(mutex) e só depois P(vazio).
        Com o buffer cheio ela dorme em `vazio` segurando o `mutex`.
        """
        entrada = 0
        for amostra in range(TOTAL_AMOSTRAS):
            mutex.acquire()                         # P(mutex) primeiro (aqui está o erro)
            vazio.acquire()                         # P(vazio) segurando o mutex
            buffer[entrada] = amostra
            entrada = (entrada + 1) % N
            tmp = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = tmp + 1
            mutex.release()
            cheio.release()
            estado["produzidas"] += 1

    def consumidor() -> None:
        """Thread do motor, igual à da versão 2.

        Parâmetros: nenhum (usa buffer, semáforos, estado e recebidas da função de fora).
        Retorno: None. As amostras lidas vão para a lista `recebidas`.
        Funcionamento: P(cheio), P(mutex), lê, V(mutex), V(vazio). Se algum P
        esperar mais de TIMEOUT_TRAVAMENTO segundos, marca travamento e encerra.
        """
        saida = 0
        for _ in range(TOTAL_AMOSTRAS):
            if not cheio.acquire(timeout=TIMEOUT_TRAVAMENTO):
                estado["travou"] = True
                return
            if not mutex.acquire(timeout=TIMEOUT_TRAVAMENTO):
                estado["travou"] = True
                return
            recebidas.append(buffer[saida])
            saida = (saida + 1) % N
            tmp = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = tmp - 1
            mutex.release()
            vazio.release()

    inicio = agora()
    tp = threading.Thread(target=produtor, name="sensor", daemon=True)
    tc = threading.Thread(target=consumidor, name="motor", daemon=True)
    tp.start(); tc.start()
    tc.join()
    tp.join(timeout=TIMEOUT_TRAVAMENTO)
    return contabilizar(recebidas, estado["produzidas"], estado["travou"], agora() - inicio)


if __name__ == "__main__":
    rodar_varias("Versão 3 - semáforos com ordem trocada no produtor", executar)
