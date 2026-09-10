# ============================================================================
# PROJETO UEPA - SISTEMA DE APOIO À DECISÃO PARA EXPANSÃO DE CURSOS
# Interface Streamlit para visualização e consulta dos resultados
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

import os
import sys

# Configurar página
st.set_page_config(
    page_title="UEPA - Expansão de Cursos",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 1. CARREGAR DADOS
# ============================================================================

@st.cache_data
def load_data():
    """Carrega todos os datasets necessários"""
    data_dir = "data"
    
    # Tentar carregar do diretório data, se não existir, usar o diretório atual
    if not os.path.exists(data_dir):
        data_dir = "."
    
    files = {
        'matriz': f"{data_dir}/55_matriz_final_auditada.csv",
        'resumo': f"{data_dir}/56_resumo_classificacoes_finais.csv",
        'implantacao': f"{data_dir}/57_implantacoes_plausiveis.csv",
        'expansao': f"{data_dir}/58_expansoes_plausiveis.csv",
        'priorizacao': f"{data_dir}/21_priorizacao_corrigida.csv",
        'shap': f"{data_dir}/33_shap_importance_by_class.csv"
    }
    
    data = {}
    for name, path in files.items():
        try:
            data[name] = pd.read_csv(path, encoding='utf-8-sig')
            st.sidebar.success(f"✅ {name}.csv carregado")
        except FileNotFoundError:
            st.sidebar.warning(f"⚠️ {name}.csv não encontrado")
            data[name] = None
    
    return data

data = load_data()

# Verificar se os dados principais foram carregados
if data['matriz'] is None:
    st.error("❌ Arquivo 55_matriz_final_auditada.csv não encontrado!")
    st.stop()

df = data['matriz']
df_implantacao = data['implantacao']
df_expansao = data['expansao']
df_resumo = data['resumo']
df_shap = data['shap']

# ============================================================================
# 2. FUNÇÕES AUXILIARES
# ============================================================================

def formatar_numero(valor):
    """Formata números para exibição"""
    if isinstance(valor, float):
        return f"{valor:.4f}"
    return str(valor)

def get_cores_prioridade():
    """Retorna o dicionário de cores por prioridade"""
    return {
        'Muito Alta': '#e74c3c',
        'Alta': '#e67e22',
        'Média': '#f1c40f',
        'Baixa': '#2ecc71'
    }

def get_cores_classificacao():
    """Retorna o dicionário de cores por classificação"""
    return {
        'Fase 1 - Prioridade Máxima para Estudo de Implantação': '#e74c3c',
        'Fase 2 - Prioridade Alta para Estudo de Implantação': '#e67e22',
        'Fase 3 - Avaliação Complementar': '#f1c40f',
        'Fase 4 - Expansão de Vagas': '#2ecc71',
        'Manutenção/Ajuste': '#3498db'
    }

# ============================================================================
# 3. SIDEBAR - NAVEGAÇÃO
# ============================================================================

st.sidebar.title("🎓 UEPA - Expansão de Cursos")
st.sidebar.markdown("---")

# Seleção de página
pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Painel Geral", "📍 Análise por Município", "📚 Análise por Curso", 
     "🏗️ Implantação", "📈 Expansão", "🔍 Explicabilidade", "🧪 Simulador"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Sistema de Apoio à Decisão v1.0")
st.sidebar.caption("Projeto UEPA - Expansão de Cursos")

# ============================================================================
# 4. PÁGINA: PAINEL GERAL
# ============================================================================

if pagina == "📊 Painel Geral":
    st.title("📊 Painel Geral - Expansão de Cursos UEPA")
    st.markdown("Visão consolidada das oportunidades de expansão da UEPA no Pará.")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Combinações", f"{len(df)}")
    with col2:
        st.metric("Cursos Ofertados", f"{len(df[df['ofertado_prosel_2026'] == True])}")
    with col3:
        st.metric("Cursos Não Ofertados", f"{len(df[df['ofertado_prosel_2026'] == False])}")
    with col4:
        st.metric("Implantações Plausíveis", f"{len(df_implantacao) if df_implantacao is not None else 0}")
    with col5:
        st.metric("Expansões Plausíveis", f"{len(df_expansao) if df_expansao is not None else 0}")
    
    st.markdown("---")
    
    # Distribuição das classificações
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Distribuição das Classificações")
        classificacao_counts = df['classificacao_final'].value_counts()
        
        fig = px.bar(
            x=classificacao_counts.values,
            y=classificacao_counts.index,
            orientation='h',
            title="Classificações Finais",
            labels={'x': 'Quantidade', 'y': 'Classificação'},
            color=classificacao_counts.index,
            color_discrete_map=get_cores_classificacao()
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Resumo")
        st.dataframe(
            df_resumo,
            column_config={
                "classificacao": "Classificação",
                "quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
                "percentual": st.column_config.NumberColumn("%", format="%.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Top municípios
    st.markdown("---")
    st.subheader("🏆 Top 10 Municípios por IP Médio")
    
    top_municipios = df.groupby('municipio')['IP'].mean().sort_values(ascending=False).reset_index()
    top_municipios.columns = ['municipio', 'ip_medio']
    
    fig = px.bar(
        top_municipios.head(10),
        x='ip_medio',
        y='municipio',
        orientation='h',
        title="IP Médio por Município",
        labels={'ip_medio': 'IP Médio', 'municipio': 'Município'},
        color='ip_medio',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top cursos
    st.markdown("---")
    st.subheader("📚 Top 10 Cursos por IP Médio")
    
    top_cursos = df.groupby('curso')['IP'].mean().sort_values(ascending=False).reset_index()
    top_cursos.columns = ['curso', 'ip_medio']
    
    fig = px.bar(
        top_cursos.head(10),
        x='ip_medio',
        y='curso',
        orientation='h',
        title="IP Médio por Curso",
        labels={'ip_medio': 'IP Médio', 'curso': 'Curso'},
        color='ip_medio',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 5. PÁGINA: ANÁLISE POR MUNICÍPIO
# ============================================================================

elif pagina == "📍 Análise por Município":
    st.title("📍 Análise por Município")
    st.markdown("Visualize as oportunidades de expansão para cada município.")
    
    # Selecionar município
    municipios = sorted(df['municipio'].unique())
    municipio_selecionado = st.selectbox("Selecione um município", municipios)
    
    if municipio_selecionado:
        df_municipio = df[df['municipio'] == municipio_selecionado]
        
        # Métricas do município
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ip_medio = df_municipio['IP'].mean()
            st.metric("IP Médio", f"{ip_medio:.4f}")
        with col2:
            ofertados = len(df_municipio[df_municipio['ofertado_prosel_2026'] == True])
            st.metric("Cursos Ofertados", f"{ofertados}")
        with col3:
            nao_ofertados = len(df_municipio[df_municipio['ofertado_prosel_2026'] == False])
            st.metric("Cursos Não Ofertados", f"{nao_ofertados}")
        with col4:
            prioridade = df_municipio['prioridade_final'].value_counts().index[0]
            st.metric("Prioridade Principal", prioridade)
        
        st.markdown("---")
        
        # Distribuição de prioridades
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribuição das Prioridades")
            prioridades = df_municipio['prioridade_final'].value_counts()
            fig = px.pie(
                values=prioridades.values,
                names=prioridades.index,
                title=f"Prioridades - {municipio_selecionado}",
                color=prioridades.index,
                color_discrete_map=get_cores_prioridade()
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Classificações Finais")
            classificacoes = df_municipio['classificacao_final'].value_counts()
            fig = px.pie(
                values=classificacoes.values,
                names=classificacoes.index,
                title=f"Classificações - {municipio_selecionado}",
                color=classificacoes.index,
                color_discrete_map=get_cores_classificacao()
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Tabela de cursos
        st.subheader(f"📋 Cursos - {municipio_selecionado}")
        
        display_cols = ['curso', 'IP', 'prioridade_final', 'decisao_final', 'classificacao_final']
        display_cols = [c for c in display_cols if c in df_municipio.columns]
        
        st.dataframe(
            df_municipio[display_cols].sort_values('IP', ascending=False),
            column_config={
                "IP": st.column_config.NumberColumn("IP", format="%.4f"),
                "prioridade_final": "Prioridade",
                "decisao_final": "Decisão",
                "classificacao_final": "Classificação"
            },
            hide_index=True,
            use_container_width=True
        )

# ============================================================================
# 6. PÁGINA: ANÁLISE POR CURSO
# ============================================================================

elif pagina == "📚 Análise por Curso":
    st.title("📚 Análise por Curso")
    st.markdown("Visualize as oportunidades de expansão para cada curso.")
    
    # Selecionar curso
    cursos = sorted(df['curso'].unique())
    curso_selecionado = st.selectbox("Selecione um curso", cursos)
    
    if curso_selecionado:
        df_curso = df[df['curso'] == curso_selecionado]
        
        # Métricas do curso
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ip_medio = df_curso['IP'].mean()
            st.metric("IP Médio", f"{ip_medio:.4f}")
        with col2:
            ofertados = len(df_curso[df_curso['ofertado_prosel_2026'] == True])
            st.metric("Municípios com Oferta", f"{ofertados}")
        with col3:
            nao_ofertados = len(df_curso[df_curso['ofertado_prosel_2026'] == False])
            st.metric("Municípios sem Oferta", f"{nao_ofertados}")
        with col4:
            prioridade = df_curso['prioridade_final'].value_counts().index[0]
            st.metric("Prioridade Principal", prioridade)
        
        st.markdown("---")
        
        # IP por município
        st.subheader(f"IP do Curso por Município")
        
        df_curso_plot = df_curso[['municipio', 'IP', 'prioridade_final']].sort_values('IP', ascending=False)
        
        fig = px.bar(
            df_curso_plot,
            x='IP',
            y='municipio',
            orientation='h',
            title=f"IP de {curso_selecionado} por Município",
            labels={'IP': 'IP', 'municipio': 'Município'},
            color='prioridade_final',
            color_discrete_map=get_cores_prioridade()
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Tabela de municípios
        st.subheader(f"📋 Municípios - {curso_selecionado}")
        
        display_cols = ['municipio', 'IP', 'prioridade_final', 'decisao_final', 'classificacao_final']
        display_cols = [c for c in display_cols if c in df_curso.columns]
        
        st.dataframe(
            df_curso[display_cols].sort_values('IP', ascending=False),
            column_config={
                "IP": st.column_config.NumberColumn("IP", format="%.4f"),
                "prioridade_final": "Prioridade",
                "decisao_final": "Decisão",
                "classificacao_final": "Classificação"
            },
            hide_index=True,
            use_container_width=True
        )

# ============================================================================
# 7. PÁGINA: IMPLANTAÇÃO
# ============================================================================

elif pagina == "🏗️ Implantação":
    st.title("🏗️ Oportunidades de Implantação")
    st.markdown("Cursos não ofertados com alta prioridade para estudo de implantação.")
    
    if df_implantacao is not None and len(df_implantacao) > 0:
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            prioridades = ['Todos'] + sorted(df_implantacao['prioridade_final'].unique().tolist())
            prioridade_filtro = st.selectbox("Filtrar por Prioridade", prioridades)
        
        with col2:
            municipios = ['Todos'] + sorted(df_implantacao['municipio'].unique().tolist())
            municipio_filtro = st.selectbox("Filtrar por Município", municipios)
        
        # Aplicar filtros
        df_filtrado = df_implantacao.copy()
        if prioridade_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['prioridade_final'] == prioridade_filtro]
        if municipio_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_filtro]
        
        st.markdown("---")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Oportunidades", f"{len(df_filtrado)}")
        with col2:
            st.metric("Prioridade Máxima", f"{len(df_filtrado[df_filtrado['prioridade_final'] == 'Muito Alta'])}")
        with col3:
            st.metric("Prioridade Alta", f"{len(df_filtrado[df_filtrado['prioridade_final'] == 'Alta'])}")
        
        st.markdown("---")
        
        # Tabela
        st.subheader("📋 Candidatos à Implantação")
        
        display_cols = ['municipio', 'curso', 'IP', 'prioridade_final', 'decisao_final']
        display_cols = [c for c in display_cols if c in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[display_cols].sort_values('IP', ascending=False),
            column_config={
                "IP": st.column_config.NumberColumn("IP", format="%.4f"),
                "prioridade_final": "Prioridade",
                "decisao_final": "Decisão"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Dados de implantação não disponíveis.")

# ============================================================================
# 8. PÁGINA: EXPANSÃO
# ============================================================================

elif pagina == "📈 Expansão":
    st.title("📈 Oportunidades de Expansão de Vagas")
    st.markdown("Cursos já ofertados com recomendação de expansão de vagas.")
    
    if df_expansao is not None and len(df_expansao) > 0:
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            municipios = ['Todos'] + sorted(df_expansao['municipio'].unique().tolist())
            municipio_filtro = st.selectbox("Filtrar por Município", municipios)
        
        with col2:
            cursos = ['Todos'] + sorted(df_expansao['curso'].unique().tolist())
            curso_filtro = st.selectbox("Filtrar por Curso", cursos)
        
        # Aplicar filtros
        df_filtrado = df_expansao.copy()
        if municipio_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_filtro]
        if curso_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['curso'] == curso_filtro]
        
        st.markdown("---")
        
        # Métricas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Expansões", f"{len(df_filtrado)}")
        with col2:
            st.metric("Municípios Atendidos", f"{df_filtrado['municipio'].nunique()}")
        
        st.markdown("---")
        
        # Tabela
        st.subheader("📋 Candidatos à Expansão de Vagas")
        
        display_cols = ['municipio', 'curso', 'IP', 'prioridade_final', 'decisao_final']
        display_cols = [c for c in display_cols if c in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[display_cols].sort_values('IP', ascending=False),
            column_config={
                "IP": st.column_config.NumberColumn("IP", format="%.4f"),
                "prioridade_final": "Prioridade",
                "decisao_final": "Decisão"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Dados de expansão não disponíveis.")

# ============================================================================
# 9. PÁGINA: EXPLICABILIDADE
# ============================================================================

elif pagina == "🔍 Explicabilidade":
    st.title("🔍 Explicabilidade do Modelo")
    st.markdown("Interpretação das variáveis que influenciam as decisões de priorização.")
    
    if df_shap is not None:
        st.info("📌 SHAP representa contribuição do modelo, não causalidade.")
        
        # Importância por classe
        st.subheader("Importância das Variáveis por Classe")
        
        fig = px.bar(
            df_shap,
            x='mean_abs_shap',
            y='feature',
            color='classe',
            orientation='h',
            title="SHAP Feature Importance por Classe",
            labels={'mean_abs_shap': 'Mean |SHAP value|', 'feature': 'Variável'},
            barmode='group'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela
        st.subheader("📋 Importância das Variáveis")
        
        df_shap_pivot = df_shap.pivot(index='feature', columns='classe', values='mean_abs_shap')
        df_shap_pivot['Média'] = df_shap_pivot.mean(axis=1)
        df_shap_pivot = df_shap_pivot.sort_values('Média', ascending=False)
        
        st.dataframe(
            df_shap_pivot,
            column_config={col: st.column_config.NumberColumn(col, format="%.4f") for col in df_shap_pivot.columns},
            use_container_width=True
        )
        
        st.markdown("---")
        st.caption("SHAP (SHapley Additive exPlanations) - Método de interpretação de modelos de Machine Learning.")
    else:
        st.warning("Dados SHAP não disponíveis.")

# ============================================================================
# 10. PÁGINA: SIMULADOR
# ============================================================================

elif pagina == "🧪 Simulador":
    st.title("🧪 Simulador de Prioridade")
    st.markdown("Simule a prioridade de uma combinação município-curso com diferentes cenários.")
    
    st.warning("⚠️ Esta é uma simulação baseada nos parâmetros do IP. Os resultados são indicativos.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        municipio = st.selectbox("Município", sorted(df['municipio'].unique()))
        curso = st.selectbox("Curso", sorted(df['curso'].unique()))
    
    with col2:
        # Parâmetros para simulação
        demanda = st.slider("Demanda (D4)", 0.0, 1.0, 0.5, 0.05)
        necessidade = st.slider("Necessidade Social", 0.0, 1.0, 0.5, 0.05)
        aderencia = st.slider("Aderência Setorial", 0.0, 1.0, 0.5, 0.05)
        concorrencia = st.slider("Concorrência", 0.0, 1.0, 0.5, 0.05)
    
    # Calcular IP simulado
    # Pesos do IP
    pesos = {'demanda': 0.30, 'social': 0.25, 'setor': 0.20, 'concorrencia': 0.25}
    
    ip_simulado = (
        pesos['demanda'] * demanda +
        pesos['social'] * necessidade +
        pesos['setor'] * aderencia +
        pesos['concorrencia'] * (1 - concorrencia)
    )
    
    # Classificação
    if ip_simulado >= 0.75:
        classificacao = "Muito Alta"
        cor = "#e74c3c"
    elif ip_simulado >= 0.50:
        classificacao = "Alta"
        cor = "#e67e22"
    elif ip_simulado >= 0.25:
        classificacao = "Média"
        cor = "#f1c40f"
    else:
        classificacao = "Baixa"
        cor = "#2ecc71"
    
    st.markdown("---")
    
    # Resultado da simulação
    st.subheader("📊 Resultado da Simulação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("IP Simulado", f"{ip_simulado:.4f}")
    with col2:
        st.metric("Classificação", classificacao)
    with col3:
        st.metric("Combinação", f"{municipio} - {curso}")
    
    # Visualização do IP
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ip_simulado * 100,
        title={'text': "IP Simulado (%)"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': cor},
            'steps': [
                {'range': [0, 25], 'color': "#2ecc71"},
                {'range': [25, 50], 'color': "#f1c40f"},
                {'range': [50, 75], 'color': "#e67e22"},
                {'range': [75, 100], 'color': "#e74c3c"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': ip_simulado * 100
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.caption("Simulador baseado nos pesos do Índice de Priorização (IP) do projeto UEPA.")

# ============================================================================
# 11. FOOTER
# ============================================================================

st.markdown("---")
st.caption("Projeto UEPA - Expansão de Cursos | Sistema de Apoio à Decisão")