from langgraph.graph import StateGraph, END
from database.database import executar_sql
from agents.nodes import gerar_sql, corrigir_sql, gerar_resposta, planejar, explicar_resposta
from typing import TypedDict, Optional
import pandas as pd


class State(TypedDict, total=False):
    pergunta: str
    schema: str
    plano: str
    sql: Optional[str]
    df: Optional[pd.DataFrame]
    erro: Optional[str]
    resposta: Optional[str]
    tentativas: Optional[int]
    historico_sql: Optional[list[str]]


def node_planejar(state):
    pergunta = state.get("pergunta")
    plano = planejar(pergunta)
    return {**state, "plano": plano}


def node_gerar_sql(state):
    pergunta = state.get("pergunta")
    schema = state.get("schema")
    plano = state.get("plano")

    if not pergunta:
        raise ValueError(f"❌ State sem pergunta: {state}")

    sql = gerar_sql(pergunta, schema, plano)

    # 🔥 tratamento de indisponível
    if sql == "INDISPONIVEL":
        return {**state, "erro": "PERGUNTA_INVALIDA"}

    historico = list(state.get("historico_sql", []))
    historico.append(sql)

    return {**state, "sql": sql, "historico_sql": historico}


def node_executar_sql(state):
    sql = state.get("sql")

    if not validar_sql(sql):
        return {**state, "erro": "SQL_INVALIDA"}

    try:
        df = executar_sql(sql)

        if df.empty:
            return {
                **state,
                "df": df,
                "erro": "RESULTADO_VAZIO"
            }

        return {**state, "df": df, "erro": None}

    except Exception as e:
        return {**state, "erro": str(e)}


def node_corrigir_sql(state):
    erro = state.get("erro")
    sql_atual = state.get("sql")
    schema = state.get("schema")

    if erro == "RESULTADO_VAZIO":
        prompt_erro = "A query não retornou dados. Revise filtros (datas, canal, etc)."
    else:
        prompt_erro = erro

    nova_sql = corrigir_sql(sql_atual, prompt_erro, schema)

    tentativas = state.get("tentativas", 0) + 1

    historico = list(state.get("historico_sql", []))
    historico.append(nova_sql)

    return {
        **state,
        "sql": nova_sql,
        "tentativas": tentativas,
        "historico_sql": historico
    }


def node_responder(state):
    df = state.get("df")

    if df is None or df.empty:
        return {
            **state,
            "resposta": "Não foram encontrados dados para essa pergunta."
        }

    resposta = gerar_resposta(state["pergunta"], df)
    explicacao = explicar_resposta(state["pergunta"], state["sql"])

    tipo = escolher_grafico(df)
    visualizacao = {"tipo": tipo}

    if tipo in ["linha", "barra"]:
        df_plot = df.copy()
        df_plot = df_plot.set_index(df_plot.columns[0])
        visualizacao["df_plot"] = df_plot

    elif tipo == "tabela":
        visualizacao["df_plot"] = df

    else:
        visualizacao["df_plot"] = None

    return {
        **state,
        "resposta": resposta,
        "explicacao": explicacao,
        "visualizacao": visualizacao
    }


def decidir(state):
    erro = state.get("erro")
    tentativas = state.get("tentativas", 0)

    if erro == "PERGUNTA_INVALIDA":
        return "ok"

    if erro == "RESULTADO_VAZIO":
        return "ok"

    if erro and tentativas < 2:
        return "corrigir"

    return "ok"


def criar_graph():
    builder = StateGraph(State)

    builder.add_node("planejar", node_planejar)
    builder.add_node("gerar_sql", node_gerar_sql)
    builder.add_node("executar_sql", node_executar_sql)
    builder.add_node("corrigir_sql", node_corrigir_sql)
    builder.add_node("responder", node_responder)

    builder.set_entry_point("planejar")

    builder.add_edge("planejar", "gerar_sql")
    builder.add_edge("gerar_sql", "executar_sql")

    builder.add_conditional_edges(
        "executar_sql",
        decidir,
        {
            "corrigir": "corrigir_sql",
            "ok": "responder"
        }
    )

    builder.add_edge("corrigir_sql", "executar_sql")
    builder.add_edge("responder", END)

    return builder.compile()


def escolher_grafico(df):
    colunas = [col.lower() for col in df.columns]

    if any("data" in c or "mes" in c or "ano" in c for c in colunas):
        return "linha"

    if len(df.columns) > 2:
        segunda = df.columns[1]
        if df[segunda].dtype in ["int64", "float64"]:
            return "barra"

    return "tabela"



def validar_sql(sql: str):
    if not sql:
        return False

    sql = sql.strip().lower()

    # remove possíveis comentários ou textos antes
    if "select" not in sql:
        return False

    if not sql.lstrip().startswith("select"):
        return False

    if any(p in sql for p in ["drop", "delete", "update", "insert"]):
        return False

    return True