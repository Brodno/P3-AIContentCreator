"""
Context Loader - wczytuje pliki .md (ghost, persona, oferta, contentmachine)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Główny folder projektu (4 poziomy wyżej od code/modules/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

def load_file(relative_path):
    """
    Wczytaj plik .md z projektu.

    Args:
        relative_path (str): Ścieżka relatywna (np. "_ZESPOL/ghost.md")

    Returns:
        str: Zawartość pliku
    """
    full_path = os.path.join(BASE_DIR, relative_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"❌ Nie znaleziono: {full_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"✅ Wczytano: {relative_path} ({len(content)} znaków)")
    return content

def load_context():
    """
    Wczytaj wszystkie pliki kontekstowe.

    Returns:
        dict: {
            'ghost': str,
            'persona': str,
            'oferta': str,
            'contentmachine': str,
            'profil_summary': str  # Skrócony profil dla promptów
        }
    """
    print("\n📂 Ładowanie kontekstu...")

    # Wczytaj z .env lub użyj domyślnych
    ghost_path = os.getenv("GHOST_PATH", "_ZESPOL/ghost.md")
    persona_path = os.getenv("PERSONA_PATH", "_KONTEKST/persona.md")
    oferta_path = os.getenv("OFERTA_PATH", "_KONTEKST/oferta.md")
    contentmachine_path = os.getenv("CONTENTMACHINE_PATH", "_ZESPOL/contentmachine.md")

    context = {
        'ghost': load_file(ghost_path),
        'persona': load_file(persona_path),
        'oferta': load_file(oferta_path),
        'contentmachine': load_file(contentmachine_path)
    }

    # Wyciągnij kluczowe info z profilu (dla promptów)
    context['profil_summary'] = extract_profil_summary(context)

    print(f"\n✅ Kontekst załadowany ({sum(len(v) for v in context.values())} znaków total)\n")

    return context

def extract_profil_summary(context):
    """
    Wyciągnij kluczowe info o przedsiębiorcy (do promptów).

    Returns:
        str: Skrócone info o Łukaszu
    """
    # Można zrobić bardziej zaawansowane parsowanie, ale na razie prosty string
    return """
Łukasz Rymkowski - AgencjaOP
- 6 lat doświadczenia w budowaniu maszyn przemysłowych (WiR Automation)
- Inżynier + operator produkcji + AI enthusiast
- Specjalizacja: Audyt maszyn przed zakupem (500k-2M PLN)
- Branża: Produkcja przemysłowa B2B (właściciele firm MŚP, 35-60 lat)
- Ton: Inżynierski konkret z pazurem, praktyk, bez korpo-mowy
- E-E-A-T: Real stories z hali, konkretne kwoty, normy ISO
"""

if __name__ == "__main__":
    # Test
    try:
        ctx = load_context()
        print("\n📊 Podsumowanie:")
        for key, value in ctx.items():
            if key != 'profil_summary':
                print(f"   {key}: {len(value)} znaków")
        print(f"\n   profil_summary:\n{ctx['profil_summary']}")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
