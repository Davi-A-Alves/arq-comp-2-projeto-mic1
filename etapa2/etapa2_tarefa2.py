# Etapa 2 - Tarefa 2: caminho de dados da Mic-1 (registradores + barramentos B e C).
# Instrucao de 21 bits: 8 (ULA) + 9 (barramento C) + 4 (barramento B)
# Uso: python etapa2_tarefa2.py [programa] [registradores] [log]

import sys

MASCARA = 0xFFFFFFFF

# ordem de impressao dos registradores
ORDEM = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]

# nomes do barramento B: o indice e o valor do decodificador
NOMES_B = ["mdr", "pc", "mbr", "mbru", "sp", "lv", "cpp", "tos", "opc"]

# nomes do barramento C: do bit 8 (esquerda) ao bit 0 (direita)
NOMES_C = ["h", "opc", "tos", "cpp", "lv", "sp", "pc", "mdr", "mar"]


def em_binario(valor, bits):
    return format(valor, "0" + str(bits) + "b")


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
    if len(lista) == 0:
        return "none"
    return ", ".join(lista)


def escreve_regs(log, reg):
    for nome in ORDEM:
        if nome == "mbr":
            log.write("mbr = " + em_binario(reg["mbr"], 8) + "\n")
        else:
            log.write(nome + " = " + em_binario(reg[nome], 32) + "\n")


def valida(ir):
    # 21 digitos 0/1, SLL8 e SRA1 nao juntos, decodificador B de 0 a 8
    if len(ir) != 21:
        return False
    for c in ir:
        if c != "0" and c != "1":
            return False
    if ir[0] == "1" and ir[1] == "1":
        return False
    if int(ir[17:21], 2) > 8:
        return False
    return True


nome_programa = "programa_etapa2_tarefa2.txt"
nome_regs = "registradores_etapa2_tarefa2.txt"
nome_log = "log_etapa2_tarefa2.txt"
if len(sys.argv) > 1:
    nome_programa = sys.argv[1]
if len(sys.argv) > 2:
    nome_regs = sys.argv[2]
if len(sys.argv) > 3:
    nome_log = sys.argv[3]

# le o programa
arquivo = open(nome_programa)
linhas = arquivo.readlines()
arquivo.close()

# le o estado inicial dos registradores (formato "nome = valor")
reg = {}
arquivo = open(nome_regs)
for linha in arquivo.readlines():
    if "=" in linha:
        partes = linha.split("=")
        reg[partes[0].strip().lower()] = int(partes[1].strip(), 2)
arquivo.close()

log = open(nome_log, "w")
for linha in linhas:
    if linha.strip() != "":
        log.write(linha.strip() + "\n")
log.write("\n" + "=" * 53 + "\n")
log.write("> Initial register states\n")
escreve_regs(log, reg)
log.write("\n" + "=" * 53 + "\n")
log.write("Start of program\n")

ciclo = 0
while True:
    log.write("=" * 53 + "\n")
    # fim do programa: linha vazia ou acabou o arquivo
    if ciclo >= len(linhas) or linhas[ciclo].strip() == "":
        log.write("Cycle " + str(ciclo) + "\n")
        log.write("No more lines, EOP.\n")
        break

    ir = linhas[ciclo].strip()
    ciclo = ciclo + 1
    log.write("Cycle " + str(ciclo) + "\n")

    if not valida(ir):
        log.write("ir = " + ir + "\n")
        log.write("> Error, invalid control signals.\n")
        continue

    ula_bits = ir[0:8]
    c_bits = ir[8:17]
    b_cod = int(ir[17:21], 2)
    log.write("ir = " + ula_bits + " " + c_bits + " " + ir[17:21] + "\n\n")
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

log.close()
print("Pronto! Veja o arquivo " + nome_log)
