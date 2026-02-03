"""
Google Custom Search API Integration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Próba importu Google API
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("⚠️ google-api-python-client nie zainstalowany. Użyj: pip install google-api-python-client")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


def google_search(query, num_results=5):
    """
    Wyszukuje w Google Custom Search API

    Args:
        query (str): Zapytanie do wyszukania
        num_results (int): Ile wyników zwrócić (max 10)

    Returns:
        str: Sformatowane wyniki wyszukiwania
    """
    if not GOOGLE_API_AVAILABLE:
        return "❌ Google API client nie zainstalowany. Użyj: pip install google-api-python-client"

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        return "❌ Brak GOOGLE_API_KEY w .env. Skonfiguruj Google Custom Search API."

    if not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_SEARCH_ENGINE_ID_HERE":
        return "❌ Brak GOOGLE_CSE_ID w .env. Utwórz Custom Search Engine."

    try:
        # Zbuduj service
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

        # Wykonaj wyszukiwanie
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10),  # Max 10 wyników per request
            lr="lang_pl",  # Preferuj polskie wyniki
        ).execute()

        # Sprawdź czy są wyniki
        if 'items' not in result:
            return f"Brak wyników dla zapytania: {query}"

        # Formatuj wyniki
        formatted_results = []
        for item in result['items']:
            title = item.get('title', 'Brak tytułu')
            snippet = item.get('snippet', 'Brak opisu')
            link = item.get('link', '')

            formatted_results.append(f"""
Tytuł: {title}
Opis: {snippet}
Źródło: {link}
""")

        # Złącz wszystkie wyniki
        output = "\n".join(formatted_results)

        # Dodaj metadane
        total_results = result.get('searchInformation', {}).get('totalResults', 'N/A')
        search_time = result.get('searchInformation', {}).get('searchTime', 'N/A')

        header = f"Zapytanie: {query}\nZnaleziono: {total_results} wyników (czas: {search_time}s)\n\n"

        return header + output

    except Exception as e:
        return f"❌ Błąd Google Search API: {str(e)}"


def google_search_raw(query, num_results=5):
    """
    Wyszukuje i zwraca surowe wyniki (lista dict)

    Args:
        query (str): Zapytanie
        num_results (int): Ile wyników

    Returns:
        list: Lista wyników [{'title': ..., 'snippet': ..., 'link': ...}]
    """
    if not GOOGLE_API_AVAILABLE:
        return []

    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        return []

    if not GOOGLE_CSE_ID or GOOGLE_CSE_ID == "YOUR_SEARCH_ENGINE_ID_HERE":
        return []

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10),
            lr="lang_pl",
        ).execute()

        if 'items' not in result:
            return []

        # Zwróć uproszczone wyniki
        return [
            {
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'link': item.get('link', '')
            }
            for item in result['items']
        ]

    except Exception as e:
        print(f"❌ Google Search Error: {e}")
        return []


# Test
if __name__ == "__main__":
    import sys
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("🧪 Test Google Custom Search API\n")

    test_query = "cena oleju hydraulicznego HLP 46 Polska"
    print(f"Zapytanie: {test_query}\n")

    result = google_search(test_query, num_results=3)
    print(result)

    print("\n" + "="*60)
    print("\n📊 Sprawdzam konfigurację:")
    print(f"   API Key: {'✅ OK' if GOOGLE_API_KEY and GOOGLE_API_KEY != 'YOUR_API_KEY_HERE' else '❌ Brak'}")
    print(f"   CSE ID: {'✅ OK' if GOOGLE_CSE_ID and GOOGLE_CSE_ID != 'YOUR_SEARCH_ENGINE_ID_HERE' else '❌ Brak'}")
    print(f"   Google API Library: {'✅ Zainstalowana' if GOOGLE_API_AVAILABLE else '❌ Brak'}")
