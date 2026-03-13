import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Formation Correlator Pro", layout="centered")

st.title("🛢️ Formation Name Correlator")

REFERENCE_FILE = "reference.xlsx"


@st.cache_data
def load_reference(file_path):
    if os.path.exists(file_path):
        # Carrega o arquivo de referência
        return pd.read_excel(file_path)
    return None


df_ref = load_reference(REFERENCE_FILE)

if df_ref is not None:
    try:
        # Usando iloc para pegar as colunas pela posição caso o nome mude
        # No seu arquivo original:
        # Coluna J é o índice 9 (Short Name)
        # Coluna K é o índice 10 (Full Name)

        # Vamos tentar identificar as colunas dinamicamente
        # Se o arquivo tiver muitas colunas vazias, pegamos as duas últimas que têm dados
        cols = df_ref.dropna(axis=1, how='all').columns

        # Mapeamento: usamos a última coluna como Nome Completo e a penúltima como Abreviação
        # Isso geralmente corresponde ao layout J e K que você enviou
        mapping = dict(zip(
            df_ref[cols[-1]].astype(str).str.strip(),
            df_ref[cols[-2]].astype(str).str.strip()
        ))

        st.success(
            f"✅ Biblioteca carregada ({len(mapping)} formações encontradas)")

        data_file = st.file_uploader(
            "Suba o arquivo de dados para processar", type="xlsx")

        if data_file:
            df_data = pd.read_excel(data_file)

            # Ajuste os nomes das colunas do arquivo de TRABALHO (o que você faz upload)
            # No arquivo que você enviou, elas são 'formation Tops/Reservoir' (D) e 'Short Name' (E)
            COL_TARGET = 'formation Tops/Reservoir'
            COL_RESULT = 'Short Name'

            if st.button("Correlacionar e Gerar Arquivo"):
                if COL_TARGET in df_data.columns:
                    def match_row(row):
                        val = str(row[COL_TARGET]).strip()
                        return mapping.get(val, row[COL_RESULT] if COL_RESULT in df_data.columns else "")

                    df_data[COL_RESULT] = df_data.apply(match_row, axis=1)

                    st.success("Processamento concluído!")

                    # Gerar Excel
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
                        f"A coluna '{COL_TARGET}' não foi encontrada no arquivo enviado.")
    except Exception as e:
        st.error(f"Erro ao processar a biblioteca: {e}")
else:
    st.error(f"Arquivo '{REFERENCE_FILE}' não encontrado no GitHub.")
