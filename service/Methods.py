import matplotlib.pyplot as plt
import io
import base64


class Api:
    def __init__(self):
        pass

    @staticmethod
    def generate_output_json(treats, create_graph):
        filtered_treats = [item for item in treats if not any('expressao' in value for value in item.values())]

        output_json = {'expressao': filtered_treats, 'image': create_graph}
        return output_json

    def start(self, json):
        calculation = self.collect(json=json)
        treats = self.transform_to_dict_list(calculation)
        create_graph = self.create_graph(treats)

        output_json = self.generate_output_json(treats, create_graph)
        return output_json

    @staticmethod
    def calculation(json):
        qtd1 = json['qtdx1']
        qtd2 = json['qtdx2']
        maxi = json['max']
        restricao = json['restricao']
        nome = json['nome']
        array = []

        x2_linha1 = f"{qtd1}x1 + {qtd2}x2 {restricao} {maxi}"
        x2_linha2 = f"{qtd2}x2 {restricao} {maxi}"
        x2_linha3 = f"x2 {restricao} {maxi}/{qtd2}"
        x2_calculo = maxi / qtd2
        x2_linha4 = f"x2 {restricao} {x2_calculo}"

        x1_linha1 = f"{qtd1}x1 + {qtd2}x2 {restricao} {maxi}"
        x1_linha2 = f"{qtd1}x1 {restricao} {maxi}"
        x1_linha3 = f"x1 {restricao} {maxi}/{qtd1}"
        x1_calculo = maxi / qtd1
        x1_linha4 = f"x1 {restricao} {x1_calculo}"

        x2 = {'nome': nome, 'linha1': x2_linha1, 'linha2': x2_linha2, 'linha3': x2_linha3, 'linha4': x2_linha4,
              'x2': int(x2_calculo)}
        array.append(x2)
        x1 = {'nome': nome, 'linha1': x1_linha1, 'linha2': x1_linha2, 'linha3': x1_linha3, 'linha4': x1_linha4,
              'x1': int(x1_calculo)}
        array.append(x1)

        results = {'nome': nome, "expressao": x1_linha1, 'x2': int(x1_calculo), 'x1': int(x2_calculo)}
        array.append(results)

        return array

    def collect(self, json):
        b = []
        for i in json['dados']:
            a = self.calculation(i)
            b.append(a)
        return b

    @staticmethod
    def transform_to_dict_list(list_of_lists):
        return [{item['nome']: {key: value for key, value in item.items() if key != 'nome'}}
                for sublist in list_of_lists for item in sublist]

    @staticmethod
    def create_graph(data):
        data = data

        for item in data:
            for key, value in item.items():
                if 'expressao' in value:
                    exp = value['expressao']
                    coef_x1 = int(value['x2'])
                    coef_x2 = int(value['x1'])

                    plt.plot([0, coef_x1], [coef_x2, 0], label=exp)

                    plt.text(coef_x1, 0, f'({coef_x1}, 0)', fontsize=8, verticalalignment='bottom')
                    plt.text(0, coef_x2, f'(0, {coef_x2})', fontsize=8, horizontalalignment='right')

        # Set labels and title
        plt.xlabel('X2')
        plt.ylabel('X1')
        plt.title('Grafico de Solução Gráfica')

        # Show legend
        plt.legend()

        # Save the plot to a BytesIO object
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', bbox_inches='tight')
        img_stream.seek(0)

        # Close the figure
        plt.close()

        # Convert the BytesIO object to base64
        img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')

        return img_base64


