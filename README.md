# 🤖 Assistente Virtual de Dados

## 📌 Sobre o Projeto

Este projeto implementa um **Assistente Virtual de Dados inteligente**, capaz de interpretar perguntas em linguagem natural e gerar automaticamente consultas SQL para responder perguntas de negócio.

A solução atua como um **analista de dados júnior**, sendo capaz de:

- Entender perguntas abertas
- Explorar o banco de dados dinamicamente (sem queries fixas)
- Corrigir erros automaticamente
- Apresentar respostas em formato adequado (tabela, gráfico ou valor único)
- Mostrar transparência sobre o raciocínio (plano de análise, SQL executada, explicação)

---

## 🎯 Objetivo do Desafio

Criar um sistema capaz de:

- Traduzir linguagem natural → SQL
- Consultar um banco SQLite
- Lidar com erros de execução
- Exibir visualizações adequadas
- Mostrar como chegou à resposta

---

## 🧠 Arquitetura da Solução

A solução foi construída utilizando um fluxo baseado em **agentes com LangGraph**, dividido em etapas:

### 🔁 Fluxo do agente

1. **Entrada do usuário** → Pergunta em linguagem natural.
2. **Planejar** → Quebra a pergunta em passos de análise.
3. **Gerar SQL** → Cria a query baseada no schema dinâmico.
4. **Validação** → Se a query falhar ou não retornar dados, o sistema identifica o erro.
5. **Correção automática** → O modelo ajusta a query com base no erro e tenta novamente.
6. **Resposta final** → Retorna SQL, resultado e visualização adequada.

---

## ⚙️ Tecnologias Utilizadas

- Python
- SQLite
- Streamlit
- LangGraph
- LLM (Groq)

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
GROQ_MODEL=your_model_here
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

## 🔮 Melhorias Futuras

- Suporte a mais tipos de gráficos (pizza, stacked bar, heatmap).
- Exportar resultados para CSV/Excel.
- Cache de consultas frequentes.
- Suporte a múltiplos bancos de dados além de SQLite.
- Autenticação e controle de acesso para uso corporativo.
- Testes automatizados com conjunto de perguntas esperadas.

## ✅ Testes e Validação
O sistema foi validado com perguntas de negócio reais, verificando:
   - Se a SQL gerada é válida e executável.
   - Se erros são identificados e corrigidos automaticamente.
   - Se a resposta final é coerente com os dados.
   - Se a visualização escolhida é adequada ao tipo de pergunta.
