import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Função para conectar ao banco de dados PostgreSQL
def conectar_db():
    return psycopg2.connect(
        dbname="",
        user="",
        password="",
        host="localhost",
        port="5432"
    )

# Função para carregar dados de clientes
@st.cache_data
def carregar_clientes():
    conn = conectar_db()
    query = "SELECT id_cliente, nome, data_cadastro FROM clientes;"
    df = pd.read_sql(query, conn)
    df["data_cadastro"] = pd.to_datetime(df["data_cadastro"])  # Converter para datetime
    conn.close()
    return df

# Função para carregar dados de pedidos
@st.cache_data
def carregar_pedidos():
    conn = conectar_db()
    query = "SELECT id_pedido, data_pedido, valor_total, id_cliente FROM pedidos;"
    df = pd.read_sql(query, conn)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])  # Converter para datetime
    conn.close()
    return df

# Função para carregar dados de itens_pedidos
@st.cache_data
def carregar_itens_pedidos():
    conn = conectar_db()
    query = "SELECT id_pedido, id_produto, quantidade, preco_unitario FROM itens_pedido;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Configuração da página no Streamlit
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

st.title("📊 Dashboard de Vendas")

# Carregar os dados
clientes = carregar_clientes()
pedidos = carregar_pedidos()
itens_pedidos = carregar_itens_pedidos()

# **Seção de Filtros**
st.sidebar.header("Filtros")

# Seleção de período com duas datas
data_inicial = st.sidebar.date_input("Data inicial", min_value=pedidos["data_pedido"].min().date(), max_value=pedidos["data_pedido"].max().date())
data_final = st.sidebar.date_input("Data final", min_value=pedidos["data_pedido"].min().date(), max_value=pedidos["data_pedido"].max().date())

# Converter datas para datetime
data_inicial = pd.to_datetime(data_inicial)
data_final = pd.to_datetime(data_final)

# Filtragem dos pedidos pelo período selecionado
pedidos_filtrados = pedidos[(pedidos["data_pedido"] >= data_inicial) & (pedidos["data_pedido"] <= data_final)]

# **Exibir Tabelas**
st.subheader("📌 Tabela de Clientes")
st.dataframe(clientes)

st.subheader("📌 Tabela de Pedidos")
st.dataframe(pedidos_filtrados)

# **Gerar Gráficos com Filtros Aplicados**
st.subheader("📊 Total de Vendas por Mês")

# Converter para string para evitar erro com JSON
pedidos_filtrados["mes_ano"] = pedidos_filtrados["data_pedido"].dt.strftime("%Y-%m")

# Agrupar vendas por mês
vendas_mensais = pedidos_filtrados.groupby("mes_ano")["valor_total"].sum().reset_index()

# Gráfico de evolução das vendas
fig1 = px.line(vendas_mensais, x="mes_ano", y="valor_total", title="Evolução das Vendas")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📊 Vendas por Cliente")
vendas_clientes = pedidos_filtrados.groupby("id_cliente")["valor_total"].sum().reset_index()

# Gráfico de vendas por cliente
fig2 = px.bar(vendas_clientes, x="id_cliente", y="valor_total", title="Total de Compras por Cliente")
st.plotly_chart(fig2, use_container_width=True)
