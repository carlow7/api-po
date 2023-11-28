import streamlit as st
import requests
from io import BytesIO
import re
from PIL import Image
import base64


def create_form():
    st.title("Sistema de cálculo - Solução Gráfica")

    num_forms = st.slider("Quantidade de formulários", min_value=1, max_value=5, value=1)

    forms_data = []
    for i in range(num_forms):
        col1, col2 = st.columns(2)
        with col1:
            st.header(f"Expressão {i + 1}")
            valor_x = st.number_input(f"Digite valor de X para a Expressão {i + 1}", value=0, key=f"valor_x_{i}")
            restricao_nome = st.text_input(f"Digite Nome Restrição para a Expressão {i + 1}", key=f"restricao_nome_{i}")
            expression = st.text_input(f"Digite a Expressão {i + 1} (ex: 2x1 + 3x2 = 12)", key=f"expression_{i}")

        forms_data.append((valor_x, restricao_nome, expression))

    submit_button = st.button("Mostrar resultados", key="submit_button")

    if submit_button:
        payloads = []
        for valor_x, restricao_nome, expression in forms_data:
            if not all([valor_x, restricao_nome, expression]):
                st.warning("Por favor, preencha todos os campos para as expressões.")
                return

            coefficients = re.findall(r'(\d+)\s*x(\d+)', expression)
            constant = int(re.search(r'= (\d+)', expression).group(1))

            if not constant:
                st.warning("Forneça uma expressão válida com um valor constante.")
                return

            qtdx1, qtdx2 = 0, 0
            for coef, var in coefficients:
                if var == '1':
                    qtdx1 = int(coef)
                elif var == '2':
                    qtdx2 = int(coef)

            payload_data = {
                "x1": valor_x,
                "x2": valor_x,
                "qtdx1": qtdx1,
                "qtdx2": qtdx2,
                "max": constant,
                "restricao": '=',
                "nome": restricao_nome,
            }

            payloads.append(payload_data)

        payload = {"dados": payloads}

        print(payload)
        # Enviar a payload para a rota fornecida
        response = requests.post("http://127.0.0.1:5000/operational/graphic", json=payload)

        # Verificar se a solicitação foi bem-sucedida
        if response.status_code == 200:
            st.success("Payload enviado com sucesso!")
            st.balloons()
            # Armazenar os resultados na sessão do Streamlit
            st.session_state.results = response.json()["expressao"]
            # Armazenar a imagem na sessão do Streamlit
            st.session_state.image_data = response.json()["image"]

            # Levar o usuário para a página de resultados
            st.experimental_rerun()

# Página de Resultados
if "results" in st.session_state:
    st.title("Resultados")

    col1, col2 = st.columns(2)

    # Certifique-se de que results é uma lista
    results_list = st.session_state.results if isinstance(st.session_state.results, list) else [st.session_state.results]

    # Mostrar os resultados em duas colunas separadas
    for result in results_list:
        for nome, data in result.items():
            if nome == "nome":
                with col1:
                    st.write(f"### Resultado para {nome}")
                    for linha, valor in data.items():
                        st.write(f"{linha}: {valor}")
            elif nome == "nome_2":
                with col2:
                    st.write(f"### Resultado para {nome}")
                    for linha, valor in data.items():
                        st.write(f"{linha}: {valor}")

    # Adicionar cards para os resultados
    st.title("Resultados em Cards")
    for result in results_list:
        for nome, data in result.items():
            st.write(f"#### Resultado para {nome}")
            for linha, valor in data.items():
                st.info(f"{linha}: {valor}")

    # Converter a imagem de base64 para imagem e exibir
    if "image_data" in st.session_state:
        image_data = st.session_state.image_data
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        st.image(image, caption='Imagem Resultado', use_column_width=True)

# Executar o formulário
create_form()

