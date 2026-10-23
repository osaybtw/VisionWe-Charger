"""
VisionWe Charger - logica da estacao de recarga.

Versao em Python do recarga.c (Sprints 3 e 4). Aqui fica so a parte de
dados e calculos. A interface (Interface.py e a pasta telas) usa as
funcoes deste arquivo.
"""

from dataclasses import dataclass
from datetime import datetime

MAX_SESSOES = 100
POTENCIA_CARREGADOR = 7.0        # kW, a estacao tem um unico carregador
TARIFA_COMERCIAL = 1.80          # R$ por kWh fora das faixas especiais
MAX_MINUTOS_SESSAO = 480         # uma recarga dura no maximo 8 horas
MAX_HORAS_SIMULACAO = 24
MAX_NOME = 29

# criterios da ordenacao
CRIT_ID = 1
CRIT_ENERGIA = 2
CRIT_CUSTO = 3
CRIT_TEMPO = 4

# faixas de horario mostradas no cabecalho: (texto, hora inicial, hora final)
FAIXAS = [
    ("00h às 06h", 0, 6),
    ("07h às 17h", 7, 17),
    ("18h às 22h", 18, 22),
    ("23h", 23, 23),
]


@dataclass
class Sessao:
    """Uma sessao de recarga (o struct Sessao do C)."""
    id: int
    veiculo: str
    hora_inicio: int         # minutos desde 00:00
    hora_final: int          # minutos desde 00:00
    minutos_recarga: int
    potencia: float
    energia: float           # kWh
    tarifa: float            # tarifa media: custo / energia
    custo: float
    ativa: bool = True


@dataclass
class LinhaTabela:
    """Uma linha da tabela de recarga (um trecho de ate uma hora)."""
    hora: int
    minuto: int
    duracao: float           # em horas
    tarifa: float
    energia: float
    custo: float


@dataclass
class Previa:
    """Recarga calculada, esperando o usuario confirmar."""
    veiculo: str
    inicio: int              # minutos desde 00:00
    fim: int
    minutos: int
    linhas: list
    energia: float
    custo: float


# vetor de sessoes e o controle de quantas estao ocupadas (len)
sessoes = []

# True quando o vetor esta em ordem crescente de id (a busca binaria precisa disso)
ordenado_por_id = True


def resetar():
    """Apaga todas as sessoes (usado nos testes)."""
    global ordenado_por_id
    sessoes.clear()
    ordenado_por_id = True


# ---------------------------------------------------------------- relogio e tarifa

def hora_atual():
    """Hora e minuto do relogio do computador."""
    agora = datetime.now()
    return agora.hour, agora.minute


def calcular_tarifa(hora):
    """Valor do kWh para uma hora cheia (0 a 23)."""
    if 18 <= hora <= 22:
        return 1.20
    elif 0 <= hora <= 6:
        return 0.60
    else:
        return TARIFA_COMERCIAL


def tabela_faixas():
    """Lista de (texto, tarifa, hora inicial, hora final) para o cabecalho."""
    return [(texto, calcular_tarifa(ini), ini, fim) for texto, ini, fim in FAIXAS]


def proximas_tarifas(hora, quantidade=3):
    """Tarifa das proximas horas: lista de (hora, tarifa)."""
    resultado = []
    for i in range(1, quantidade + 1):
        h = (hora + i) % 24
        resultado.append((h, calcular_tarifa(h)))
    return resultado


# ---------------------------------------------------------------- formatacao

def formatar_reais(valor):
    """1.2 -> 'R$1,20'."""
    centavos = int(valor * 100 + 0.5)
    reais = "{:,}".format(centavos // 100).replace(",", ".")
    return "R${},{:02d}".format(reais, centavos % 100)


def formatar_horas(minutos):
    """150 -> '2h30'."""
    return "{}h{:02d}".format(minutos // 60, minutos % 60)


def formatar_hora(minutos_do_dia):
    """870 -> '14:30'."""
    minutos_do_dia = minutos_do_dia % (24 * 60)
    return "{:02d}:{:02d}".format(minutos_do_dia // 60, minutos_do_dia % 60)


# ---------------------------------------------------------------- leitura e validacao

def ler_horario(texto):
    """Le 'HH:MM' (ou so a hora). Devolve (hora, minuto) ou levanta ValueError."""
    texto = texto.strip()
    erro = ValueError("Horário inválido. Digite no formato HH:MM, de 00:00 até 23:59.")

    if texto == "":
        raise erro

    partes = texto.split(":")
    if len(partes) > 2:
        raise erro

    try:
        hora = int(partes[0])
        minuto = int(partes[1]) if len(partes) == 2 and partes[1] != "" else 0
    except ValueError:
        raise erro

    if hora < 0 or hora > 23 or minuto < 0 or minuto > 59:
        raise erro

    return hora, minuto


def validar_nome(nome):
    nome = " ".join(nome.split())          # tira espacos sobrando, mantem os do meio

    if nome == "":
        raise ValueError("Digite o nome do veículo.")

    if len(nome) > MAX_NOME:
        raise ValueError("O nome do veículo pode ter até {} caracteres.".format(MAX_NOME))

    return nome


def calcular_minutos(hora_ini, minuto_ini, hora_fim, minuto_fim):
    """Duracao da recarga em minutos. Se o fim for menor, passou da meia-noite."""
    minutos = (hora_fim * 60 + minuto_fim) - (hora_ini * 60 + minuto_ini)

    if minutos < 0:
        minutos = minutos + 24 * 60

    if minutos < 1 or minutos > MAX_MINUTOS_SESSAO:
        raise ValueError("A recarga deve durar entre 1 e {} minutos.".format(MAX_MINUTOS_SESSAO))

    return minutos


# ---------------------------------------------------------------- tabela de recarga

def montar_tabela(hora, minuto, minutos):
    """
    Divide a recarga em trechos de ate uma hora do relogio e usa a tarifa de
    cada hora. Devolve (linhas, energia total, custo total).
    """
    linhas = []
    energia_total = 0.0
    custo_total = 0.0

    restante = minutos
    h = hora
    m = minuto

    while restante > 0:

        # ate o fim da hora atual ou ate o fim da recarga
        parte = 60 - m
        if parte > restante:
            parte = restante

        duracao = parte / 60
        tarifa = calcular_tarifa(h)
        energia = POTENCIA_CARREGADOR * duracao
        custo = energia * tarifa

        energia_total = energia_total + energia
        custo_total = custo_total + custo

        linhas.append(LinhaTabela(h, m, duracao, tarifa, energia, custo))

        restante = restante - parte
        m = 0
        h = (h + 1) % 24

    return linhas, energia_total, custo_total


def simular_recarga(texto_hora, texto_horas):
    """
    Simulacao: o usuario informa a hora em que esta (0 a 23) e quantas horas
    quer carregar. Nada e salvo. Devolve (linhas, energia, custo, minutos).
    """
    try:
        hora = int(texto_hora.strip())
    except ValueError:
        raise ValueError("Horário inválido! Digite de 0 a 23.")

    if hora < 0 or hora > 23:
        raise ValueError("Horário inválido! Digite de 0 a 23.")

    try:
        horas = float(texto_horas.strip().replace(",", "."))   # aceita virgula
    except ValueError:
        raise ValueError("Tempo inválido! Digite de 1 minuto até {} horas.".format(MAX_HORAS_SIMULACAO))

    minutos = int(horas * 60 + 0.5)

    if minutos < 1 or horas > MAX_HORAS_SIMULACAO:
        raise ValueError("Tempo inválido! Digite de 1 minuto até {} horas.".format(MAX_HORAS_SIMULACAO))

    linhas, energia, custo = montar_tabela(hora, 0, minutos)
    return linhas, energia, custo, minutos


# ---------------------------------------------------------------- sessoes

def preparar_recarga(nome, texto_hora_final, agora=None):
    """
    Calcula a recarga sem salvar. A hora de inicio e a hora em que o veiculo
    foi conectado (relogio do computador); o usuario so informa a hora final.
    """
    if len(sessoes) >= MAX_SESSOES:
        raise ValueError("Limite de sessões atingido!")

    nome = validar_nome(nome)
    hora_ini, minuto_ini = agora if agora else hora_atual()
    hora_fim, minuto_fim = ler_horario(texto_hora_final)

    minutos = calcular_minutos(hora_ini, minuto_ini, hora_fim, minuto_fim)
    linhas, energia, custo = montar_tabela(hora_ini, minuto_ini, minutos)

    return Previa(
        veiculo=nome,
        inicio=hora_ini * 60 + minuto_ini,
        fim=hora_fim * 60 + minuto_fim,
        minutos=minutos,
        linhas=linhas,
        energia=energia,
        custo=custo,
    )


def confirmar_recarga(previa):
    """Guarda a recarga no vetor de sessoes e devolve a Sessao criada."""
    if len(sessoes) >= MAX_SESSOES:
        raise ValueError("Limite de sessões atingido!")

    nova = Sessao(
        id=len(sessoes) + 1,
        veiculo=previa.veiculo,
        hora_inicio=previa.inicio,
        hora_final=previa.fim,
        minutos_recarga=previa.minutos,
        potencia=POTENCIA_CARREGADOR,
        energia=previa.energia,
        tarifa=previa.custo / previa.energia,
        custo=previa.custo,
    )

    sessoes.append(nova)
    return nova


def finalizar_sessao(id_sessao):
    pos, _ = busca_linear(id_sessao)

    if pos == -1:
        raise ValueError("Sessão não encontrada.")

    if not sessoes[pos].ativa:
        raise ValueError("A sessão {} já está encerrada.".format(id_sessao))

    sessoes[pos].ativa = False
    return sessoes[pos]


# ---------------------------------------------------------------- ordenacao

def valor_criterio(sessao, criterio):
    """Campo usado na ordenacao."""
    if criterio == CRIT_ENERGIA:
        return sessao.energia
    elif criterio == CRIT_CUSTO:
        return sessao.custo
    elif criterio == CRIT_TEMPO:
        return sessao.minutos_recarga
    else:
        return sessao.id


def bubble_sort(criterio, crescente=True):
    """
    Bubble Sort feito a mao (sem sort() nem sorted()).
    Devolve quantas comparacoes foram feitas.
    """
    global ordenado_por_id

    n = len(sessoes)
    comparacoes = 0

    for i in range(n - 1):

        trocou = False

        for j in range(n - 1 - i):

            a = valor_criterio(sessoes[j], criterio)
            b = valor_criterio(sessoes[j + 1], criterio)
            comparacoes += 1

            if crescente:
                trocar = a > b
            else:
                trocar = a < b

            if trocar:
                sessoes[j], sessoes[j + 1] = sessoes[j + 1], sessoes[j]
                trocou = True

        # se nenhuma troca aconteceu, o vetor ja esta ordenado
        if not trocou:
            break

    ordenado_por_id = (criterio == CRIT_ID and crescente)
    return comparacoes


# ---------------------------------------------------------------- busca

def busca_linear(id_sessao):
    """Devolve (posicao ou -1, comparacoes). Complexidade O(n)."""
    comparacoes = 0

    for i in range(len(sessoes)):
        comparacoes += 1

        if sessoes[i].id == id_sessao:
            return i, comparacoes

    return -1, comparacoes


def busca_binaria(id_sessao):
    """
    Devolve (posicao ou -1, comparacoes). Complexidade O(log n).
    O vetor precisa estar ordenado por id.
    """
    inicio = 0
    fim = len(sessoes) - 1
    comparacoes = 0

    while inicio <= fim:

        meio = (inicio + fim) // 2
        comparacoes += 1

        if sessoes[meio].id == id_sessao:
            return meio, comparacoes
        elif sessoes[meio].id < id_sessao:
            inicio = meio + 1
        else:
            fim = meio - 1

    return -1, comparacoes


def buscar_sessao(id_sessao, metodo):
    """
    metodo: 'linear' ou 'binaria'.
    Devolve (sessao ou None, comparacoes, reordenou).
    """
    reordenou = False

    if metodo == "binaria":

        # a busca binaria so funciona com o vetor ordenado por id
        if not ordenado_por_id:
            bubble_sort(CRIT_ID, True)
            reordenou = True

        pos, comparacoes = busca_binaria(id_sessao)
    else:
        pos, comparacoes = busca_linear(id_sessao)

    if pos == -1:
        return None, comparacoes, reordenou

    return sessoes[pos], comparacoes, reordenou


# ---------------------------------------------------------------- estatisticas

def estatisticas():
    """Numeros da estacao, ou None se nao houver sessoes."""
    if len(sessoes) == 0:
        return None

    total_energia = 0.0
    total_faturamento = 0.0
    maior = sessoes[0].energia
    menor = sessoes[0].energia

    for s in sessoes:
        total_energia = total_energia + s.energia
        total_faturamento = total_faturamento + s.custo

        if s.energia > maior:
            maior = s.energia

        if s.energia < menor:
            menor = s.energia

    return {
        "sessoes": len(sessoes),
        "energia": total_energia,
        "faturamento": total_faturamento,
        "ticket_medio": total_faturamento / len(sessoes),
        "maior_consumo": maior,
        "menor_consumo": menor,
    }
