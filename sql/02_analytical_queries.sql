-- ============================================================
-- QUERIES ANALÍTICAS — Industrial Sales Analytics
-- Autor: Paulo Augusto Colodiano Martins
-- ============================================================

-- ------------------------------------------------------------
-- 1. RECEITA MENSAL vs META — Atingimento por Mês
-- ------------------------------------------------------------
WITH mensal AS (
    SELECT
        t.ano,
        t.mes,
        t.nome_mes,
        SUM(f.receita_liquida)  AS receita_realizada,
        SUM(f.meta_receita)     AS meta_receita,
        SUM(f.quantidade)       AS volume_kg,
        COUNT(DISTINCT f.cliente_id) AS clientes_ativos
    FROM fato_vendas f
    JOIN dim_tempo t ON t.tempo_id = f.tempo_id
    GROUP BY t.ano, t.mes, t.nome_mes
)
SELECT
    ano,
    mes,
    nome_mes,
    receita_realizada,
    meta_receita,
    volume_kg,
    clientes_ativos,
    ROUND(receita_realizada / NULLIF(meta_receita, 0) * 100, 1) AS pct_atingimento,
    receita_realizada - meta_receita                             AS gap_vs_meta
FROM mensal
ORDER BY ano, mes;


-- ------------------------------------------------------------
-- 2. RANKING DE PRODUTOS — Top 10 por Receita e Margem
-- ------------------------------------------------------------
SELECT
    p.categoria,
    p.nome_produto,
    p.sku,
    SUM(f.quantidade)       AS volume_total,
    SUM(f.receita_liquida)  AS receita_total,
    SUM(f.margem_bruta)     AS margem_total,
    ROUND(SUM(f.margem_bruta) / NULLIF(SUM(f.receita_liquida), 0) * 100, 1) AS pct_margem,
    ROUND(SUM(f.receita_liquida) /
          SUM(SUM(f.receita_liquida)) OVER () * 100, 2)                      AS share_receita,
    RANK() OVER (ORDER BY SUM(f.receita_liquida) DESC)                       AS rank_receita
FROM fato_vendas f
JOIN dim_produto p ON p.produto_id = f.produto_id
GROUP BY p.categoria, p.nome_produto, p.sku
ORDER BY receita_total DESC
LIMIT 10;


-- ------------------------------------------------------------
-- 3. PERFORMANCE POR REGIONAL (Vendedor x Região)
-- ------------------------------------------------------------
SELECT
    v.regional,
    v.equipe,
    v.nome                                          AS vendedor,
    COUNT(DISTINCT f.cliente_id)                    AS clientes_ativos,
    COUNT(DISTINCT f.numero_pedido)                 AS total_pedidos,
    SUM(f.receita_liquida)                          AS receita_total,
    SUM(f.meta_receita)                             AS meta_total,
    ROUND(AVG(f.desconto_pct), 2)                   AS desconto_medio_pct,
    ROUND(SUM(f.receita_liquida) /
          NULLIF(SUM(f.meta_receita), 0) * 100, 1) AS pct_atingimento
FROM fato_vendas f
JOIN dim_vendedor v ON v.vendedor_id = f.vendedor_id
GROUP BY v.regional, v.equipe, v.nome
ORDER BY pct_atingimento DESC;


-- ------------------------------------------------------------
-- 4. ANÁLISE DE DEVOLUÇÕES — Taxa por Categoria
-- ------------------------------------------------------------
SELECT
    p.categoria,
    SUM(f.quantidade)                                              AS vol_vendido,
    SUM(f.quantidade_dev)                                          AS vol_devolvido,
    ROUND(SUM(f.quantidade_dev) /
          NULLIF(SUM(f.quantidade), 0) * 100, 2)                  AS taxa_devolucao_pct,
    SUM(f.receita_liquida)                                         AS receita_liquida,
    SUM(f.quantidade_dev * f.preco_unitario)                       AS impacto_financeiro_dev
FROM fato_vendas f
JOIN dim_produto p ON p.produto_id = f.produto_id
GROUP BY p.categoria
ORDER BY taxa_devolucao_pct DESC;


-- ------------------------------------------------------------
-- 5. ANÁLISE DE CURVA ABC DE CLIENTES
-- ------------------------------------------------------------
WITH cliente_receita AS (
    SELECT
        c.razao_social,
        c.segmento,
        c.estado,
        SUM(f.receita_liquida) AS receita_total
    FROM fato_vendas f
    JOIN dim_cliente c ON c.cliente_id = f.cliente_id
    GROUP BY c.razao_social, c.segmento, c.estado
),
curva AS (
    SELECT *,
        SUM(receita_total) OVER (ORDER BY receita_total DESC) AS receita_acumulada,
        SUM(receita_total) OVER ()                            AS receita_geral
    FROM cliente_receita
)
SELECT
    razao_social,
    segmento,
    estado,
    receita_total,
    ROUND(receita_acumulada / receita_geral * 100, 2) AS pct_acumulado,
    CASE
        WHEN receita_acumulada / receita_geral <= 0.80 THEN 'A'
        WHEN receita_acumulada / receita_geral <= 0.95 THEN 'B'
        ELSE 'C'
    END AS curva_abc
FROM curva
ORDER BY receita_total DESC;


-- ------------------------------------------------------------
-- 6. YoY — Comparativo Ano a Ano por Categoria
-- ------------------------------------------------------------
WITH base AS (
    SELECT
        t.ano,
        p.categoria,
        SUM(f.receita_liquida) AS receita
    FROM fato_vendas f
    JOIN dim_tempo   t ON t.tempo_id   = f.tempo_id
    JOIN dim_produto p ON p.produto_id = f.produto_id
    GROUP BY t.ano, p.categoria
)
SELECT
    curr.categoria,
    curr.ano                                          AS ano_atual,
    curr.receita                                      AS receita_atual,
    prev.receita                                      AS receita_anterior,
    curr.receita - prev.receita                       AS variacao_abs,
    ROUND((curr.receita - prev.receita) /
          NULLIF(prev.receita, 0) * 100, 1)           AS variacao_pct
FROM base curr
LEFT JOIN base prev
    ON prev.categoria = curr.categoria
   AND prev.ano       = curr.ano - 1
ORDER BY curr.categoria, curr.ano;
