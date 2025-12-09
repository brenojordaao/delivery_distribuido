from fastapi import FastAPI

app = FastAPI()

@app.post("/pagamentos")
def processar_pagamento(pedido: dict):
    return {"status_pagamento": "aprovado"}
