from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def raiz():
    return {"mensagem": "Servico de Catalogo rodando. Use /produtos"}

@app.get("/produtos")
def listar_produtos():
    with open("produtos.json") as f:
        return json.load(f)
