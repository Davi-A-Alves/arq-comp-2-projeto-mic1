# Etapa 2 - Tarefa 2: caminho de dados da Mic-1 (registradores + barramentos B e C).
# Instrucao de 21 bits: 8 (ULA) + 9 (barramento C) + 4 (barramento B)
# Uso: python etapa2_tarefa2.py [programa.txt] [registradores.txt]

import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))


def argumento(posicao, padrao):
    # pega o caminho da linha de comando ou usa o arquivo padrao da pasta
    if len(sys.argv) > posicao:
        return sys.argv[posicao]
    return os.path.join(PASTA, padrao)


MASCARA = 0xFFFFFFFF

# ordem de impressao dos registradores
ORDEM = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]

# nomes do barramento B: o indice e o valor do decodificador
NOMES_B = ["mdr", "pc", "mbr", "mbru", "sp", "lv", "cpp", "tos", "opc"]

# nomes do barramento C: do bit 8 (esquerda) ao bit 0 (direita)
NOMES_C = ["h", "opc", "tos", "cpp", "lv", "sp", "pc", "mdr", "mar"]


def em_binario(valor, bits):
    # numero vira texto em binario, separado de 4 em 4
    texto = format(valor, "0" + str(bits) + "b")
    grupos = []
    for i in range(0, bits, 4):
        grupos.append(texto[i:i + 4])
    return " ".join(grupos)


def com_sinal(valor, bits):
    # le o numero em complemento de 2 (bit mais alto = 1 quer dizer negativo)
    if valor >> (bits - 1) == 1:
        return valor - (1 << bits)
    return valor


def nome_operacao(ir, nome_b):
    # nome da operacao, ex: "H + MBR, then SLL8". A da ULA e sempre o H.
    sll8, sra1, f0, f1, ena, enb, inva, inc = [int(bit) for bit in ir]
    a_txt = "H" if ena == 1 else "0"
    if inva == 1:
        a_txt = "NOT " + a_txt
    b_txt = nome_b.upper() if enb == 1 else "0"

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
    # ir tem 8 bits: SLL8 SRA1 F0 F1 ENA ENB INVA INC
    sll8 = int(ir[0])
    sra1 = int(ir[1])
    f0 = int(ir[2])
    f1 = int(ir[3])
    ena = int(ir[4])
    enb = int(ir[5])
    inva = int(ir[6])
    inc = int(ir[7])

    if ena == 0:
        a = 0
    if enb == 0:
        b = 0
    if inva == 1:
        a = ~a & MASCARA

    if f0 == 0 and f1 == 0:
        s = a & b
    elif f0 == 0 and f1 == 1:
        s = a | b
    elif f0 == 1 and f1 == 0:
        s = ~b & MASCARA
    else:
        s = (a + b + inc) & MASCARA

    # deslocador
    sd = s
    if sll8 == 1:
        sd = (s << 8) & MASCARA
    if sra1 == 1:
        sd = (s >> 1) | ((s >> 31) << 31)
    return sd


def decodificador_b(codigo, reg):
    # devolve o valor de 32 bits que vai para a entrada B da ULA
    nome = NOMES_B[codigo]
    if nome == "mbr":
        valor = reg["mbr"]
        if valor >> 7 == 1:
            valor = valor | 0xFFFFFF00  # estende o sinal
        return valor
    if nome == "mbru":
        return reg["mbr"]  # completa com zeros
    return reg[nome]


def seletor_c(bits, reg, valor):
    # escreve o valor em todos os registradores habilitados
    for i in range(9):
        if bits[i] == "1":
            reg[NOMES_C[i]] = valor


def nomes_c_ativos(bits):
    lista = []
    for i in range(9):
        if bits[i] == "1":
            lista.append(NOMES_C[i])
    return ", ".join(lista)


def linha_reg(nome, valor):
    # mbr tem 8 bits, o resto tem 32
    bits = 8 if nome == "mbr" else 32
    return nome.ljust(4) + "= " + em_binario(valor, bits) + "   (" + str(com_sinal(valor, bits)) + ")\n"


def escreve_regs(log, reg):
    for nome in ORDEM:
        log.write(linha_reg(nome, reg[nome]))



# le o programa
arquivo = open(argumento(1, "programa_etapa2_tarefa2.txt"))
linhas = arquivo.readlines()
arquivo.close()

# le o estado inicial dos registradores (formato "nome = valor")
reg = {}
arquivo = open(argumento(2, "registradores_etapa2_tarefa2.txt"))
for linha in arquivo.readlines():
    if "=" in linha:
        partes = linha.split("=")
        reg[partes[0].strip().lower()] = int(partes[1].strip(), 2)
arquivo.close()
inicial = dict(reg)  # copia para comparar no resumo

log = open(os.path.join(PASTA, "log_etapa2_tarefa2.txt"), "w")
for linha in linhas:
    if linha.strip() != "":
        log.write(linha.strip() + "\n")
log.write("\n" + "=" * 60 + "\n")
log.write("> Initial register states\n")
escreve_regs(log, reg)
log.write("\n" + "=" * 60 + "\n")
log.write("Start of program\n")

executadas = 0  # instrucoes que rodaram
erros = 0       # instrucoes com SLL8 e SRA1 juntos

ciclo = 0
while True:
    log.write("=" * 60 + "\n")
    # fim do programa: linha vazia ou acabou o arquivo
    if ciclo >= len(linhas) or linhas[ciclo].strip() == "":
        log.write("Cycle " + str(ciclo + 1) + "\n")
        log.write("No more lines, EOP.\n")
        break

    ir = linhas[ciclo].strip()
    ciclo = ciclo + 1
    log.write("Cycle " + str(ciclo) + "\n")

    if ir[0] == "1" and ir[1] == "1":  # SLL8 e SRA1 nao podem ficar juntos
        log.write("ir = " + ir + "\n")
        log.write("> Error, invalid control signals.\n")
        erros = erros + 1
        continue

    ula_bits = ir[0:8]
    c_bits = ir[8:17]
    b_cod = int(ir[17:21], 2)
    log.write("ir = " + ula_bits + " " + c_bits + " " + ir[17:21] + "\n")
    log.write("op = " + nome_operacao(ula_bits, NOMES_B[b_cod]) + "\n\n")
    log.write("b_bus = " + NOMES_B[b_cod] + "\n")
    log.write("c_bus = " + nomes_c_ativos(c_bits) + "\n\n")

    log.write("> Registers before instruction\n")
    escreve_regs(log, reg)

    # A = H, B = registrador escolhido; resultado vai para o barramento C
    b = decodificador_b(b_cod, reg)
    sd = ula(ula_bits, reg["h"], b)
    seletor_c(c_bits, reg, sd)

    log.write("\n> Registers after instruction\n")
    escreve_regs(log, reg)
    executadas = executadas + 1

log.write("=" * 60 + "\n")
log.write("Summary\n\n")
log.write("Instructions executed = " + str(executadas) + "\n")
log.write("Invalid instructions  = " + str(erros) + "\n\n")
log.write("> Registers changed by the program\n")
mudou = False
for nome in ORDEM:
    if reg[nome] != inicial[nome]:
        log.write(linha_reg(nome, reg[nome]))
        mudou = True
if not mudou:
    log.write("none\n")
log.close()
print("Pronto! Veja o arquivo log_etapa2_tarefa2.txt")
