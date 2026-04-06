from langgraph.graph import StateGraph, END
from database.database import executar_sql
from agent.nodes import gerar_sql, corrigir_sql, gerar_resposta
from typing import TypedDict, Optional
import pandas as pd

class State(dict):
    pass

class State(TypedDict, total=False):
    pergunta: str
    schema: str
    sql: Optional[str]
    df: Optional[pd.DataFrame]
    erro: Optional[str]
    resposta: Optional[str]
    tentativas: Optional[int]


def node_gerar_sql(state):
    # print("STATE INICIAL:", state)

    pergunta = state.get("pergunta")
    schema = state.get("schema")

    if not pergunta:
        raise ValueError(f"❌ State sem pergunta: {state}")

    sql = gerar_sql(pergunta, schema)

    return {**state, "sql": sql}


def node_executar_sql(state):
    # print("DEBUG executa_sql:", state)
    try:
        df = executar_sql(state["sql"])
        return {**state, "df": df, "erro": None}
    except Exception as e:
        return {**state, "erro": str(e)}


def node_corrigir_sql(state):
    nova_sql = corrigir_sql(state["sql"], state["erro"])
    tentativas = state.get("tentativas", 0) + 1

    return {**state, "sql": nova_sql, "tentativas": tentativas}


def node_responder(state):
    resposta = gerar_resposta(state["pergunta"], state["df"])
    return {**state, "resposta": resposta}


def decidir(state):
    if state.get("erro") and state.get("tentativas", 0) < 2:
        return "corrigir"
    return "ok"


def criar_graph():
    builder = StateGraph(State)

    builder.add_node("gerar_sql", node_gerar_sql)
    builder.add_node("executar_sql", node_executar_sql)
    builder.add_node("corrigir_sql", node_corrigir_sql)

    builder.set_entry_point("gerar_sql")

    builder.add_edge("gerar_sql", "executar_sql")

    builder.add_conditional_edges(
        "executar_sql",
        decidir,
        {
            "corrigir": "corrigir_sql",
            "ok": END
        }
    )

    builder.add_edge("corrigir_sql", "executar_sql")
    return builder.compile()


def escolher_grafico(df):
    colunas = [col.lower() for col in df.columns]

    
    if any("data" in c or "mes" in c or "ano" in c for c in colunas):
        return "linha"

    # Identifica comparação simples
    if len(df.columns) == 2:
        return "barra"

    return "tabela"