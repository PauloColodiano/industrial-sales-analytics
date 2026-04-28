"""
analysis.py
===========
Análise completa de performance comercial para o setor industrial.
Gera 6 visualizações publicáveis em Python (matplotlib + seaborn + plotly).

Autor: Paulo Augusto Colodiano Martins
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "..", "data", "vendas_industriais.csv")
OUT_DIR    = os.path.join(BASE_DIR, "visualizations")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Paleta e estilo ──────────────────────────────────────────────────────────
PALETTE     = ["#1B4F72", "#2E86C1", "#AED6F1", "#F39C12", "#E74C3C", "#27AE60", "#8E44AD"]
ACCENT      = "#F39C12"
DARK        = "#1B4F72"
LIGHT_BG    = "#F7F9FC"
GRID_COLOR  = "#DDE3EC"

plt.rcParams.update({
    "figure.facecolor":  LIGHT_BG,
    "axes.facecolor":    LIGHT_BG,
    "axes.grid":         True,
    "grid.color":        GRID_COLOR,
    "grid.linewidth":    0.8,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.titlecolor":   DARK,
    "axes.labelcolor":   "#555",
    "xtick.color":       "#555",
    "ytick.color":       "#555",
})

fmt_brl = lambda x: f"R$ {x/1e6:.1f}M" if x >= 1e6 else f"R$ {x/1e3:.0f}K"


# ── Carrega dados ────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["data"])
    df["ano_mes"] = df["data"].dt.to_period("M")
    return df


# ────────────────────────────────────────────────────────────────────────────
# VIZ 1 — Receita Mensal vs Meta (realizado x meta, com gap highlight)
# ────────────────────────────────────────────────────────────────────────────
def viz_receita_vs_meta(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle("Receita Mensal vs Meta — 2023/2024", fontsize=16, fontweight="bold", color=DARK, y=1.01)

    mensal = (
        df.groupby(["ano", "mes"])
        .agg(receita=("receita_liquida", "sum"), meta=("meta_receita", "sum"))
        .reset_index()
        .sort_values(["ano", "mes"])
    )
    mensal["label"] = mensal.apply(lambda r: f"{int(r['mes']):02d}/{int(r['ano'])}", axis=1)
    mensal["ating"] = mensal["receita"] / mensal["meta"] * 100

    x = np.arange(len(mensal))
    w = 0.38

    ax = axes[0]
    bars_r = ax.bar(x - w/2, mensal["receita"], width=w, color=DARK, label="Realizado", alpha=0.9)
    bars_m = ax.bar(x + w/2, mensal["meta"],    width=w, color=ACCENT, label="Meta", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(mensal["label"], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_brl(v)))
    ax.set_ylabel("Receita Líquida")
    ax.legend(loc="upper left")

    # atingimento
    ax2 = axes[1]
    colors = [DARK if v >= 100 else "#E74C3C" for v in mensal["ating"]]
    ax2.bar(x, mensal["ating"], color=colors, alpha=0.85)
    ax2.axhline(100, color=ACCENT, linestyle="--", linewidth=1.2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(mensal["label"], rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("% Ating.")
    ax2.set_ylim(50, 130)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "01_receita_vs_meta.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ────────────────────────────────────────────────────────────────────────────
# VIZ 2 — Share de Receita por Categoria (donut + barras)
# ────────────────────────────────────────────────────────────────────────────
def viz_share_categoria(df: pd.DataFrame):
    cat = df.groupby("categoria")["receita_liquida"].sum().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Performance por Categoria de Produto", fontsize=15, fontweight="bold", color=DARK)

    # Donut
    wedges, texts, autotexts = ax1.pie(
        cat.values,
        labels=cat.index,
        colors=PALETTE[:len(cat)],
        autopct="%1.1f%%",
        pctdistance=0.78,
        startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
    ax1.set_title("Share de Receita", pad=15)

    # Barras horizontais
    ax2.barh(cat.index[::-1], cat.values[::-1], color=PALETTE[:len(cat)][::-1], alpha=0.88)
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_brl(v)))
    ax2.set_title("Receita Total por Categoria")
    for i, v in enumerate(cat.values[::-1]):
        ax2.text(v * 1.01, i, fmt_brl(v), va="center", fontsize=9, color=DARK, fontweight="bold")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "02_share_categoria.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ────────────────────────────────────────────────────────────────────────────
# VIZ 3 — Top 10 Produtos por Receita + Margem %
# ────────────────────────────────────────────────────────────────────────────
def viz_top_produtos(df: pd.DataFrame):
    prod = (
        df.groupby("produto")
        .agg(receita=("receita_liquida", "sum"), margem=("margem_bruta", "sum"))
        .assign(pct_margem=lambda d: d["margem"] / d["receita"] * 100)
        .nlargest(10, "receita")
        .sort_values("receita")
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle("Top 10 Produtos — Receita e Margem Bruta", fontsize=15, fontweight="bold", color=DARK)

    bars = ax.barh(prod.index, prod["receita"], color=DARK, alpha=0.85, height=0.55)
    ax2  = ax.twiny()
    ax2.plot(prod["pct_margem"], prod.index, "o-", color=ACCENT, linewidth=2, markersize=7, label="Margem %")
    ax2.set_xlabel("Margem Bruta (%)", color=ACCENT)
    ax2.tick_params(axis="x", colors=ACCENT)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_brl(v)))
    ax.set_xlabel("Receita Líquida")
    for bar, (_, row) in zip(bars, prod.iterrows()):
        ax.text(bar.get_width() * 0.02, bar.get_y() + bar.get_height() / 2,
                fmt_brl(row["receita"]), va="center", color="white", fontsize=9, fontweight="bold")

    ax.legend(["Receita"], loc="lower right")
    ax2.legend(loc="upper left")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "03_top_produtos.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ────────────────────────────────────────────────────────────────────────────
# VIZ 4 — Heatmap de Vendas: Mês × Categoria
# ────────────────────────────────────────────────────────────────────────────
def viz_heatmap(df: pd.DataFrame):
    pivot = (
        df.groupby(["nome_mes", "mes", "categoria"])["receita_liquida"]
        .sum()
        .reset_index()
        .sort_values("mes")
        .pivot_table(index="categoria", columns="nome_mes", values="receita_liquida", aggfunc="sum")
    )
    # reorder months
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    month_order = [m for m in month_order if m in pivot.columns]
    pivot = pivot[month_order]

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.suptitle("Heatmap de Receita — Categoria × Mês (2023+2024 somados)", fontsize=14, fontweight="bold", color=DARK)
    sns.heatmap(
        pivot / 1e3,
        ax=ax, cmap="Blues", annot=True, fmt=".0f",
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Receita (R$ K)"},
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=35, ha="right")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "04_heatmap_categoria_mes.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ────────────────────────────────────────────────────────────────────────────
# VIZ 5 — Curva ABC de Clientes
# ────────────────────────────────────────────────────────────────────────────
def viz_curva_abc(df: pd.DataFrame):
    cli = (
        df.groupby("cliente")["receita_liquida"].sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    cli["pct_acum"] = cli["receita_liquida"].cumsum() / cli["receita_liquida"].sum() * 100
    cli["curva"] = cli["pct_acum"].apply(lambda x: "A" if x <= 80 else ("B" if x <= 95 else "C"))
    color_map = {"A": DARK, "B": ACCENT, "C": "#AED6F1"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Curva ABC de Clientes", fontsize=15, fontweight="bold", color=DARK)

    # Receita por cliente
    colors = [color_map[c] for c in cli["curva"]]
    ax1.bar(range(len(cli)), cli["receita_liquida"], color=colors, alpha=0.85)
    ax1.set_xticklabels([])
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_brl(v)))
    ax1.set_xlabel("Clientes (ordenados por receita)")
    ax1.set_title("Receita por Cliente")

    from matplotlib.patches import Patch
    legend = [Patch(color=color_map[k], label=f"Curva {k}") for k in ["A", "B", "C"]]
    ax1.legend(handles=legend)

    # % acumulado (pareto)
    ax2.plot(range(len(cli)), cli["pct_acum"], color=DARK, linewidth=2)
    ax2.axhline(80, color=PALETTE[3], linestyle="--", linewidth=1, label="80% — Curva A")
    ax2.axhline(95, color=PALETTE[4], linestyle="--", linewidth=1, label="95% — Curva B")
    ax2.fill_between(range(len(cli)), cli["pct_acum"], alpha=0.08, color=DARK)
    ax2.set_xticklabels([])
    ax2.set_ylabel("% Receita Acumulada")
    ax2.set_title("Curva de Pareto")
    ax2.legend()

    # Summary
    resumo = cli.groupby("curva").agg(qtd=("cliente", "count"), receita=("receita_liquida", "sum"))
    for i, (curva, row) in enumerate(resumo.iterrows()):
        ax2.text(0.97, 0.95 - i * 0.13,
                 f"Curva {curva}: {row['qtd']} clientes → {fmt_brl(row['receita'])}",
                 transform=ax2.transAxes, ha="right", fontsize=9, color=color_map[curva], fontweight="bold")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "05_curva_abc_clientes.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ────────────────────────────────────────────────────────────────────────────
# VIZ 6 — YoY: Crescimento Anual por Região
# ────────────────────────────────────────────────────────────────────────────
def viz_yoy_regiao(df: pd.DataFrame):
    reg = (
        df.groupby(["ano", "regiao"])["receita_liquida"].sum()
        .reset_index()
    )
    pivot = reg.pivot(index="regiao", columns="ano", values="receita_liquida").fillna(0)
    pivot["variacao_pct"] = (pivot[2024] - pivot[2023]) / pivot[2023] * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Crescimento YoY por Região — 2023 vs 2024", fontsize=15, fontweight="bold", color=DARK)

    x = np.arange(len(pivot))
    w = 0.35
    ax1.bar(x - w/2, pivot[2023], width=w, label="2023", color=DARK, alpha=0.85)
    ax1.bar(x + w/2, pivot[2024], width=w, label="2024", color=ACCENT, alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(pivot.index, rotation=25, ha="right")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_brl(v)))
    ax1.set_title("Receita por Região")
    ax1.legend()

    colors = [DARK if v >= 0 else "#E74C3C" for v in pivot["variacao_pct"]]
    ax2.bar(pivot.index, pivot["variacao_pct"], color=colors, alpha=0.85)
    ax2.axhline(0, color="#555", linewidth=0.8)
    for i, (reg, v) in enumerate(pivot["variacao_pct"].items()):
        ax2.text(i, v + (1 if v >= 0 else -3), f"{v:.1f}%",
                 ha="center", fontsize=9, fontweight="bold",
                 color=DARK if v >= 0 else "#E74C3C")
    ax2.set_title("Variação % (YoY)")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax2.set_xticklabels(pivot.index, rotation=25, ha="right")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "06_yoy_regiao.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ {path}")


# ── KPIs Summary ─────────────────────────────────────────────────────────────
def print_kpis(df: pd.DataFrame):
    print("\n" + "="*55)
    print("  📊 KPIs — Industrial Sales Analytics")
    print("="*55)
    print(f"  Pedidos analisados  : {len(df):,}")
    print(f"  Receita Líquida     : {fmt_brl(df['receita_liquida'].sum())}")
    print(f"  Margem Bruta Total  : {fmt_brl(df['margem_bruta'].sum())}")
    print(f"  Margem Média (%)    : {df['margem_bruta'].sum()/df['receita_liquida'].sum()*100:.1f}%")
    print(f"  Clientes Únicos     : {df['cliente'].nunique()}")
    print(f"  Produtos Únicos     : {df['produto'].nunique()}")
    print(f"  Ticket Médio/Pedido : {fmt_brl(df.groupby('numero_pedido')['receita_liquida'].sum().mean())}")
    print(f"  Taxa Devolução      : {df['quantidade_dev'].sum()/df['quantidade'].sum()*100:.2f}%")
    print("="*55 + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔄 Carregando dados...")
    df = load_data()
    print_kpis(df)

    print("📈 Gerando visualizações...")
    viz_receita_vs_meta(df)
    viz_share_categoria(df)
    viz_top_produtos(df)
    viz_heatmap(df)
    viz_curva_abc(df)
    viz_yoy_regiao(df)

    print(f"\n✅ Todas as visualizações salvas em: {OUT_DIR}")
