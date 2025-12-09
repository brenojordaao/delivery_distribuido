from fastapi import FastAPI, HTTPException
import json
import os
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Serviço de Catálogo")
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ARQUIVO_PRODUTOS = "produtos.json"


# ------------------------------------------
# Funções internas para carregar/salvar dados
# ------------------------------------------
def carregar_produtos() -> List[Dict]:
    """Lê o arquivo produtos.json ou cria um padrão caso não exista."""
    if not os.path.exists(ARQUIVO_PRODUTOS):
        produtos_padrao = [
            {"id": 1, "nome": "Hambúrguer", "preco": 20.0},
            {"id": 2, "nome": "Pizza", "preco": 35.0},
            {"id": 3, "nome": "Refrigerante", "preco": 6.0}
        ]
        with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
            json.dump(produtos_padrao, f, indent=4, ensure_ascii=False)

    with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_produtos(produtos: List[Dict]):
    """Sobrescreve o arquivo com a lista atualizada de produtos."""
    with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)


# ---------------------------
# Rotas da API do Catálogo
# ---------------------------

@app.get("/")
def raiz():
    return {"mensagem": "Serviço de Catálogo ativo. Use /produtos"}


@app.get("/produtos")
def listar_produtos():
    """Retorna a lista completa de produtos."""
    return carregar_produtos()


@app.get("/produtos/{produto_id}")
def obter_produto(produto_id: int):
    """Retorna os detalhes de um produto específico."""
    produtos = carregar_produtos()

    for p in produtos:
        if p["id"] == produto_id:
            return p

    raise HTTPException(status_code=404, detail="Produto não encontrado")


@app.post("/produtos")
def adicionar_produto(produto: Dict):
    """Adiciona um novo produto ao catálogo."""
    produtos = carregar_produtos()

    # validar ID duplicado
    for p in produtos:
        if p["id"] == produto["id"]:
            raise HTTPException(status_code=400, detail="ID já existe no catálogo")

    produtos.append(produto)
    salvar_produtos(produtos)

    return {"mensagem": "Produto adicionado com sucesso", "produto": produto}


@app.delete("/produtos/{produto_id}")
def remover_produto(produto_id: int):
    """Remove um produto do catálogo pelo ID."""
    produtos = carregar_produtos()

    novos_produtos = [p for p in produtos if p["id"] != produto_id]

    if len(novos_produtos) == len(produtos):
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    salvar_produtos(novos_produtos)

    return {"mensagem": "Produto removido com sucesso", "id": produto_id}
