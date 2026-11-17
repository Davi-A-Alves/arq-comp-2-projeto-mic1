# Etapa 2 - Tarefa 1: ULA de 8 bits de controle com deslocador, N e Z.
# Instrucao: SLL8 SRA1 F0 F1 ENA ENB INVA INC
# Uso: python etapa2_tarefa1.py [programa.txt]

import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))


def argumento(posicao, padrao):
    # pega o caminho da linha de comando ou usa o arquivo padrao da pasta
    if len(sys.argv) > posicao:
        return sys.argv[posicao]
    return os.path.join(PASTA, padrao)


MASCARA = 0xFFFFFFFF  # deixa o numero com 32 bits

# valores fixos das entradas (os mesmos do exemplo do professor)
A = 0x00000001
B = 0x80000000


def em_binario(valor):
    # numero vira texto com 32 bits, separado de 4 em 4
    texto = format(valor, "032b")
    grupos = []
    for i in range(0, 32, 4):
        grupos.append(texto[i:i + 4])
    return " ".join(grupos)


def com_sinal(valor):
    # le o numero em complemento de 2 (bit 31 = 1 quer dizer negativo)
    if valor >> 31 == 1:
        return valor - (1 << 32)
    return valor


def linha_valor(nome, valor):
    # ex: "sd = 1100 ... 0000   (-1073741824)"
    return nome.ljust(3) + "= " + em_binario(valor) + "   (" + str(com_sinal(valor)) + ")\n"


def nome_operacao(ir):
    # nome da operacao da ULA + deslocamento, ex: "A + B, then SLL8"
    sll8, sra1, f0, f1, ena, enb, inva, inc = [int(bit) for bit in ir]
    a_txt = "A" if ena == 1 else "0"
    if inva == 1:
        a_txt = "NOT " + a_txt
    b_txt = "B" if enb == 1 else "0"

    if f0 == 0 and f1 == 0:
        texto = a_txt + " AND " + b_txt
    elif f0 == 0 and f1 == 1:
        texto = a_txt + " OR " + b_txt
    elif f0 == 1 and f1 == 0:
        texto = "NOT " + b_txt
    else:
        texto = a_txt + " + " + b_txt
        if inc == 1:
            texto = texto + " + 1"

    if sll8 == 1:
        texto = texto + ", then SLL8 (shift left 8)"
    if sra1 == 1:
        texto = texto + ", then SRA1 (shift right 1)"
    return texto


def ula(ir, a, b):
    # separa os 8 bits da instrucao
    sll8 = int(ir[0])
    sra1 = int(ir[1])
    f0 = int(ir[2])
    f1 = int(ir[3])
    ena = int(ir[4])
    enb = int(ir[5])
    inva = int(ir[6])
    inc = int(ir[7])

    # ENA e ENB: se for 0, a entrada vira 0
    if ena == 0:
        a = 0
    if enb == 0:
        b = 0

    # INVA inverte os bits de A
    if inva == 1:
        a = ~a & MASCARA

    # F0 F1 escolhem a operacao
    vai_um = 0
    if f0 == 0 and f1 == 0:
        s = a & b
    elif f0 == 0 and f1 == 1:
        s = a | b
    elif f0 == 1 and f1 == 0:
        s = ~b & MASCARA
    else:
        total = a + b + inc
        s = total & MASCARA
        vai_um = (total >> 32) & 1

    # deslocador (depois da ULA)
    sd = s
    if sll8 == 1:
        sd = (s << 8) & MASCARA  # esquerda 8 bits
    if sra1 == 1:
        sinal = s >> 31
        sd = (s >> 1) | (sinal << 31)  # direita 1 bit, mantem o sinal

    n = sd >> 31             # 1 se negativo
    z = 1 if sd == 0 else 0  # 1 se zero
    return a, b, s, sd, n, z, vai_um


arquivo = open(argumento(1, "programa_etapa2_tarefa1.txt"))
linhas = arquivo.readlines()
arquivo.close()

log = open(os.path.join(PASTA, "log_etapa2_tarefa1.txt"), "w")
log.write(linha_valor("b", B))
log.write(linha_valor("a", A) + "\n")
log.write("Start of Program\n")

executadas = 0  # instrucoes que rodaram
erros = 0       # instrucoes com SLL8 e SRA1 juntos
ultimo_sd = None

pc = 0
while True:
    pc = pc + 1
    log.write("=" * 60 + "\n")
    log.write("Cycle " + str(pc) + "\n\n")
    log.write("PC = " + str(pc) + "\n")

    if pc > len(linhas) or linhas[pc - 1].strip() == "":
        log.write("> Line is empty, EOP.\n")
        break

    ir = linhas[pc - 1].strip()
    log.write("IR = " + ir + "\n")
    if ir[0] == "1" and ir[1] == "1":  # SLL8 e SRA1 nao podem ficar juntos
        log.write("> Error, invalid control signals.\n")
        erros = erros + 1
        continue

    a, b, s, sd, n, z, vai_um = ula(ir, A, B)
    log.write("op = " + nome_operacao(ir) + "\n\n")
    log.write(linha_valor("b", b))
    log.write(linha_valor("a", a))
    log.write(linha_valor("s", s))
    log.write(linha_valor("sd", sd))
    log.write("n  = " + str(n) + "\n")
    log.write("z  = " + str(z) + "\n")
    log.write("co = " + str(vai_um) + "\n")

    executadas = executadas + 1
    ultimo_sd = sd

log.write("=" * 60 + "\n")
log.write("Summary\n\n")
log.write("Instructions executed = " + str(executadas) + "\n")
log.write("Invalid instructions  = " + str(erros) + "\n")
if ultimo_sd is not None:
    log.write("Last result: " + linha_valor("sd", ultimo_sd))
log.close()
print("Pronto! Veja o arquivo log_etapa2_tarefa1.txt")
