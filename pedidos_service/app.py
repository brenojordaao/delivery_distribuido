from fastapi import FastAPI
import requests
import json
import uuid

CATALOGO_URL = "http://127.0.0.1:8001"

app = FastAPI()

@app.post("/pedidos")
def criar_pedido(itens: list):
    produtos = requests.get(f"{CATALOGO_URL}/produtos").json()

    total = 0
    for item in itens:
        prod = next((p for p in produtos if p["id"] == item["id"]), None)
        if prod:
            total += prod["preco"] * item["quantidade"]

    pedido_id = str(uuid.uuid4())

    pedido = {
        "id": pedido_id,
        "itens": itens,
        "total": total,
        "status": "aguardando pagamento"
    }

    with open("pedidos_db.json", "r+") as f:
        data = json.load(f)
        data.append(pedido)
        f.seek(0)
        json.dump(data, f, indent=4)

    return pedido
