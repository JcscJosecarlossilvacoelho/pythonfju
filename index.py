import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu

# Nome dos arquivos CSV para guardar os dados
CSV_FILE = "pontos_tribos.csv"
CONEXAO_FILE = "conexao_tribos.csv"


# Função para carregar dados existentes ou criar um arquivo vazio
def carregar_dados(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=columns)


# Função para salvar dados no CSV
def salvar_dados(df, filename):
    df.to_csv(filename, index=False)


# Carregar os dados iniciais
dados = carregar_dados(CSV_FILE, ["Data", "Tribo", "Jogo", "Pontos"])
conexao_dados = carregar_dados(CONEXAO_FILE, ["Data", "Tribo", "Jovens"])
if not conexao_dados.empty:
    conexao_dados["Data"] = pd.to_datetime(conexao_dados["Data"], errors="coerce")  # Converte e ignora erros
    conexao_dados = conexao_dados.dropna(subset=["Data"])
# Código de login fixo
LOGIN_CODE = "1247"


# Função para verificar o login
def verificar_login():
    st.sidebar.title("Login")
    codigo = st.sidebar.text_input("Digite o código de acesso:", type="password", key="login_code")
    if st.sidebar.button("Entrar"):
        if codigo == LOGIN_CODE:
            st.session_state.logged_in = True
            st.sidebar.success("Login bem-sucedido!")
        else:
            st.sidebar.error("Código incorreto. Tente novamente.")


# Verificar se o usuário está logado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Exibir a interface de login se o usuário não estiver logado
if not st.session_state.logged_in:
    verificar_login()
    st.stop()  # Impede o restante do aplicativo de ser executado

# Se o usuário estiver logado, exibir o aplicativo principal
st.title("Gestão Encontro Jovem")

# Menu com streamlit-option-menu
menu = option_menu(
    menu_title=None,  # Não exibe o título do menu
    options=["Registar Pontos", "Consultar Pontos", "Conexão Jovem"],
    icons=["pencil", "bar-chart", "people"],  # Ícones correspondentes
    menu_icon="cast",  # Ícone do menu principal
    default_index=0,  # Abre na primeira opção por padrão
    orientation="horizontal",  # Define a orientação horizontal
)

if menu == "Registar Pontos":
    st.header("Registar Pontos")
    tribo = st.selectbox("Selecionar Tribo", ["Tribo Levi", "Tribo Judá"])
    jogo = st.text_input("Jogo")
    pontos = st.number_input("Pontos", min_value=0, step=1)
    data = st.date_input("Data")

    if st.button("Salvar Pontos"):
        novo_registro = {"Data": data, "Tribo": tribo, "Jogo": jogo, "Pontos": pontos}
        novo_registro_df = pd.DataFrame([novo_registro])  # Convert the new record to a DataFrame
        dados = pd.concat([dados, novo_registro_df],
                          ignore_index=True)  # Concatenate the new record with the existing data
        salvar_dados(dados, CSV_FILE)
        st.success("Pontos salvos com sucesso!")

elif menu == "Consultar Pontos":
    st.header("Consultar Pontos")

    # Filtro por tribo
    filtro_tribo = st.selectbox("Filtrar por Tribo", ["Todas"] + dados["Tribo"].unique().tolist())

    # Filtro por data
    data_inicio = st.date_input("Data de Início", value=pd.to_datetime(dados["Data"]).min())
    data_fim = st.date_input("Data de Fim", value=pd.to_datetime(dados["Data"]).max())

    # Aplicar filtros
    dados_filtrados = dados[(pd.to_datetime(dados["Data"]) >= pd.to_datetime(data_inicio)) & (
                pd.to_datetime(dados["Data"]) <= pd.to_datetime(data_fim))]
    if filtro_tribo != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados["Tribo"] == filtro_tribo]

    # Exibir tabela editável
    st.subheader("Tabela de Pontos (Editar ou Excluir)")
    edited_df = st.data_editor(dados_filtrados, num_rows="dynamic", key="edit_pontos", use_container_width=True)

    # Botão para salvar alterações
    if st.button("Salvar Alterações"):
        dados.update(edited_df)  # Atualiza o DataFrame original com as alterações
        salvar_dados(dados, CSV_FILE)
        st.success("Alterações salvas com sucesso!")

    # Botão para excluir registros selecionados
    if st.button("Excluir Registros Selecionados"):
        indices_para_excluir = edited_df.index.difference(dados_filtrados.index)  # Identifica as linhas excluídas
        dados = dados.drop(indices_para_excluir)  # Remove as linhas do DataFrame original
        salvar_dados(dados, CSV_FILE)
        st.success("Registros excluídos com sucesso!")

    # Gráfico de pontos por tribo
    if not dados_filtrados.empty:
        st.subheader("Gráfico de Pontos por Tribo")
        grafico = dados_filtrados.groupby("Tribo")["Pontos"].sum().sort_values()
        st.bar_chart(grafico)

elif menu == "Conexão Jovem":
    st.header("Conexão Jovem")

    tribo_conexao = st.selectbox("Selecionar Tribo", ["Tribo Levi", "Tribo Judá"], key="tribo_conexao")
    jovens = st.number_input("Número de Jovens", min_value=0, step=1, key="jovens_conexao")
    data_conexao = st.date_input("Data", key="data_conexao")

    if st.button("Salvar Conexão Jovem"):
        novo_conexao = {"Data": data_conexao, "Tribo": tribo_conexao, "Jovens": jovens}
        novo_conexao_df = pd.DataFrame([novo_conexao])  # Convert the new record to a DataFrame
        conexao_dados = pd.concat([conexao_dados, novo_conexao_df],
                                  ignore_index=True)  # Concatenate the new record with the existing data
        salvar_dados(conexao_dados, CONEXAO_FILE)
        st.success("Dados da Conexão Jovem salvos com sucesso!")

    st.subheader("Tabela de Conexão Jovem (Editar ou Excluir)")

    # Filtro por data
    data_inicio_conexao = st.date_input("Data de Início", value=pd.to_datetime(conexao_dados["Data"]).min(),
                                        key="data_inicio_conexao")
    data_fim_conexao = st.date_input("Data de Fim", value=pd.to_datetime(conexao_dados["Data"]).max(),
                                     key="data_fim_conexao")

    # Aplicar filtro de data
    conexao_dados_filtrados = conexao_dados[
        (pd.to_datetime(conexao_dados["Data"]) >= pd.to_datetime(data_inicio_conexao)) & (
                    pd.to_datetime(conexao_dados["Data"]) <= pd.to_datetime(data_fim_conexao))]

    # Exibir tabela editável
    edited_conexao_df = st.data_editor(conexao_dados_filtrados, num_rows="dynamic", key="edit_conexao",
                                       use_container_width=True)

    # Botão para salvar alterações
    if st.button("Salvar Alterações (Conexão Jovem)"):
        conexao_dados.update(edited_conexao_df)  # Atualiza o DataFrame original com as alterações
        salvar_dados(conexao_dados, CONEXAO_FILE)
        st.success("Alterações salvas com sucesso!")

    # Botão para excluir registros selecionados
    if st.button("Excluir Registros Selecionados (Conexão Jovem)"):
        indices_para_excluir = edited_conexao_df.index.difference(
            conexao_dados_filtrados.index)  # Identifica as linhas excluídas
        conexao_dados = conexao_dados.drop(indices_para_excluir)  # Remove as linhas do DataFrame original
        salvar_dados(conexao_dados, CONEXAO_FILE)
        st.success("Registros excluídos com sucesso!")

    # Gráfico de jovens por tribo
    if not conexao_dados_filtrados.empty:
        st.subheader("Gráfico de Jovens por Tribo")
        grafico_conexao = conexao_dados_filtrados.groupby("Tribo")["Jovens"].sum().sort_values()
        st.bar_chart(grafico_conexao)