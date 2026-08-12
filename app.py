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
import streamlit as st

st.set_page_config(page_title="CSAT Negativo", page_icon="📊", layout="wide")

# ==================================================================
# TEMA ESCURO — CSS
# ==================================================================
ACCENT = "#FF7A1A"
BG = "#0B0B0D"
BG_CARD = "#151517"
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
.stApp {{ background-color: {BG}; color: {TEXT}; }}
section[data-testid="stSidebar"] {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}
div[data-testid="stMetric"] {{
    background-color: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 14px 16px;
}}
div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED}; }}
div[data-testid="stMetricValue"] {{ color: {TEXT}; }}
.card {{
    background-color: {BG_CARD}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 18px 20px; margin-bottom: 14px;
}}
.card-title {{
    color: {TEXT_MUTED}; font-size: 0.72rem; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 4px;
}}
.card-value {{ color: {TEXT}; font-size: 1rem; line-height: 1.5; }}
.section-label {{
    color: {ACCENT}; font-weight: 700; font-size: 0.95rem; text-transform: uppercase;
    letter-spacing: 0.04em; border-bottom: 1px solid {BORDER};
    padding-bottom: 6px; margin-bottom: 14px; margin-top: 6px;
}}
.hr-soft {{ border-top: 1px solid {BORDER}; margin: 18px 0; }}
h1, h2, h3 {{ color: {TEXT}; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{
    background-color: {BG_CARD}; border-radius: 8px 8px 0 0; color: {TEXT_MUTED}; padding: 8px 16px;
}}
.stTabs [aria-selected="true"] {{ color: {ACCENT} !important; border-bottom: 2px solid {ACCENT} !important; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Categorias fixas de motivo (reduzidas)
# ------------------------------------------------------------------
MOTIVOS = ["Procedimentos", "Atendimento", "Produtos/Serviços", "N/A"]


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
    linhas = []
    _id = 16750000
    for p in periodos:
        for canal in canais:
            n_casos = rng.integers(8, 20)
            for _ in range(n_casos):
                motivo = rng.choice(MOTIVOS, p=[0.30, 0.45, 0.15, 0.10])
                atendente = rng.choice(atendentes)
                resolvido = rng.choice(["Sim", "Não"], p=[0.35, 0.65])
                _id += 1
                linhas.append({
                    "id": str(int(_id)),
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
                    "status": rng.choice(["Aberto", "Em andamento", "Resolvido"]),
                    "selecionado_aprofundamento": "Não",
                })
    base = pd.DataFrame(linhas)
    for (p, canal), grp in base.groupby(["periodo", "canal"]):
        idx = grp.sample(min(2, len(grp)), random_state=1).index
        base.loc[idx, "selecionado_aprofundamento"] = "Sim"
    return base


# ------------------------------------------------------------------
# Sidebar — dados e parâmetros
# ------------------------------------------------------------------
st.sidebar.header("⚙️ Configuração")
usar_exemplo = st.sidebar.checkbox("Usar dados de exemplo", value=True)
up_base = st.sidebar.file_uploader("base_atendimentos.csv", type="csv", disabled=usar_exemplo)
st.sidebar.markdown("---")
DEMANDA_MENSAL = st.sidebar.number_input("Demanda mensal de atendimentos", min_value=1, value=80)

COLUNAS_EXTRA_OPCIONAIS = [
    "nome_cliente", "superior", "problema_resolvido", "solicitou_outro_atendente",
    "transferencia_justificada", "tempo_espera", "chamado", "protocolo_asc", "resumo_caso",
]

if usar_exemplo or up_base is None:
    if not usar_exemplo:
        st.sidebar.warning("Suba o arquivo para usar dados reais — mostrando exemplo por enquanto.")
    df_base = gerar_dados_exemplo()
else:
    df_base = pd.read_csv(up_base)
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
# ABA 1 — VISÃO GERAL
# ==================================================================
with aba_visao:

    # --------------------------------------------------------------
    # 1. Resumo executivo — 100% MANUAL, sem cálculo automático
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">1. Resumo executivo por período e canal (edição manual)</div>', unsafe_allow_html=True)
    st.caption("Preencha os valores como quiser — nada nesta tabela é calculado a partir de outra base.")

    if "resumo_manual" not in st.session_state:
        st.session_state.resumo_manual = {}

    canais_disponiveis = sorted(df_base["canal"].unique())

    def resumo_padrao(canais):
        return pd.DataFrame({
            "canal": canais,
            "notas_csat": [0.0] * len(canais),
            "csat": [0.0] * len(canais),
            "quantidade": [0] * len(canais),
            "pct_notas": [0.0] * len(canais),
            "amostra": [0] * len(canais),
            "pct_amostra": [0.0] * len(canais),
        })

    if periodo_foco not in st.session_state.resumo_manual:
        st.session_state.resumo_manual[periodo_foco] = resumo_padrao(canais_disponiveis)

    resumo_editado = st.data_editor(
        st.session_state.resumo_manual[periodo_foco],
        column_config={
            "canal": st.column_config.TextColumn("Canal", disabled=True),
            "notas_csat": st.column_config.NumberColumn("Notas CSAT", format="%.1f", step=0.1),
            "csat": st.column_config.NumberColumn("CSAT (%)", format="%.2f", step=0.1),
            "quantidade": st.column_config.NumberColumn("Quantidade", format="%d", step=1),
            "pct_notas": st.column_config.NumberColumn("% Notas", format="%.2f", step=0.1),
            "amostra": st.column_config.NumberColumn("Amostra", format="%d", step=1),
            "pct_amostra": st.column_config.NumberColumn("% Amostra", format="%.2f", step=0.1),
        },
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        key=f"editor_resumo_{periodo_foco}",
    )
    st.session_state.resumo_manual[periodo_foco] = resumo_editado

    soma = resumo_editado.drop(columns="canal").sum(numeric_only=True)
    soma_row = pd.DataFrame([{"canal": "Soma", **soma.to_dict()}])
    st.dataframe(soma_row, hide_index=True, use_container_width=True)

    cobertura_media = resumo_editado["pct_amostra"].mean()
    csat_medio = resumo_editado["csat"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Amostra total (soma)", int(resumo_editado["amostra"].sum()))
    c2.metric("Notas CSAT (soma)", f"{resumo_editado['notas_csat'].sum():.1f}")
    c3.metric("CSAT médio", f"{csat_medio:.1f}%")
    c4.metric("Cobertura média da amostra", f"{cobertura_media:.1f}%")

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 2 e 3. Distribuição por motivo + Tendência (automático, com base na 2)
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
            textprops={"fontsize": 9, "color": TEXT},
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
        st.caption("Calculado automaticamente a partir da distribuição acima.")
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
    # 4. Casos aprofundados — abrem como formulário editável e invertido
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">4. Casos aprofundados do período</div>', unsafe_allow_html=True)
    casos = df_base[(df_base["periodo"] == periodo_foco) & (df_base["selecionado_aprofundamento"] == "Sim")]

    if "casos_editados" not in st.session_state:
        st.session_state.casos_editados = {}

    if len(casos) == 0:
        st.write("Nenhum caso marcado como 'selecionado_aprofundamento = Sim' neste período.")
    else:
        for i, (_, caso_original) in enumerate(casos.iterrows(), start=1):
            cid = caso_original["id"]
            if cid not in st.session_state.casos_editados:
                st.session_state.casos_editados[cid] = caso_original.to_dict()
            caso = st.session_state.casos_editados[cid]

            with st.expander(f"Caso {i} — #{cid} · {caso['motivo']} (nota {caso['nota_csat']})"):
                st.caption(f"ID {cid} · Canal {caso['canal']} · Atendente {caso['atendente']}")

                # Ordem invertida: resumo do caso primeiro
                caso["resumo_caso"] = st.text_area(
                    "Resumo do caso", value=caso.get("resumo_caso", ""), key=f"resumo_{cid}",
                )
                caso["motivo"] = st.selectbox(
                    "Tipo de insatisfação", MOTIVOS,
                    index=MOTIVOS.index(caso["motivo"]) if caso["motivo"] in MOTIVOS else 0,
                    key=f"motivo_{cid}",
                )
                opcoes_transf = ["Sim", "Não", "N/A"]
                caso["transferencia_justificada"] = st.selectbox(
                    "A transferência do atendimento foi justificada?", opcoes_transf,
                    index=opcoes_transf.index(caso["transferencia_justificada"])
                    if caso["transferencia_justificada"] in opcoes_transf else 2,
                    key=f"transf_{cid}",
                )
                opcoes_sim_nao = ["Sim", "Não"]
                caso["solicitou_outro_atendente"] = st.selectbox(
                    "Solicitou falar com outro atendente?", opcoes_sim_nao,
                    index=opcoes_sim_nao.index(caso["solicitou_outro_atendente"])
                    if caso["solicitou_outro_atendente"] in opcoes_sim_nao else 1,
                    key=f"solic_{cid}",
                )
                caso["problema_resolvido"] = st.selectbox(
                    "Problema foi resolvido?", opcoes_sim_nao,
                    index=opcoes_sim_nao.index(caso["problema_resolvido"])
                    if caso["problema_resolvido"] in opcoes_sim_nao else 1,
                    key=f"resolvido_{cid}",
                )
                caso["nota_csat"] = st.number_input(
                    "Nota CSAT", min_value=1, max_value=5, value=int(caso["nota_csat"]), key=f"nota_{cid}",
                )

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 5. Conclusão automática — enxuta, no máx. 5 itens
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">5. Conclusão automática</div>', unsafe_allow_html=True)
    motivo_top = dist_motivos.index[0] if len(dist_motivos) else "N/A"

    ids_periodo = casos["id"].tolist() if len(casos) else []
    casos_atualizados = [st.session_state.casos_editados[cid] for cid in ids_periodo if cid in st.session_state.casos_editados]
    casos_df_atual = pd.DataFrame(casos_atualizados) if casos_atualizados else casos

    itens = [f"Maior concentração de insatisfação em: **{motivo_top}**."]
    if comparativo is not None:
        top = comparativo.iloc[0]
        sinal = "cresceu" if top["variacao"] > 0 else "caiu"
        itens.append(
            f"Motivo que mais {sinal}: **{comparativo.index[0]}** "
            f"({'+' if top['variacao']>=0 else ''}{int(top['variacao'])} casos)."
        )
    itens.append(f"Cobertura média da amostra informada: **{cobertura_media:.1f}%**.")
    itens.append(f"CSAT médio informado no período: **{csat_medio:.1f}%**.")
    if len(casos_df_atual):
        nao_resolvidos_pct = (casos_df_atual["problema_resolvido"] == "Não").mean() * 100
        itens.append(f"**{nao_resolvidos_pct:.0f}%** dos casos aprofundados seguem sem o problema resolvido.")

    itens = itens[:5]
    texto_conclusao = [f"**Resumo do período {periodo_foco}:**"] + [f"- {item}" for item in itens]
    st.markdown("\n\n".join(texto_conclusao))

    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    # --------------------------------------------------------------
    # 6. Exportar
    # --------------------------------------------------------------
    st.markdown('<div class="section-label">6. Exportar</div>', unsafe_allow_html=True)
    csv_bytes = resumo_editado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar resumo em CSV", data=csv_bytes,
                        file_name="resumo_csat_negativo.csv", mime="text/csv")
    try:
        buf = io.BytesIO()
        resumo_editado.to_excel(buf, index=False, engine="openpyxl")
        st.download_button("⬇️ Baixar resumo em Excel", data=buf.getvalue(),
                            file_name="resumo_csat_negativo.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception:
        st.caption("Instale 'openpyxl' para habilitar exportação em Excel.")


# ==================================================================
# ABA 2 — VISUALIZAÇÃO DO ATENDIMENTO (somente leitura)
# ==================================================================
with aba_atendimento:

    dados_periodo_full = df_base[df_base["periodo"] == periodo_foco].copy()

    if len(dados_periodo_full) == 0:
        st.info("Não há atendimentos neste período.")
    else:
        opcoes_ids = dados_periodo_full["id"].tolist()
        labels = {
            row["id"]: f"#{row['id']} — {row.get('nome_cliente', row['atendente'])} ({row['motivo']})"
            for _, row in dados_periodo_full.iterrows()
        }
        id_selecionado = st.selectbox(
            "Selecionar atendimento", options=opcoes_ids, format_func=lambda i: labels.get(i, i),
        )
        caso = dados_periodo_full[dados_periodo_full["id"] == id_selecionado].iloc[0]

        st.markdown(f"### #{caso['id']}")
        st.markdown(f"**{caso.get('nome_cliente', '—')}**")
        st.caption(f"Atendente: {caso['atendente']} · Canal: {caso['canal']}")
        st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

        col_form, col_lateral = st.columns([2.2, 1])

        with col_form:
            st.markdown('<div class="section-label">Avaliação CSAT negativo</div>', unsafe_allow_html=True)

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
            campo("Problema foi resolvido?", caso.get("problema_resolvido", "—"))
            campo("Solicitou falar com outro atendente?", caso.get("solicitou_outro_atendente", "—"))
            campo("A transferência do atendimento foi justificada?", caso.get("transferencia_justificada", "—"))
            campo("Tipo de insatisfação", caso["motivo"])
            campo("Resumo do caso", "Resumo", caso.get("resumo_caso"))

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
