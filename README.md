# API IBGE — Sistema de Consulta e Otimização de Dataset Municipal

Este projeto consiste em uma API REST de alta performance projetada e otimizada para gerenciar, filtrar e recuperar com eficiência um volume de dados massivo composto por 4.000.000 (quatro milhões) de registros municipais sintéticos. O ecossistema foi desenvolvido como um protótipo arquitetural com foco em estratégias avançadas de otimização de rede, eficiência de banco de dados, compressão dinâmica e validação condicional de cache HTTP.

---

## 1. Visão Geral e Arquitetura do Sistema

Para sustentar a carga de 4 milhões de registros sem degradação de performance e com consumo mínimo de recursos (processamento, memória e largura de banda), a arquitetura implementa as seguintes estratégias de engenharia:

### Estrutura de Banco de Dados e Indexação
O backend utiliza o PostgreSQL com mapeamento via SQLAlchemy. A busca em conjuntos de dados massivos sofre degradação severa caso as tabelas não sejam devidamente otimizadas. Para mitigar esse problema, o sistema implementa:
* **Indexação Estratégica**: Criação de índices específicos (`idx_municipios_estado` e `idx_municipios_regiao`) sobre as colunas mais utilizadas em filtros operacionais. Isso reduz a complexidade de busca de uma varredura linear (`Seq Scan`) para uma busca indexada em tempo logarítmico (`Index Scan`).
* **Gerenciamento de Conexões**: Configuração de um pool de conexões reutilizáveis (`pool_size=10`, `max_overflow=20`) para evitar o overhead de abertura e fechamento de conexões TCP com o banco a cada requisição HTTP.

### Paginação Baseada em Cursor (Cursor-based Pagination)
Diferente da paginação tradicional por deslocamento (`LIMIT / OFFSET`), onde o banco precisa ler e descartar todos os registros anteriores até alcançar o deslocamento desejado — gerando gargalos severos em tabelas grandes —, a paginação por cursor utiliza uma técnica de busca determinística (`WHERE id > :cursor ORDER BY id LIMIT :limit`). Essa abordagem garante tempo de resposta constante ($O(1)$ em relação ao deslocamento), independentemente de o cliente estar consultando a primeira ou a milionésima página.

### Otimizações na Camada de Rede (HTTP)
* **Validação Condicional via HTTP ETag**: O servidor calcula um hash MD5 sobre o payload de dados bruto gerado. Esse hash é enviado ao cliente através do cabeçalho `ETag`. Em requisições subsequentes, o cliente envia esse hash no cabeçalho `If-None-Match`. Se os dados no banco não mudaram, o servidor intercepta a requisição e retorna um status `304 Not Modified` com corpo vazio, economizando 100% da banda de rede dedicada aos dados.
* **Compressão Manual Gzip**: O servidor analisa o cabeçalho `Accept-Encoding` enviado pelo cliente. Caso haja suporte para compressão, o JSON de resposta é comprimido via algoritmo Gzip em nível de memória ativa (`gzip.compress`) antes do tráfego de rede, reduzindo drasticamente o volume de dados em trânsito.
* **Controle Dinâmico de Payload (Verbosidade)**: O endpoint suporta filtragem seletiva de atributos via parâmetro de busca (`?fields=`). O servidor realiza a filtragem dinâmica dos dicionários antes da serialização, diminuindo o tamanho final da string JSON gerada.

---

## 2. Organização do Repositório

O repositório está estruturado de forma limpa, separando a lógica de sementeira, a aplicação principal e a interface de validação.

### Estrutura de Arquivos
* `main.py`: Aplicação central desenvolvida em FastAPI contendo os endpoints da API REST, as regras de compressão, geração de ETags e gerenciamento do pool do banco de dados.
* `seed.py`: Script de configuração e inserção de dados em lote (*batch insert*), responsável pela criação estrutural da tabela, geração dos índices e inserção otimizada de 10.000 em 10.000 dos 4 milhões de registros.
* `index.html`: Dashboard SPA (Single Page Application) em JavaScript puro que serve tanto como cliente oficial de visualização quanto como plataforma interativa de testes e validação das otimizações.
* `.gitignore`: Arquivo de configuração que instrui o Git sobre quais caminhos e arquivos locais devem ser completamente ignorados pelo controle de versão.

### Detalhamento dos Arquivos do Sistema Ocultos
O projeto faz uso de estruturas locais que não devem ser enviadas ao repositório público:
* `venv/`: Diretório do Ambiente Virtual (Virtual Environment) do Python. Ele contém uma cópia isolada do interpretador Python e de todas as bibliotecas instaladas (FastAPI, SQLAlchemy, etc.) necessárias para que o projeto execute na máquina local sem gerar conflitos com o sistema operacional.
* `__pycache__/`: Diretório criado automaticamente pelo interpretador Python. Ele armazena arquivos compilados em bytecode (`.pyc`). Quando um arquivo `.py` é importado ou executado, o Python o converte em um formato binário intermediário otimizado para acelerar o tempo de inicialização nas execuções seguintes.
* **Tratamento no `.gitignore`**: Para garantir a portabilidade do código, o arquivo `.gitignore` barra o upload dessas pastas locais, contendo explicitamente as instruções:
  ```text
  venv/
  __pycache__/
  *.pyc

## 3. Guia de Reprodução do Ambiente
Siga detalhadamente os passos técnicos abaixo para compilar o banco de dados, configurar as dependências, rodar o servidor e inicializar o cliente.

Pré-requisitos do Sistema
Python versão 3.12 ou superior instalado.

Sistema Gerenciador de Banco de Dados PostgreSQL instalado e ativo localmente.

## Passo 1: Clonar e Acessar o Diretório do Projeto
Bash
git clone [https://github.com/joao-pedro-gg/api-ibge.git](https://github.com/joao-pedro-gg/api-ibge.git)
cd api-ibge
## Passo 2: Inicializar e Ativar o Ambiente Virtual (venv)
Execute o comando apropriado de acordo com o seu sistema operacional para isolar as dependências do projeto:

# No Windows:
python -m venv venv
venv\Scripts\activate

## Passo 3: Instalar as Dependências Estruturais
Atualize o gerenciador de pacotes e instale os módulos necessários para a execução:

python -m pip install --upgrade pip
python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary
## Passo 4: Configuração e Sementeira do Banco de Dados
Acesse o seu gerenciador do PostgreSQL (ex: pgAdmin ou psql) e crie um banco de dados vazio chamado ibge.

Certifique-se de que a string de conexão nos arquivos main.py e seed.py aponta para as suas credenciais locais corretas:

DATABASE_URL = "postgresql://postgres:SUA_SENHA_AQUI@localhost:5432/ibge"
Execute o script de população de dados massivos. O script criará a tabela, aplicará os índices operacionais e efetuará a inserção otimizada por blocos:

python seed.py
Nota: Devido ao volume massivo de 4 milhões de registros, este processo consome processamento e levará alguns minutos para concluir, exibindo o progresso a cada 10.000 inserções.

## Passo 5: Inicializar o Servidor ASGI (API)
Com o banco de dados populado, inicie o servidor HTTP localmente:

python main.py
O servidor estará ativo em http://localhost:8000. A documentação técnica detalhada e interativa da arquitetura REST estará acessível automaticamente nos endpoints:

Swagger UI (OpenAPI Docs): http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

## Passo 6: Executar o Cliente do Sistema
Para abrir a interface do usuário e o painel de testes, basta acessar o endpoint direto mapeado no servidor através de qualquer navegador web:

http://localhost:8000/app
## 4. Scripts e Painel de Validação de Performance
A validação das estratégias de resiliência sob pressão, eficiência de largura de banda e comportamento da fila de conexões é realizada de forma visual e empírica através do Painel de Demonstração integrado ao cliente (index.html). O painel simula cenários reais de rede baseados nos 4 milhões de registros do banco de dados, comprovando a integridade das otimizações.

## Validação 1: Resiliência de Cache Condicional (ETag / 304 Not Modified)
Objetivo do Teste: Comprovar que o servidor não gasta largura de banda desnecessária e nem retransmite dados repetidos se o dataset de municípios não foi modificado.

Metodologia: O painel efetua uma requisição inicial sem cache para capturar a assinatura hash gerada pela API para 100 registros. Em seguida, uma segunda requisição consecutiva é disparada injetando a assinatura hash no protocolo de rede.

Resultado Comprovado:

Requisição 1 (Dados Brutos): Retorna status 200 OK, demandando um tempo médio de 314ms para transferir aproximadamente ~14.8 KB de dados pela rede.

Requisição 2 (Verificação de ETag): Identifica que os hashes da assinatura são idênticos. O servidor intercepta o processamento e responde imediatamente com o status 304 Not Modified.

Eficiência Mensurada: O tempo de resposta despenca para apenas 6ms e o tráfego na rede é reduzido para 0 bytes (sem retransmissão de dados).

Validação 2: Eficiência de Carga e Compressão de Banda (Gzip)
Objetivo do Teste: Avaliar a eficiência de transmissão de dados na rede sob estresse de payloads volumosos em grandes consultas sequenciais.

Metodologia: Uma requisição pesada é feita solicitando um bloco contínuo de 500 registros municipais concorrentes de uma só vez pelo endpoint /municipios?limit=500.

Resultado Comprovado:

O servidor codifica dinamicamente a resposta devolvendo o cabeçalho Content-Encoding: gzip.

Tamanho Estimado Bruto (Sem Compressão): O payload JSON bruto ocuparia cerca de ~297.9 KB trafegando de forma pura pela rede.

Tamanho Real Recebido (Com Compressão Gzip): O payload otimizado trafega ocupando apenas ~74.5 KB.

Eficiência Mensurada: Uma economia de banda real de aproximadamente ~75%, aliviando os canais de rede e agilizando consideravelmente a taxa de vazão da API.

Validação 3: Redução de Verbosidade do Payload JSON
Objetivo do Teste: Avaliar o impacto na performance ao podar os campos e estruturas do JSON na transmissão de dados sob pressão.

Metodologia: O painel compara uma requisição padrão de 100 registros retornando o objeto com todas as suas propriedades contra uma requisição idêntica que restringe os campos aos atributos mínimos funcionais usando ?fields=nome,estado,populacao.

Resultado Comprovado:

Resposta Completa: Retorna o modelo de dados íntegro contendo todos os 8 campos estruturados da tabela, resultando em um payload de ~14.8 KB.

Resposta Reduzida: Filtra e retorna estritamente os 3 campos parametrizados pela URL, derrubando o tamanho do payload na rede para ~5.4 KB.

Eficiência Mensurada: Redução cirúrgica na estrutura do dado que gera uma economia de banda de ~63%, diminuindo o uso de memória no processo de serialização de strings no Python.