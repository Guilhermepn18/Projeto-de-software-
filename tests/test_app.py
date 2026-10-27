import sys
from pathlib import Path

import pytest

# Localiza o backend dentro da pasta do projeto.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "estoquefacil"))

import app as app_module
import database


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Cada teste usa seu próprio banco temporário.
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    database.initialize_database()

    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as test_client:
        yield test_client


def get_product_id(client, name):
    products = client.get("/api/products").get_json()
    return next(product["id"] for product in products if product["name"] == name)


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_list_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.get_json()) > 0


def test_create_product(client):
    response = client.post("/api/products", json={
        "name": "Produto Teste",
        "price": 10.50,
        "quantity": 5,
        "minimum": 2,
    })
    assert response.status_code == 201
    assert response.get_json()["name"] == "Produto Teste"


def test_create_product_without_name(client):
    response = client.post("/api/products", json={"name": " "})
    assert response.status_code == 400


def test_create_product_with_negative_price(client):
    response = client.post("/api/products", json={
        "name": "Produto Negativo",
        "price": -1,
        "quantity": 1,
        "minimum": 0,
    })
    assert response.status_code == 400


def test_create_duplicate_product(client):
    payload = {
        "name": "Produto Teste",
        "price": 10,
        "quantity": 1,
        "minimum": 0,
    }
    assert client.post("/api/products", json=payload).status_code == 201
    response = client.post("/api/products", json=payload)
    assert response.status_code == 409


def test_update_product(client):
    product_id = get_product_id(client, "Coca-Cola 2 L")
    response = client.put(f"/api/products/{product_id}", json={
        "name": "Coca-Cola 2 L",
        "price": 8.50,
        "quantity": 10,
        "minimum": 3,
    })
    assert response.status_code == 200
    assert response.get_json()["quantity"] == 10


def test_update_missing_product(client):
    response = client.put("/api/products/999999", json={
        "name": "Inexistente",
        "price": 10,
        "quantity": 1,
        "minimum": 0,
    })
    assert response.status_code == 404


def test_delete_product(client):
    response = client.post("/api/products", json={
        "name": "Produto Para Excluir",
        "price": 5,
        "quantity": 1,
        "minimum": 0,
    })
    product_id = response.get_json()["id"]

    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == 200


def test_delete_missing_product(client):
    response = client.delete("/api/products/999999")
    assert response.status_code == 404


def test_create_stock_entry(client):
    product_id = get_product_id(client, "Skol Lata 350 ml")
    response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "ENTRADA",
        "quantity": 3,
        "unitCost": 4.50,
        "date": "2026-10-27",
    })
    assert response.status_code == 201
    assert response.get_json()["product"]["quantity"] == 3


def test_create_stock_exit(client):
    product_id = get_product_id(client, "Coca-Cola 2 L")
    response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "SAIDA",
        "quantity": 1,
        "unitCost": 0,
        "date": "2026-10-27",
    })
    assert response.status_code == 201
    assert response.get_json()["product"]["quantity"] == 3


def test_stock_exit_with_insufficient_quantity(client):
    product_id = get_product_id(client, "Skol Lata 350 ml")
    response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "SAIDA",
        "quantity": 1,
        "unitCost": 0,
        "date": "2026-10-27",
    })
    assert response.status_code == 409


def test_invalid_movement_type(client):
    product_id = get_product_id(client, "Coca-Cola 2 L")
    response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "TRANSFERENCIA",
        "quantity": 1,
        "unitCost": 0,
        "date": "2026-10-27",
    })
    assert response.status_code == 400


def test_invalid_movement_date(client):
    product_id = get_product_id(client, "Coca-Cola 2 L")
    response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "SAIDA",
        "quantity": 1,
        "unitCost": 0,
        "date": "data-invalida",
    })
    assert response.status_code == 400


def test_list_movements(client):
    response = client.get("/api/movements")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_api_route_not_found(client):
    response = client.get("/api/rota-inexistente")
    assert response.status_code == 404


def test_cannot_delete_product_with_movement(client):
    product_id = get_product_id(client, "Skol Lata 350 ml")

    movement_response = client.post("/api/movements", json={
        "productId": product_id,
        "type": "ENTRADA",
        "quantity": 1,
        "unitCost": 4.50,
        "date": "2026-10-27",
    })
    assert movement_response.status_code == 201

    response = client.delete(f"/api/products/{product_id}")
    assert response.status_code == 409