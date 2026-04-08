import streamlit as st
import database.database as db
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


@st.cache_data(ttl=60)
def get_schema():
    schema = ""
    for tabela in db.listar_tabelas():
        schema += f"\nTabela {tabela}:\n"
        schema += str(db.schema_tabela(tabela)) + "\n"
    return schema


col1, col2, col3 = st.columns([1, 3, 1])

with col2:

    st.title("Assistente de Dados IA")

    schema = get_schema()

    if "graph" not in st.session_state:
        st.session_state.graph = criar_graph()

    graph = st.session_state.graph

    pergunta = st.text_input("Pergunta de negócio")

    if pergunta:
        with st.spinner("Analisando sua pergunta..."):
            resultado = graph.invoke({
                "pergunta": pergunta,
                "schema": schema,
                "tentativas": 0,
                "historico_sql": []
            })

        #  RESPOSTA
        st.subheader("Resposta")
        st.write(resultado.get("resposta"))

        df = resultado.get("df")
    
        if df is not None and not df.empty:
            tipo = escolher_grafico(df)
            if tipo in ["linha", "barra"]:
                if len(df.columns) > 0:
                    df_plot = df.copy()
                    df_plot = df_plot.set_index(df_plot.columns[0])

                    if tipo == "linha":
                        st.line_chart(df_plot)
                    else:
                        st.bar_chart(df_plot)

        

        #  EXPLICAÇÃO (fora do visualizacao!)
        with st.expander("🔍 Como cheguei nessa resposta", expanded=False):

            if resultado.get("plano"):
                st.markdown("**Plano de análise:**")
                st.write(resultado.get("plano"))

            if resultado.get("explicacao"):
                st.markdown("**Explicação:**")
                st.write(resultado.get("explicacao"))

        

        #  HISTÓRICO (só se teve tentativa)
        with st.expander("🛠 Debug SQL", expanded=False):
            # 📊 STATUS
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown("**Tentativas**")
                st.write(resultado.get("tentativas", 0))
    
            with col_info2:
                st.markdown("**Erro (se houve)**")
    
                erro = resultado.get("erro")
    
                if erro == "PERGUNTA_INVALIDA":
                    st.warning("Não consegui entender essa pergunta com os dados disponíveis.")
                elif erro == "RESULTADO_VAZIO":
                    st.info("Nenhum dado encontrado com esses filtros.")
                elif erro == "SQL_INVALIDA":
                    st.error("Houve um problema ao gerar a consulta.")
                elif erro:
                    st.error(f"Erro: {erro}")
                else:
                    st.success("Consulta executada com sucesso.")


            historico = resultado.get("historico_sql", [])

            if historico:
                for i, sql in enumerate(historico, 1):
                    st.markdown(f"**Tentativa {i}:**")
                    st.code(sql, language="sql")
            else:
                st.info("Nenhuma tentativa de correção foi necessária.")

            if resultado.get("sql"):
                st.markdown("**SQL final executada:**")
                st.code(resultado.get("sql"), language="sql")

        