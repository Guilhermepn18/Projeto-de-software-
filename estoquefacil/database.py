"""Acesso ao banco SQLite do EstoqueFácil."""
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "estoquefacil.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

INITIAL_PRODUCTS = [
    ("Skol Lata 350 ml", 3.50, 0, 12, "🍺"),
    ("Heineken Long Neck", 6.50, 0, 8, "🍾"),
    ("Vinho Tinto Reservado", 29.90, 0, 4, "🍷"),
    ("Brahma Lata 350 ml", 3.20, 6, 10, "🍺"),
    ("Coca-Cola 2 L", 7.50, 4, 8, "🥤"),
    ("Original Lata 350 ml", 3.80, 48, 12, "🍺"),
    ("Espumante Chandon", 59.90, 12, 4, "🥂"),
]


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        count = conn.execute("SELECT COUNT(*) FROM produto").fetchone()[0]
        if count == 0:
            conn.executemany(
                """INSERT INTO produto (nome, preco, quantidade_atual, estoque_minimo, emoji)
                   VALUES (?, ?, ?, ?, ?)""",
                INITIAL_PRODUCTS,
            )


def product_to_dict(row):
    return {
        "id": row["id_produto"],
        "name": row["nome"],
        "price": float(row["preco"]),
        "quantity": int(row["quantidade_atual"]),
        "minimum": int(row["estoque_minimo"]),
        "emoji": row["emoji"],
    }


def movement_to_dict(row):
    return {
        "id": row["id_movimentacao"],
        "productId": row["id_produto"],
        "productName": row["nome"],
        "type": row["tipo_movimentacao"],
        "quantity": row["quantidade"],
        "unitCost": float(row["custo_unitario"]),
        "supplier": row["fornecedor"],
        "unit": row["unidade"],
        "date": row["data_movimentacao"],
        "notes": row["observacoes"],
        "createdAt": row["criado_em"],
    }
