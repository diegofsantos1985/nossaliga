from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import urllib3

# Desativa os avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361"

def extrair_dados():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"A aceder ao site: {URL}")
    response = requests.get(URL, headers=headers, verify=False)

    dados_liga = {
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status_conexao": response.status_code,
        "tabela": [],
        "jogos": []
    }

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Procura por todas as tabelas presentes na página
        tabelas = soup.find_all("table")
        
        if len(tabelas) > 0:
            # Extrai as linhas da primeira tabela encontrada (geralmente a classificação)
            linhas = tabelas[0].find_all("tr")
            for linha in linhas:
                colunas = [td.get_text(strip=True) for td in linha.find_all(["td", "th"])]
                if colunas:
                    dados_liga["tabela"].append(colunas)
            print(f"Encontradas {len(dados_liga['tabela'])} linhas na tabela.")
        else:
            print("Nenhuma tabela encontrada no HTML.")

        print("Extração concluída!")
    else:
        print(f"Erro ao aceder ao site: {response.status_code}")

    # Guarda os dados atualizados no dados.json
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump(dados_liga, f, ensure_ascii=False, indent=4)
    print("Ficheiro dados.json atualizado com sucesso!")

if __name__ == "__main__":
    extrair_dados()
