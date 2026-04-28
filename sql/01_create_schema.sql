-- ============================================================
-- PROJETO: Industrial Sales Analytics
-- Autor: Paulo Augusto Colodiano Martins
-- Descrição: Modelagem dimensional (Star Schema) para análise
--            de performance comercial no setor industrial
-- ============================================================

-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS industrial_sales;
\c industrial_sales;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- Dimensão: Produto
CREATE TABLE dim_produto (
    produto_id      SERIAL PRIMARY KEY,
    sku             VARCHAR(20) NOT NULL UNIQUE,
    nome_produto    VARCHAR(100) NOT NULL,
    categoria       VARCHAR(50) NOT NULL,   -- ex: Bebidas, Snacks, Laticínios
    subcategoria    VARCHAR(50),
    unidade_medida  VARCHAR(10) NOT NULL,   -- ex: KG, UN, CX
    peso_kg         NUMERIC(8,3),
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Dimensão: Cliente (canal de distribuição)
CREATE TABLE dim_cliente (
    cliente_id      SERIAL PRIMARY KEY,
    cnpj            VARCHAR(18) UNIQUE,
    razao_social    VARCHAR(150) NOT NULL,
    segmento        VARCHAR(50) NOT NULL,   -- ex: Atacado, Varejo, Food Service
    porte           VARCHAR(20),            -- Pequeno, Médio, Grande
    cidade          VARCHAR(80),
    estado          CHAR(2),
    regiao          VARCHAR(20),            -- Sul, Sudeste, Norte, etc.
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Dimensão: Vendedor / Representante
CREATE TABLE dim_vendedor (
    vendedor_id     SERIAL PRIMARY KEY,
    matricula       VARCHAR(20) NOT NULL UNIQUE,
    nome            VARCHAR(100) NOT NULL,
    equipe          VARCHAR(50),
    regional        VARCHAR(50),
    cargo           VARCHAR(50),
    ativo           BOOLEAN DEFAULT TRUE,
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- Dimensão: Tempo (Date Dimension)
CREATE TABLE dim_tempo (
    tempo_id        SERIAL PRIMARY KEY,
    data            DATE NOT NULL UNIQUE,
    ano             INT NOT NULL,
    semestre        INT NOT NULL,
    trimestre       INT NOT NULL,
    mes             INT NOT NULL,
    nome_mes        VARCHAR(20) NOT NULL,
    semana_ano      INT NOT NULL,
    dia_semana      INT NOT NULL,
    nome_dia        VARCHAR(20) NOT NULL,
    is_fim_semana   BOOLEAN NOT NULL,
    is_feriado      BOOLEAN DEFAULT FALSE
);

-- Dimensão: Canal de Venda
CREATE TABLE dim_canal (
    canal_id        SERIAL PRIMARY KEY,
    nome_canal      VARCHAR(50) NOT NULL,  -- Direto, Distribuidor, E-commerce
    descricao       TEXT
);

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE fato_vendas (
    venda_id        BIGSERIAL PRIMARY KEY,
    tempo_id        INT NOT NULL REFERENCES dim_tempo(tempo_id),
    produto_id      INT NOT NULL REFERENCES dim_produto(produto_id),
    cliente_id      INT NOT NULL REFERENCES dim_cliente(cliente_id),
    vendedor_id     INT NOT NULL REFERENCES dim_vendedor(vendedor_id),
    canal_id        INT NOT NULL REFERENCES dim_canal(canal_id),

    -- Métricas de volume
    quantidade      NUMERIC(12,3) NOT NULL,
    quantidade_dev  NUMERIC(12,3) DEFAULT 0,  -- devoluções

    -- Métricas de valor
    preco_unitario  NUMERIC(12,4) NOT NULL,
    desconto_pct    NUMERIC(5,2) DEFAULT 0,
    receita_bruta   NUMERIC(14,2) NOT NULL,
    receita_liquida NUMERIC(14,2) NOT NULL,
    custo_total     NUMERIC(14,2),
    margem_bruta    NUMERIC(14,2),

    -- Métricas de meta
    meta_quantidade NUMERIC(12,3),
    meta_receita    NUMERIC(14,2),

    -- Controle
    numero_pedido   VARCHAR(30),
    criado_em       TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- ÍNDICES para performance
-- ============================================================

CREATE INDEX idx_fato_tempo    ON fato_vendas(tempo_id);
CREATE INDEX idx_fato_produto  ON fato_vendas(produto_id);
CREATE INDEX idx_fato_cliente  ON fato_vendas(cliente_id);
CREATE INDEX idx_fato_vendedor ON fato_vendas(vendedor_id);
CREATE INDEX idx_fato_canal    ON fato_vendas(canal_id);
CREATE INDEX idx_fato_pedido   ON fato_vendas(numero_pedido);
