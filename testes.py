"""
Testes da logica (VisionWeCharger.py). Para rodar:  python testes.py
Os valores esperados sao os mesmos que o recarga.c mostra.
"""

import random

import VisionWeCharger as c


def erro(funcao, *args, **kwargs):
    """True se a funcao levantar ValueError."""
    try:
        funcao(*args, **kwargs)
    except ValueError:
        return True
    return False


def teste_tarifa():
    assert c.calcular_tarifa(0) == 0.60 and c.calcular_tarifa(6) == 0.60
    assert c.calcular_tarifa(7) == 1.80 and c.calcular_tarifa(17) == 1.80
    assert c.calcular_tarifa(18) == 1.20 and c.calcular_tarifa(22) == 1.20
    assert c.calcular_tarifa(23) == 1.80


def teste_tabela():
    # simulacao das 21h por 2,5 h: R$ 23,10 (igual ao programa em C)
    linhas, energia, custo, minutos = c.simular_recarga("21", "2,5")
    assert minutos == 150 and len(linhas) == 3
    assert round(energia, 2) == 17.50 and round(custo, 2) == 23.10

    # das 22h por 3,5 h: a tarifa muda tres vezes
    _, _, custo, _ = c.simular_recarga("22", "3,5")
    assert round(custo, 2) == 27.30

    # recarga conectada as 12:10 ate 14:40
    previa = c.preparar_recarga("Cachorro Pro Max", "14:40", agora=(12, 10))
    assert previa.minutos == 150 and round(previa.custo, 2) == 31.50
    assert [(l.hora, l.minuto) for l in previa.linhas] == [(12, 10), (13, 0), (14, 0)]


def teste_validacoes():
    assert c.calcular_minutos(22, 0, 2, 0) == 240            # passa da meia-noite
    assert erro(c.preparar_recarga, "", "14:00", agora=(12, 0))
    assert erro(c.preparar_recarga, "a" * 30, "14:00", agora=(12, 0))
    assert erro(c.preparar_recarga, "X", "12:00", agora=(12, 0))     # 0 minuto
    assert erro(c.preparar_recarga, "X", "23:00", agora=(12, 0))     # mais de 8 h
    for ruim in ["25:00", "12:60", "abc", "12:30:10", ""]:
        assert erro(c.ler_horario, ruim), ruim
    assert erro(c.simular_recarga, "24", "1")
    assert erro(c.simular_recarga, "10", "25")
    assert erro(c.simular_recarga, "10", "0")


def teste_sessoes_e_ordenacao():
    c.resetar()
    for nome, fim in [("A", "14:00"), ("B", "13:00"), ("C", "15:00")]:
        c.confirmar_recarga(c.preparar_recarga(nome, fim, agora=(12, 0)))
    assert [s.id for s in c.sessoes] == [1, 2, 3]
    assert [s.energia for s in c.sessoes] == [14, 7, 21]

    comparacoes = c.bubble_sort(c.CRIT_ENERGIA, False)
    assert [s.energia for s in c.sessoes] == [21, 14, 7] and comparacoes == 3
    assert not c.ordenado_por_id

    # Bubble Sort manual tem que dar o mesmo resultado do sorted()
    campos = {1: lambda s: s.id, 2: lambda s: s.energia,
              3: lambda s: s.custo, 4: lambda s: s.minutos_recarga}
    for criterio, campo in campos.items():
        for crescente in (True, False):
            c.resetar()
            for i in range(30):
                fim = "{:02d}:{:02d}".format(random.randint(14, 19), random.randint(0, 59))
                c.confirmar_recarga(c.preparar_recarga("V%d" % i, fim, agora=(12, random.randint(0, 59))))
            c.bubble_sort(criterio, crescente)
            valores = [campo(s) for s in c.sessoes]
            assert valores == sorted(valores, reverse=not crescente)


def teste_busca():
    c.resetar()
    for nome, fim in [("A", "14:00"), ("B", "13:00"), ("C", "15:00")]:
        c.confirmar_recarga(c.preparar_recarga(nome, fim, agora=(12, 0)))

    c.bubble_sort(c.CRIT_ENERGIA, False)                       # tira o vetor da ordem de id
    sessao, _, reordenou = c.buscar_sessao(2, "binaria")
    assert sessao.id == 2 and reordenou and c.ordenado_por_id
    assert [s.id for s in c.sessoes] == [1, 2, 3]

    sessao, comparacoes, _ = c.buscar_sessao(9, "linear")
    assert sessao is None and comparacoes == 3

    # com 100 sessoes a busca binaria faz no maximo 7 comparacoes
    c.resetar()
    for i in range(100):
        c.confirmar_recarga(c.preparar_recarga("V", "13:00", agora=(12, 0)))
    assert max(c.busca_binaria(i)[1] for i in range(1, 101)) <= 7
    assert erro(c.preparar_recarga, "V", "13:00", agora=(12, 0))   # vetor cheio


def teste_estatisticas_e_finalizar():
    c.resetar()
    assert c.estatisticas() is None
    c.confirmar_recarga(c.preparar_recarga("A", "14:00", agora=(12, 0)))
    c.confirmar_recarga(c.preparar_recarga("B", "13:00", agora=(12, 0)))

    e = c.estatisticas()
    assert e["sessoes"] == 2 and round(e["energia"], 2) == 21
    assert round(e["faturamento"], 2) == 37.80 and round(e["ticket_medio"], 2) == 18.90
    assert e["maior_consumo"] == 14 and e["menor_consumo"] == 7

    c.finalizar_sessao(1)
    assert not c.sessoes[0].ativa
    assert erro(c.finalizar_sessao, 1)           # ja encerrada
    assert erro(c.finalizar_sessao, 99)          # nao existe


def teste_formatacao():
    assert c.formatar_reais(1.2) == "R$1,20"
    assert c.formatar_reais(1234.5) == "R$1.234,50"
    assert c.formatar_horas(150) == "2h30"
    assert c.formatar_hora(870) == "14:30"


if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("teste_")]

    for teste in testes:
        teste()
        print("ok  ", teste.__name__)

    c.resetar()
    print("\n{} testes passaram.".format(len(testes)))
