"""
VisionWe Charger - janela principal.

Para abrir:  python Interface.py
A logica fica em VisionWeCharger.py e cada tela em um arquivo da pasta telas.
"""

import tkinter as tk
from tkinter import ttk

import VisionWeCharger as carregador
from telas import estilo
from telas.recarga import TelaRecarga
from telas.simulacao import TelaSimulacao
from telas.sessoes import TelaSessoes
from telas.consulta import TelaConsulta
from telas.estatisticas import TelaEstatisticas

# (chave, texto do botao, classe da tela)
TELAS = [
    ("recarga", "Nova sessão", TelaRecarga),
    ("simulacao", "Simular recarga", TelaSimulacao),
    ("sessoes", "Sessões", TelaSessoes),
    ("consulta", "Buscar sessão", TelaConsulta),
    ("estatisticas", "Estatísticas", TelaEstatisticas),
]


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("VisionWe Charger")
        self.geometry("1120x800")
        self.minsize(1000, 720)
        self.configure(bg=estilo.COR_FUNDO)
        estilo.configurar(self)

        self._montar_cabecalho()

        corpo = tk.Frame(self, bg=estilo.COR_FUNDO)
        corpo.pack(fill="both", expand=True)

        self._montar_menu(corpo)

        # area onde as telas aparecem, uma em cima da outra
        self.area = tk.Frame(corpo, bg=estilo.COR_FUNDO)
        self.area.pack(side="left", fill="both", expand=True, padx=22, pady=18)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)

        self.telas = {}
        for chave, _, classe in TELAS:
            tela = classe(self.area, self)
            tela.grid(row=0, column=0, sticky="nsew")
            self.telas[chave] = tela

        self.mostrar_tela("recarga")
        self.atualizar_relogio()

    # ------------------------------------------------------------ cabecalho

    def _montar_cabecalho(self):
        cab = tk.Frame(self, bg=estilo.COR_CABECALHO)
        cab.pack(fill="x")
        miolo = tk.Frame(cab, bg=estilo.COR_CABECALHO)
        miolo.pack(fill="x", padx=26, pady=12)

        # nome e hora certa
        esquerda = tk.Frame(miolo, bg=estilo.COR_CABECALHO)
        esquerda.pack(side="left", anchor="n")
        tk.Label(esquerda, text="VisionWe Charger", font=(estilo.FONTE, 20, "bold"),
                 bg=estilo.COR_CABECALHO, fg="white").pack(anchor="w")
        tk.Label(esquerda, text="Estação de recarga  ·  carregador de {:.0f} kW".format(
            carregador.POTENCIA_CARREGADOR), font=estilo.F_PEQUENA,
            bg=estilo.COR_CABECALHO, fg=estilo.COR_CLARO).pack(anchor="w")

        tk.Label(esquerda, text="Hora certa", font=estilo.F_PEQUENA, bg=estilo.COR_CABECALHO,
                 fg=estilo.COR_CLARO).pack(anchor="w", pady=(8, 0))
        self.rotulo_hora = tk.Label(esquerda, text="--:--", font=(estilo.FONTE, 26, "bold"),
                                    bg=estilo.COR_CABECALHO, fg="white")
        self.rotulo_hora.pack(anchor="w")

        # tarifa atual
        meio = tk.Frame(miolo, bg=estilo.COR_CABECALHO)
        meio.pack(side="left", anchor="n", padx=(60, 0))
        tk.Label(meio, text="Tarifa atual", font=estilo.F_PEQUENA, bg=estilo.COR_CABECALHO,
                 fg=estilo.COR_CLARO).pack(anchor="w", pady=(4, 0))
        self.rotulo_tarifa = tk.Label(meio, text="-", font=(estilo.FONTE, 26, "bold"),
                                      bg=estilo.COR_CABECALHO, fg="#5fd9a4")
        self.rotulo_tarifa.pack(anchor="w")
        tk.Label(meio, text="por kWh", font=estilo.F_PEQUENA, bg=estilo.COR_CABECALHO,
                 fg=estilo.COR_CLARO).pack(anchor="w")

        # proximas horas
        proximas = tk.Frame(miolo, bg=estilo.COR_CABECALHO)
        proximas.pack(side="right", anchor="n", padx=(40, 0))
        tk.Label(proximas, text="Próximas horas", font=estilo.F_NEGRITO, bg=estilo.COR_CABECALHO,
                 fg="white").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.linhas_proximas = []
        for i in range(3):
            hora = tk.Label(proximas, text="", font=estilo.F_TEXTO, bg=estilo.COR_CABECALHO,
                            fg=estilo.COR_CLARO, anchor="w", width=6)
            valor = tk.Label(proximas, text="", font=estilo.F_TEXTO, bg=estilo.COR_CABECALHO,
                             fg="white", anchor="e", width=8)
            hora.grid(row=i + 1, column=0, sticky="w")
            valor.grid(row=i + 1, column=1, sticky="e")
            self.linhas_proximas.append((hora, valor))

        # tarifa dinamica por horario
        faixas = tk.Frame(miolo, bg=estilo.COR_CABECALHO)
        faixas.pack(side="right", anchor="n", padx=(40, 0))
        tk.Label(faixas, text="Tarifa dinâmica por horário", font=estilo.F_NEGRITO,
                 bg=estilo.COR_CABECALHO, fg="white").grid(row=0, column=0, columnspan=2,
                                                          sticky="w", pady=(0, 4))
        self.linhas_faixas = []
        for i, (texto, tarifa, ini, fim) in enumerate(carregador.tabela_faixas()):
            nome = tk.Label(faixas, text=texto, font=estilo.F_TEXTO, bg=estilo.COR_CABECALHO,
                            fg=estilo.COR_CLARO, anchor="w", width=12)
            valor = tk.Label(faixas, text=carregador.formatar_reais(tarifa), font=estilo.F_TEXTO,
                             bg=estilo.COR_CABECALHO, fg=estilo.COR_CLARO, anchor="e", width=8)
            nome.grid(row=i + 1, column=0, sticky="w")
            valor.grid(row=i + 1, column=1, sticky="e")
            self.linhas_faixas.append((nome, valor, ini, fim))

    def atualizar_relogio(self):
        """Atualiza hora, tarifa atual e proximas horas. Roda a cada segundo."""
        hora, minuto = carregador.hora_atual()

        self.rotulo_hora.configure(text="{:02d}:{:02d}".format(hora, minuto))
        self.rotulo_tarifa.configure(text=carregador.formatar_reais(carregador.calcular_tarifa(hora)))

        for (rotulo_hora, rotulo_valor), (h, tarifa) in zip(self.linhas_proximas,
                                                            carregador.proximas_tarifas(hora)):
            rotulo_hora.configure(text="{:02d}h".format(h))
            rotulo_valor.configure(text=carregador.formatar_reais(tarifa))

        # destaca a faixa em que estamos
        for nome, valor, ini, fim in self.linhas_faixas:
            atual = ini <= hora <= fim
            cor = "white" if atual else estilo.COR_CLARO
            fonte = estilo.F_NEGRITO if atual else estilo.F_TEXTO
            nome.configure(fg=cor, font=fonte)
            valor.configure(fg=cor, font=fonte)

        self.after(1000, self.atualizar_relogio)

    # ------------------------------------------------------------ menu

    def _montar_menu(self, pai):
        menu = tk.Frame(pai, bg=estilo.COR_CABECALHO, width=210)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)

        self.botoes = {}
        for chave, texto, _ in TELAS:
            botao = ttk.Button(menu, text=texto, style="Menu.TButton",
                               command=lambda c=chave: self.mostrar_tela(c))
            botao.pack(fill="x")
            self.botoes[chave] = botao

        ttk.Button(menu, text="Encerrar", style="Menu.TButton",
                   command=self.destroy).pack(fill="x", side="bottom", pady=(0, 10))

    def mostrar_tela(self, chave):
        """Mostra a tela escolhida e avisa a tela para se atualizar."""
        tela = self.telas[chave]
        tela.tkraise()

        for c, botao in self.botoes.items():
            botao.configure(style="MenuAtivo.TButton" if c == chave else "Menu.TButton")

        if hasattr(tela, "atualizar"):
            tela.atualizar()


if __name__ == "__main__":
    App().mainloop()
