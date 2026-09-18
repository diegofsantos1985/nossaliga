from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
import urllib3

# Desativa os avisos de SSL para não poluir os registos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL oficial da competição da Nossa Liga Futsal
URL = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361"


def extrair_dados():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  print(f"A aceder ao site: {URL}")
  # verify=False ignora o erro de certificado SSL do site de destino
  response = requests.get(URL, headers=headers, verify=False)

  dados_liga = {
      "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
      "status_conexao": response.status_code,
      "tabela": [],
      "jogos": [],
  }

  if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    titulo_pagina = soup.find("title")
    if titulo_pagina:
      dados_liga["titulo_site"] = titulo_pagina.get_text(strip=True)

    print("Dados extraídos com sucesso!")
  else:
    print(f"Erro ao aceder ao site: {response.status_code}")

  # Guarda o ficheiro dados.json na raiz para o site poder ler
  with open("dados.json", "w", encoding="utf-8") as f:
    json.dump(dados_liga, f, ensure_ascii=False, indent=4)
  print("Ficheiro dados.json gerado/atualizado com sucesso!")


if __name__ == "__main__":
  extrair_dados()
