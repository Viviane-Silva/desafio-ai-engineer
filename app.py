import streamlit as st
import matplotlib.pyplot as plt
import database.database as db
from agents.graph import criar_graph, preparar_df_grafico


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
            if df.shape == (1, 1):
                # já mostramos a resposta acima, não precisa renderizar tabela/gráfico
                pass 
            else:
                tipo = resultado.get("visualizacao", "tabela").lower()

                # normaliza possíveis respostas em inglês
                if tipo in ["line", "linha"]:
                    tipo = "linha"
                elif tipo in ["bar", "barra"]:
                    tipo = "barra"
                elif tipo in ["pie", "pizza"]:
                    tipo = "pizza"
                elif tipo in ["table", "tabela"]:
                    tipo = "tabela"


                # prepara df para gráfico
                df_plot = preparar_df_grafico(df, tipo)
        
                if tipo == "linha":
                    if df_plot.empty:
                        st.warning("Não há dados numéricos suficientes para o gráfico.")
                    else:
                        st.line_chart(df_plot)
        
                elif tipo == "barra":
                    if df_plot.empty:
                        st.dataframe(df)
                    else:
                        st.bar_chart(df_plot)
        
                elif tipo == "pizza":
                    if df_plot.empty or df_plot.iloc[:, 0].isna().all():
                        st.dataframe(df)
                    else:
                        fig, ax = plt.subplots()
                        ax.pie(df_plot.iloc[:, 0], labels=df_plot.index, autopct='%1.1f%%')
                        st.pyplot(fig)
        
                else:
                    # fallback: tabela
                    st.dataframe(df)
        

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

        