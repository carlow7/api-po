import json
import re
from backend.app.resources.ContentTypes import ContentTypes
from flask import Blueprint
from flask import Response
from flask import jsonify, request
from backend.service.Methods import Api
from werkzeug.exceptions import HTTPException

api_po: Blueprint = Blueprint(
    'operational', __name__, url_prefix='/operational'
)

api_service = Api()


@api_po.errorhandler(HTTPException)
def handle_exception(error: any) -> Response:
    """
    Function to intercept error and formatter return response
    :param error: Exception error found server
    :return: Response with error formatted
    """
    response: Response = error.get_response()
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": str(error.description)
    })
    response.content_type = ContentTypes.APPLICATION_JSON
    return response


@api_po.route('/graphic', methods=['POST'])
def start_graphic():
    try:
        json_data = request.json

        result = api_service.start(json_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': e}), 404


@api_po.route('/simplex', methods=['POST'])
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


