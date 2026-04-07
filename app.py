import streamlit as st
from database import database as db
from agents.graph import criar_graph, escolher_grafico



st.set_page_config(
    layout="wide",          
    page_title="Assistente Júnior", 
    page_icon="📊"              
)
st.markdown("""
<style>
    h1 { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])

with col2:

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

        #resposta
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
    
        with st.expander("🔍 Como cheguei nessa resposta", expanded=False):
            st.code(resultado.get("sql"), language="sql")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Tentativas**")
            st.write(resultado.get("tentativas", 0))

        with col2:
            st.markdown("**Erro (se houve)**")
            st.write(resultado.get("erro"))

        if "historico_sql" in resultado:
            st.markdown("### Histórico de SQL")
            for i, sql in enumerate(resultado["historico_sql"]):
                st.code(sql, language="sql")
        
        

        