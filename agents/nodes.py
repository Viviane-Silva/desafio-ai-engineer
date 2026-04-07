from llm.client import ask_llm


def planejar(pergunta):
    prompt = f"""
    Quebre a pergunta em passos simples de análise de dados.

    Pergunta:
    {pergunta}

    Retorne lista de passos.
    """

    resposta = ask_llm(prompt)
    return resposta

def limpar_sql(sql):
    return sql.replace("```sql", "").replace("```", "").strip()


def gerar_sql(pergunta, schema, plano=None):
    prompt = f"""
    Você é especialista em SQL SQLite.

    Estrutura do banco:
    {schema}

    Gere uma query SQL para responder:
    {pergunta}

    Regras:

    - Use apenas tabelas e colunas do schema
    - Use JOIN apenas se necessário
    - Clientes → COUNT(DISTINCT cliente_id)
    - Compras/Reclamações → COUNT(*)
    - Use LOWER() para comparações de texto
    - Se não houver ano, filtre apenas por mês
    - "top N" → use LIMIT N
    - "quais/liste" → não use LIMIT
    - Retorne APENAS SQL
    - Se a pergunta não corresponder aos dados do schema, retornar:
       "Indisponível."
    """

    sql = ask_llm(prompt)
    return limpar_sql(sql)


def corrigir_sql(sql, erro):
    prompt = f"""
    A query abaixo deu erro:

    {sql}

    Erro:
    {erro}

    Corrija a query SQL.
    Retorne apenas SQL válida.
    """

    return limpar_sql(ask_llm(prompt))


def gerar_resposta(pergunta, df):
    preview = df.head().to_string()

    prompt = f"""
    Pergunta: {pergunta}

    Resultado:
    {preview}

    """

    return ask_llm(prompt)

