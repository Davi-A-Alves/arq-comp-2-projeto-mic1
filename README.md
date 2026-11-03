# Projeto Mic-1 - Arquitetura de Computadores II (UFPB)

Etapa 1 do projeto: simulação da ULA da Mic-1 em Python.

Grupo:
- Davi Araujo Alves
- Davi Ramos Soares
- Rafael Ramalho Pessoa Albuquerque de Brito

## Como rodar

    python ula.py

O programa lê o `programa_etapa1.txt` (uma instrução de 6 bits por linha: F0 F1 ENA ENB INVA INC) e escreve o resultado de cada linha no `log_execucao_etapa1.txt`.

## Arquivos

- `ula.py`: o código
- `programa_etapa1.txt`: instruções de teste que a professora passou
- `saída_etapa1.txt`: log que a professora passou como resposta esperada
- `log_execucao_etapa1.txt`: log que o nosso código gera

## Observação

Na linha 1 do `programa_etapa1.txt` está `111110`, mas o `saída_etapa1.txt` mostra `IR = 111100` nesse ciclo. Nosso código segue o arquivo de entrada. Trocando a linha 1 para `111100`, o log fica igual ao da professora.
