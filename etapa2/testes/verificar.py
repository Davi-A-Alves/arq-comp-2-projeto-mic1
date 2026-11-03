# Testes extras da etapa 2. Os valores esperados foram calculados a mao.
# Uso (dentro da pasta etapa2): python testes/verificar.py

import subprocess
import sys

passou = 0
total = 0


def confere(nome, obtido, esperado):
    global passou, total
    total = total + 1
    if obtido == esperado:
        passou = passou + 1
        print("ok    " + nome)
    else:
        print("ERRO  " + nome + " obtido=" + str(obtido) + " esperado=" + str(esperado))


def bin32(x):
    return format(x, "032b")


# ---------------- Tarefa 1 (A = 1, B = 0x80000000) ----------------
# (instrucao, sd, n, z, co)  ou (instrucao, "erro")
casos1 = [
    ("00111101", 0x80000002, 1, 0, 0),  # A + B + 1
    ("00111110", 0x7FFFFFFE, 0, 0, 1),  # ~A + B tem vai-um
    ("00001100", 0x00000000, 0, 1, 0),  # A AND B = 0, Z = 1
    ("01110100", 0xC0000000, 1, 0, 0),  # SRA1 de negativo
    ("10110100", 0x00000000, 0, 1, 0),  # SLL8 de B: tudo sai, Z = 1
    ("01111000", 0x00000000, 0, 1, 0),  # SRA1 de 1 vira 0
    ("10111000", 0x00000100, 0, 0, 0),  # SLL8 de A
    ("00011100", 0x80000001, 1, 0, 0),  # A OR B
    ("00100100", 0x7FFFFFFF, 0, 0, 0),  # NOT B
    ("00110000", 0x00000000, 0, 1, 0),  # ENA=0 e ENB=0: zero
    ("00111111", 0x7FFFFFFF, 0, 0, 1),  # ~A + B + 1 = 0x17FFFFFFF
    ("11110000", "erro"),                # SLL8 e SRA1 juntos
]

f = open("testes/prog1.txt", "w")
for caso in casos1:
    f.write(caso[0] + "\n")
f.close()
subprocess.run([sys.executable, "etapa2_tarefa1.py", "testes/prog1.txt", "testes/log1.txt"],
               stdout=subprocess.DEVNULL)

texto = open("testes/log1.txt").read()
ciclos = texto.split("=" * 60 + "\n")[1:]
for i in range(len(casos1)):
    caso = casos1[i]
    bloco = ciclos[i]
    if caso[1] == "erro":
        confere("t1 " + caso[0], "invalid control signals" in bloco, True)
    else:
        campos = {}
        for linha in bloco.split("\n"):
            if " = " in linha:
                campos[linha.split(" = ")[0]] = linha.split(" = ")[1]
        obtido = (campos["sd"], campos["n"], campos["z"], campos["co"])
        esperado = (bin32(caso[1]), str(caso[2]), str(caso[3]), str(caso[4]))
        confere("t1 " + caso[0], obtido, esperado)

# ---------------- Tarefa 2 ----------------
inicial = {"mar": 0, "mdr": 5, "pc": 0x10, "mbr": 0xF0, "sp": 0x100,
           "lv": 0x200, "cpp": 0x300, "tos": 0xFFFFFFFF, "opc": 7, "h": 3}
ordem = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]

f = open("testes/regs2.txt", "w")
for nome in ordem:
    if nome == "mbr":
        f.write("mbr = " + format(inicial[nome], "08b") + "\n")
    else:
        f.write(nome + " = " + bin32(inicial[nome]) + "\n")
f.close()

# (instrucao, registradores que mudam)
casos2 = [
    # h + mdr = 8, escreve em mdr e mar
    ("00111100" + "000000011" + "0000", {"mdr": 8, "mar": 8}),
    # B = mbr (sinal 1): h = 0xFFFFFFF0
    ("00110100" + "100000000" + "0010", {"h": 0xFFFFFFF0}),
    # B = mbru (zeros): lv = 0xF0
    ("00110100" + "000010000" + "0011", {"lv": 0xF0}),
    # h + tos com vai-um: 0xFFFFFFEF em sp e pc
    ("00111100" + "000001100" + "0111", {"sp": 0xFFFFFFEF, "pc": 0xFFFFFFEF}),
    # SLL8 de sp para cpp
    ("10110100" + "000100000" + "0100", {"cpp": 0xFFFFEF00}),
    # SRA1 de cpp para tos
    ("01110100" + "001000000" + "0110", {"tos": 0xFFFFF780}),
    # ENA=0 ENB=0: zero em opc
    ("00110000" + "010000000" + "0000", {"opc": 0}),
    # B = lv, escreve em todos os 9 registradores
    ("00110100" + "111111111" + "0101",
     {"h": 0xF0, "opc": 0xF0, "tos": 0xF0, "cpp": 0xF0, "lv": 0xF0,
      "sp": 0xF0, "pc": 0xF0, "mdr": 0xF0, "mar": 0xF0}),
    # ~h (INVA) para mar
    ("00111010" + "000000001" + "0000", {"mar": 0xFFFFFF0F}),
    # h AND pc para mdr
    ("00001100" + "000000010" + "0001", {"mdr": 0xF0}),
]

f = open("testes/prog2.txt", "w")
for caso in casos2:
    f.write(caso[0] + "\n")
f.close()
subprocess.run([sys.executable, "etapa2_tarefa2.py", "testes/prog2.txt",
                "testes/regs2.txt", "testes/log2.txt"], stdout=subprocess.DEVNULL)

texto = open("testes/log2.txt").read()
ciclos = texto.split("> Registers after instruction\n")[1:]
estado = dict(inicial)
for i in range(len(casos2)):
    for nome in casos2[i][1]:
        estado[nome] = casos2[i][1][nome]
    lidos = {}
    for linha in ciclos[i].split("\n"):
        if " = " in linha and linha.split(" = ")[0] in ordem:
            lidos[linha.split(" = ")[0]] = int(linha.split(" = ")[1], 2)
    confere("t2 instrucao " + str(i + 1), lidos, estado)

print(str(passou) + " de " + str(total) + " passaram")
