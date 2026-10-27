"""Backend Flask do EstoqueFácil.

Execute com: python app.py
A interface e a API são servidas pelo mesmo processo Flask.
"""
from datetime import date
import sqlite3

from flask import Flask, jsonify, request, send_from_directory

from database import (
    BASE_DIR,
    INITIAL_PRODUCTS,
    get_connection,
    initialize_database,
    movement_to_dict,
    product_to_dict,
)

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


def error(message, status=400):
    return jsonify({"error": message}), status


def read_json():
    return request.get_json(silent=True) or {}


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "application": "EstoqueFácil"})


@app.get("/api/products")
def list_products():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM produto ORDER BY nome COLLATE NOCASE").fetchall()
    return jsonify([product_to_dict(row) for row in rows])


@app.post("/api/products")
def create_product():
    data = read_json()
    name = str(data.get("name", "")).strip()
    if not name:
        return error("Informe o nome do produto.")
    try:
        price = float(data.get("price", 0))
        quantity = int(data.get("quantity", 0))
        minimum = int(data.get("minimum", 0))
    except (TypeError, ValueError):
        return error("Preço e quantidades devem ser numéricos.")
    if price < 0 or quantity < 0 or minimum < 0:
        return error("Preço e quantidades não podem ser negativos.")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO produto (nome, preco, quantidade_atual, estoque_minimo, emoji) VALUES (?, ?, ?, ?, ?)",
                (name, price, quantity, minimum, str(data.get("emoji", "📦"))[:12]),
            )
            row = conn.execute("SELECT * FROM produto WHERE id_produto = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(product_to_dict(row)), 201
    except sqlite3.IntegrityError:
        return error("Já existe um produto com esse nome.", 409)


@app.put("/api/products/<int:product_id>")
def update_product(product_id):
    data = read_json()
    name = str(data.get("name", "")).strip()
    if not name:
        return error("Informe o nome do produto.")
    try:
        price = float(data.get("price", 0))
        minimum = int(data.get("minimum", 0))
        quantity = int(data.get("quantity", 0))
    except (TypeError, ValueError):
        return error("Preço e quantidades devem ser numéricos.")
    if price < 0 or minimum < 0 or quantity < 0:
        return error("Preço e quantidades não podem ser negativos.")
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "UPDATE produto SET nome=?, preco=?, quantidade_atual=?, estoque_minimo=?, emoji=? WHERE id_produto=?",
                (name, price, quantity, minimum, str(data.get("emoji", "📦"))[:12], product_id),
            )
            if cursor.rowcount == 0:
                return error("Produto não encontrado.", 404)
            row = conn.execute("SELECT * FROM produto WHERE id_produto=?", (product_id,)).fetchone()
        return jsonify(product_to_dict(row))
    except sqlite3.IntegrityError:
        return error("Já existe outro produto com esse nome.", 409)


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    try:
        with get_connection() as conn:
            cursor = conn.execute("DELETE FROM produto WHERE id_produto=?", (product_id,))
            if cursor.rowcount == 0:
                return error("Produto não encontrado.", 404)
        return jsonify({"message": "Produto excluído."})
    except sqlite3.IntegrityError:
        return error("Não é possível excluir um produto que possui movimentações registradas.", 409)


@app.get("/api/movements")
def list_movements():
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT m.*, p.nome FROM movimentacao_estoque m
               JOIN produto p ON p.id_produto=m.id_produto
               ORDER BY m.id_movimentacao DESC"""
        ).fetchall()
    return jsonify([movement_to_dict(row) for row in rows])


@app.post("/api/movements")
def create_movement():
    data = read_json()
    movement_type = str(data.get("type", "ENTRADA")).strip().upper()
    if movement_type not in ("ENTRADA", "SAIDA"):
        return error("Tipo de movimentação inválido. Use ENTRADA ou SAIDA.")
    try:
        product_id = int(data.get("productId"))
        quantity = int(data.get("quantity"))
        unit_cost = float(data.get("unitCost", 0) or 0)
    except (TypeError, ValueError):
        return error("Produto, quantidade e custo devem ser válidos.")
    if quantity <= 0:
        return error("A quantidade deve ser um número inteiro maior que zero.")
    if unit_cost < 0 or (movement_type == "ENTRADA" and unit_cost <= 0):
        return error("Informe um custo unitário válido para a entrada.")
    movement_date = str(data.get("date", "")).strip()
    try:
        date.fromisoformat(movement_date)
    except ValueError:
        return error("Informe uma data válida no formato AAAA-MM-DD.")

    try:
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            product = conn.execute("SELECT * FROM produto WHERE id_produto=?", (product_id,)).fetchone()
            if product is None:
                return error("Produto não encontrado.", 404)
            current = int(product["quantidade_atual"])
            if movement_type == "SAIDA" and quantity > current:
                return error(f"Saldo insuficiente. Estoque atual: {current} unidade(s).", 409)
            new_quantity = current + quantity if movement_type == "ENTRADA" else current - quantity
            if movement_type == "ENTRADA":
                conn.execute("UPDATE produto SET quantidade_atual=?, preco=? WHERE id_produto=?", (new_quantity, unit_cost, product_id))
            else:
                conn.execute("UPDATE produto SET quantidade_atual=? WHERE id_produto=?", (new_quantity, product_id))
            cursor = conn.execute(
                """INSERT INTO movimentacao_estoque
                   (id_produto, tipo_movimentacao, quantidade, custo_unitario, fornecedor, unidade, data_movimentacao, observacoes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    product_id, movement_type, quantity, unit_cost,
                    str(data.get("supplier", "")).strip()[:100],
                    str(data.get("unit", "unidades")).strip()[:30],
                    movement_date, str(data.get("notes", "")).strip()[:300],
                ),
            )
            movement = conn.execute(
                """SELECT m.*, p.nome FROM movimentacao_estoque m
                   JOIN produto p ON p.id_produto=m.id_produto WHERE m.id_movimentacao=?""",
                (cursor.lastrowid,),
            ).fetchone()
        return jsonify({"movement": movement_to_dict(movement), "product": {
            **product_to_dict({"id_produto": product_id, "nome": product["nome"], "preco": unit_cost if movement_type == "ENTRADA" else product["preco"], "quantidade_atual": new_quantity, "estoque_minimo": product["estoque_minimo"], "emoji": product["emoji"]}),
        }}), 201
    except sqlite3.IntegrityError as exc:
        return error(f"Não foi possível salvar a movimentação: {exc}", 400)


@app.post("/api/reset-demo")
def reset_demo():
    with get_connection() as conn:
        conn.execute("DELETE FROM movimentacao_estoque")
        conn.execute("DELETE FROM produto")
        conn.executemany(
            "INSERT INTO produto (nome, preco, quantidade_atual, estoque_minimo, emoji) VALUES (?, ?, ?, ?, ?)",
            INITIAL_PRODUCTS,
        )
    return jsonify({"message": "Dados de demonstração restaurados."})


@app.errorhandler(404)
def not_found(_exc):
    if request.path.startswith("/api/"):
        return error("Rota da API não encontrada.", 404)
    return _exc


initialize_database()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
