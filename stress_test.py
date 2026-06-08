import concurrent.futures
import urllib.request
import time

# Endpoint da sua API que puxa dados do banco
URL = "http://localhost:8000/municipios?limit=100"

def disparar_requisicao(id_requisicao):
    try:
        # Tenta abrir a URL simulando um cliente acessando a API
        with urllib.request.urlopen(URL) as response:
            return response.getcode()
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    print("==================================================")
    print("   Simulador de Teste de Carga e Pressão (API)    ")
    print("==================================================")
    print("Disparando 200 requisições concorrentes (20 threads)...")
    
    tempo_inicio = time.time()
    
    # Simula 20 usuários disparando requisições ao mesmo tempo
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Mapeia as 200 requisições nas threads em paralelo
        resultados = list(executor.map(disparar_requisicao, range(200)))
        
    tempo_fim = time.time()
    
    # Contabiliza quantas deram Status 200 OK (Sucesso)
    sucessos = resultados.count(200)
    erros = len(resultados) - sucessos
    
    print("\n================== RESULTADOS ==================")
    print(f"Tempo total de estresse: {tempo_fim - tempo_inicio:.2f} segundos")
    print(f"Requisições com Sucesso (200 OK): {sucessos}/200")
    print(f"Requisições com Falha/Erro: {erros}")
    print("==================================================")
    
    if erros == 0:
        print("Sucesso Absoluto! A API aguentou a pressão sem derrubar o pool.")
    else:
        print("Atenção: Algumas requisições falharam sob pressão.")