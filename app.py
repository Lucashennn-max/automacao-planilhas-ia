app.py



%%writefile app.py
import streamlit as st
import pandas as pd
import openai
from time import sleep

# 🔹 Configure sua chave da OpenAI aqui
openai.api_key = "SEU_API_KEY"

st.title("Automação de Planilhas com IA - Preenchimento de Equipamentos")
st.write("""
Faça upload da sua planilha (.xlsx ou .csv). A IA vai ler a coluna 'Descrição' e preencher automaticamente a coluna 'Código / Equipamento', escolhendo exatamente o nome que já existe na lista de equipamentos.
""")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha sua planilha", type=["xlsx", "csv"])

def identificar_equipamento_normalizado(descricao, lista_equipamentos):
    """Usa a IA para escolher o equipamento correto a partir da descrição e lista de referência"""
    try:
        prompt = f"""
        Leia a seguinte descrição do problema: "{descricao}".
        A partir disso, escolha exatamente um equipamento da lista abaixo que corresponde a esta descrição.
        Lista de equipamentos: {lista_equipamentos}
        Retorne apenas o nome exato do equipamento da lista.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

if uploaded_file:
    # Lê o arquivo dependendo da extensão
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Visualização da planilha original:")
    st.dataframe(df)

    # Lista de equipamentos existente (para normalização)
    if "Código / Equipamento" in df.columns:
        equipamentos_lista = df["Código / Equipamento"].dropna().unique().tolist()
    else:
        st.error("A coluna 'Código / Equipamento' não existe na planilha.")
        st.stop()

    # Botão para processar a planilha
    if st.button("Atualizar coluna de Equipamento"):
        if "Descrição" not in df.columns:
            st.error("Não foi encontrada a coluna 'Descrição' na planilha.")
        else:
            # Barra de progresso
            progress_text = "Processando linhas..."
            my_bar = st.progress(0, text=progress_text)
            total = len(df)
            equipamentos_atualizados = []

            for i, desc in enumerate(df["Descrição"]):
                equipamento = identificar_equipamento_normalizado(desc, equipamentos_lista)
                equipamentos_atualizados.append(equipamento)
                # Atualiza barra de progresso
                my_bar.progress((i+1)/total, text=f"{i+1}/{total} linhas processadas")
                sleep(0.1)  # Pequena pausa para atualizar interface

            df["Código / Equipamento"] = equipamentos_atualizados

            st.success("Coluna de Equipamento atualizada com sucesso!")
            st.dataframe(df)

            # Botão para download da planilha atualizada
            output_file = "planilha_atualizada.xlsx"
            df.to_excel(output_file, index=False)
            st.download_button(
                label="Baixar planilha atualizada",
                data=open(output_file, "rb").read(),
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
