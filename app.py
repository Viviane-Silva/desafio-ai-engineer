import streamlit as st
import database.database as db
from agent.graph import criar_graph
from agent.graph import escolher_grafico

# st.set_page_config(layout="wide")

st.title("Assistente de Dados IA")

# schema dinâmico
schema = ""
for tabela in db.listar_tabelas():
    schema += f"\nTabela {tabela}:\n"
    schema += str(db.schema_tabela(tabela)) + "\n"

# inicializa graph
if "graph" not in st.session_state:
    st.session_state.graph = criar_graph()

graph = st.session_state.graph

pergunta = st.text_input("Pergunta de negócio")

if pergunta:
    resultado = graph.invoke({
        "pergunta": pergunta,
        "schema": schema,
        "tentativas": 0
    })


    with st.expander("SQL"):
        st.code(resultado.get("sql"))

    st.subheader("Resposta")
    st.write(resultado.get("resposta"))

    if "df" in resultado:
        df = resultado["df"]
        # st.dataframe(df)

        # gráfico automático
        #  valor único 
        if df.shape == (1, 1):
            valor = df.iloc[0, 0]
            st.metric(label="Resultado", value=valor)

        #  se não, gera tabela/gráfico
        else:
            st.dataframe(df)

            tipo = escolher_grafico(df)

            if tipo in ["linha", "barra"]:
                df_plot = df.copy()
                df_plot = df_plot.set_index(df_plot.columns[0])

                if tipo == "linha":
                    st.line_chart(df_plot)
                else:
                    st.bar_chart(df_plot)