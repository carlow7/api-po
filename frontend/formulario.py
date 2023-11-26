import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64

def create_form():
    st.title("Sistema de cálculo - Solução Gráfica")

    col1, col2 = st.columns(2)

    with col1:
        st.header("Expressão 1")
        x1 = st.number_input("x1", value=0, key="x1_obj1")
        x2 = st.number_input("x2", value=x1, key="x2_obj1")
        qtdx1 = st.number_input("qtdx1", value=0, key="qtdx1_obj1")
        qtdx2 = st.number_input("qtdx2", value=0, key="qtdx2_obj1")
        max_val = st.number_input("max", value=0, key="max_obj1")
        restricao = st.selectbox("Restrição", ["="], key="restricao_obj1")
        nome = st.text_input("Nome", "Nome do produto 1", key="nome_obj1")

    with col2:
        st.header("Expressão 2")
        x1_2 = st.number_input("x1", value=0, key="x1_obj2")
        x2_2 = st.number_input("x2", value=x1_2, key="x2_obj2")
        qtdx1_2 = st.number_input("qtdx1", value=0, key="qtdx1_obj2")
        qtdx2_2 = st.number_input("qtdx2", value=0, key="qtdx2_obj2")
        max_val_2 = st.number_input("max", value=0, key="max_obj2")
        restricao_2 = st.selectbox("Restrição", ["="], key="restricao_obj2")
        nome_2 = st.text_input("Nome", "Nome do produto 2", key="nome_obj2")

    submit_button = st.button("Mostrar resultados", key="submit_button")

    if submit_button:
        # Verificar se todos os campos obrigatórios estão preenchidos
        if not all([x1, x2, qtdx1, qtdx2, max_val, restricao, nome, x1_2, x2_2, qtdx1_2, qtdx2_2, max_val_2, restricao_2, nome_2]):
            st.warning("Por favor, preencha todos os campos.")
            return


        payload = {
            "dados": [
                {
                    "x1": x1,
                    "x2": x2,
                    "qtdx1": qtdx1,
                    "qtdx2": qtdx2,
                    "max": max_val,
                    "restricao": restricao,
                    "nome": nome,
                },
                {
                    "x1": x1_2,
                    "x2": x2_2,
                    "qtdx1": qtdx1_2,
                    "qtdx2": qtdx2_2,
                    "max": max_val_2,
                    "restricao": restricao_2,
                    "nome": nome_2,
                },
            ]
        }


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
