import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Formation Correlator Pro", layout="centered")

st.title("🛢️ Formation Name Correlator")
st.write("O arquivo de referência foi carregado do sistema. Basta subir o arquivo de dados.")

# Nome do arquivo que você subiu para o GitHub
REFERENCE_FILE = "reference.xlsx"

# Função para carregar a biblioteca de referência


@st.cache_data  # Isso faz com que o arquivo de referência seja lido apenas uma vez, poupando memória
def load_reference(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return None


df_ref = load_reference(REFERENCE_FILE)

if df_ref is not None:
    # Mapeamento fixo baseado nas colunas que vimos antes
    # Ajuste os nomes das colunas abaixo se forem diferentes no seu reference.xlsx
    COL_LIB_FULL = 'formation Tops/Reservoir.1'
    COL_LIB_CODE = 'Short Name.1'

    mapping = dict(zip(
        df_ref[COL_LIB_FULL].astype(str).str.strip(),
        df_ref[COL_LIB_CODE].astype(str).str.strip()
    ))

    st.success("✅ Biblioteca de referência carregada com sucesso!")

    # Upload do arquivo de trabalho
    data_file = st.file_uploader(
        "Suba o arquivo de dados para processar", type="xlsx")

    if data_file:
        df_data = pd.read_excel(data_file)

        # Identifica as colunas automaticamente ou permite seleção
        col_target = 'formation Tops/Reservoir'
        col_result = 'Short Name'

        if st.button("Correlacionar e Gerar Arquivo"):
            def match_row(row):
                val = str(row[col_target]).strip()
                # Busca na biblioteca fixa; se não achar, mantém o que está na célula
                return mapping.get(val, row[col_result])

            df_data[col_result] = df_data.apply(match_row, axis=1)

            st.success("Processamento concluído!")
            st.dataframe(df_data[[col_target, col_result]].head(10))

            # Preparar download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_data.to_excel(writer, index=False)

            st.download_button(
                label="📥 Baixar Arquivo Processado",
                data=output.getvalue(),
                file_name="resultado_correlacionado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.error(
        f"Arquivo '{REFERENCE_FILE}' não encontrado no repositório. Certifique-se de que ele foi enviado via Git.")
