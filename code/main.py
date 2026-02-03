import sys
import os

# Ensure the script can find modules even if run from weird paths, 
# as long as it's run as 'python main.py' from 'code/' directory.
sys.path.append(os.getcwd())

try:
    from modules.generator import generate_post
    from config.gemini_config import test_connection
except ImportError as e:
    print("❌ Błąd importu! Upewnij się, że uruchamiasz ten plik z katalogu 'code/'.")
    print(f"Szczegóły: {e}")
    sys.exit(1)

def main():
    print("--- AI OS Personal: LinkedIn Post Generator (Gemini 2.0/3.0) ---")
    
    # 1. Sprawdź połączenie
    print("\n1. Sprawdzanie połączenia z API...")
    if not test_connection():
        print("❌ Nie można połączyć się z Gemini API. Sprawdź .env i klucz API.")
        return

    # 2. Pobierz dane od użytkownika (symulacja lub input)
    print("\n2. Konfiguracja posta")
    # Check if we are running non-interactively
    if not sys.stdin.isatty():
        try:
             # Read from stdin if available (piped)
             input_data = sys.stdin.readline().strip()
             topic = input_data if input_data else ""
             print(f"Otrzymano temat z wejścia: '{topic}'")
        except:
             topic = ""
    else:
        topic = input("Podaj temat posta: ").strip()

    if not topic:
        topic = "Jak AI zmienia pracę inżyniera?"
        print(f"Wybrano temat domyślny: {topic}")

    # Dummy context - docelowo tu będzie context_loader
    context = {
        'profil_summary': "Łukasz Rymkowski. Ekspert od umów wdrożeniowych IT. Styl: Inżynierski konkret."
    }
    
    # 3. Generuj
    print("\n3. Generowanie treści (Może potrwać kilka sekund)...")
    try:
        post = generate_post(topic, context=context)
        print("\n" + "="*50)
        print("WYGENEROWANY POST:")
        print("="*50 + "\n")
        print(post)
        print("\n" + "="*50)
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas generowania: {e}")

if __name__ == "__main__":
    main()
