# PONDERADA-CC08-Bernardo

**Autor:** Bernardo Laurindo Gonzaga (D1 = 8, D2 = 3, N = 6)

Ponderada de Computação CC08 ("Do pipeline ao deadlock"): arquitetura, pipeline, processos/threads, semáforos e deadlock aplicados à pulseira sensorial Tato, mais a decisão de CTO.

## Estrutura

```
README.md
.gitignore
ponderada/
├── ponderada-tato.md     # Parte A (problema técnico) e Parte B (memorando do CTO)
├── codigo/               # Questão A4: produtor/consumidor com buffer de N = 6
│   ├── comum.py          # parâmetros e contabilização compartilhados
│   ├── versao1.py        # sem sincronização (condição de corrida)
│   ├── versao2.py        # com semáforos vazio/cheio/mutex
│   └── versao3.py        # semáforos com ordem trocada (deadlock)
└── img/                  # prints usados no ponderada-tato.md
```

## Como rodar as três versões da A4

Requisito: Python 3.8 ou mais recente, sem bibliotecas externas. Entre na pasta do código:

```bash
cd ponderada/codigo
```

Cada comando roda a versão **3 vezes** com 20.000 amostras e imprime a tabela de consumidas, perdidas, duplicadas e travamento:

```bash
python3 versao1.py   # Versão 1: sem sincronização
python3 versao2.py   # Versão 2: com semáforos
python3 versao3.py   # Versão 3: ordem trocada (trava; cada execução leva ~2 s)
```

No Windows, use `python` ou `py` no lugar de `python3`. Para outro número de execuções, passe-o como argumento, por exemplo `python3 versao1.py 5`.
