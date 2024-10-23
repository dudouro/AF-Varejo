import yfinance as yf
import pandas as pd
from traducao import field_translation_balance_sheet, field_translation_cashflow, field_translation_dre

# Função para obter o balanço patrimonial, fluxo de caixa e DRE em português
def get_financials_in_portuguese(ticker):
    stock = yf.Ticker(ticker)

    # Obter e traduzir o balanço patrimonial
    balance_sheet = stock.balance_sheet.rename(index=field_translation_balance_sheet)

    # Obter e traduzir o fluxo de caixa
    cashflow = stock.cashflow.rename(index=field_translation_cashflow)

    # Obter e traduzir o DRE (Demonstração de Resultados)
    financials = stock.financials.rename(index=field_translation_dre)

    # Selecionar apenas os anos 2021, 2022 e 2023
    selected_years = ["2021-12-31", "2022-12-31", "2023-12-31"]
    balance_sheet = balance_sheet[selected_years]
    cashflow = cashflow[selected_years]
    financials = financials[selected_years]

    # Substituir valores vazios por zero
    balance_sheet.fillna(0, inplace=True)
    cashflow.fillna(0, inplace=True)
    financials.fillna(0, inplace=True)

    # Concatenar os dados em um único DataFrame
    combined_df = pd.concat([balance_sheet, cashflow, financials])

    return combined_df

def analisar_fleuriet_df(df_balanco):
  """
  Analisa o modelo de Fleuriet a partir de um DataFrame do balanço patrimonial.

  Args:
      df_balanco (pd.DataFrame): DataFrame contendo os dados do balanço patrimonial
                                   com os anos como colunas e as contas como linhas.

  Returns:
      pd.DataFrame: DataFrame com os resultados da análise de Fleuriet para cada ano.
  """

  # Criar um DataFrame para armazenar os resultados
  resultados = pd.DataFrame(index=df_balanco.columns,
                             columns=['CDG', 'NCG', 'T', 'Regra', 'Tipo de BP'])

  for ano in df_balanco.columns:
    # Obter os valores do balanço patrimonial para o ano
    ativo_circulante = df_balanco.loc['Ativos Correntes', ano]
    ativo_nao_circulante = df_balanco.loc['Ativos Não Corrente', ano]
    passivo_circulante = df_balanco.loc['Dívida Corrente', ano]  # Ajustado, se necessário
    passivo_nao_circulante = df_balanco.loc['Total de Passivos Não Correntes Líquidos de Participações Minoritárias', ano]
    patrimonio_liquido = df_balanco.loc['Patrimônio Líquido dos Acionistas', ano]

    # Calcular as componentes do Fleuriet
    cdg = df_balanco.loc['Capital de Giro', ano]
    ncg = ativo_circulante - passivo_circulante
    saldo_tesouraria = cdg - ncg

    # Determinar a regra e o tipo de balanço patrimonial
    if cdg > 0 and ncg < 0:
      regra = 1
      tipo_bp = 'Excelente'
    elif cdg > 0 and ncg > 0 and saldo_tesouraria > 0:
      regra = 2
      tipo_bp = 'Sólida'
    elif cdg > 0 and ncg > 0 and saldo_tesouraria < 0:
      regra = 3
      tipo_bp = 'Insatisfatória'
    elif cdg < 0 and ncg < 0:
      regra = 4
      tipo_bp = 'Alto risco'
    elif cdg < 0 and saldo_tesouraria < 0:
      regra = 5
      tipo_bp = 'Muito Ruim'
    else:
      regra = 6
      tipo_bp = 'Péssima'

    # Armazenar os resultados no DataFrame
    resultados.loc[ano, 'CDG'] = cdg
    resultados.loc[ano, 'NCG'] = ncg
    resultados.loc[ano, 'T'] = saldo_tesouraria
    resultados.loc[ano, 'Regra'] = regra
    resultados.loc[ano, 'Tipo de BP'] = tipo_bp

  return resultados

def analisar_dupont_df(df_financeiro):
    """
    Analisa o modelo de DuPont a partir de um DataFrame com dados financeiros.

    Args:
        df_financeiro (pd.DataFrame): DataFrame contendo os dados financeiros
                                       com os anos como colunas e as contas como linhas.

    Returns:
        pd.DataFrame: DataFrame com os resultados da análise DuPont para cada ano.
    """

    # Criar um DataFrame para armazenar os resultados
    resultados = pd.DataFrame(index=df_financeiro.columns,
                             columns=['ROE', 'ROA', 'MARGEM_LIQUIDA', 'GIRO_DO_ATIVO', 'ALAVANCAGEM'])

    for ano in df_financeiro.columns:
        # Obter os valores financeiros para o ano
        lucro_liquido = df_financeiro.loc['Lucro Líquido', ano]
        patrimonio_liquido = df_financeiro.loc['Patrimônio Líquido dos Acionistas', ano]
        ativo_total = df_financeiro.loc['Ativo Total', ano]
        vendas = df_financeiro.loc['Receita Total', ano]  # Usando Receita Total como vendas

        # Calcular os indicadores do modelo DuPont
        roe = lucro_liquido / patrimonio_liquido if patrimonio_liquido != 0 else None
        roa = lucro_liquido / ativo_total if ativo_total != 0 else None
        margem_liquida = lucro_liquido / vendas if vendas != 0 else None
        giro_do_ativo = vendas / ativo_total if ativo_total != 0 else None
        alavancagem = ativo_total / patrimonio_liquido if patrimonio_liquido != 0 else None

        # Armazenar os resultados no DataFrame
        resultados.loc[ano, 'ROE'] = roe
        resultados.loc[ano, 'ROA'] = roa
        resultados.loc[ano, 'MARGEM_LIQUIDA'] = margem_liquida
        resultados.loc[ano, 'GIRO_DO_ATIVO'] = giro_do_ativo
        resultados.loc[ano, 'ALAVANCAGEM'] = alavancagem

    return resultados

def calcular_zscore_df(df):
    """
    Calcula o Z-Score a partir de um DataFrame contendo os dados financeiros.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados financeiros com os anos como colunas e as contas como linhas.

    Returns:
        pd.DataFrame: DataFrame com os resultados do Z-Score para cada ano.
    """
    # Criar um DataFrame para armazenar os resultados
    resultados = pd.DataFrame(index=df.columns, columns=['Z-Score'])
    
    # Possíveis nomes para dividendos
    possiveis_nomes_dividendos = ['Dividendos em Dinheiro Pagos', 'Dividendos de Ações Ordinárias Pagos']

    for ano in df.columns:
        # Obter os valores financeiros para o ano
        capital_giro = df.loc['Capital de Giro', ano]
        lucro_liquido = df.loc['Lucro Líquido', ano]
        # Procurar pela linha correta de dividendos
        dividendos = None
        for nome in possiveis_nomes_dividendos:
          if nome in df.index:
            dividendos = df.loc[nome, ano]
            break

        if dividendos is None:
          raise KeyError("Nenhuma linha de dividendos encontrada para o ano {}".format(ano))
            
        ativo_total = df.loc['Ativo Total', ano]
        passivo_total = df.loc['Total Liabilities Net Minority Interest', ano]
        vendas_totais = df.loc['Receita Total', ano]

        # Calcular o lucro retido
        lucro_retido = lucro_liquido - dividendos

        # Calcular os componentes do Z-Score
        x1 = capital_giro / ativo_total if ativo_total != 0 else 0
        x2 = lucro_retido / ativo_total if ativo_total != 0 else 0
        x3 = df.loc['EBIT', ano] / ativo_total if ativo_total != 0 else 0
        x4 = df.loc['Patrimônio Líquido dos Acionistas', ano] / passivo_total if passivo_total != 0 else 0
        x5 = vendas_totais / ativo_total if ativo_total != 0 else 0

        # Calcular o Z-Score
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)

        # Armazenar os resultados no DataFrame
        resultados.loc[ano, 'Z-Score'] = z_score
        resultados.loc[ano, 'x1'] = x1
        resultados.loc[ano, 'x2'] = x2
        resultados.loc[ano, 'x3'] = x3
        resultados.loc[ano, 'x4'] = x4
        resultados.loc[ano, 'x5'] = x5

    return resultados

def calcular_termometro_kanitz(df):
    """
    Calcula o Termômetro de Kanitz e seus componentes a partir de um DataFrame contendo os dados financeiros.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados financeiros com os anos como colunas e as contas como linhas.

    Returns:
        pd.DataFrame: DataFrame com os resultados do Termômetro de Kanitz e seus componentes para cada ano.
    """
    # Criar um DataFrame para armazenar os resultados
    resultados = pd.DataFrame(index=df.columns, columns=['Termômetro de Kanitz', 'Liquidez Geral', 'Endividamento Geral', 'RSPL'])

    for ano in df.columns:
        try:
            # Obter os valores financeiros para o ano
            ativo_total = df.loc['Ativo Total', ano]
            passivo_corrente = df.loc['Passivos Correntes', ano]
            passivo_nao_corrente = df.loc['Total de Passivos Não Correntes Líquidos de Participações Minoritárias', ano]
            patrimonio_liquido = df.loc['Patrimônio Líquido dos Acionistas', ano]
            ativo_circulante = df.loc['Ativos Correntes', ano]
            realizavel_longo_prazo = df.loc['Investimento em Ações de Longo Prazo', ano]
            lucro_liquido = df.loc['Lucro Líquido', ano]
            passivo_total = df.loc['Total Liabilities Net Minority Interest', ano]

            # Calcular Endividamento Geral
            endividamento_geral = passivo_total / ativo_total if ativo_total != 0 else 0

            # Calcular Liquidez Geral
            liquidez_geral = ativo_total / passivo_total if passivo_total != 0 else 0

            # Calcular Rentabilidade sobre Patrimônio Líquido (RSPL)
            rspl = lucro_liquido / patrimonio_liquido if patrimonio_liquido != 0 else 0

            # Calcular o Termômetro de Kanitz
            termometro_kanitz = (0.01 * endividamento_geral) + (1.5 * liquidez_geral) + (0.08 * rspl)

            # Armazenar os resultados no DataFrame
            resultados.loc[ano, 'Termômetro de Kanitz'] = termometro_kanitz
            resultados.loc[ano, 'Liquidez Geral'] = liquidez_geral
            resultados.loc[ano, 'Endividamento Geral'] = endividamento_geral
            resultados.loc[ano, 'RSPL'] = rspl

        except KeyError as e:
            print(f"Erro: {e} não encontrado para o ano {ano}. Verifique se o nome da coluna está correto.")
    
    return resultados

    return resultados




