# Explicação da Etapa 1 (ULA da Mic-1)

## 1. O que é uma ULA?
ULA = Unidade Lógica e Aritmética. É o "calculadora" do processador.
Ela recebe dois números (A e B) e um código de controle, e devolve o resultado (S) e o vai-um.

## 2. A instrução de 6 bits
Cada linha do arquivo é algo como `111100`. Cada posição é um interruptor:

| Posição | Nome | O que faz |
|---|---|---|
| 1 | F0 | junto com F1, escolhe a operação |
| 2 | F1 | junto com F0, escolhe a operação |
| 3 | ENA | 1 = usa A, 0 = A vira zero |
| 4 | ENB | 1 = usa B, 0 = B vira zero |
| 5 | INVA | 1 = inverte os bits de A |
| 6 | INC | 1 = soma mais 1 ao resultado |

Operação escolhida por F0 F1:

| F0 F1 | Operação |
|---|---|
| 00 | A E B (AND) |
| 01 | A OU B (OR) |
| 10 | NÃO B (NOT) |
| 11 | A + B (soma) |

## 3. Os números A e B
O exemplo da professora usa B = 1 e A = -1.
Em 32 bits, -1 é "32 uns": `11111111111111111111111111111111`.
No código: `A = 0xFFFFFFFF` e `B = 1`.

## 4. Passo a passo do código (`ula.py`)
1. Lê o arquivo `programa_etapa1.txt` e guarda as linhas.
2. `pc` começa em 0 e sobe 1 a cada volta: é o número da linha executada.
3. Pega a linha do `pc` e guarda em `ir` (registrador de instrução).
4. Chama a função `ula(ir, A, B)`, que:
   - separa os 6 bits;
   - se ENA = 0, zera A; se ENB = 0, zera B;
   - se INVA = 1, inverte A;
   - olha F0 F1 e faz AND, OR, NOT ou soma;
   - na soma, calcula `a + b + inc`. Os 32 bits de baixo são S. O bit 33 é o vai-um.
5. Escreve no log: PC, IR, b, a, s, co.
6. Linha vazia ou fim do arquivo: escreve `> Line is empty, EOP.` e para.

## 5. Os 4 exemplos feitos à mão (com `111100` na primeira linha)
- `111100`: soma, A e B ligados. -1 + 1 = 0. S = 0, vai-um = 1.
- `110101`: soma, A desligado (vale 0), INC ligado. 0 + 1 + 1 = 2. S = 2, vai-um = 0.
- `110100`: soma, só B. 0 + 1 = 1. S = 1.
- `011100`: OR de A e B. -1 OR 1 = -1 (32 uns). S = 32 uns.

## 6. Observação sobre a primeira linha
O `programa_etapa1.txt` tem `111110`, mas a saída esperada mostra `111100`.
Com `111110`, INVA = 1 inverte A (-1 vira 0), então S = 0 + 1 = 1.
O código segue o arquivo de entrada.

## 7. Truques de Python usados
- `int(ir[0])`: pega o primeiro caractere do texto e vira número.
- `& 0xFFFFFFFF`: corta o número em 32 bits.
- `~a`: inverte todos os bits.
- `(total >> 32) & 1`: pega o bit 33, que é o vai-um.
- `format(valor, "032b")`: escreve o número em binário com 32 dígitos.
