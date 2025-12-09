from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"mensagem": "Serviço de Pagamentos ativo"}

@app.post("/pagamentos")
def processar_pagamento(dados: dict):
    pedido_id = dados.get("pedido_id")
    total = dados.get("total", 0)

    if total <= 0:
        return {
            "status_pagamento": "recusado",
            "mensagem": f"Pagamento do pedido {pedido_id} recusado."
        }

    return {
        "status_pagamento": "aprovado",
        "mensagem": f"Pagamento do pedido {pedido_id} aprovado."
    }
