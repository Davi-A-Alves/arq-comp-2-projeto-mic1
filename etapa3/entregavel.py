# Entregavel: le instrucoes IJVM (ILOAD x, DUP, BIPUSH byte), traduz cada uma
# em microinstrucoes de 23 bits e executa na Mic-1 da etapa 3.
#
# Uso: python entregavel.py [instrucoes.txt] [registradores.txt] [dados.txt]
# Sem argumentos, usa os arquivos desta pasta.

import os
import shutil
import sys

import mic1

PASTA = os.path.dirname(os.path.abspath(__file__))

# microinstrucoes fixas: nome -> 23 bits (ULA | C | MEM | B)
MICRO = {
    "H = LV":              "00110100" + "100000000" + "00" + "0101",
    "H = H+1":             "00111001" + "100000000" + "00" + "0000",
    "MAR = H; rd":         "00111000" + "000000001" + "01" + "0000",
    "MAR = SP = SP+1; wr": "00110101" + "000001001" + "10" + "0100",
    "MAR = SP = SP+1":     "00110101" + "000001001" + "00" + "0100",
    "TOS = MDR":           "00110100" + "001000000" + "00" + "0000",
    "MDR = TOS; wr":       "00110100" + "000000010" + "10" + "0111",
    "MDR = TOS = H; wr":   "00111000" + "001000010" + "10" + "0000",
}


def argumento(posicao, padrao):
    # pega o caminho da linha de comando ou usa o arquivo padrao da pasta
    if len(sys.argv) > posicao:
        return sys.argv[posicao]
    return os.path.join(PASTA, padrao)


def traduz(linha):
    # devolve a lista de (nome, 23 bits) da instrucao, ou um texto de erro
    partes = linha.split()
    nome = partes[0].upper()

    if nome == "DUP":
        if len(partes) != 1:
            return "DUP has no argument"
        return [("MAR = SP = SP+1", MICRO["MAR = SP = SP+1"]),
                ("MDR = TOS; wr", MICRO["MDR = TOS; wr"])]

    if nome == "ILOAD":
        if len(partes) != 2 or not partes[1].isdigit():
            return "ILOAD needs a number, ex: ILOAD 1"
        x = int(partes[1])
        lista = [("H = LV", MICRO["H = LV"])]
        for i in range(x):  # um H = H+1 para cada unidade de x
            lista.append(("H = H+1", MICRO["H = H+1"]))
        lista.append(("MAR = H; rd", MICRO["MAR = H; rd"]))
        lista.append(("MAR = SP = SP+1; wr", MICRO["MAR = SP = SP+1; wr"]))
        lista.append(("TOS = MDR", MICRO["TOS = MDR"]))
        return lista

    if nome == "BIPUSH":
        if len(partes) != 2 or len(partes[1]) != 8 or partes[1].count("0") + partes[1].count("1") != 8:
            return "BIPUSH needs a byte of 8 bits, ex: BIPUSH 00110011"
        byte = partes[1]
        # o fetch tem os 8 primeiros bits iguais ao byte e WRITE = READ = 1
        fetch = byte + "000000000" + "11" + "0000"
        return [("MAR = SP = SP+1", MICRO["MAR = SP = SP+1"]),
                ("fetch", fetch),
                ("MDR = TOS = H; wr", MICRO["MDR = TOS = H; wr"])]

    return "unknown instruction"


caminho_instr = argumento(1, "instrucoes.txt")
caminho_regs = argumento(2, "registradores_etapa3_tarefa1.txt")
caminho_dados = argumento(3, "dados_etapa3_tarefa1.txt")

# o WRITE regrava o arquivo de dados. Para nao estragar o arquivo de teste,
# o programa trabalha numa copia: dados_saida_entregavel.txt
caminho_saida = os.path.join(PASTA, "dados_saida_entregavel.txt")
shutil.copyfile(caminho_dados, caminho_saida)

arquivo = open(caminho_instr, encoding="utf-8")
instrucoes = []
for linha in arquivo.readlines():
    if linha.strip() != "":
        instrucoes.append(linha.strip())
arquivo.close()

reg = mic1.le_registradores(caminho_regs)
mem = mic1.le_memoria(caminho_saida)
reg_inicial = dict(reg)
mem_inicial = list(mem)

log = open(os.path.join(PASTA, "log_entregavel.txt"), "w", encoding="utf-8")
log.write("Program\n")
for i in range(len(instrucoes)):
    log.write(str(i + 1) + ". " + instrucoes[i] + "\n")
log.write("\n")
mic1.escreve_estado_inicial(log, reg, mem)

executadas = 0
total_micro = 0
erros = 0
for i in range(len(instrucoes)):
    numero = str(i + 1)
    log.write(mic1.SEPARADOR + "\n")
    log.write("Instruction " + numero + ": " + instrucoes[i] + "\n")

    micros = traduz(instrucoes[i])
    if isinstance(micros, str):
        log.write("> Error, " + micros + ". Instruction ignored.\n")
        erros = erros + 1
        continue

    # mostra a traducao antes de executar
    log.write("Translated to " + str(len(micros)) + " microinstructions:\n")
    for j in range(len(micros)):
        nome, bits = micros[j]
        log.write("  " + numero + "." + str(j + 1) + "  " + nome.ljust(20) + " " + bits[0:8] + " " + bits[8:17] + " " + bits[17:19] + " " + bits[19:23] + "\n")

    executadas = executadas + 1
    mem_antes = list(mem)
    for j in range(len(micros)):
        nome, bits = micros[j]
        log.write(mic1.TRACOS + "\n")
        log.write("Microinstruction " + numero + "." + str(j + 1) + ": " + nome + "\n")
        if not mic1.executa_micro(bits, reg, mem, log, caminho_saida):
            erros = erros + 1
        total_micro = total_micro + 1

    log.write(mic1.TRACOS + "\n")
    log.write("> Memory after instruction " + numero + " (* = changed)\n" + mic1.ESTRELAS + "\n")
    mic1.escreve_memoria(log, mem, mem_antes)

log.write(mic1.SEPARADOR + "\n")
log.write("End of Program\n")
log.write(mic1.SEPARADOR + "\n")
log.write("Summary\n\n")
log.write("Instructions executed      = " + str(executadas) + "\n")
log.write("Microinstructions executed = " + str(total_micro) + "\n")
log.write("Errors                     = " + str(erros) + "\n\n")
log.write("> Final register state (* = changed by the program)\n" + mic1.ESTRELAS + "\n")
mic1.escreve_regs(log, reg, reg_inicial)
log.write("\n> Final memory state (* = changed by the program)\n" + mic1.ESTRELAS + "\n")
mic1.escreve_memoria(log, mem, mem_inicial)
log.write("\nTop of stack: TOS = " + str(mic1.com_sinal(reg["tos"])) + ", SP = " + str(reg["sp"]) + "\n")
log.close()
print("Pronto! Veja o arquivo log_entregavel.txt")
