import streamlit as st
import pandas as pd
from financeira import get_financials_in_portuguese, analisar_fleuriet_df, analisar_dupont_df, calcular_zscore_df, calcular_termometro_kanitz

# Função para verificar se o ticker é de uma ação brasileira
def is_brazilian_stock(ticker):
    # Ações brasileiras geralmente têm 4 letras e um número no final (ex: PETR4, VALE3)
    return len(ticker) == 5 and ticker[-1].isdigit()

# Interface Streamlit
st.title("Análise Financeira de Ações")

# Input do usuário para o ticker
ticker = st.text_input("UFU - Financias Corporativas. Digite o ticker da ação (ex: AMER3, BHIA3, MGLU3):")

# Adicionar botão para realizar a pesquisa
if st.button("Pesquisar"):
    if is_brazilian_stock(ticker):
        ticker = ticker + ".SA"  # Adicionar sufixo para ações brasileiras

    try:
        # Obter os dados financeiros
        balance_sheet = get_financials_in_portuguese(ticker)

        # Análise utilizando as funções fornecidas
        fleuriet_df = analisar_fleuriet_df(balance_sheet)
        dupont_df = analisar_dupont_df(balance_sheet)
        zscore_df = calcular_zscore_df(balance_sheet)
        termo = calcular_termometro_kanitz(balance_sheet)

        # Exibir os resultados das análises
        st.subheader("Análise Fleuriet")
        st.dataframe(fleuriet_df)

        st.subheader("Análise DuPont")
        st.dataframe(dupont_df)

        st.subheader("Cálculo do Z-Score")
        st.dataframe(zscore_df)

        st.subheader("Termômetro de Kanitz")
        st.dataframe(termo)

    except Exception as e:
        st.error(f"Ocorreu um erro ao realizar as análises: {e}")
