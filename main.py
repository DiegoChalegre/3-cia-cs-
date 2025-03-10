import streamlit as st
import pandas as pd
import gspread
import json

# Verifica se a variável não é None
if sua_variavel is not None:
    dados= json.loads(sua_variavel)
else:
    print("a variavel está como None and nãopode ser parseada.") 

import os
from oauth2client.service_account import ServiceAccountCredentials

# 🔹 Configuração do Google Sheets usando a variável de ambiente para as credenciais
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Usando a variável de ambiente para obter a chave JSON diretamente
creds_json = os.getenv('GOOGLE_SHEET_CREDENTIALS_JSON')
creds_dict = json.loads(creds_json)  # Carregar como dicionário JSON

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 🔹 Inicializando a lista de conscritos no estado da sessão
if "conscritos" not in st.session_state:
    st.session_state.conscritos = []

# 🔹 Peso para menções
peso_mencao = {
    "Excelente": 10,
    "Muito Bom": 8,
    "Bom": 6,
    "Regular": 4,
    "Insuficiente": 0
}

# 🔹 Função para coletar dados de cada conscrito
def coletar_dados():
    st.subheader("Cadastro de Conscritos")
    nome = st.text_input("Nome do conscrito:")
    if not nome:
        st.warning("Por favor, preencha o nome do conscrito.")
        return

    # Perguntas em layout de colunas
    col1, col2 = st.columns(2)
    with col1:
        obeso = st.radio("É obeso?", ("Sim", "Não"))
        passou_saude = st.radio("Passou na saúde?⛑️", ("Sim", "Não"))
        passou_teste_fisico = st.radio("Passou no teste físico?🏃‍♂️‍➡️", ("Sim", "Não"))
        menção = st.selectbox("Menção na entrevista:", ["Excelente", "Muito Bom", "Bom", "Regular", "Insuficiente"])
        contra_indicado = st.radio("É contra indicado?🚨", ("Sim", "Não"))

    with col2:
        apto_instrucao = st.radio("Apto pela equipe de instrução?", ("Sim", "Não"))
        habilidades = st.number_input("Habilidades (quantidade):", min_value=0, max_value=10)
        habilidades_descricao = st.text_area("Quais habilidades? (Descreva)")

    # Verificação de reprovação
    status = "Apto"
    if obeso == "Sim":
        status = "Inapto - Obesidade"
    elif passou_saude == "Não":
        status = "Inapto - Saúde"
    elif passou_teste_fisico == "Não":
        status = "Inapto - Teste Físico"
    elif contra_indicado == "Sim":
        status = "Inapto - Contraindicado"
    elif apto_instrucao == "Não":
        status = "Inapto - Não Apto pela Instrução"

    # Se o conscrito não tiver habilidades, colocar "-"
    habilidades_str = str(habilidades) if habilidades > 0 else "-"
    habilidades_descricao = habilidades_descricao if habilidades > 0 else "-"

    # Verificar se o conscrito já foi registrado para evitar duplicações
    conscritos_existentes = [c[1] for c in st.session_state.conscritos]
    if nome in conscritos_existentes:
        st.warning(f"O conscrito {nome} já foi registrado.")
        return

    # Criar botão "Gravar"
    gravar = st.button("🦅Gravar🦅")

    if gravar:
        # Salvar no Google Sheets com 6 colunas (sem "Nr")
        sheet.append_row([nome, menção, habilidades_str, habilidades_descricao, peso_mencao[menção], status])

        # Atualizar a lista de conscritos na sessão
        st.session_state.conscritos.append((nome, menção, habilidades_str, habilidades_descricao, peso_mencao[menção], status))

        # Mostrar o status do conscrito
        st.success(f"✅ Dados de {nome} salvos com sucesso!")

# 🔹 Função para exibir os conscritos organizados por pelotão
def exibir_conscritos():
    # Buscar os dados salvos no Google Sheets
    conscritos = sheet.get_all_values()[1:]  # Ignorar cabeçalho

    # Ordenar conscritos primeiro pela menção (peso), depois pelo status (Apto/Inapto) e por último pela ordem alfabética
    conscritos_ordenados = sorted(conscritos, key=lambda x: (
        peso_mencao.get(x[1], 0),  # Ordenar pela menção (agora é a segunda coluna)
        x[5] == "Apto",            # "Apto" vem antes de "Inapto"
        x[0]                        # Ordenar alfabeticamente pelo nome
    ), reverse=True)  # Invertido para ter "Excelente" primeiro

    pelotao_3 = [c for c in conscritos_ordenados if c[0][0].upper() in "JK"]
    pelotao_4 = [c for c in conscritos_ordenados if c[0][0].upper() in "LMNO"]

    # 🔹 Atualizar colunas para incluir todas as 6 colunas corretamente
    colunas = ["Nome", "Menção", "Habilidades", "Quais Habilidades", "Peso da Menção", "Situação"]

    # 🔹 Exibir a tabela do 3º Pelotão
    st.subheader("3º Pelotão (J a K)")
    pelotao_3_df = pd.DataFrame(pelotao_3, columns=colunas)

    # Adicionar cor para aptos e inaptos
    pelotao_3_df['Situação'] = pelotao_3_df['Situação'].apply(lambda x: "Inapto" if "Inapto" in x else "Apto")
    st.table(pelotao_3_df.style.apply(
        lambda x: ['background-color: lightcoral' if 'Inapto' in v else 'background-color: lightgreen' if 'Apto' in v else '' for v in x], 
        axis=1
    ))

    # 🔹 Exibir a tabela do 4º Pelotão
    st.subheader("4º Pelotão (L a O)")
    pelotao_4_df = pd.DataFrame(pelotao_4, columns=colunas)

    # Adicionar cor para aptos e inaptos
    pelotao_4_df['Situação'] = pelotao_4_df['Situação'].apply(lambda x: "Inapto" if "Inapto" in x else "Apto")
    st.table(pelotao_2_df.style.apply(
        lambda x: ['background-color: lightcoral' if 'Inapto' in v else 'background-color: lightgreen' if 'Apto' in v else '' for v in x], 
        axis=1
    ))

# 🔹 Função para gerar relatório Excel
def gerar_relatorio_pelotao(pelotao):
    conscritos = sheet.get_all_values()[1:]  # Ignorar cabeçalho
    colunas = ["Nome", "Menção", "Habilidades", "Quais Habilidades", "Peso da Menção", "Situação"]

    # Ordenar conscritos primeiro pela menção (peso), depois pelo status (Apto/Inapto) e por último pela ordem alfabética
    conscritos_ordenados = sorted(conscritos, key=lambda x: (
        peso_mencao.get(x[1], 0),  # Ordenar pela menção (agora é a segunda coluna)
        x[5] == "Apto",            # "Apto" vem antes de "Inapto"
        x[0]                        # Ordenar alfabeticamente pelo nome
    ), reverse=True)  # Invertido para ter "Excelente" primeiro

    if pelotao == 1:
        conscritos_filtrados = [c for c in conscritos_ordenados if c[0][0].upper() in "JK"]
    else:
        conscritos_filtrados = [c for c in conscritos_ordenados if c[0][0].upper() in "LMNO"]

    df = pd.DataFrame(conscritos_filtrados, columns=colunas)

    # Criar arquivo CSV
    excel_file = df.to_csv(index=False).encode('utf-8')
    return excel_file

# 🔹 Interface Streamlit
# Adicionando o fundo preto e texto branco
st.markdown("""
    <style>
    .reportview-container {
        background-color: black;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white;
    }
    .css-ffhzg2 { 
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Imagem do 1º BPE com fundo transparente e ajustada para tamanho menor, acima do título
st.image('IMG_1118.png', width=60, use_container_width=True)

# Títulos com espaçamento ajustado
st.markdown('<h1 style="text-align: center; font-size: 40px; margin-bottom: 5px;">SELEÇÃO COMPLEMENTAR 2025</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; margin-top: 0px; margin-bottom: 30px;">3ª CIA - PANTERA</h2>', unsafe_allow_html=True)

# Seção de cadastro
coletar_dados()

# Seção de exibição
exibir_conscritos()

# Botão para gerar relatório
st.subheader("Gerar Relatório")
st.download_button(label="Baixar Relatório (3º Pelotão)", data=gerar_relatorio_pelotao(1), file_name="relatorio_3pelotao.csv", mime="text/csv")
st.download_button(label="Baixar Relatório (4º Pelotão)", data=gerar_relatorio_pelotao(2), file_name="relatorio_4pelotao.csv", mime="text/csv")

# Créditos abaixo de "Gerar Relatório", centralizado
st.markdown("""
    <p style="font-size: 10px; color: white; text-align: center;">Código Python feito por CAP TREMMEL - PQDT 90.360</p>
    <p style="font-size: 10px; color: white; text-align: center;">Qualquer erro, entre em contato: 21 974407682</p>
""", unsafe_allow_html=True)
