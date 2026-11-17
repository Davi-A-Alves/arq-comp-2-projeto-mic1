# Etapa 3 - Mic-1 com memoria.
# Este arquivo guarda as pecas da maquina (ULA, barramentos, memoria e log).
# Os programas etapa3_tarefa1.py e entregavel.py usam estas funcoes.
#
# Microinstrucao de 23 bits:
#   ULA (8) | barramento C (9) | memoria (2: WRITE READ) | barramento B (4)

MASCARA = 0xFFFFFFFF

# ordem de impressao dos registradores (a mesma do exemplo da professora)
ORDEM = ["mar", "mdr", "pc", "mbr", "sp", "lv", "cpp", "tos", "opc", "h"]

# nomes do barramento B: o indice e o valor do decodificador
NOMES_B = ["mdr", "pc", "mbr", "mbru", "sp", "lv", "cpp", "tos", "opc"]

# nomes do barramento C: do bit 8 (esquerda) ao bit 0 (direita)
NOMES_C = ["h", "opc", "tos", "cpp", "lv", "sp", "pc", "mdr", "mar"]

SEPARADOR = "=" * 60
ESTRELAS = "*" * 31
TRACOS = "-" * 60


# ---------------------------------------------------------------- formatacao

def em_binario(valor, bits=32):
    # numero vira texto em binario, separado de 4 em 4
    texto = format(valor, "0" + str(bits) + "b")
    grupos = []
    for i in range(0, bits, 4):
        grupos.append(texto[i:i + 4])
    return " ".join(grupos)


def com_sinal(valor, bits=32):
    # le o numero em complemento de 2 (bit mais alto = 1 quer dizer negativo)
    if valor >> (bits - 1) == 1:
        return valor - (1 << bits)
    return valor


def linha_reg(nome, valor):
    # ex: "sp  = 0000 ... 1000   (8)". mbr tem 8 bits, o resto tem 32
    bits = 8 if nome == "mbr" else 32
    return nome.ljust(4) + "= " + em_binario(valor, bits) + "   (" + str(com_sinal(valor, bits)) + ")\n"


def escreve_regs(log, reg, antes=None):
    # se receber o estado de antes, marca com * o que mudou
    for nome in ORDEM:
        linha = linha_reg(nome, reg[nome])
        if antes is not None and antes[nome] != reg[nome]:
            linha = linha[:-1] + "   *\n"
        log.write(linha)


def escreve_memoria(log, mem, antes=None):
    # uma linha por endereco; marca com * o que mudou
    for i in range(len(mem)):
        linha = "[" + str(i).rjust(2) + "] " + em_binario(mem[i]) + "   (" + str(com_sinal(mem[i])) + ")"
        if antes is not None and antes[i] != mem[i]:
            linha = linha + "   *"
        log.write(linha + "\n")


# ---------------------------------------------------------------- leitura dos arquivos

def le_registradores(caminho):
    # formato "nome = valor", valor em binario
    reg = {}
    arquivo = open(caminho, encoding="utf-8")
    for linha in arquivo.readlines():
        if "=" in linha:
            partes = linha.split("=")
            reg[partes[0].strip().lower()] = int(partes[1].strip(), 2)
    arquivo.close()
    for nome in ORDEM:  # registrador que faltar no arquivo comeca com 0
        if nome not in reg:
            reg[nome] = 0
    return reg


def le_memoria(caminho):
    # uma palavra de 32 bits por linha; o endereco e o numero da linha
    mem = []
    arquivo = open(caminho, encoding="utf-8")
    for linha in arquivo.readlines():
        if linha.strip() != "":
            mem.append(int(linha.strip(), 2))
    arquivo.close()
    return mem


def grava_memoria(caminho, mem):
    # o WRITE regrava o arquivo de dados
    arquivo = open(caminho, "w", encoding="utf-8")
    for valor in mem:
        arquivo.write(format(valor, "032b") + "\n")
    arquivo.close()


# ---------------------------------------------------------------- pecas da maquina

def ula(ir, a, b):
    # ir tem 8 bits: SLL8 SRA1 F0 F1 ENA ENB INVA INC
    sll8, sra1, f0, f1, ena, enb, inva, inc = [int(bit) for bit in ir]

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

    # deslocador (depois da ULA)
    sd = s
    if sll8 == 1:
        sd = (s << 8) & MASCARA
    if sra1 == 1:
        sd = (s >> 1) | ((s >> 31) << 31)
    return sd


def nome_operacao(ir, nome_b):
    # nome da operacao da ULA, ex: "SP + 1". A entrada A e sempre o H.
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
        # tira as parcelas que sao 0 para ficar mais facil de ler
        partes = []
        if a_txt != "0":
            partes.append(a_txt)
        if b_txt != "0":
            partes.append(b_txt)
        if inc == 1:
            partes.append("1")
        if len(partes) == 0:
            partes.append("0")
        texto = " + ".join(partes)

    if sll8 == 1:
        texto = texto + ", then SLL8"
    if sra1 == 1:
        texto = texto + ", then SRA1"
    return texto


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


def nomes_c_ativos(bits):
    lista = []
    for i in range(9):
        if bits[i] == "1":
            lista.append(NOMES_C[i])
    if len(lista) == 0:
        return "none"
    return ", ".join(lista)


def executa_micro(ir, reg, mem, log, caminho_dados=None):
    # executa uma microinstrucao de 23 bits e escreve tudo no log.
    # devolve False se a microinstrucao foi recusada por erro.
    ir = ir.strip()
    if len(ir) != 23 or ir.count("0") + ir.count("1") != 23:
        log.write("ir = " + ir + "\n")
        log.write("> Error, microinstruction must have 23 bits (0 or 1).\n")
        return False

    ula_bits = ir[0:8]
    c_bits = ir[8:17]
    mem_bits = ir[17:19]
    b_bits = ir[19:23]
    b_cod = int(b_bits, 2)
    write = mem_bits[0] == "1"
    read = mem_bits[1] == "1"
    log.write("ir = " + ula_bits + " " + c_bits + " " + mem_bits + " " + b_bits + "\n")

    antes = dict(reg)

    # caso especial: WRITE e READ juntos = fetch
    if write and read:
        log.write("op = fetch: MBR = " + ula_bits + ", H = MBR (zeros on the left)\n")
        log.write("     ALU and C bus are not used\n\n")
        log.write("> Registers before instruction\n" + ESTRELAS + "\n")
        escreve_regs(log, reg)
        reg["mbr"] = int(ula_bits, 2)
        reg["h"] = reg["mbr"]
        log.write("\n> Registers after instruction (* = changed)\n" + ESTRELAS + "\n")
        escreve_regs(log, reg, antes)
        return True

    if ula_bits[0] == "1" and ula_bits[1] == "1":  # SLL8 e SRA1 nao podem ficar juntos
        log.write("> Error, invalid control signals.\n")
        return False
    if b_cod > 8:
        log.write("> Error, B bus code " + b_bits + " does not exist.\n")
        return False

    nome_b = NOMES_B[b_cod]
    log.write("op = " + nome_operacao(ula_bits, nome_b) + "\n")
    log.write("b = " + nome_b + "\n")
    log.write("c = " + nomes_c_ativos(c_bits) + "\n")
    if write:
        log.write("mem = WRITE (mem[MAR] = MDR)\n")
    elif read:
        log.write("mem = READ (MDR = mem[MAR])\n")
    else:
        log.write("mem = none\n")

    log.write("\n> Registers before instruction\n" + ESTRELAS + "\n")
    escreve_regs(log, reg)

    # 1) ULA: A = H, B = registrador do barramento B
    sd = ula(ula_bits, reg["h"], decodificador_b(b_cod, reg))
    # 2) barramento C: escreve Sd nos registradores habilitados
    for i in range(9):
        if c_bits[i] == "1":
            reg[NOMES_C[i]] = sd
    # 3) memoria: so depois da ULA e do barramento C
    if write or read:
        endereco = reg["mar"]
        if endereco >= len(mem):
            log.write("\n> Error, memory address " + str(endereco) + " out of range, memory operation ignored.\n")
        elif write:
            mem[endereco] = reg["mdr"]
            if caminho_dados is not None:
                grava_memoria(caminho_dados, mem)
            log.write("\n> WRITE: mem[" + str(endereco) + "] = MDR = " + str(com_sinal(reg["mdr"])) + "\n")
        else:
            reg["mdr"] = mem[endereco]
            log.write("\n> READ: MDR = mem[" + str(endereco) + "] = " + str(com_sinal(reg["mdr"])) + "\n")

    log.write("\n> Registers after instruction (* = changed)\n" + ESTRELAS + "\n")
    escreve_regs(log, reg, antes)
    return True


def escreve_estado_inicial(log, reg, mem):
    log.write(SEPARADOR + "\n")
    log.write("Initial memory state\n" + ESTRELAS + "\n")
    escreve_memoria(log, mem)
    log.write(ESTRELAS + "\n")
    log.write("Initial register state\n" + ESTRELAS + "\n")
    escreve_regs(log, reg)
    log.write(SEPARADOR + "\n")
    log.write("Start of Program\n")
