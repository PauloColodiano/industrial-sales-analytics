"""
generate_data.py
================
Gera dados sintéticos realistas para o projeto Industrial Sales Analytics.
Simula 2 anos de vendas de uma indústria de alimentos/bebidas.

Autor: Paulo Augusto Colodiano Martins
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import random
import os

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Configurações gerais ─────────────────────────────────────────────────────
DATA_INICIO = date(2023, 1, 1)
DATA_FIM    = date(2024, 12, 31)
N_PEDIDOS   = 8_000

# ── Dimensões ────────────────────────────────────────────────────────────────
PRODUTOS = [
    # (sku, nome, categoria, subcategoria, unidade, peso_kg, preco_base, custo_pct)
    ("BEV-001", "Suco de Laranja 1L", "Bebidas", "Sucos", "CX12", 13.0, 42.00, 0.52),
    ("BEV-002", "Água Mineral 500ml", "Bebidas", "Água", "CX24", 12.5, 18.00, 0.38),
    ("BEV-003", "Refrigerante Cola 2L", "Bebidas", "Refrigerantes", "CX6", 13.2, 28.00, 0.45),
    ("BEV-004", "Isotônico Limão 500ml", "Bebidas", "Funcionais", "CX12", 7.2, 55.00, 0.50),
    ("SNK-001", "Batata Chips 100g", "Snacks", "Salgados", "CX24", 2.4, 72.00, 0.48),
    ("SNK-002", "Amendoim Torrado 200g", "Snacks", "Nuts", "CX20", 4.0, 60.00, 0.42),
    ("SNK-003", "Biscoito Cream Cracker", "Snacks", "Biscoitos", "CX30", 9.0, 65.00, 0.44),
    ("LAT-001", "Leite Integral UHT 1L", "Laticínios", "Leite", "CX12", 12.6, 38.00, 0.65),
    ("LAT-002", "Iogurte Natural 170g", "Laticínios", "Iogurte", "CX12", 2.04, 32.00, 0.58),
    ("LAT-003", "Queijo Mussarela KG", "Laticínios", "Queijos", "UN", 1.0, 35.00, 0.62),
    ("GRA-001", "Arroz Parboilizado 5kg", "Grãos", "Arroz", "SC", 5.0, 22.00, 0.55),
    ("GRA-002", "Feijão Carioca 1kg", "Grãos", "Feijão", "SC", 1.0, 9.50, 0.52),
    ("PAD-001", "Macarrão Espaguete 500g", "Padaria/Massas", "Massas", "CX20", 10.0, 44.00, 0.48),
]

CLIENTES = [
    ("Atacadão Centro-Oeste", "Atacado", "Grande", "Goiânia", "GO", "Centro-Oeste"),
    ("Makro Sudeste", "Atacado", "Grande", "São Paulo", "SP", "Sudeste"),
    ("Supermercado Boa Sorte", "Varejo", "Médio", "Curitiba", "PR", "Sul"),
    ("Rede Hiper Sul", "Varejo", "Grande", "Porto Alegre", "RS", "Sul"),
    ("Distribuidora Norte Ltda", "Distribuidor", "Médio", "Belém", "PA", "Norte"),
    ("Food Service Express", "Food Service", "Médio", "Rio de Janeiro", "RJ", "Sudeste"),
    ("Mercearia São João", "Varejo", "Pequeno", "Florianópolis", "SC", "Sul"),
    ("Grupo Varejo NE", "Varejo", "Grande", "Recife", "PE", "Nordeste"),
    ("Restaurantes União", "Food Service", "Grande", "Belo Horizonte", "MG", "Sudeste"),
    ("Distribuidora Alfa", "Distribuidor", "Grande", "Campinas", "SP", "Sudeste"),
    ("Supermercado Econômico", "Varejo", "Médio", "Londrina", "PR", "Sul"),
    ("Cash & Carry Nordeste", "Atacado", "Médio", "Salvador", "BA", "Nordeste"),
]

VENDEDORES = [
    ("V001", "Carlos Mendes", "Equipe Sul", "Sul"),
    ("V002", "Ana Paula Lima", "Equipe Sul", "Sul"),
    ("V003", "Roberto Santos", "Equipe Sudeste", "Sudeste"),
    ("V004", "Fernanda Costa", "Equipe Sudeste", "Sudeste"),
    ("V005", "Marcos Oliveira", "Equipe Norte/NE", "Norte/Nordeste"),
    ("V006", "Juliana Ferreira", "Equipe CO", "Centro-Oeste"),
]

CANAIS = ["Direto", "Distribuidor", "E-commerce", "Televendas"]


# ── Sazonalidade mensal (fator multiplicador de volume) ──────────────────────
SAZONALIDADE = {
    1: 0.85, 2: 0.80, 3: 0.90, 4: 0.95,
    5: 1.00, 6: 0.95, 7: 1.00, 8: 1.05,
    9: 1.10, 10: 1.15, 11: 1.30, 12: 1.25
}


def gerar_datas(n: int) -> list[date]:
    delta = (DATA_FIM - DATA_INICIO).days
    datas = []
    for _ in range(n):
        d = DATA_INICIO + timedelta(days=random.randint(0, delta))
        # Sem domingos (indústria)
        if d.weekday() == 6:
            d += timedelta(days=1)
        datas.append(d)
    return datas


def main():
    datas = gerar_datas(N_PEDIDOS)

    rows = []
    for i, data in enumerate(datas):
        prod   = random.choice(PRODUTOS)
        client = random.choice(CLIENTES)
        vend   = random.choice(VENDEDORES)
        canal  = random.choice(CANAIS)

        saz    = SAZONALIDADE[data.month]
        trend  = 1 + 0.12 * ((data.year - 2023) + (data.month - 1) / 12)  # crescimento YoY
        qty_base = np.random.lognormal(mean=2.5, sigma=0.6)
        qty    = round(qty_base * saz * trend, 3)

        preco  = prod[6] * np.random.uniform(0.95, 1.10)
        desc   = round(np.random.choice([0, 2, 3, 5, 7, 10], p=[0.30, 0.20, 0.20, 0.15, 0.10, 0.05]), 2)
        rec_br = round(qty * preco, 2)
        rec_lq = round(rec_br * (1 - desc / 100), 2)
        custo  = round(rec_br * prod[7], 2)
        margem = round(rec_lq - custo, 2)

        dev    = round(qty * np.random.choice([0, 0, 0, 0.02, 0.05], p=[0.80, 0.10, 0.05, 0.03, 0.02]), 3)

        meta_qty = round(qty * np.random.uniform(0.90, 1.15), 3)
        meta_rec = round(rec_lq * np.random.uniform(0.90, 1.15), 2)

        rows.append({
            "data":           data.isoformat(),
            "ano":            data.year,
            "mes":            data.month,
            "nome_mes":       data.strftime("%B"),
            "trimestre":      (data.month - 1) // 3 + 1,
            "numero_pedido":  f"PED-{2023 + (data.year - 2023)}-{i+1:05d}",
            "sku":            prod[0],
            "produto":        prod[1],
            "categoria":      prod[2],
            "subcategoria":   prod[3],
            "unidade":        prod[4],
            "cliente":        client[0],
            "segmento":       client[1],
            "porte":          client[2],
            "cidade":         client[3],
            "estado":         client[4],
            "regiao":         client[5],
            "vendedor":       vend[2],
            "equipe":         vend[3],
            "regional":       vend[3],
            "canal":          canal,
            "quantidade":     qty,
            "quantidade_dev": dev,
            "preco_unitario": round(preco, 4),
            "desconto_pct":   desc,
            "receita_bruta":  rec_br,
            "receita_liquida": rec_lq,
            "custo_total":    custo,
            "margem_bruta":   margem,
            "meta_quantidade": meta_qty,
            "meta_receita":   meta_rec,
        })

    df = pd.DataFrame(rows).sort_values("data").reset_index(drop=True)
    out = os.path.join(OUTPUT_DIR, "vendas_industriais.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"✅ Dataset gerado: {out}")
    print(f"   Linhas: {len(df):,}")
    print(f"   Período: {df['data'].min()} → {df['data'].max()}")
    print(f"   Receita total: R$ {df['receita_liquida'].sum():,.2f}")
    return df


if __name__ == "__main__":
    main()
