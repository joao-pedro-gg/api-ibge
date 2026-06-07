from sqlalchemy import create_engine, text
import random

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/ibge"
engine = create_engine(DATABASE_URL)

# Mapeamento estado → região
ESTADO_REGIAO = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
}

POPULACAO = {
    'SP': (5000, 12_000_000), 'RJ': (5000, 6_700_000), 'MG': (2000, 2_700_000),
    'BA': (2000, 2_900_000), 'PR': (2000, 1_900_000), 'RS': (2000, 1_500_000),
    'PE': (2000, 1_600_000), 'CE': (2000, 1_300_000), 'PA': (2000, 1_500_000),
    'SC': (2000, 700_000),   'MA': (2000, 1_100_000), 'GO': (2000, 1_400_000),
    'AM': (1000, 2_100_000), 'ES': (2000, 400_000),   'PB': (2000, 500_000),
    'RN': (2000, 900_000),   'MT': (1000, 600_000),   'AL': (2000, 1_000_000),
    'PI': (2000, 900_000),   'MS': (1000, 900_000),   'DF': (50000, 3_000_000),
    'SE': (2000, 650_000),   'RO': (1000, 500_000),   'TO': (1000, 300_000),
    'AC': (1000, 400_000),   'AP': (1000, 500_000),   'RR': (1000, 400_000),
}

AREA = {
    'Norte':        (100.0, 70000.0),
    'Nordeste':     (50.0,  30000.0),
    'Centro-Oeste': (100.0, 50000.0),
    'Sudeste':      (30.0,  15000.0),
    'Sul':          (20.0,  10000.0),
}

PIB = {
    'Norte':        (8000.0,  35000.0),
    'Nordeste':     (6000.0,  28000.0),
    'Centro-Oeste': (15000.0, 65000.0),
    'Sudeste':      (18000.0, 80000.0),
    'Sul':          (16000.0, 70000.0),
}

# 200 nomes reais de municípios brasileiros para sortear
NOMES_MUNICIPIOS = [
    "Água Branca", "Águas Belas", "Águas de Lindóia", "Além Paraíba", "Alegre",
    "Alegrete", "Alenquer", "Alfenas", "Almeirim", "Altamira",
    "Alto Araguaia", "Alto Taquari", "Alvorada", "Amargosa", "Americana",
    "Amparo", "Anápolis", "Andradina", "Angra dos Reis", "Apucarana",
    "Aquidauana", "Araçatuba", "Aracaju", "Araçuaí", "Araguaína",
    "Araguari", "Araguatins", "Arapongas", "Araraquara", "Araras",
    "Araxá", "Arcoverde", "Ariquemes", "Arujá", "Assis",
    "Assis Brasil", "Astorga", "Ataléia", "Atibaia", "Avaré",
    "Bagé", "Balsas", "Bandeirantes", "Barreiras", "Barretos",
    "Barueri", "Batatais", "Bauru", "Belém", "Belo Horizonte",
    "Bento Gonçalves", "Betim", "Birigui", "Blumenau", "Boa Vista",
    "Botucatu", "Bragança", "Bragança Paulista", "Brasília", "Brumado",
    "Caçapava", "Caçador", "Cacoal", "Cachoeira do Sul", "Cachoeiro de Itapemirim",
    "Camaçari", "Camaragibe", "Cambé", "Campina Grande", "Campinas",
    "Campo Grande", "Campo Largo", "Campo Mourão", "Campos do Jordão", "Campos dos Goytacazes",
    "Canaã dos Carajás", "Cândido Mota", "Canoas", "Caratinga", "Cariacica",
    "Caruaru", "Cascavel", "Cataguases", "Caxias do Sul", "Chapecó",
    "Colatina", "Congonhas", "Conselheiro Lafaiete", "Contagem", "Coronel Fabriciano",
    "Corumbá", "Cotia", "Criciúma", "Crixás", "Cruz Alta",
    "Cruzeiro", "Cruzeiro do Sul", "Cubatão", "Cuiabá", "Curitiba",
    "Divinópolis", "Dourados", "Dracena", "Duque de Caxias", "Erechim",
    "Escada", "Estância", "Euclides da Cunha", "Fair de Santana", "Farroupilha",
    "Foz do Iguaçu", "Franca", "Francisco Morato", "Franco da Rocha", "Garanhuns",
    "Goiânia", "Governador Valadares", "Gravataí", "Guarapuava", "Guaratinguetá",
    "Guarujá", "Guarulhos", "Gurupi", "Horizonte", "Igarassu",
    "Ilhéus", "Imperatriz", "Indaiatuba", "Ipatinga", "Ipiranga",
    "Itabira", "Itabirito", "Itabuna", "Itajaí", "Itajubá",
    "Itapecerica da Serra", "Itapetinga", "Itapetininga", "Itapeva", "Itapipoca",
    "Itaquaquecetuba", "Itatiba", "Ituiutaba", "Iturama", "Ituverava",
    "Jaboatão dos Guararapes", "Jacareí", "Jaguariaíva", "Jales", "Jequié",
    "Ji-Paraná", "João Monlevade", "João Pessoa", "Joinville", "Juazeiro",
    "Juazeiro do Norte", "Juiz de Fora", "Jundiaí", "Lages", "Lajeado",
    "Lavras", "Leme", "Limeira", "Linhares", "Londrina",
    "Luziânia", "Macaé", "Macapá", "Maceió", "Manaus",
    "Maraba", "Maracanaú", "Marília", "Maringá", "Mauá",
    "Mineiros", "Miracema do Tocantins", "Mococa", "Mogi das Cruzes", "Mogi Guaçu",
    "Montes Claros", "Mossoró", "Muriaé", "Natal", "Niterói",
    "Nova Friburgo", "Nova Iguaçu", "Nova Lima", "Nova Odessa", "Novo Hamburgo",
    "Olinda", "Osasco", "Palmas", "Pará de Minas", "Parnaíba",
    "Parnamirim", "Passo Fundo", "Passos", "Patos", "Patos de Minas",
    "Paulo Afonso", "Pelotas", "Petrolina", "Petrópolis", "Pindamonhangaba",
    "Piracicaba", "Pirassununga", "Poços de Caldas", "Ponta Grossa", "Porto Alegre",
    "Porto Seguro", "Porto Velho", "Pouso Alegre", "Presidente Prudente", "Recife",
    "Ribeirão das Neves", "Ribeirão Preto", "Rio Branco", "Rio Claro", "Rio de Janeiro",
    "Rio Grande", "Rio Verde", "Rondonópolis", "Salvador", "Santa Cruz do Sul",
    "Santa Luzia", "Santa Maria", "Santarém", "Santo André", "Santos",
    "São Bernardo do Campo", "São Caetano do Sul", "São Carlos", "São João del-Rei", "São José",
    "São José do Rio Preto", "São José dos Campos", "São Luís", "São Paulo", "São Vicente",
    "Sapucaia do Sul", "Sete Lagoas", "Sinop", "Sobral", "Sorocaba",
    "Sumaré", "Suzano", "Taubaté", "Teófilo Otoni", "Teresina",
    "Teresópolis", "Timóteo", "Uberaba", "Uberlândia", "Umuarama",
    "Uruguaiana", "Varginha", "Várzea Grande", "Viamão", "Vila Velha",
    "Vitória", "Vitória da Conquista", "Volta Redonda"
]

ESTADOS = list(ESTADO_REGIAO.keys())

def criar_tabela():
    with engine.connect() as conn:
        conn.execute(text("""
            DROP TABLE IF EXISTS municipios;
            CREATE TABLE municipios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100),
                estado CHAR(2),
                populacao INTEGER,
                area_km2 FLOAT,
                pib_per_capita FLOAT,
                regiao VARCHAR(20),
                codigo_ibge VARCHAR(10)
            );
            CREATE INDEX idx_municipios_estado ON municipios(estado);
            CREATE INDEX idx_municipios_regiao ON municipios(regiao);
        """))
        conn.commit()
    print("Tabela criada!")

def popular_banco():
    print("Inserindo 4 milhões de registros... isso pode demorar alguns minutos.")

    with engine.connect() as conn:
        batch = []
        for i in range(1, 4_000_001):
            estado = random.choice(ESTADOS)
            regiao = ESTADO_REGIAO[estado]
            pop_min, pop_max = POPULACAO[estado]
            area_min, area_max = AREA[regiao]
            pib_min, pib_max = PIB[regiao]

            batch.append({
                "nome": random.choice(NOMES_MUNICIPIOS),
                "estado": estado,
                "populacao": random.randint(pop_min, pop_max),
                "area_km2": round(random.uniform(area_min, area_max), 2),
                "pib_per_capita": round(random.uniform(pib_min, pib_max), 2),
                "regiao": regiao,
                "codigo_ibge": str(random.randint(1000000, 9999999))
            })

            if i % 10000 == 0:
                conn.execute(text("""
                    INSERT INTO municipios (nome, estado, populacao, area_km2, pib_per_capita, regiao, codigo_ibge)
                    VALUES (:nome, :estado, :populacao, :area_km2, :pib_per_capita, :regiao, :codigo_ibge)
                """), batch)
                conn.commit()
                batch = []
                print(f"{i:,} registros inseridos...")

    print("Pronto! 4 milhões de registros inseridos.")

if __name__ == "__main__":
    criar_tabela()
    popular_banco()