# Arquitetura de Computadores II - Projeto 2026.2 - Etapa 1 (APS 01)

ULA da Mic-1 simulada em Python.

Grupo:
- Davi Araujo Alves
- Davi Ramos Soares
- Rafael Ramalho Pessoa Albuquerque de Brito

## Como executar
python ula.py

O programa le `programa_etapa1.txt` (uma instrucao de 6 bits por linha: F0 F1 ENA ENB INVA INC)
e escreve o log em `log_execucao_etapa1.txt`.

## Arquivos
- ula.py: codigo
- programa_etapa1.txt: instrucoes de teste fornecidas pela professora
- log_execucao_etapa1.txt: log gerado pelo codigo
- saída_etapa1.txt: saida esperada fornecida pela professora

## Observacao
Na linha 1, o programa de teste tem `111110`, mas a saida esperada da professora mostra `IR = 111100`.
O codigo segue o arquivo de entrada. Com `111100` o log fica identico ao esperado.
