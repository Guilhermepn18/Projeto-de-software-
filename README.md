# EstoqueFácil

Protótipo web responsivo para controle de estoque de uma adega, pensado para uso principalmente pelo celular. Desenvolvido com HTML, CSS e JavaScript puro.

## Funcionalidades
- Painel inicial com resumo de produtos, estoque baixo e produtos zerados.
- Registro de entrada de mercadorias com quantidade, custo unitário, fornecedor, data e observações.
- Cálculo automático do total da entrada e validação de campos obrigatórios.
- Atualização do saldo do produto após confirmar a entrada.
- Consulta de estoque com busca e filtros: Todos, Zerados, Baixo e OK.
- Alertas de reposição com base na quantidade mínima configurada para cada produto.
- Salvamento local no navegador usando `localStorage`.
- Layout responsivo, navegação inferior e estados acessíveis com rótulos textuais.

## Como executar
1. Baixe ou clone o repositório.
2. Abra `index.html` no navegador. Não é necessário instalar dependências.
3. Opcional: use a extensão Live Server no Visual Studio Code para executar um servidor local.

## Arquivos
- `index.html`: estrutura das telas.
- `style.css`: estilos e adaptação para telas menores.
- `app.js`: navegação, validação, filtros e atualização do estoque.

## Dados de demonstração
O protótipo inicia com produtos e quantidades de exemplo para permitir testar os alertas e filtros. Os dados ficam no navegador utilizado; use o botão de restauração no cabeçalho para voltar ao estado inicial.

## Limitações
Este é um protótipo acadêmico, não um sistema pronto para operação comercial. Os dados não são sincronizados entre dispositivos e não há autenticação, backend, banco de dados remoto, backups, integração fiscal ou pagamentos. Para uso real, é necessário implementar backend, banco persistente, controle de acesso, backups e testes adicionais.

## Próximas evoluções
- Cadastro e edição de produtos.
- Registro de saídas com bloqueio de saldo negativo.
- Histórico de movimentações.
- Backend com Python/Flask e banco de dados SQLite ou PostgreSQL.
- Testes automatizados das regras de estoque.

## Melhorias futuras

- Implementar testes automatizados para as regras de estoque.
- Aprimorar os relatórios de movimentação.
- Adicionar autenticação de usuários.
