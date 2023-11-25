from flask import Flask, jsonify, request
from flask_cors import CORS
import re
import ast
import copy

app = Flask(__name__)

CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])


@app.route('/api/PesquisaOperacional/Simplex', methods=['POST'])
def PesquisaOperacional_Simplex():
    try:
        # Informacoes recebidas
        data = request.get_json()
        variaveis = data.get('variaveis')
        informacoes = data.get('informacoes')

        # Organizar as solucoes em formato de matriz
        qtde = (len(variaveis[0]['variaveis']))
        cont = 1
        listsolucoes = []
        for x in range(qtde):
            var = ""
            for y in variaveis:
                var += f" {str(y['variaveis'][x]['valor'])}"
            item = {
                "solucao": cont,
                "var": var.split()
            }
            listsolucoes.append(item)
            cont += 1

        # Criando nova lista incluindo calculo e organizando as informações
        ListaInfo = []
        for x in listsolucoes:
            for y in informacoes:
                nome_res = y['nome_res']
                expressao = y['restricao']
                restricao = expressao
                solucao = x['solucao']
                dados = x['var']

                for i, valor in enumerate(dados, start=1):
                    expressao = expressao.replace(f'x{i}', '*' + valor if f'x{i}' in expressao else valor)

                process_calculo = calcularSimplex(expressao)

                item = {
                    "solucao": f"Solução {solucao}: {dados}",
                    "nome_restricao": nome_res,
                    "restricao": restricao,
                    "expressao": expressao,
                    "calculo": process_calculo,
                }
                ListaInfo.append(item)

        # Organizando resultados de Solução entre true e false
        qtde = len(variaveis)
        cont = 1
        lista = []
        newlist = []
        for l in ListaInfo:
            item = {
                "solucao": l['solucao'],
                "nome_restricao": l["nome_restricao"],
                "resultado": l['calculo']['result']
            }
            lista.append(item)
            if cont == qtde:
                newlist.append(lista)
                lista = []
                cont = 0
            cont += 1
        lista = []
        nomeslist_false = []
        for l in newlist:
            contTotal = 1
            for i in l:
                solucao = i['solucao']
                if (i['resultado']) == False:
                    lista.append(i['nome_restricao'])

                if contTotal == int(qtde):
                    item = {
                        "solucao": solucao,
                        "lista_restricoes": lista
                    }
                    lista = []
                    nomeslist_false.append(item)
                    contTotal = 0
                contTotal += 1

        lista_mensagem = []
        for i in nomeslist_false:
            if (i['lista_restricoes'] == []):
                msg = "Viável - Há disponibilidade em todos os recursos"
            else:
                msg = "Inviável - "
                for x in range(len(i['lista_restricoes'])):
                    if x == 3:
                        msg += f", {i['lista_restricoes'][x]}"
                        if len(i['lista_restricoes']) == 4:
                            msg += " o suficiente"
                    elif x == 2:
                        msg += f", {i['lista_restricoes'][x]}"
                        if len(i['lista_restricoes']) == 3:
                            msg += " o suficiente"
                    elif x == 1:
                        msg += f", {i['lista_restricoes'][x]}"
                        if len(i['lista_restricoes']) == 2:
                            msg += " o suficiente"
                    elif x == 0:
                        msg += f"não há {i['lista_restricoes'][x]}"
                        if len(i['lista_restricoes']) == 1:
                            msg += " o suficiente"
            item = {
                "solucao": i['solucao'],
                "msg": msg
            }
            lista_mensagem.append(item)

        # Organizando todas as informações em uma só lista
        qtde = len(listsolucoes[0]['var'])
        cont = 1
        cont2 = 1  # Identificador de solução
        listafinal = []
        lista = []
        numposition = 0
        for x in ListaInfo:
            lista.append(x)
            if cont == qtde:
                item = {
                    "informacao": lista,
                    "mensagem": lista_mensagem[numposition]
                }
                numposition += 1
                listafinal.append(item)
                cont2 += 1
                cont = 0
                lista = []
            cont += 1

        # Retornando soluções já caluladas em formato de lista
        return jsonify({'Solucoes': listafinal}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Ocorreu um erro no servidor'}), 500


def calcularSimplex(expressao):
    cont = 0
    for x in expressao:
        if x == "<" or x == ">":
            cort = cont
        cont += 1
    expressaocalc = str(expressao)[:cort]
    padrao_multiplicacao = re.findall(r'\d+\*\d+', expressaocalc)
    # Calcular o resultado das multiplicações
    for operacao in padrao_multiplicacao:
        numeros = list(map(int, re.findall(r'\d+', operacao)))
        resultado = numeros[0] * numeros[1]
        expressaocalc = expressaocalc.replace(operacao, str(resultado))
    parte_1 = expressaocalc + str(expressao[cort:])
    parte_2 = str(eval(expressaocalc)) + str(expressao[cort:])
    result = eval(str(eval(expressaocalc)) + str(expressao[cort:]))

    item = {
        "parte1_calc": parte_1,
        "parte2_calc": parte_2,
        "result": result
    }
    return item


# Verificar Opções de lucro
@app.route('/api/PesquisaOperacional/LucroSimplex', methods=['POST'])
def PesquisaOperacional_LucroSimplex():
    try:
        # Informacoes recebidas
        data = request.get_json()
        expressao = data.get('Equacao')
        listaviaveis = data.get('listviaveis')

        dados = []
        solucoes = []
        for x in listaviaveis:
            d = x['informacao'][0]['solucao']
            solucoes.append(d)
            dados.append(d[11:])
        dados = [ast.literal_eval(dado) for dado in dados]

        lista = []
        for x in dados:
            equacao = expressao
            for i, valor in enumerate(x, start=1):
                equacao = equacao.replace(f'x{i}', '*' + valor if f'x{i}' in expressao else valor)
            lista.append(equacao)

        cont = 0
        lista_lucro = []
        for x in lista:
            padrao_multiplicacao = re.findall(r'\d+\*\d+', x)
            # Calcular o resultado das multiplicações
            for operacao in padrao_multiplicacao:
                numeros = list(map(int, re.findall(r'\d+', operacao)))
                resultado = numeros[0] * numeros[1]
                expressaocalc = x.replace(operacao, str(resultado))

            parte_1 = (expressaocalc)
            parte_2 = str(eval(expressaocalc))

            item = {
                "solucao": solucoes[cont],
                "equacao": expressao,
                "expressao": x,
                "parte_1": parte_1,
                "parte_2": parte_2,
            }
            lista_lucro.append(item)
            cont += 1

        # Retornando soluções já caluladas em formato de lista
        return jsonify({'Solucoes': lista_lucro}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Ocorreu um erro no servidor'}), 500


# Verificar Viabilidades Grafico
@app.route('/api/PesquisaOperacional/Grafic', methods=['POST'])
def PesquisaOperacional_Grafic():
    try:
        # Informacoes recebidas
        data = request.get_json()
        qtdevariaveis = data.get('qtdevariaveis')
        lista_restricoes = data.get('informacoes')

        lista_info_prev = []
        for x in lista_restricoes:
            lista_x1 = copy.deepcopy(x)
            lista_x2 = copy.deepcopy(x)
            restricao = x['restricao']

            x1 = []
            x1.append(lista_x1)
            for item in x1:
                item['restricao'] = item['restricao'].replace('x2', '*0')

            x2 = []
            x2.append(lista_x2)
            for item in x2:
                item['restricao'] = item['restricao'].replace('x1', '*0')

            item = {
                "nome_restricao": x['nome_res'],
                "restricao": restricao,
                "expressao_x1": x1,
                "expressao_x2": x2
            }
            lista_info_prev.append(item)

        return jsonify({'Solucoes': "lista_lucro"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Ocorreu um erro no servidor'}), 500










if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    # app.run(host='0.0.0.0', port=5000, ssl_context=(cert_path, key_path))
    app.run(host='0.0.0.0', port=5000)
