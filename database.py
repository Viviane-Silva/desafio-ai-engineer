import sqlite3
import pandas as pd

con = sqlite3.connect("database/anexo_desafio_1.db")
df = pd.read_sql_query("SELECT*FROM clientes LIMIT 5" , con)
print (df)