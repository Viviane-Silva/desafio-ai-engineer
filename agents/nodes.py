from llm.client import ask_llm


def planejar(pergunta):
    prompt = f"""
    Quebre a pergunta em passos simples de análise de dados.

    Pergunta:
    {pergunta}

    Retorne lista de passos.
    """
    return ask_llm(prompt)


def limpar_sql(sql):
    if not sql:
        return ""

    sql = sql.replace("```sql", "").replace("```", "").strip()

    # garante que começa no SELECT
    if "select" in sql.lower():
        sql = sql[sql.lower().find("select"):]

    return sql.strip()


def gerar_sql(pergunta, schema, plano=None):

    BASE_RULES = """
    - Use apenas tabelas do schema
    - Normalize textos com LOWER(TRIM())
    - Datas estão no formato YYYY-MM-DD
    - Use STRFTIME('%m') para mês
    - Toda comparação de texto deve usar LOWER(TRIM(coluna))
    - Retorne apenas SQL
    - Se não souber: INDISPONIVEL
    """

    prompt = f"""
    Gere uma query SQL (SQLite).

    Schema:
    {schema}

    Pergunta:
    {pergunta}

    Plano:
    {plano}

    Regras:
    {BASE_RULES}

    SQL:
    """

    sql = ask_llm(prompt)
    sql = limpar_sql(sql)

    if sql.upper() == "INDISPONIVEL":
        return "INDISPONIVEL"

    return sql


def corrigir_sql(sql_atual, prompt_erro, schema):
    prompt = f"""
    A query abaixo deu erro:

    {sql_atual}

    Erro:
    {prompt_erro}

    Schema:
    {schema}

    Corrija a query SQL.

    Regras:
    - Retorne APENAS SQL
    - NÃO explique nada
    - NÃO escreva texto
    - NÃO use markdown
    - NÃO use ```
    - Não invente colunas

    SQL:
    """

    return limpar_sql(ask_llm(prompt))


def gerar_resposta(pergunta, df):
    preview = df.head().to_string()

    prompt = f"""
    Pergunta: {pergunta}

    Resultado (amostra):
    {preview}

    Responda de forma objetiva, em português.
    Destaque números importantes se houver.
    Não invente informações.
    """

    return ask_llm(prompt)


def explicar_resposta(pergunta, sql):
    prompt = f"""
    Explique de forma simples e curta como a query responde a pergunta.

    Pergunta:
    {pergunta}

    SQL:
    {sql}

    Seja direto e didático.
    """

    return ask_llm(prompt)