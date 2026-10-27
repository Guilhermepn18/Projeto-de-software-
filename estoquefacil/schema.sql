PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produto (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    preco REAL NOT NULL DEFAULT 0 CHECK (preco >= 0),
    quantidade_atual INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_atual >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    emoji TEXT NOT NULL DEFAULT '📦',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimentacao_estoque (
    id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    tipo_movimentacao TEXT NOT NULL CHECK (tipo_movimentacao IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    custo_unitario REAL NOT NULL DEFAULT 0 CHECK (custo_unitario >= 0),
    fornecedor TEXT NOT NULL DEFAULT '',
    unidade TEXT NOT NULL DEFAULT 'unidades',
    data_movimentacao TEXT NOT NULL,
    observacoes TEXT NOT NULL DEFAULT '',
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_movimentacao_produto_data
ON movimentacao_estoque (id_produto, data_movimentacao);
