# EstoqueFácil

Protótipo web responsivo para controle de estoque de uma adega. A versão atual integra interface HTML/CSS/JavaScript a uma API Python com Flask e banco SQLite.

## Funcionalidades

- Painel com resumo dos produtos, estoque baixo e produtos zerados.
- Registro de entradas pela interface, com atualização persistente do saldo no SQLite.
- Consulta, busca e filtros de estoque.
- API para cadastro, edição e exclusão de produtos.
- API para consulta do histórico e registro de entradas e saídas.
- Bloqueio de saída quando a quantidade solicitada é maior que o saldo disponível.
- Validação de dados e transação no banco para atualizar saldo e histórico juntos.
- Dados iniciais de demonstração inseridos automaticamente no primeiro uso.

## Requisitos

- Python 3.10 ou superior (recomendado Python 3.12).
- pip.

## Executar localmente

Abra o terminal dentro desta pasta e execute:

### Windows

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Se o PowerShell bloquear a ativação do ambiente, execute diretamente `py -m pip install -r requirements.txt` e depois `py app.py`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000** no navegador. Mantenha o terminal aberto enquanto usa o sistema. O arquivo `estoquefacil.db` será criado automaticamente nesta pasta.

## Endpoints da API

- `GET /api/health` — verifica se o backend está ativo.
- `GET /api/products` — lista produtos.
- `POST /api/products` — cadastra produto. JSON exemplo: `{"name":"Água 500 ml","price":2.5,"quantity":10,"minimum":4,"emoji":"💧"}`.
- `PUT /api/products/<id>` — atualiza dados de um produto.
- `DELETE /api/products/<id>` — exclui produto sem movimentações vinculadas.
- `GET /api/movements` — consulta movimentações.
- `POST /api/movements` — registra entrada ou saída. Exemplo de entrada: `{"productId":1,"type":"ENTRADA","quantity":24,"unitCost":3.5,"date":"2026-11-10","supplier":"Distribuidora","unit":"unidades","notes":"Entrega"}`. Para saída, use `"type":"SAIDA"` e `unitCost:0`.
- `POST /api/reset-demo` — restaura os produtos iniciais e apaga as movimentações de demonstração.

## Estrutura principal

- `app.py`: servidor Flask e endpoints HTTP.
- `database.py`: conexão SQLite, inicialização e conversão dos registros.
- `schema.sql`: tabelas e índice de movimentações.
- `requirements.txt`: dependências Python.
- `index.html`, `style.css`, `app.js`: frontend responsivo integrado à API.

## Observações importantes

O sistema é um protótipo acadêmico. Não inclui autenticação, autorização por usuário, backups automáticos nem configuração de produção. Não exponha o servidor de desenvolvimento diretamente à internet nem armazene dados comerciais reais antes de implementar controles de segurança e backups.

O GitHub Pages não executa Python/Flask. Para publicar o sistema completo, hospede o backend em uma plataforma compatível com Python e configure a persistência do banco. Para desenvolvimento e apresentação local, siga os comandos acima.
