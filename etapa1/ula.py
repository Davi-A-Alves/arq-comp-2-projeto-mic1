# Etapa 1 - ULA da Mic-1
# Le instrucoes de 6 bits (F0 F1 ENA ENB INVA INC) e escreve um log.

MASCARA = 0xFFFFFFFF  # deixa o numero com 32 bits

# valores fixos das entradas A e B (os mesmos do exemplo do professor)
A = 0xFFFFFFFF  # -1 em 32 bits
B = 1


def em_binario(valor):
    # transforma um numero em texto com 32 bits, ex: 000...0001
    return format(valor, "032b")


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


arquivo_programa = open("programa_etapa1.txt")
linhas = arquivo_programa.readlines()
arquivo_programa.close()

log = open("log_execucao_etapa1.txt", "w")
log.write("b = " + em_binario(B) + "\n")
log.write("a = " + em_binario(A) + "\n\n")
log.write("Start of Program\n")

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
    log.write("b = " + em_binario(b) + "\n")
    log.write("a = " + em_binario(a) + "\n")
    log.write("s = " + em_binario(s) + "\n")
    log.write("co = " + str(vai_um) + "\n")

log.close()
print("Pronto! Veja o arquivo log_execucao_etapa1.txt")
