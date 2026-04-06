import sqlite3
import pandas as pd


DB_PATH = "database/anexo_desafio_1.db"

def conectar_banco():
    return sqlite3.connect(DB_PATH)

def listar_tabelas():
    con = conectar_banco()
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [t[0] for t in cursor.fetchall()]
    con.close()
    return tabelas

def schema_tabela(nome):
    con = conectar_banco()
    df = pd.read_sql_query(f"PRAGMA table_info({nome});", con)
    con.close()
    return df

def executar_sql(sql):
    con = conectar_banco()
    df = pd.read_sql_query(sql, con)
    con.close()
    return df