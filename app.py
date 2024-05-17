from flask import Flask, render_template, request, jsonify
import csv
from collections import defaultdict

app = Flask(__name__)

# Função para salvar os dados em um arquivo CSV
def salvar_em_csv(dados, nome_arquivo): 
    with open(nome_arquivo, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for linha in dados:
            writer.writerow(linha)

# Função para ler dados do arquivo CSV e contar a ocorrência de cada produto
def contar_produtos(nome_arquivo):
    contagem_produtos = defaultdict(int)
    nome_sku_dict = {}

    # Ler dados do arquivo "bd-produtos.csv" e criar um dicionário com nome e SKU
    with open('bd-produtos.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nome_sku_dict[row['Produto']] = {'nome': row['Nome'], 'sku': row['SKU']}

    # Ler dados do arquivo CSV "etiquetas_e_produtos.csv" e contar os produtos
    with open(nome_arquivo, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            # Ignorar a primeira coluna (etiqueta) e contar os produtos
            for produto in row[1:]:
                if produto:  # Contar apenas se o produto não estiver vazio
                    contagem_produtos[produto] += 1

    # Combinar dados de contagem de produtos com nome e SKU
    contagem_produtos_com_info = {}
    for produto, contagem in contagem_produtos.items():
        if produto in nome_sku_dict:
            nome = nome_sku_dict[produto]['nome']
            sku = nome_sku_dict[produto]['sku']
        else:
            nome = ''
            sku = ''
        contagem_produtos_com_info[produto] = {'nome': nome, 'sku': sku, 'contagem': contagem}

    return contagem_produtos_com_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    produtos = request.json.get('produtos', [])
    dados = [[''] + produtos]  # Usar uma string vazia para a etiqueta
    salvar_em_csv(dados, 'etiquetas_e_produtos.csv')
    return jsonify({'status': 'success'})

@app.route('/remove', methods=['POST'])
def remove():
    produto = request.json.get('produto', '')
    if produto:
        with open('etiquetas_e_produtos.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            linhas = list(reader)

        # Remover uma unidade do produto no arquivo CSV
        for linha in linhas:
            if produto in linha:
                linha.remove(produto)
                break

        # Reescrever o arquivo CSV sem a unidade removida
        with open('etiquetas_e_produtos.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerows(linhas)

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Produto não especificado'})

@app.route('/report')
def report():
    contagem_produtos = contar_produtos('etiquetas_e_produtos.csv')
    return render_template('report.html', contagem_produtos=contagem_produtos)

if __name__ == '__main__':
    app.run(debug=True)
