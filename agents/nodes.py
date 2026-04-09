from llm.client import ask_llm
import re

# ----------------------
# Planejamento da pergunta
# ----------------------
def planejar(pergunta):
    prompt = f"""
    Quebre a pergunta em passos simples de análise de dados.

    Pergunta:
    {pergunta}

    Retorne apenas a lista de passos, sem explicações longas.
    Cada passo deve ter uma frase curta e objetiva.
    """
    return ask_llm(prompt)

# ----------------------
# Limpeza e normalização de SQL
# ----------------------
def limpar_sql(sql):
    if not sql:
        return ""
    # remove markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()
    # pega apenas SELECT
    match = re.search(r"(select .*?;)", sql, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1)
    else:
        if "select" in sql.lower():
            sql = sql[sql.lower().find("select"):]
    # remove múltiplos espaços
    sql = re.sub(r"\s+", " ", sql)
    return sql.strip()

def aplicar_lower_trim(sql):
    def repl(match):
        coluna = match.group(1)
        valor = match.group(2).lower()
        return f"LOWER(TRIM({coluna})) = '{valor}'"

    return re.sub(
        r"(\w+\.\w+)\s*=\s*'([^']+)'",
        repl,
        sql,
        flags=re.IGNORECASE
    )

# ----------------------
# Geração de SQL
# ----------------------
def gerar_sql(pergunta, schema, plano=None):
    BASE_RULES = """
    - Retorne SOMENTE SQL
    - Use apenas o schema fornecido
    - Use LOWER(TRIM()) para texto
    - Use GROUP BY corretamente
    - Use ORDER BY DESC quando fizer sentido
    - Use LIMIT apenas se explicitamente pedido
    - Para clientes: COUNT(DISTINCT cliente_id)
    - Para datas: STRFTIME
    - Se não for possível responder, retorne 'INDISPONIVEL'
    """
    prompt = f"""
    Você é especialista em SQL SQLite.

    Gere uma query SQL válida e executável.

    Regras:
    {BASE_RULES}

    Schema:
    {schema}

    Pergunta:
    {pergunta}

    Plano:
    {plano}

    SQL:
    """
    sql = ask_llm(prompt)
    sql = limpar_sql(sql)
    sql = aplicar_lower_trim(sql)

    if sql.upper() == "INDISPONIVEL":
        return "INDISPONIVEL"

    return sql

# ----------------------
# Correção de SQL
# ----------------------
def corrigir_sql(sql_atual, prompt_erro, schema):
    prompt = f"""
    A query abaixo deu erro no SQLite:

    Query:
    {sql_atual}

    Erro:
    {prompt_erro}

    Schema:
    {schema}

    Corrija a query garantindo:
    - Identifique exatamente o problema
    - Corrija a query sem inventar colunas
    - Use apenas colunas que EXISTEM no schema
    - Corrija tabelas ou joins se necessário
    - NÃO repita a mesma query
    - Retorne apenas SQL válida

    SQL corrigido:
    """
    return limpar_sql(ask_llm(prompt))

# ----------------------
# Geração de resposta
# ----------------------
def gerar_resposta(pergunta, df):
    if df.shape == (1, 1):
        valor = df.iloc[0, 0]
        prompt = f"""
        Pergunta: {pergunta}

        Resultado obtido: {valor}

        Responda de forma direta e objetiva.
        Use exatamente o valor retornado.
        """
    else:
        preview = df.head(10).to_string()
        prompt = f"""
        Pergunta: {pergunta}

        Resultado (dados reais):
        {preview}

        Gere uma resposta curta e objetiva baseada nesses dados.
        """
    return ask_llm(prompt)

# ----------------------
# Explicação da resposta
# ----------------------
def explicar_resposta(pergunta, sql):
    prompt = f"""
    Explique de forma simples e curta como a query abaixo responde à pergunta.
    Seja direto e didático. 
    Retorne apenas explicação objetiva, sem conclusões adicionais e em português.

    Pergunta:
    {pergunta}

    SQL:
    {sql}

     Regras adicionais:
    - Se a pergunta envolver proporções ou participação, destaque que a query mostra a distribuição relativa por categoria.
    - Use termos como 'comparação', 'participação' ou 'proporção' para deixar claro o sentido.
    - Evite conclusões extras, apenas explique como os dados respondem à pergunta.

    Explicação:
    """
    return ask_llm(prompt)

# ----------------------
# Escolher visualização
# ----------------------
def escolher_visualizacao(pergunta, df):
    preview = df.head(10).to_string()
    prompt = f"""
    Pergunta: {pergunta}

    Dados disponíveis:
    {preview}

     Escolha a melhor forma de visualização:
    - tabela → quando a pergunta pede listagem ou ordenação
    - barra → quando a pergunta compara categorias
    - linha → quando há tendência temporal (datas, meses, anos)
    - pizza → quando a pergunta envolve proporções ou participação

    Retorne apenas UMA palavra em português: tabela, barra, linha ou pizza.
    """
    return ask_llm(prompt).strip().lower()
