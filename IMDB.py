import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from googletrans import Translator
import asyncio

async def buscar_sinopse_imdb(nome_filme):
    try:
        url_busca = f"https://www.imdb.com/find/?q={nome_filme}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        response_busca = requests.get(url_busca, headers=headers)
        response_busca.raise_for_status()

        soup_busca = BeautifulSoup(response_busca.text, 'html.parser')

        primeiro_resultado = soup_busca.find('a', class_='ipc-metadata-list-summary-item__t')
        if not primeiro_resultado or not primeiro_resultado.has_attr('href'):
            return "Filme não encontrado na busca do IMDB."

        link_filme = "https://www.imdb.com" + primeiro_resultado['href']

        response_filme = requests.get(link_filme, headers=headers)
        response_filme.raise_for_status()

        soup_filme = BeautifulSoup(response_filme.text, 'html.parser')

        sinopse_tag = soup_filme.find('span', {'data-testid': 'plot-l'})
        if sinopse_tag:
            return sinopse_tag.get_text(strip=True)
        else:
            return "Sinopse não encontrada na página do filme."

    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro de rede: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

async def traduzir_texto(texto, dest_lang='pt'):

    if not texto or "não encontrado" in texto.lower() or "erro" in texto.lower():
        return texto
    try:
        translator = Translator()
        traducao = await translator.translate(texto, dest=dest_lang)
        return traducao.text
    except Exception as e:
        return f"Erro na tradução: {e}"

async def analisar_sentimento_pt(texto_em_portugues):

    texto_em_ingles = await traduzir_texto(texto_em_portugues, dest_lang='en')

    blob = TextBlob(texto_em_ingles)
    polaridade = blob.sentiment.polarity

    if polaridade > 0.2:
        sentimento = "Positivo 😊"
    elif polaridade < -0.2:
        sentimento = "Negativo 😠"
    else:
        sentimento = "Neutro 😐"

    return sentimento, polaridade

async def main():
    print("🎬 Bem-vindo ao Analisador de Críticas de Filmes v5.0 🎬")
    nome_do_filme = input("Qual filme/série você quer pesquisar no IMDB? ")

    sinopse_en = await buscar_sinopse_imdb(nome_do_filme)

    print("\nTraduzindo sinopse...")
    sinopse_pt = await traduzir_texto(sinopse_en, dest_lang='pt')

    print("\n--- SINOPSE ENCONTRADA (em Português) ---")
    print(sinopse_pt)
    print("-----------------------------------------")

    if "não encontrado" not in sinopse_pt.lower() and "erro" not in sinopse_pt.lower():
        critica_usuario = input("\nCom base na sinopse, escreva uma crítica curta em PORTUGUÊS:\n> ")

        sentimento, polaridade = await analisar_sentimento_pt(critica_usuario)

        print(f"\nAnálise da sua crítica: {sentimento} (Polaridade: {polaridade:.2f})")

    print("\nPrograma finalizado.")

if __name__ == "__main__":
    asyncio.run(main())