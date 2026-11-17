# Etapa 1 - ULA da Mic-1
# Le instrucoes de 6 bits (F0 F1 ENA ENB INVA INC) e escreve um log.
# Uso: python ula.py [programa.txt]

import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))


def argumento(posicao, padrao):
    # pega o caminho da linha de comando ou usa o arquivo padrao da pasta
    if len(sys.argv) > posicao:
        return sys.argv[posicao]
    return os.path.join(PASTA, padrao)


MASCARA = 0xFFFFFFFF  # deixa o numero com 32 bits

# valores fixos das entradas A e B (os mesmos do exemplo do professor)
A = 0xFFFFFFFF  # -1 em 32 bits
B = 1


def em_binario(valor):
    # transforma um numero em texto com 32 bits, separado de 4 em 4
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
    # ex: "a  = 1111 ... 1111   (-1)"
    return nome.ljust(3) + "= " + em_binario(valor) + "   (" + str(com_sinal(valor)) + ")\n"


def nome_operacao(ir):
    # monta o nome da operacao a partir dos bits, ex: "A + B + 1"
    f0, f1, ena, enb, inva, inc = [int(bit) for bit in ir]
    a_txt = "A" if ena == 1 else "0"
    if inva == 1:
        a_txt = "NOT " + a_txt
    b_txt = "B" if enb == 1 else "0"

    if f0 == 0 and f1 == 0:
        return a_txt + " AND " + b_txt
    if f0 == 0 and f1 == 1:
        return a_txt + " OR " + b_txt
    if f0 == 1 and f1 == 0:
        return "NOT " + b_txt
    texto = a_txt + " + " + b_txt
    if inc == 1:
        texto = texto + " + 1"
    return texto


def ula(ir, a, b):
    # separa os 6 bits da instrucao
    f0 = int(ir[0])
    f1 = int(ir[1])
    ena = int(ir[2])
    enb = int(ir[3])
    inva = int(ir[4])
    inc = int(ir[5])

    # ENA e ENB: se for 0, a entrada vira 0
    if ena == 0:
        a = 0
    if enb == 0:
        b = 0

    # INVA: inverte todos os bits de A
    if inva == 1:
        a = ~a & MASCARA

    # F0 F1 escolhem a operacao
    vai_um = 0
    if f0 == 0 and f1 == 0:
        s = a & b          # AND
    elif f0 == 0 and f1 == 1:
        s = a | b          # OR
    elif f0 == 1 and f1 == 0:
        s = ~b & MASCARA   # NOT B
    else:
        total = a + b + inc  # soma (INC soma mais 1)
        s = total & MASCARA  # guarda so 32 bits
        vai_um = (total >> 32) & 1  # o que passou de 32 bits e o vai-um

    return a, b, s, vai_um


arquivo_programa = open(argumento(1, "programa_etapa1.txt"))
linhas = arquivo_programa.readlines()
arquivo_programa.close()

log = open(os.path.join(PASTA, "log_execucao_etapa1.txt"), "w")
log.write(linha_valor("b", B))
log.write(linha_valor("a", A) + "\n")
log.write("Start of Program\n")

executadas = 0   # quantas instrucoes rodaram
vai_uns = 0      # quantas vezes deu vai-um
ultimo_s = None  # resultado da ultima instrucao

pc = 0  # contador de programa: qual linha esta sendo executada
while True:
    pc = pc + 1
    log.write("=" * 60 + "\n")
    log.write("Cycle " + str(pc) + "\n\n")
    log.write("PC = " + str(pc) + "\n")

    # se acabaram as linhas ou a linha esta vazia, termina
    if pc > len(linhas) or linhas[pc - 1].strip() == "":
        log.write("> Line is empty, EOP.\n")
        break

    ir = linhas[pc - 1].strip()  # registrador de instrucao
    a, b, s, vai_um = ula(ir, A, B)

    log.write("IR = " + ir + "\n")
    log.write("op = " + nome_operacao(ir) + "\n\n")
    log.write(linha_valor("b", b))
    log.write(linha_valor("a", a))
    log.write(linha_valor("s", s))
    log.write("co = " + str(vai_um) + "\n")

    executadas = executadas + 1
    vai_uns = vai_uns + vai_um
    ultimo_s = s

log.write("=" * 60 + "\n")
log.write("Summary\n\n")
log.write("Instructions executed = " + str(executadas) + "\n")
log.write("Carry outs            = " + str(vai_uns) + "\n")
if ultimo_s is not None:
    log.write("Last result: " + linha_valor("s", ultimo_s))
log.close()
print("Pronto! Veja o arquivo log_execucao_etapa1.txt")
