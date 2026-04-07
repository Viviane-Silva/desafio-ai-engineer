from langgraph.graph import StateGraph, END
from database.database import executar_sql
from agents.nodes import gerar_sql, corrigir_sql, gerar_resposta, planejar
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

def node_planejar(state):
    pergunta = state.get("pergunta")

    plano = planejar(pergunta)

    return {**state, "plano": plano}    


def node_gerar_sql(state):
    # print("STATE INICIAL:", state)

    pergunta = state.get("pergunta")
    schema = state.get("schema")
    plano  = state.get("plano")

    if not pergunta:
        raise ValueError(f"❌ State sem pergunta: {state}")

    sql = gerar_sql(pergunta, schema, plano)

    return {**state, "sql": sql}


def node_executar_sql(state):
    # print("DEBUG executa_sql:", state)
    try:
        df = executar_sql(state["sql"])
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
    erro = state["erro"]

    if erro == "RESULTADO_VAZIO":
        prompt_erro = "A query não retornou dados. Revise os filtros (datas, canal, etc)."
    else:
        prompt_erro = erro

    nova_sql = corrigir_sql(state["sql"], state["erro"])
    tentativas = state.get("tentativas", 0) + 1

    return {**state, "sql": nova_sql, "tentativas": tentativas}


def node_responder(state):
    df = state.get("df")

    if df is None or df.empty:
        return {
            **state,
            "resposta": "Não foram encontrados dados para essa pergunta."
        }

    resposta = gerar_resposta(state["pergunta"], state["df"])

    df = state.get("df")

    if df is None or df.empty:
        return {
            **state,
            "resposta": "Não foram encontrados dados para essa pergunta."
        }
    return {**state, "resposta": resposta}


def decidir(state):
    if state.get("erro") and state.get("tentativas", 0) < 2:
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

    # Identifica comparação simples
    if len(df.columns) == 2:
        return "barra"

    return "tabela"

def validar_sql(sql: str):
    sql = sql.strip().lower()

    if not sql.startswith("select"):
        return False

    if "```" in sql:
        return False

    return True