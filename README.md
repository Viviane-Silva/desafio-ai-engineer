# 🤖 Assistente Virtual de Dados

## 📌 Sobre o Projeto

Este projeto implementa um **Assistente Virtual de Dados inteligente**, capaz de interpretar perguntas em linguagem natural e gerar automaticamente consultas SQL para responder perguntas de negócio.

A solução atua como um **analista de dados júnior**, sendo capaz de:

- Entender perguntas abertas
- Explorar o banco de dados dinamicamente (sem queries fixas)
- Corrigir erros automaticamente
- Apresentar respostas em formato adequado (tabela, gráfico ou valor único)

---

## 🎯 Objetivo do Desafio

Criar um sistema capaz de:

- Traduzir linguagem natural → SQL
- Consultar um banco SQLite
- Lidar com erros de execução
- Exibir visualizações adequadas

---

## 🧠 Arquitetura da Solução

A solução foi construída utilizando um fluxo baseado em **agentes com LangGraph**, dividido em etapas:

### 🔁 Fluxo do agente

1. **Entrada do usuário**
   - Pergunta em linguagem natural

2. **Geração de SQL**
   - O modelo interpreta a pergunta + schema do banco
   - Gera uma query SQL válida

3. **Execução da query**
   - Consulta no SQLite
   - Retorna DataFrame

4. **Validação**
   - Se erro → entra no loop de correção automática

5. **Correção automática**
   - O modelo ajusta a query com base no erro retornado

6. **Resposta final**
   - Retorna:
     - SQL gerada
     - Resultado
     - Visualização adequada

---

## ⚙️ Tecnologias Utilizadas

- Python
- SQLite
- Streamlit
- LangGraph
- LLM (Groq )

---

## 🚀 Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/Viviane-Silva/desafio-ai-engineer
cd desafio-ai-engineer
```

### 2. Criar ambiente virtual

```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```
GROQ_API_KEY=your_key_here
```

### 5. Rodar aplicação

```
streamlit run app.py
```

## 💬 Exemplos de Perguntas

- "Liste os 5 estados com maior número de clientes que compraram via app em maio"
- "Quantos clientes interagiram com campanhas de WhatsApp em 2024?"
- "Qual o número de reclamações não resolvidas por canal?"
- "Qual a tendência de reclamações por canal no último ano?"
