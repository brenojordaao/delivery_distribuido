from fastapi import FastAPI, HTTPException
import requests
import json
import uuid
import os

CATALOGO_URL = "http://127.0.0.1:8001/produtos"
PAGAMENTO_URL = "http://127.0.0.1:8003/pagamentos"
ARQUIVO_PEDIDOS = "pedidos.json"

app = FastAPI()

# -------------------------
# Funções auxiliares
# -------------------------

def carregar_pedidos():
    """Carrega pedidos do arquivo."""
    if os.path.exists(ARQUIVO_PEDIDOS):
        with open(ARQUIVO_PEDIDOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_pedidos(pedidos):
    """Salva lista completa de pedidos no arquivo."""
    with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, indent=4, ensure_ascii=False)

# -------------------------
# Rotas
# -------------------------

@app.get("/")
def raiz():
    return {"mensagem": "Serviço de Pedidos ativo. Use /pedidos"}

@app.get("/pedidos")
def listar_pedidos():
    return carregar_pedidos()

@app.get("/pedidos/{pedido_id}")
def obter_pedido(pedido_id: str):
    pedidos = carregar_pedidos()

    for p in pedidos:
        if p["id"] == pedido_id:
            return p

    raise HTTPException(status_code=404, detail="Pedido não encontrado")

@app.post("/pedidos")
def criar_pedido(itens: list):
    """
    Estrutura esperada:
    [
        {"id": 1, "quantidade": 2},
        {"id": 3, "quantidade": 1}
    ]
    """

    # 1) Obter produtos do catálogo
    try:
        resposta = requests.get(CATALOGO_URL)
        produtos = resposta.json()
    except:
        raise HTTPException(status_code=500, detail="Erro ao consultar o catálogo")

    # 2) Validar itens e calcular total
    total = 0
    for item in itens:
        prod = next((p for p in produtos if p["id"] == item["id"]), None)
        if not prod:
            raise HTTPException(status_code=400, detail=f"Produto ID {item['id']} inválido")

        total += prod["preco"] * item["quantidade"]

    # 3) Criar pedido local
    pedido = {
        "id": str(uuid.uuid4()),
        "itens": itens,
        "total": total,
        "status": "aguardando pagamento"
    }

    # 4) Enviar para o serviço de pagamento
    pagamento_payload = {
        "pedido_id": pedido["id"],
        "total": total
    }

    try:
        resposta_pg = requests.post(PAGAMENTO_URL, json=pagamento_payload)
        pagamento = resposta_pg.json()

        if pagamento["status_pagamento"] == "aprovado":
            pedido["status"] = "pago"
        else:
            pedido["status"] = "pagamento recusado"

    except:
        pedido["status"] = "erro no serviço de pagamento"

    # 5) Salvar pedido
    pedidos = carregar_pedidos()
    pedidos.append(pedido)
    salvar_pedidos(pedidos)

    return pedido
