import streamlit as st
import pandas as pd
from financeira import get_financials_in_portuguese, analisar_fleuriet_df, analisar_dupont_df, calcular_zscore_df

# Interface Streamlit
st.title("Análise Financeira de Ações")

ticker = st.text_input("Digite o ticker da ação (ex: AAPL, MSFT):")+".SA"

if ticker:
    
    balance_sheet = get_financials_in_portuguese(ticker)

    # Análise utilizando as funções fornecidas
    try:
        fleuriet_df = analisar_fleuriet_df(balance_sheet)
        dupont_df = analisar_dupont_df(balance_sheet)
        zscore_df = calcular_zscore_df(balance_sheet)

        st.subheader("Análise Fleuriet")
        st.dataframe(fleuriet_df)

        st.subheader("Análise DuPont")
        st.dataframe(dupont_df)

        st.subheader("Cálculo do Z-Score")
        st.dataframe(zscore_df)
        
    except Exception as e:
        st.error(f"Ocorreu um erro ao realizar as análises: {e}")