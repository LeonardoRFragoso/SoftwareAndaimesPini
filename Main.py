import sqlite3
import PySimpleGUI as sg
import pandas as pd
from datetime import datetime

# Criação do banco de dados SQLite3
conn = sqlite3.connect('pedidos.db')
c = conn.cursor()

# Criação da tabela 'pedidos' no banco de dados SQLite3
c.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        numero_nota TEXT,
        nome TEXT,
        endereco TEXT,
        telefone TEXT,
        ponto_referencia TEXT,
        valor REAL,
        tempo_locacao INTEGER,
        data_pedido TEXT,
        produtos TEXT
    )
''')

class Pedido:
    def __init__(self, numero_nota, nome, endereco, telefone, ponto_referencia, valor, tempo_locacao, produtos, data_pedido=None):
        self.numero_nota = numero_nota
        self.nome = nome
        self.endereco = endereco
        self.telefone = telefone
        self.ponto_referencia = ponto_referencia
        self.valor = valor
        self.tempo_locacao = tempo_locacao
        self.data_pedido = data_pedido
        self.produtos = produtos

class Controller:
    def __init__(self, conn):
        self.conn = conn

    def registrar_pedido(self, pedido):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO pedidos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pedido.numero_nota, pedido.nome, pedido.endereco, pedido.telefone, pedido.ponto_referencia, pedido.valor, pedido.tempo_locacao, pedido.data_pedido, ','.join(pedido.produtos)))
        self.conn.commit()

    def exportar_pedidos(self, data_inicial, data_final):
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM pedidos WHERE data_pedido BETWEEN ? AND ?
        ''', (data_inicial, data_final))
        pedidos = c.fetchall()
        df = pd.DataFrame(pedidos, columns=['numero_nota', 'nome', 'endereco', 'telefone', 'ponto_referencia', 'valor', 'tempo_locacao', 'data_pedido', 'produtos'])
        df['valor'] = df['valor'].apply(lambda x: 'R$ {:.2f}'.format(float(x.replace('R$', '').replace(',', '.'))).replace('.', ',')) # Formata o valor com duas casas decimais e vírgula
        df.to_excel('pedidos.xlsx', index=False)

# Catálogo de produtos
catalogo = {
    'Escora': ['Escoras de 2,80m', 'Escoras de 3,00m', 'Escoras de 3,20m', 'Escoras de 3,50m', 'Escoras de 3,80m', 'Escoras de 4,00m'],
    'Andaime': ['Andaime de 1M', 'Andaime diagonal de 1M', 'Andaime Pranchões 1M', 'Andaime 1,5M', 'Andaime diagonal 1,7M', 'Rodizios', 'Andaimes Rack', 'Sapata Fixa', 'Sapata Regulavel'],
    'Forcados': ['Padrão'],
    'Madeira': ['Grande', 'Média']
}

# Layout da janela
layout = [
    [sg.Text('Andaimes Pini - Controle de pedidos', size=(30,1), justification='center', font=("Helvetica", 25, 'bold'))],
    [
        sg.Column([
            [sg.Text('Dados do Cliente', font=("Helvetica", 12, 'bold'))],
            [sg.Text(''), sg.Text('')],
            [sg.HorizontalSeparator()],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Número da Nota', font=("Helvetica", 12, 'bold')), sg.Input(key='-NUMERO_NOTA-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Nome', font=("Helvetica", 12, 'bold')), sg.Input(key='-NOME-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Endereço', font=("Helvetica", 12, 'bold')), sg.Input(key='-ENDERECO-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Telefone', font=("Helvetica", 12, 'bold')), sg.Input(key='-TELEFONE-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Ponto de Referência', font=("Helvetica", 12, 'bold')), sg.Input(key='-PONTO_REFERENCIA-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Valor Total', font=("Helvetica", 12, 'bold')), sg.Input(key='-VALOR-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Tempo de Locação (dias)', font=("Helvetica", 12, 'bold')), sg.Input(key='-TEMPO_LOCACAO-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Data do Pedido', font=("Helvetica", 12, 'bold')), sg.Input(key='-DATA_PEDIDO-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
        ]),
        sg.VSeperator(),
        sg.Column([
            [sg.Text(''), sg.Text('')],
            [sg.Text(''), sg.Text('')],
            [sg.Text(''), sg.Text('')],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Produtos do Catálogo', font=("Helvetica", 12, 'bold'))],
            [sg.Text(''), sg.Text('')],
            [sg.HorizontalSeparator()],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Produto', font=("Helvetica", 12, 'bold')), sg.Combo(list(catalogo.keys()), key='-PRODUTO-', size=(20,1), enable_events=True)],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Modelo', font=("Helvetica", 12, 'bold')), sg.Combo([], key='-MODELO-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Quantidade de Peças', font=("Helvetica", 12, 'bold')), sg.Input(key='-QUANTIDADE-', size=(20,1))],
            [sg.Text(''), sg.Text('')],
            [sg.Button('Adicionar ao Pedido'), sg.Button('Remover do Pedido')],
            [sg.Text(''), sg.Text('')],
            [sg.HorizontalSeparator()],
            [sg.Text(''), sg.Text('')],
            [sg.Text('Pedido Final', font=("Helvetica", 12, 'bold'))],
            [sg.Text(''), sg.Text('')],
            [sg.Listbox(values=[], key='-PEDIDO-', size=(40,10))],
            [sg.Text(''), sg.Text('')],
            [sg.HorizontalSeparator()],
            [sg.Text(''), sg.Text('')],
            [sg.Button('Registrar Pedido'), sg.Button('Gerar Relatório')]
        ])
    ]
]

controller = Controller(conn)
produtos = []

# Criação da janela
window = sg.Window('Andaimes Pini - Controle de pedidos', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == '-PRODUTO-':
        window['-MODELO-'].update(values=catalogo[values['-PRODUTO-']])
    if event == 'Adicionar ao Pedido':
        produto = values['-PRODUTO-']
        modelo = values['-MODELO-']
        quantidade = values['-QUANTIDADE-']
        produtos.append(f'{produto} {modelo} - {quantidade} peças')
        window['-PEDIDO-'].update(produtos)
    if event == 'Remover do Pedido':
        try:
            produtos.remove(values['-PEDIDO-'][0])
            window['-PEDIDO-'].update(produtos)
        except:
            pass
    if event == 'Registrar Pedido':
        novo_pedido = Pedido(
            numero_nota=values['-NUMERO_NOTA-'],
            nome=values['-NOME-'],
            endereco=values['-ENDERECO-'],
            telefone=values['-TELEFONE-'],
            ponto_referencia=values['-PONTO_REFERENCIA-'],
            valor='R$ {:.2f}'.format(float(values['-VALOR-'].replace('R$', '').replace(',', '.'))).replace('.', ','), # Formata o valor com duas casas decimais e vírgula
            tempo_locacao=int(values['-TEMPO_LOCACAO-']),
            produtos=produtos,
            data_pedido=values['-DATA_PEDIDO-']
        )
        controller.registrar_pedido(novo_pedido)
        window['-NUMERO_NOTA-'].update('')
        window['-NOME-'].update('')
        window['-ENDERECO-'].update('')
        window['-TELEFONE-'].update('')
        window['-PONTO_REFERENCIA-'].update('')
        window['-VALOR-'].update('')
        window['-TEMPO_LOCACAO-'].update('')
        window['-DATA_PEDIDO-'].update('')
        window['-PRODUTO-'].update('')
        window['-MODELO-'].update('')
        window['-QUANTIDADE-'].update('')
        produtos.clear()
        window['-PEDIDO-'].update(produtos)
        sg.popup('Pedido registrado com sucesso!')
    if event == 'Gerar Relatório':
        data_inicial = sg.popup_get_text('Digite a data inicial (formato DD/MM/YYYY):')
        data_final = sg.popup_get_text('Digite a data final (formato DD/MM/YYYY):')
        controller.exportar_pedidos(data_inicial, data_final)
        sg.popup('Relatório gerado com sucesso!')

window.close()
