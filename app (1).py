# -*- coding: utf-8 -*-
"""
Dashboard de Análise de CSAT Negativo
Rode local com: streamlit run app.py
Ou publique de graça no Streamlit Community Cloud (streamlit.io/cloud).
"""

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import streamlit as st

st.set_page_config(page_title="CSAT Negativo", page_icon="📊", layout="wide")

# ==================================================================
# TEMA ESCURO — CSS
# ==================================================================
ACCENT = "#FF7A1A"
BG = "#0B0B0D"
BG_CARD = "#151517"
BG_CARD_2 = "#1B1B1E"
BORDER = "#2A2A2E"
TEXT = "#E8E8EA"
TEXT_MUTED = "#9A9AA0"

plt.rcParams["figure.facecolor"] = BG_CARD
plt.rcParams["axes.facecolor"] = BG_CARD
plt.rcParams["savefig.facecolor"] = BG_CARD
plt.rcParams["text.color"] = TEXT
plt.rcParams["axes.edgecolor"] = BORDER
plt.rcParams["axes.labelcolor"] = TEXT
plt.rcParams["xtick.color"] = TEXT_MUTED
plt.rcParams["ytick.color"] = TEXT_MUTED
plt.rcParams["font.size"] = 10
PALETTE = ["#FF7A1A", "#4472C4", "#5AC8A8", "#C97BD6", "#E0C341",
           "#6C8EBF", "#D65D5D", "#8CC152", "#A0A0A8", "#3EC1D3"]

st.markdown(f"""
<style>
.stApp {{
    background-color: {BG};
    color: {TEXT};
}}
section[data-testid="stSidebar"] {{
    background-color: {BG_CARD};
    border-right: 1px solid {BORDER};
}}
div[data-testid="stMetric"] {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 16px;
}}
div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; }}
div[data-testid="stMetricValue"] {{ color: {TEXT}; }}
.card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
}}
.card-title {{
    color: {TEXT_MUTED};
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}
.card-value {{
    color: {TEXT};
    font-size: 1rem;
    line-height: 1.5;
}}
.badge {{
    display: inline-block;
    background-color: rgba(255,122,26,0.15);
    color: {ACCENT};
    border: 1px solid {ACCENT};
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}}
.section-label {{
    color: {ACCENT};
    font-weight: 700;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 6px;
    margin-bottom: 14px;
    margin-top: 6px;
}}
.hr-soft {{ border-top: 1px solid {BORDER}; margin: 18px 0; }}
h1, h2, h3 {{ color: {TEXT}; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{
    background-color: {BG_CARD};
    border-radius: 8px 8px 0 0;
    color: {TEXT_MUTED};
    padding: 8px 16px;
}}
.stTabs [aria-selected="true"] {{
    color: {ACCENT} !important;
    border-bottom: 2px solid {ACCENT} !important;
}}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Dados de exemplo (usados até você subir os CSVs reais)
# ------------------------------------------------------------------
def gerar_dados_exemplo():
    rng = np.random.default_rng(42)
    periodos = ["11/2025", "12/2025", "01/2026"]
    canais = ["Digital", "Telefônico"]
    atendentes = ["Ana Souza", "Bruno Lima", "Carla Dias", "Diane C.", "Lucas Sabino", "Vitor Tanus"]
    superiores = {
        "Ana Souza": "Helio Marcelo Silva Reis", "Bruno Lima": "Helio Marcelo Silva Reis",
        "Carla Dias": "Fernanda Nogueira", "Diane C.": "Fernanda Nogueira",
        "Lucas Sabino": "Helio Marcelo Silva Reis", "Vitor Tanus": "Fernanda Nogueira",
    }
    motivos = [
        "Interrupção do serviço/quedas constantes",
        "Falta de suporte adequado",
        "Prazo de atendimento muito longo",
        "Descumprimento de prazo informado",
        "Falta de empatia/humanização",
        "Encerramento brusco do atendimento",
        "Não aplicável",
    ]
    tipos_insatisfacao = ["Atendimento", "Produto/Serviço", "Prazo", "Cobrança", "Outros"]
    linhas = []
    _id = 16750000
    for p in periodos:
        for canal in canais:
            n_casos = rng.integers(8, 20)
            for _ in range(n_casos):
                motivo = rng.choice(motivos, p=[0.30, 0.15, 0.20, 0.10, 0.10, 0.05, 0.10])
                atendente = rng.choice(atendentes)
                resolvido = rng.choice(["Sim", "Não"], p=[0.35, 0.65])
                _id += 1
                linhas.append({
                    "id": int(_id),
                    "data": pd.Timestamp(2025 if "2025" in p else 2026, int(p.split('/')[0]), rng.integers(1, 28)),
                    "periodo": p,
                    "canal": canal,
                    "atendente": atendente,
                    "superior": superiores[atendente],
                    "nome_cliente": rng.choice([
                        "Henrique Gabriel de Souza Moreira", "Marina Alves Ferreira",
                        "João Pedro Costa Lima", "Beatriz Ramos Andrade",
                        "Rafael Nunes Barreto", "Camila Torres Vieira",
                    ]),
                    "nota_csat": int(rng.choice([1, 2], p=[0.4, 0.6])),
                    "motivo": motivo,
                    "tipo_insatisfacao": rng.choice(tipos_insatisfacao, p=[0.45, 0.2, 0.2, 0.1, 0.05]),
                    "problema_resolvido": resolvido,
                    "solicitou_outro_atendente": rng.choice(["Sim", "Não"], p=[0.25, 0.75]),
                    "transferencia_justificada": rng.choice(["Sim", "Não", "N/A"], p=[0.15, 0.15, 0.7]),
                    "tempo_espera": f"00:{rng.integers(0,10):02d}:{rng.integers(0,59):02d}",
                    "chamado": int(rng.integers(12000000, 12999999)),
                    "protocolo_asc": f"20261{rng.integers(1000000, 9999999)}",
                    "comentario": "Comentário de exemplo do cliente sobre o atendimento recebido.",
                    "resumo_caso": ("Cliente entrou em contato relatando o problema, o atendente conduziu a "
                                    "tratativa, porém houve falhas no processo que geraram a insatisfação "
                                    "relatada, encerrando o atendimento sem plena resolução."),
                    "observacao_item": ("Observação registrada durante a avaliação, detalhando o comportamento "
                                         "do atendente no ponto avaliado."),
                    "status": rng.choice(["Aberto", "Em andamento", "Resolvido"]),
                    "selecionado_aprofundamento": "Não",
                })
    base = pd.DataFrame(linhas)
    base["id"] = base["id"].astype(str)
    for (p, canal), grp in base.groupby(["periodo", "canal"]):
        idx = grp.sample(min(2, len(grp)), random_state=1).index
        base.loc[idx, "selecionado_aprofundamento"] = "Sim"

    universo_rows = []
    for p in periodos:
        for canal in canais:
            enviadas = int(rng.integers(1400, 2200))
            respondidas = int(enviadas * rng.uniform(0.45, 0.65))
            total_neg = int(respondidas * rng.uniform(0.06, 0.12))
            universo_rows.append({
                "periodo": p, "canal": canal,
                "pesquisas_enviadas": enviadas,
                "pesquisas_respondidas": respondidas,
                "total_notas_negativas_universo": total_neg,
            })
    universo = pd.DataFrame(universo_rows)
    return base, universo


# ------------------------------------------------------------------
# Sidebar — dados e parâmetros
# ------------------------------------------------------------------
st.sidebar.header("⚙️ Configuração")
usar_exemplo = st.sidebar.checkbox("Usar dados de exemplo", value=True)
up_base = st.sidebar.file_uploader("base_atendimentos.csv", type="csv", disabled=usar_exemplo)
up_universo = st.sidebar.file_uploader("universo_csat.csv", type="csv", disabled=usar_exemplo)
st.sidebar.markdown("---")
NOTA_NEGATIVA_MAX = st.sidebar.slider("Nota máxima considerada negativa", 1, 5, 2)
MIN_CASOS_RANKING = st.sidebar.slider("Mínimo de casos para ranking nominal de atendente", 1, 10, 3)
DEMANDA_MENSAL = st.sidebar.number_input("Demanda mensal de atendimentos", min_value=1, value=80)

COLUNAS_EXTRA_OPCIONAIS = [
    "nome_cliente", "superior", "tipo_insatisfacao", "problema_resolvido",
    "solicitou_outro_atendente", "transferencia_justificada", "tempo_espera",
    "chamado", "protocolo_asc", "resumo_caso", "observacao_item",
]

if usar_exemplo or up_base is None or up_universo is None:
    if not usar_exemplo:
        st.sidebar.warning("Suba os dois arquivos para usar dados reais — mostrando exemplo por enquanto.")
    df_base, df_universo = gerar_dados_exemplo()
else:
    df_base = pd.read_csv(up_base)
    df_universo = pd.read_csv(up_universo)
    for col in COLUNAS_EXTRA_OPCIONAIS:
        if col not in df_base.columns:
            df_base[col] = "--"
    df_base["id"] = df_base["id"].astype(str)

df_base["data"] = pd.to_datetime(df_base["data"])
periodos_disp = sorted(df_base["periodo"].unique())
periodo_foco = st.sidebar.selectbox("Período em foco", periodos_disp, index=len(periodos_disp) - 1)

# ------------------------------------------------------------------
# Título
# ------------------------------------------------------------------
st.title("📊 Análise de CSAT Negativo")
st.caption(f"Período em foco: **{periodo_foco}** | Demanda mensal de referência: **{DEMANDA_MENSAL}** atendimentos")

aba_visao, aba_atendimento = st.tabs(["📈 Visão Geral do Período", "🗂️ Visualização do Atendimento"])

# ==================================================================
# ABA 1 — VISÃO GERAL (resumo executivo, motivos, tendência, ranking,
# casos aprofundados, acertos, conclusão automática, exportar)
# ==================================================================
with aba_visao:

    # --------------------------------------------------------------
    # 1. Resumo executivo
    # --------------------------------------------------------------
    def montar_resumo(df_base, df_universo):
        agg = (
            df_base.groupby(["periodo", "canal"])
            .agg(amostra=("id", "count"), nota_media_amostra=("nota_csat", "mean"))
            .reset_index()
        )
        resumo = df_universo.merge(agg, on=["periodo", "canal"], how="left")
        resumo["amostra"] = resumo["amostra"].fillna(0).astype(int)
        resumo["pct_amostra"] = np.where(
            resumo["total_notas_negativas_universo"] > 0,
            resumo["amostra"] / resumo["total_notas_negativas_universo"] * 100, np.nan,
        )
        resumo["pct_notas_negativas"] = np.where(
            resumo["pesquisas_respondidas"] > 0,
            resumo["total_notas_negativas_universo"] / resumo["pesquisas_respondidas"] * 100, np.nan,
        )
        resumo["taxa_resposta_pesquisa"] = np.where(
            resumo["pesquisas_enviadas"] > 0,
            resumo["pesquisas_respondidas"] / resumo["pesquisas_enviadas"] * 100, np.nan,
        )
        cols = ["periodo", "canal", "nota_media_amostra", "pesquisas_enviadas",
                "pesquisas_respondidas", "taxa_resposta_pesquisa",
                "total_notas_negativas_universo", "pct_notas_negativas",
                "amostra", "pct_amostra"]
        return resumo[cols].round(1)

    resumo = montar_resumo(df_base, df_universo)

    st.markdown('<div class="section-label">1. Resumo executivo por período e canal</div>', unsafe_allow_html=True)
    st.dataframe(
        resumo.style
        .format({
            "nota_media_amostra": "{:.1f}",
            "taxa_resposta_pesquisa": "{:.1f}%",
            "pct_notas_negativas": "{:.1f}%",
            "pct_amostra": "{:.1f}%",
        })
        .background_gradient(subset=["pct_amostra"], cmap="RdYlGn", vmin=0, vmax=100)
        .background_gradient(subset=["taxa_resposta_pesquisa"], cmap="RdYlGn", vmin=0, vmax=100),
        use_container_width=True,
    )

    linha_periodo = resumo[resumo["periodo"] == periodo_foco]
    amostra_total = int(linha_periodo["amostra"].sum())
    cobertura_media = linha_periodo["pct_amostra"].mean()
    resposta_media = linha_periodo["taxa_resposta_pesquisa"].mean()
    nota_media = df_base[df_base["periodo"] == periodo_foco]["nota_csat"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Casos analisados no período", amostra_total)
    c2.metric("Nota média (amostra)", f"{nota_media:.1f}")
    c3.metric("Cobertura da amostra", f"{cobertura_media:.1f}%")
    c4.metric("Taxa de resposta da pesquisa", f"{resposta_media:.1f}%")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 2 e 3. Distribuição por motivo + Tendência
    # --------------------------------------------------------------
    col_pizza, col_tendencia = st.columns(2)

    with col_pizza:
        st.markdown('<div class="section-label">2. Distribuição de casos por motivo</div>', unsafe_allow_html=True)
        dist_motivos = df_base[df_base["periodo"] == periodo_foco]["motivo"].value_counts()
        fig1, ax1 = plt.subplots(figsize=(5, 5))
        ax1.pie(
            dist_motivos.values, labels=dist_motivos.index,
            autopct=lambda p: f"{p:.0f}%\n({int(round(p/100*dist_motivos.sum()))})",
            colors=PALETTE, startangle=90, pctdistance=0.75,
            textprops={"fontsize": 8, "color": TEXT},
        )
        fig1.patch.set_facecolor(BG_CARD)
        st.pyplot(fig1)

    def comparar_periodos(df_base, periodo_atual):
        periodos_ordenados = sorted(df_base["periodo"].unique())
        if periodo_atual not in periodos_ordenados or periodos_ordenados.index(periodo_atual) == 0:
            return None, None
        periodo_anterior = periodos_ordenados[periodos_ordenados.index(periodo_atual) - 1]
        atual = df_base[df_base["periodo"] == periodo_atual]["motivo"].value_counts()
        anterior = df_base[df_base["periodo"] == periodo_anterior]["motivo"].value_counts()
        comp = pd.DataFrame({"anterior": anterior, "atual": atual}).fillna(0).astype(int)
        comp["variacao"] = comp["atual"] - comp["anterior"]
        comp = comp.sort_values("variacao", ascending=False)
        return comp, periodo_anterior

    with col_tendencia:
        st.markdown('<div class="section-label">3. Motivo que mais cresceu</div>', unsafe_allow_html=True)
        comparativo, periodo_anterior = comparar_periodos(df_base, periodo_foco)
        if comparativo is not None:
            top = comparativo.iloc[0]
            sinal = "cresceu" if top["variacao"] > 0 else ("caiu" if top["variacao"] < 0 else "ficou estável")
            st.info(
                f"**{comparativo.index[0]}** {sinal} de {periodo_anterior} para {periodo_foco}: "
                f"{int(top['anterior'])} → {int(top['atual'])} casos "
                f"({'+' if top['variacao']>=0 else ''}{int(top['variacao'])})."
            )
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            comparativo[["anterior", "atual"]].plot(kind="barh", ax=ax2, color=["#5A5A60", ACCENT])
            ax2.set_xlabel("Casos")
            fig2.patch.set_facecolor(BG_CARD)
            st.pyplot(fig2)
        else:
            st.write("Não há período anterior disponível para comparar.")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 4. Ranking de atendentes
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">4. Ranking de atendentes (com cuidado estatístico)</div>', unsafe_allow_html=True)
    dados_periodo = df_base[df_base["periodo"] == periodo_foco]
    contagem = dados_periodo["atendente"].value_counts()
    aptos = contagem[contagem >= MIN_CASOS_RANKING]
    insuficientes = contagem[contagem < MIN_CASOS_RANKING]

    col_rank, col_info = st.columns([2, 1])
    with col_rank:
        if len(aptos) > 0:
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            aptos.sort_values().plot(kind="barh", ax=ax3, color=ACCENT)
            ax3.set_xlabel("Casos negativos")
            ax3.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            fig3.patch.set_facecolor(BG_CARD)
            st.pyplot(fig3)
        else:
            st.write("Nenhum atendente atingiu o mínimo de casos para ranking nominal neste período.")
    with col_info:
        st.caption(f"Mínimo para entrar no ranking: {MIN_CASOS_RANKING} casos")
        if len(insuficientes) > 0:
            st.write("**Fora do ranking (amostra insuficiente):**")
            for nome, qtd in insuficientes.items():
                st.write(f"- {nome} ({qtd})")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 5. Casos aprofundados (com atalho para a tela de visualização)
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">5. Casos aprofundados do período</div>', unsafe_allow_html=True)
    casos = df_base[(df_base["periodo"] == periodo_foco) & (df_base["selecionado_aprofundamento"] == "Sim")]
    if len(casos) == 0:
        st.write("Nenhum caso marcado como 'selecionado_aprofundamento = Sim' neste período.")
    else:
        for i, (_, caso) in enumerate(casos.iterrows(), start=1):
            with st.expander(f"Caso {i} — #{caso['id']} · {caso['motivo']} (nota {caso['nota_csat']})"):
                st.write(f"**ID:** {caso['id']} | **Canal:** {caso['canal']} | **Atendente:** {caso['atendente']}")
                st.write(f"**Comentário do cliente:** \"{caso['comentario']}\"")
                st.write(f"**Status da ação:** {caso['status']}")
                st.caption("Abra a aba 'Visualização do Atendimento' e selecione este ID para ver o formulário completo.")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 6. Acertos a replicar
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">6. Acertos que devem ser replicados</div>', unsafe_allow_html=True)
    acertos_texto = st.text_area(
        "Edite livremente (um item por linha):",
        value="Registro claro do atendimento\nPadronização de encerramento\n"
              "Transparência com o cliente sobre prazos\nLimite técnico respeitado\n"
              "Encaminhamento correto para a área responsável",
        height=120,
    )
    for linha in acertos_texto.splitlines():
        if linha.strip():
            st.write(f"✅ {linha.strip()}")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 7. Conclusão automática — junta os principais achados
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">7. Conclusão automática</div>', unsafe_allow_html=True)
    motivo_top = dist_motivos.index[0] if len(dist_motivos) else "N/A"

    # taxa de "problema não resolvido" no período, se a coluna existir de fato
    if "problema_resolvido" in dados_periodo.columns:
        nao_resolvidos = (dados_periodo["problema_resolvido"] == "Não").mean() * 100
    else:
        nao_resolvidos = None

    texto_conclusao = [f"**Resumo do período {periodo_foco}:**"]
    texto_conclusao.append(f"- Maior concentração de insatisfação em: **{motivo_top}**.")
    if comparativo is not None:
        top = comparativo.iloc[0]
        sinal = "cresceu" if top["variacao"] > 0 else "caiu"
        texto_conclusao.append(
            f"- Motivo que mais {sinal} em relação ao período anterior: **{comparativo.index[0]}** "
            f"({'+' if top['variacao']>=0 else ''}{int(top['variacao'])} casos)."
        )
    texto_conclusao.append(
        f"- Cobertura média da amostra sobre o universo de notas negativas: **{cobertura_media:.1f}%**"
        + (" — ainda baixa, tratar achados como indicativos, não como retrato completo."
           if cobertura_media < 20 else ".")
    )
    texto_conclusao.append(
        f"- Taxa média de resposta da pesquisa: **{resposta_media:.1f}%**"
        + (" — atenção ao viés de quem responde pesquisa espontaneamente costuma ser quem está mais insatisfeito."
           if resposta_media < 60 else ".")
    )
    if nao_resolvidos is not None:
        texto_conclusao.append(
            f"- **{nao_resolvidos:.0f}%** dos casos do período foram encerrados sem o problema do cliente resolvido."
        )
    if len(insuficientes):
        texto_conclusao.append(
            f"- {len(insuficientes)} atendente(s) tiveram ocorrências negativas, mas abaixo do mínimo "
            f"estatístico para entrar no ranking nominal deste período."
        )
    st.markdown("\n\n".join(texto_conclusao))

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 8. Exportar
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">8. Exportar</div>', unsafe_allow_html=True)
    csv_bytes = resumo.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar resumo em CSV", data=csv_bytes,
                        file_name="resumo_csat_negativo.csv", mime="text/csv")
    try:
        buf = io.BytesIO()
        resumo.to_excel(buf, index=False, engine="openpyxl")
        st.download_button("⬇️ Baixar resumo em Excel", data=buf.getvalue(),
                            file_name="resumo_csat_negativo.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.caption("Instale 'openpyxl' para habilitar exportação em Excel.")


# ==================================================================
# ABA 2 — VISUALIZAÇÃO DO ATENDIMENTO (tela estilo "formulário")
# Somente leitura: mostra o caso selecionado, campo a campo.
# ==================================================================
with aba_atendimento:

    dados_periodo_full = df_base[df_base["periodo"] == periodo_foco].copy()

    if len(dados_periodo_full) == 0:
        st.info("Não há atendimentos neste período.")
    else:
        col_sel, col_badge = st.columns([3, 1])
        with col_sel:
            opcoes_ids = dados_periodo_full["id"].tolist()
            labels = {
                row["id"]: f"#{row['id']} — {row.get('nome_cliente', row['atendente'])} ({row['motivo']})"
                for _, row in dados_periodo_full.iterrows()
            }
            id_selecionado = st.selectbox(
                "Selecionar atendimento",
                options=opcoes_ids,
                format_func=lambda i: labels.get(i, i),
            )
        caso = dados_periodo_full[dados_periodo_full["id"] == id_selecionado].iloc[0]
        with col_badge:
            st.markdown(
                f'<div style="margin-top:28px;"><span class="badge">CSAT NEGATIVO · {periodo_foco}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"### #{caso['id']}")
        st.markdown(f"**{caso.get('nome_cliente', '—')}**")
        st.caption(f"Atendente: {caso['atendente']} · Canal: {caso['canal']}")
        st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

        col_form, col_lateral = st.columns([2.2, 1])

        # -------------------- Coluna principal: formulário --------------------
        with col_form:
            st.markdown('<div class="section-label">Avaliação CSAT negativo</div>', unsafe_allow_html=True)
            st.caption("Seção voltada para avaliação dos casos de CSAT negativo das operações.")

            def campo(titulo, resposta, observacao=None):
                obs_html = (
                    f'<div class="card-title" style="margin-top:10px;">OBSERVAÇÃO</div>'
                    f'<div class="card-value" style="color:{TEXT_MUTED};">{observacao}</div>'
                    if observacao else ""
                )
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{titulo}</div>
                    <div class="card-title" style="margin-top:8px;">RESPOSTA</div>
                    <div class="card-value">{resposta}</div>
                    {obs_html}
                </div>
                """, unsafe_allow_html=True)

            campo("Nota CSAT", caso["nota_csat"])
            campo("Problema foi resolvido?", caso.get("problema_resolvido", "—"),
                  caso.get("observacao_item"))
            campo("Solicitou falar com outro atendente?", caso.get("solicitou_outro_atendente", "—"))
            campo("A transferência do atendimento foi justificada?", caso.get("transferencia_justificada", "—"))
            campo("Tipo de insatisfação", caso.get("tipo_insatisfacao", caso["motivo"]),
                  caso.get("observacao_item"))
            campo("Resumo do caso", "Resumo", caso.get("resumo_caso"))

            st.markdown('<div class="section-label">Observações da avaliação</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
                <div class="card-value" style="color:{TEXT_MUTED};">
                    {caso.get('comentario', 'Não foram informadas observações para esta avaliação.')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Gráfico de contexto: histórico de notas desse atendente nos períodos disponíveis
            st.markdown('<div class="section-label">📈 Histórico do atendente nos períodos</div>', unsafe_allow_html=True)
            hist_atendente = (
                df_base[df_base["atendente"] == caso["atendente"]]
                .groupby("periodo")["nota_csat"].agg(["mean", "count"])
                .reindex(sorted(df_base["periodo"].unique()))
                .fillna(0)
            )
            fig4, ax4 = plt.subplots(figsize=(6, 3))
            ax4.bar(hist_atendente.index.astype(str), hist_atendente["count"], color=ACCENT, alpha=0.85)
            ax4.set_ylabel("Casos negativos")
            ax4.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            fig4.patch.set_facecolor(BG_CARD)
            st.pyplot(fig4)

        # -------------------- Coluna lateral: dados do avaliado/contato --------------------
        with col_lateral:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">SOBRE O AVALIADO</div>
                <div class="card-value" style="margin-top:6px;">{caso['atendente']}</div>
                <div class="card-title" style="margin-top:12px;">SUPERIOR</div>
                <div class="card-value">{caso.get('superior', '—')}</div>
            </div>
            <div class="card">
                <div class="card-title">SOBRE O CONTATO</div>
                <div class="card-title" style="margin-top:10px;">DATA DO CONTATO</div>
                <div class="card-value">{caso['data'].strftime('%d/%m/%Y')}</div>
                <div class="card-title" style="margin-top:10px;">CHAMADO</div>
                <div class="card-value">{caso.get('chamado', '—')}</div>
                <div class="card-title" style="margin-top:10px;">PROTOCOLO ASC</div>
                <div class="card-value">{caso.get('protocolo_asc', '—')}</div>
                <div class="card-title" style="margin-top:10px;">CANAL DE ATENDIMENTO</div>
                <div class="card-value">{caso['canal']}</div>
                <div class="card-title" style="margin-top:10px;">TEMPO DE ESPERA</div>
                <div class="card-value">{caso.get('tempo_espera', '—')}</div>
            </div>
            <div class="card">
                <div class="card-title">STATUS DA TRATATIVA</div>
                <div class="card-value" style="margin-top:6px;">{caso['status']}</div>
            </div>
            """, unsafe_allow_html=True)
