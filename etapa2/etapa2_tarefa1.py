# Etapa 2 - Tarefa 1: ULA de 8 bits de controle com deslocador, N e Z.
# Instrucao: SLL8 SRA1 F0 F1 ENA ENB INVA INC

MASCARA = 0xFFFFFFFF  # deixa o numero com 32 bits

# valores fixos das entradas (os mesmos do exemplo do professor)
A = 0x00000001
B = 0x80000000


def em_binario(valor):
    # numero vira texto com 32 bits
    return format(valor, "032b")


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


arquivo = open("programa_etapa2_tarefa1.txt")
linhas = arquivo.readlines()
arquivo.close()

log = open("log_etapa2_tarefa1.txt", "w")
log.write("b = " + em_binario(B) + "\n")
log.write("a = " + em_binario(A) + "\n\n")
log.write("Start of Program\n")

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
        continue

    a, b, s, sd, n, z, vai_um = ula(ir, A, B)
    log.write("b = " + em_binario(b) + "\n")
    log.write("a = " + em_binario(a) + "\n")
    log.write("s = " + em_binario(s) + "\n")
    log.write("sd = " + em_binario(sd) + "\n")
    log.write("n = " + str(n) + "\n")
    log.write("z = " + str(z) + "\n")
    log.write("co = " + str(vai_um) + "\n")

log.close()
print("Pronto! Veja o arquivo log_etapa2_tarefa1.txt")
