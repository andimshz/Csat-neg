# Dashboard de CSAT Negativo

Painel web (Streamlit), tema escuro, com duas telas:

1. **Visão Geral do Período** — resumo executivo, distribuição por motivo, tendência,
   ranking de atendentes com corte estatístico, casos aprofundados, acertos a replicar,
   conclusão automática e exportação.
2. **Visualização do Atendimento** — tela somente-leitura no estilo "formulário de avaliação",
   com os dados do caso selecionado, painel lateral com informações do avaliado/contato e um
   gráfico de histórico do atendente no período.

## Rodar no seu computador

1. Instale o Python (3.9+), se ainda não tiver.
2. No terminal, dentro da pasta do projeto:

```
pip install -r requirements.txt
streamlit run app.py
```

3. Abre sozinho no navegador, em `http://localhost:8501`. Só você acessa, é local.

## Publicar como site (gratuito, com link pra compartilhar)

1. Crie uma conta em [github.com](https://github.com) (se não tiver) e crie um repositório novo.
2. Suba os 3 arquivos deste pacote: `app.py`, `requirements.txt`, `README.md`.
3. Vá em [share.streamlit.io](https://share.streamlit.io) (Streamlit Community Cloud), faça login com sua conta GitHub.
4. Clique em "New app", escolha o repositório e o arquivo `app.py`.
5. Clique em "Deploy". Em 1-2 minutos você recebe um link público (tipo `seu-app.streamlit.app`) que pode abrir de qualquer lugar — inclusive projetar direto na reunião.

## Como usar seus dados reais

Na barra lateral do app, desmarque "Usar dados de exemplo" e suba dois CSVs:

- **`base_atendimentos.csv`** — colunas obrigatórias:
  `id, data, periodo, canal, atendente, nota_csat, motivo, comentario, status, selecionado_aprofundamento`

  Colunas opcionais (usadas na tela "Visualização do Atendimento"; se não existirem, o app
  preenche automaticamente com `"--"`):
  `nome_cliente, superior, tipo_insatisfacao, problema_resolvido, solicitou_outro_atendente,
  transferencia_justificada, tempo_espera, chamado, protocolo_asc, resumo_caso, observacao_item`

- **`universo_csat.csv`** — colunas: `periodo, canal, pesquisas_enviadas, pesquisas_respondidas, total_notas_negativas_universo`

Os parâmetros (nota negativa, mínimo para ranking, demanda mensal) também ficam ajustáveis na barra lateral, sem precisar mexer no código.

## Personalizar cores/tema

As cores do tema escuro estão centralizadas no topo do `app.py`, nas constantes
`ACCENT`, `BG`, `BG_CARD`, `BORDER`, `TEXT`, `TEXT_MUTED` e na lista `PALETTE`
(usada nos gráficos). Troque os valores hexadecimais ali para ajustar a identidade visual.
