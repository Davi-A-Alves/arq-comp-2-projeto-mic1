# Etapa 3 - Tarefa 1: executa microinstrucoes de 23 bits com acesso a memoria.
#
# Uso: python etapa3_tarefa1.py [microinstrucoes.txt] [registradores.txt] [dados.txt]
# Sem argumentos, usa os arquivos de exemplo desta pasta.

import os
import shutil
import sys

import mic1

PASTA = os.path.dirname(os.path.abspath(__file__))


def argumento(posicao, padrao):
    # pega o caminho da linha de comando ou usa o arquivo padrao da pasta
    if len(sys.argv) > posicao:
        return sys.argv[posicao]
    return os.path.join(PASTA, padrao)


caminho_micro = argumento(1, "microinstrucoes_etapa3_tarefa1.txt")
caminho_regs = argumento(2, "registradores_etapa3_tarefa1.txt")
caminho_dados = argumento(3, "dados_etapa3_tarefa1.txt")

# o WRITE regrava o arquivo de dados. Para nao estragar o arquivo de teste,
# o programa trabalha numa copia: dados_saida_etapa3_tarefa1.txt
caminho_saida = os.path.join(PASTA, "dados_saida_etapa3_tarefa1.txt")
shutil.copyfile(caminho_dados, caminho_saida)

arquivo = open(caminho_micro, encoding="utf-8")
linhas = arquivo.readlines()
arquivo.close()

reg = mic1.le_registradores(caminho_regs)
mem = mic1.le_memoria(caminho_saida)
reg_inicial = dict(reg)
mem_inicial = list(mem)

log = open(os.path.join(PASTA, "log_etapa3_tarefa1.txt"), "w", encoding="utf-8")
mic1.escreve_estado_inicial(log, reg, mem)

executadas = 0
erros = 0
ciclo = 0
while True:
    log.write(mic1.SEPARADOR + "\n")
    # fim do programa: linha vazia ou acabou o arquivo
    if ciclo >= len(linhas) or linhas[ciclo].strip() == "":
        log.write("Cycle " + str(ciclo + 1) + "\n")
        log.write("No more lines, EOP.\n")
        break

    ir = linhas[ciclo]
    ciclo = ciclo + 1
    log.write("Cycle " + str(ciclo) + "\n")

    mem_antes = list(mem)
    if mic1.executa_micro(ir, reg, mem, log, caminho_saida):
        executadas = executadas + 1
    else:
        erros = erros + 1

    log.write("\n> Memory after instruction (* = changed)\n" + mic1.ESTRELAS + "\n")
    mic1.escreve_memoria(log, mem, mem_antes)

log.write(mic1.SEPARADOR + "\n")
log.write("Summary\n\n")
log.write("Microinstructions executed = " + str(executadas) + "\n")
log.write("Invalid microinstructions  = " + str(erros) + "\n\n")
log.write("> Registers changed by the program\n")
mudou = False
for nome in mic1.ORDEM:
    if reg[nome] != reg_inicial[nome]:
        log.write(mic1.linha_reg(nome, reg[nome]))
        mudou = True
if not mudou:
    log.write("none\n")
log.write("\n> Memory lines changed by the program\n")
mudou = False
for i in range(len(mem)):
    if mem[i] != mem_inicial[i]:
        log.write("[" + str(i).rjust(2) + "] " + mic1.em_binario(mem[i]) + "   (" + str(mic1.com_sinal(mem[i])) + ")\n")
        mudou = True
if not mudou:
    log.write("none\n")
log.close()
print("Pronto! Veja o arquivo log_etapa3_tarefa1.txt")
