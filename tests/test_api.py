def test_create_and_get_product(client):
    """Test la création d'un produit via l'API puis sa récupération."""
    # 1. Création
    payload = {
        "name": "Sony WH-1000XM5",
        "store_name": "ShopA",
        "url": "demo_sites/shop_a.html",
        "alert_threshold": 250.0
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sony WH-1000XM5"
    product_id = data["id"]
    assert len(data["sources"]) == 1

    # 2. Récupération par ID
    get_response = client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Sony WH-1000XM5"


def test_list_products(client):
    """Test le listing des produits."""
    client.post("/api/products", json={"name": "Produit 1"})
    client.post("/api/products", json={"name": "Produit 2"})

    response = client.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2


def test_delete_product(client):
    """Test la suppression d'un produit."""
    res_create = client.post("/api/products", json={"name": "Produit A Supprimer"})
    product_id = res_create.json()["id"]

    res_delete = client.delete(f"/api/products/{product_id}")
    assert res_delete.status_code == 200

    res_get = client.get(f"/api/products/{product_id}")
    assert res_get.status_code == 404


def test_get_product_prices_history(client):
    """Test la récupération de l'historique des prix d'un produit."""
    res = client.post("/api/products", json={
        "name": "Nintendo Switch",
        "store_name": "ShopC",
        "url": "demo_sites/shop_c.html",
        "alert_threshold": 300.0
    })
    product_id = res.json()["id"]

    res_prices = client.get(f"/api/products/{product_id}/prices")
    assert res_prices.status_code == 200
    data = res_prices.json()
    assert data["product_id"] == product_id
    assert len(data["stores"]) == 1


def test_alerts_endpoint(client):
    """Test l'endpoint de consultation des alertes."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
