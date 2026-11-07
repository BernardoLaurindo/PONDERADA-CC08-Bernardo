"""
versao1.py - A4, Versão 1: produtor/consumidor SEM sincronização.

Ponderada CC08 - "Do pipeline ao deadlock" (pulseira Tato)
Autor: Bernardo Laurindo Gonzaga  (D1 = 8, D2 = 3, N = 6)

A thread do sensor (produtora) gera as amostras 0, 1, 2, ... e a thread do
motor (consumidora) as retira de um buffer circular de N posições. As duas
coordenam-se apenas por um contador compartilhado `ocupadas` e por espera
ocupada (busy waiting). Não tem trava nenhuma.

Para forçar a condição de corrida, cada thread lê o contador, chama
time.sleep(0) (cede a CPU, simulando ser interrompida no pior momento) e só
então grava o novo valor. Assim um incremento ou decremento pode ser perdido,
e o contador deixa de refletir o buffer real: o produtor sobrescreve amostras
ainda não lidas (perdas) e o consumidor relê posições antigas (duplicatas).

Uso:
    python versao1.py        # 3 execuções
    python versao1.py 5      # 5 execuções
"""

import threading
import time

from comum import N, TOTAL_AMOSTRAS, TIMEOUT_TRAVAMENTO, agora, contabilizar, rodar_varias, Resultado


def executar() -> Resultado:
    """Roda uma execução completa da versão sem sincronização.

    Parâmetros:
        Nenhum (usa N, TOTAL_AMOSTRAS e TIMEOUT_TRAVAMENTO de comum.py).

    Retorno:
        `Resultado` com consumidas, perdidas, duplicadas e se travou.

    Funcionamento:
        Cria o buffer, o contador e as duas threads, espera as duas
        terminarem e contabiliza o que o consumidor recebeu.
    """
    buffer = [None] * N
    estado = {"ocupadas": 0, "produzidas": 0, "fim_produtor": False, "travou": False}
    recebidas = []

    def produtor() -> None:
        """Thread do sensor: escreve TOTAL_AMOSTRAS amostras no buffer.

        Parâmetros: nenhum (usa buffer e estado da função de fora).
        Retorno: None.
        Funcionamento: fica em espera ocupada enquanto o contador diz que o
        buffer está cheio. Desiste se o consumidor já marcou travamento.
        """
        entrada = 0
        for amostra in range(TOTAL_AMOSTRAS):
            while estado["ocupadas"] >= N:          # espera ocupada: "buffer cheio"
                if estado["travou"]:
                    return
                time.sleep(0)
            buffer[entrada] = amostra
            entrada = (entrada + 1) % N
            # ---- região crítica (sem proteção) ----
            tmp = estado["ocupadas"]                # lê o contador
            time.sleep(0)                           # é interrompida aqui
            estado["ocupadas"] = tmp + 1            # grava valor possivelmente velho
            # ---------------------------------------
            estado["produzidas"] += 1
        estado["fim_produtor"] = True

    def consumidor() -> None:
        """Thread do motor: retira amostras do buffer até o produtor acabar.

        Parâmetros: nenhum (usa buffer, estado e recebidas da função de fora).
        Retorno: None. As amostras lidas vão para a lista `recebidas`.
        Funcionamento: fica em espera ocupada enquanto o contador diz que o
        buffer está vazio. Se passar TIMEOUT_TRAVAMENTO segundos sem receber
        nada, marca travamento e encerra.
        """
        saida = 0
        ultimo = agora()
        while True:
            while estado["ocupadas"] <= 0:          # espera ocupada: "buffer vazio"
                if estado["fim_produtor"]:
                    return
                if agora() - ultimo > TIMEOUT_TRAVAMENTO:
                    estado["travou"] = True
                    return
                time.sleep(0)
            recebidas.append(buffer[saida])
            saida = (saida + 1) % N
            ultimo = agora()
            # ---- região crítica (sem proteção) ----
            tmp = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = tmp - 1
            # ---------------------------------------

    inicio = agora()
    tp = threading.Thread(target=produtor, name="sensor", daemon=True)
    tc = threading.Thread(target=consumidor, name="motor", daemon=True)
    tp.start(); tc.start()
    tc.join()
    tp.join(timeout=TIMEOUT_TRAVAMENTO)
    return contabilizar(recebidas, estado["produzidas"], estado["travou"], agora() - inicio)


if __name__ == "__main__":
    rodar_varias("Versão 1 - sem sincronização (contador + espera ocupada)", executar)
