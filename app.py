import streamlit as st
from database import database as db
from agents.graph import criar_graph


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


@st.cache_data
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
                "tentativas": 0
            })

        # 🧠 RESPOSTA
        st.subheader("Resposta")
        st.write(resultado.get("resposta"))

        # 📊 DADOS (com tratamento correto)
        if resultado.get("df") is not None:
            df = resultado["df"]

            # 🔥 métrica única
            if df.shape == (1, 1):
                valor = df.iloc[0, 0]
                st.metric(label="Resultado", value=valor)
            else:
                st.dataframe(df)

        # 📈 VISUALIZAÇÃO
        if resultado.get("visualizacao"):
            visu = resultado["visualizacao"]
            tipo = visu.get("tipo")
            df_plot = visu.get("df_plot")

            if df_plot is not None and len(df_plot) > 1:
                if tipo == "linha":
                    st.line_chart(df_plot)
                elif tipo == "barra":
                    st.bar_chart(df_plot)
                elif tipo == "tabela":
                    st.dataframe(df_plot)

        # 🔍 EXPLICAÇÃO (fora do visualizacao!)
        with st.expander("🔍 Como cheguei nessa resposta", expanded=False):

            if resultado.get("plano"):
                st.markdown("**Plano de análise:**")
                st.write(resultado.get("plano"))

            if resultado.get("explicacao"):
                st.markdown("**Explicação:**")
                st.write(resultado.get("explicacao"))

            if resultado.get("sql"):
                st.markdown("**SQL utilizada:**")
                st.code(resultado.get("sql"), language="sql")

        # 📊 STATUS
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Tentativas**")
            st.write(resultado.get("tentativas", 0))

        with col2:
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

        # 📜 HISTÓRICO (só se teve tentativa)
        if resultado.get("tentativas", 0) > 0:
            st.markdown("### Histórico de SQL")
            for sql in resultado.get("historico_sql", []):
                st.code(sql, language="sql")