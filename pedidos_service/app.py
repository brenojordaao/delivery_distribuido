from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import os
from json import JSONDecodeError

app = FastAPI(title="Serviço de Pedidos")

# ========================
#    MODELOS
# ========================

class ItemPedido(BaseModel):
    id: int
    quantidade: int

# ========================
#   ARQUIVO JSON LOCAL
# ========================

# Caminho absoluto do arquivo, sempre dentro de pedidos_service
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PEDIDOS = os.path.join(BASE_DIR, "pedidos.json")


def carregar_pedidos():
    """Carrega pedidos do arquivo JSON. Se não existir ou estiver quebrado, retorna lista vazia."""
    if not os.path.exists(ARQUIVO_PEDIDOS):
        # cria arquivo vazio padrão
        with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as f:
            f.write("[]")
        return []

    try:
        with open(ARQUIVO_PEDIDOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except JSONDecodeError:
        # arquivo corrompido → reseta
        with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as f:
            f.write("[]")
        return []


def salvar_pedidos(pedidos):
    """Salva lista completa de pedidos no arquivo."""
    with open(ARQUIVO_PEDIDOS, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, indent=4, ensure_ascii=False)

# ========================
#   ROTAS DO SISTEMA
# ========================

@app.get("/")
def raiz():
    return {"mensagem": "Serviço de Pedidos ativo. Use /pedidos"}

@app.get("/pedidos")
def listar_pedidos():
    return carregar_pedidos()

@app.get("/pedidos/{pedido_id}")
def obter_pedido(pedido_id: int):
    pedidos = carregar_pedidos()
    pedido = next((p for p in pedidos if p["id"] == pedido_id), None)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@app.post("/pedidos")
def criar_pedido(itens: list[ItemPedido]):
    """
    Exemplo de body:
    [
      {"id": 1, "quantidade": 2},
      {"id": 3, "quantidade": 1}
    ]
    """

    # 1) Consultar catálogo
    try:
        resp = requests.get("http://127.0.0.1:8001/produtos")
        produtos = resp.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao consultar catálogo")

    # 2) Calcular total
    total = 0.0
    for item in itens:
        prod = next((p for p in produtos if p["id"] == item.id), None)
        if not prod:
            raise HTTPException(status_code=400, detail=f"Produto {item.id} não encontrado no catálogo")
        total += float(prod["preco"]) * item.quantidade

    # 3) Carregar pedidos existentes
    pedidos = carregar_pedidos()
    novo_id = len(pedidos) + 1

    pedido = {
        "id": novo_id,
        "total": total,
        "status": "confirmado",   # por enquanto sempre confirmado
        "itens": [item.dict() for item in itens]
    }

    # 4) Salvar
    pedidos.append(pedido)
    salvar_pedidos(pedidos)

    return pedido
