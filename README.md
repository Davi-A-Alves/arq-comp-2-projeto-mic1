# Projeto Mic-1

Trabalho de Arquitetura de Computadores II (UFPB), da professora Sarah Pontes Madruga.
A ideia é simular a Mic-1 em Python, uma etapa de cada vez.

Grupo:
- Davi Araujo Alves
- Davi Ramos Soares
- Rafael Ramalho Pessoa Albuquerque de Brito

## Pastas

- `etapa1`: a ULA
- `etapa2`: a ULA com deslocador (tarefa 1) e os registradores (tarefa 2)
- `etapa3`: a memória (tarefa 1) e o entregável, que executa ILOAD, DUP e BIPUSH

## Para rodar

Cada programa pode ser rodado de qualquer pasta. Sem argumentos, ele usa os
arquivos de exemplo da própria pasta. Para outro teste, passe os arquivos na
linha de comando, na ordem mostrada. O log sai em `.txt` na pasta do programa.

Etapa 1:

    python etapa1/ula.py [programa.txt]

Etapa 2:

    python etapa2/etapa2_tarefa1.py [programa.txt]
    python etapa2/etapa2_tarefa2.py [programa.txt] [registradores.txt]

Etapa 3:

    python etapa3/etapa3_tarefa1.py [microinstrucoes.txt] [registradores.txt] [dados.txt]
    python etapa3/entregavel.py [instrucoes.txt] [registradores.txt] [dados.txt]

Na etapa 1 e na tarefa 1 da etapa 2, as entradas A e B ficam no começo do `.py`.

## Formato dos arquivos

- Registradores: uma linha `nome = valor` por registrador, valor em binário
  (MBR com 8 bits, os outros com 32).
- Dados: uma palavra de 32 bits por linha. O endereço é o número da linha, a partir de 0.
- Instruções do entregável: uma por linha, por exemplo:

      BIPUSH 00110011
      DUP
      ILOAD 1

O WRITE regrava o arquivo de dados. Para não estragar o arquivo de teste, a
etapa 3 copia os dados para `dados_saida_*.txt` e escreve nessa cópia.

## O que o log mostra

- Cada valor em binário, separado de 4 em 4 bits, com o decimal com sinal ao lado.
- A linha `op` com a operação da ULA, por exemplo `SP + 1` ou `H + TOS + 1`.
- Na etapa 3, `*` marca os registradores e as linhas de memória que mudaram.
- O entregável mostra a tradução de cada instrução em microinstruções antes de executar.
- No fim, um resumo com o que foi executado, os erros e o estado final.

## Microinstruções do entregável

| Microinstrução | ULA | C | MEM | B |
|---|---|---|---|---|
| `H = LV` | 00110100 | 100000000 | 00 | 0101 |
| `H = H+1` | 00111001 | 100000000 | 00 | 0000 |
| `MAR = H; rd` | 00111000 | 000000001 | 01 | 0000 |
| `MAR = SP = SP+1; wr` | 00110101 | 000001001 | 10 | 0100 |
| `MAR = SP = SP+1` | 00110101 | 000001001 | 00 | 0100 |
| `TOS = MDR` | 00110100 | 001000000 | 00 | 0000 |
| `MDR = TOS; wr` | 00110100 | 000000010 | 10 | 0111 |
| `fetch` | byte | 000000000 | 11 | 0000 |
| `MDR = TOS = H; wr` | 00111000 | 001000010 | 10 | 0000 |

O PDF escreve `MAR = H; rd` com o barramento C ligando o H (`100000000`).
Usamos `000000001`, que liga o MAR, porque é o que a microinstrução pede.
