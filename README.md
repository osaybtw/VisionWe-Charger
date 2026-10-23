# VISIONWE CHARGER

Estação de recarga de veículos elétricos, com cálculo de energia e custo por horário.
Projeto da Sprint 4 (Python + Tkinter), evolução do simulador feito em C nas Sprints 1 a 3.

## Equipe VisionWe

Arthur de Oliveira Carvalho - RM: 573499

Gabriel Henrique S. de Melo Rodrigues - RM: 573093

Fernando Bonfim Hoefle - RM: 569920

Anna Cecília Guimarães M. Lima de Carvalho - RM: 570955

Disciplina: [preencher] · Turma: [preencher]

## Problema

Quem vai carregar o carro quer saber quanto vai pagar antes de começar, e a estação precisa
guardar as recargas e saber quanto faturou. Como a tarifa muda ao longo do dia, o custo de uma
recarga que passa por horários diferentes não pode ser calculado com um preço único.

## Solução

Uma estação com um carregador de 7 kW que registra as sessões de recarga, calcula a energia
e o custo hora a hora e mostra a tarifa do momento. O carregador pega sozinho a hora em que o
veículo foi conectado, e o usuário só informa a hora final. Antes de iniciar, ele confere os
dados numa tabela. Se algo estiver errado, o veículo é cadastrado de novo.

Fluxo dos dados:

```
usuário → Interface.py (telas) → VisionWeCharger.py (lógica) → tabela por hora → telas
```

## Tarifas

| Horário | Tarifa por kWh |
|---------|----------------|
| 00h às 06h | R$ 0,60 |
| 07h às 17h | R$ 1,80 |
| 18h às 22h | R$ 1,20 |
| 23h | R$ 1,80 |

A recarga é dividida em trechos de até uma hora do relógio, e cada trecho usa a tarifa da sua hora.
Uma recarga das 21h às 23h30, por exemplo, paga R$ 1,20 nas duas primeiras horas e R$ 1,80 nos
últimos 30 minutos.

## Funcionalidades

- **Cabeçalho do carregador**, sempre visível: hora certa, tarifa atual, tarifa por horário e tarifa das próximas horas.
- **Nova sessão**: nome do veículo (aceita espaços), hora de conexão automática, hora final, tabela por hora e confirmação.
- **Simular recarga**: informa a hora em que está e quantas horas quer carregar (qualquer tempo, até 24 h). Nada é salvo.
- **Sessões**: lista as sessões, ordena por ID, energia, custo ou tempo, e finaliza uma sessão.
- **Buscar sessão**: busca por ID, com busca linear ou binária.
- **Estatísticas**: sessões realizadas, energia fornecida, faturamento, ticket médio, maior e menor consumo.

## Estrutura do projeto

```
VisionWe_Charger/
├── Interface.py          janela principal: cabeçalho, menu e troca de telas
├── VisionWeCharger.py    lógica: sessões, tarifa, tabela, busca, ordenação, estatísticas
├── testes.py             testes da lógica

## Algoritmos e complexidade

Mantivemos os algoritmos feitos à mão no C, sem `sort()` nem `sorted()` do Python.

| Operação | Função | Complexidade |
|----------|--------|--------------|
| Cadastrar sessão | `confirmar_recarga()` | O(1) |
| Busca linear | `busca_linear()` | O(n) |
| Busca binária | `busca_binaria()` | O(log n) |
| Ordenação (Bubble Sort) | `bubble_sort()` | O(n²) |
| Estatísticas | `estatisticas()` | O(n) |

A busca binária só funciona com o vetor ordenado por ID. Por isso, se a lista foi ordenada por
outro campo, o sistema ordena por ID antes de buscar. As telas mostram quantas comparações cada
algoritmo fez, o que deixa a diferença entre O(n) e O(log n) fácil de ver.

## Como executar

Precisa do Python 3.8 ou mais novo com Tkinter (já vem no instalador do Python para Windows e macOS).
Não tem nenhuma biblioteca para instalar.

```
python Interface.py
```

Para rodar os testes da lógica:

```
python testes.py
```

No Linux, se aparecer `No module named 'tkinter'`, instale com `sudo apt install python3-tk`.

## Evoluções futuras

- Gravar as sessões em arquivo ou banco de dados, para não perder o histórico ao fechar o programa.
- Trocar o Bubble Sort por Merge Sort ou Quick Sort, que são O(n log n).
- Várias estações e carregadores com potências diferentes.
- Tarifa que varia com a demanda da rede, e não só com o horário.
- Integração com carregadores reais, lendo a energia medida em vez de calcular pela potência.
