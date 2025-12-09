fetch("http://127.0.0.1:8001/produtos")
    .then(r => r.json())
    .then(produtos => {
        document.getElementById("produtos").innerHTML =
            produtos.map(p => `<p>${p.nome} - R$ ${p.preco}</p>`).join("");
    });
