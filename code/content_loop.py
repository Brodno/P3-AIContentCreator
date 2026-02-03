"""
MAIN SCRIPT: Content Quality Loop
Orkiestrator procesu tworzenia treści.
Użycie: python content_loop.py "Temat posta" [Platforma] [--auto]
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import modułów
from modules.context_loader import load_context, BASE_DIR
from modules.generator import generate_post
from modules.evaluator import evaluate_post
from modules.improver import improve_post
from modules.history_checker import parse_index, check_uniqueness, append_to_index, get_recent_topics
from modules.fact_checker import fact_check_post
from modules.google_search import google_search

# Załaduj .env
load_dotenv()

# Konfiguracja
TARGET_SCORE = int(os.getenv("QUALITY_THRESHOLD", 95))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 10))
HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")
ENABLE_FACT_CHECK = os.getenv("ENABLE_FACT_CHECK", "true").lower() == "true"

def web_search(query):
    """
    Wrapper dla wyszukiwania w internecie
    Używa Google Custom Search API jeśli skonfigurowane,
    w przeciwnym razie fallback do mock data
    """
    print(f"      🌐 Szukam: {query}")

    # Sprawdź czy Google API jest skonfigurowane
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    if (google_api_key and google_api_key != "YOUR_API_KEY_HERE" and
        google_cse_id and google_cse_id != "YOUR_SEARCH_ENGINE_ID_HERE"):
        # Użyj prawdziwego Google Search
        try:
            result = google_search(query, num_results=3)
            return result
        except Exception as e:
            print(f"      ⚠️ Google Search error: {e}, używam mock data")
            # Fallback do mock

    # FALLBACK - mock data dla testów
    mock_results = {
        "olej hydrauliczny": "Typowa cena oleju hydraulicznego HLP 46: 30-50 PLN/L w hurtowniach przemysłowych. Oleje OEM z logo producenta: 150-250 PLN/L.",
        "przestój": "Koszt przestoju linii produkcyjnej: 5-15k PLN/h dla linii wartości 500k-1M, 10-25k PLN/h dla linii 1-2M PLN.",
        "marża OEM": "Typowa marża OEM na części zamienne: 200-500% (2-5x). Oleje i smary: 300-600% marża."
    }

    # Prosta heurystyka dopasowania
    for key, value in mock_results.items():
        if key in query.lower():
            return value

    return "Brak konkretnych danych - wymaga ręcznej weryfikacji"

def save_iteration_history(topic, history_data):
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic])[:30]
    filename = os.path.join(HISTORY_DIR, f"{timestamp}_{safe_topic}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    return filename

def format_final_file(topic, content):
    """Formatuje plik .md zgodnie ze wzorcem."""
    prompt_section = ""
    clean_content = content
    
    if "PROMPT GRAFICZNY" in content:
        parts = content.split("PROMPT GRAFICZNY")
        clean_content = parts[0].strip()
        if clean_content.endswith("---"):
            clean_content = clean_content[:-3].strip()
            
        raw_prompt = parts[1].strip()
        if raw_prompt.startswith(":") or raw_prompt.startswith("(Nano Banana Pro):"):
             raw_prompt = raw_prompt.split(":", 1)[1].strip()
             
        prompt_section = f"""
---
## 📸 PROMPT DO GENERATORA (Styl: Industrial Candid / iPhone Style)
**Opis:** Surowe zdjęcie z hali, "brudny" realizm.
**Prompt:**
> {raw_prompt}
"""

    pub_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    header = f"""# Temat: {topic}
# Data publikacji: {pub_date}
# Cel: Edukacja / Budowanie Autorytetu
# Format: Post LinkedIn

"""
    return header + clean_content + prompt_section

def get_unique_filepath(directory, filename):
    """
    Zwraca unikalną ścieżkę pliku. Jeśli plik istnieje, dodaje _v2, _v3 itd.
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    full_path = os.path.join(directory, new_filename)
    
    while os.path.exists(full_path):
        counter += 1
        new_filename = f"{base_name}_v{counter}{ext}"
        full_path = os.path.join(directory, new_filename)
        
    return full_path

def main():
    parser = argparse.ArgumentParser(description="AI Content Factory - Quality Loop")
    parser.add_argument("topic", help="Temat posta")
    parser.add_argument("--platform", default="LinkedIn", help="Platforma docelowa")
    parser.add_argument("--auto", action="store_true", help="Tryb automatyczny (bez pytań)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding='utf-8')

    print(f"\n🚀 START: Content Quality Loop (Wersjonowanie Plików)")
    print(f"🎯 Temat: {args.topic}")
    print(f"🎯 Cel: {TARGET_SCORE}/100 pkt\n")

    history_index = parse_index()
    recent_topics = get_recent_topics(10)
    
    uniqueness_check = check_uniqueness(args.topic, history_index)
    if not uniqueness_check['is_unique']:
        print(f"❌ DUPLIKAT! {uniqueness_check['recommendation']}")
        if not args.auto:
            choice = input("\nCzy mimo to kontynuować? (t/n): ")
            if choice.lower() != 't': sys.exit("Przerwano.")
    else:
        print("✅ Temat unikalny.")

    context = load_context()

    current_post = ""
    best_post = ""
    best_score = 0
    iteration_history = []

    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔄 ITERACJA {i}/{MAX_ITERATIONS}")
        
        if i == 1:
            print("✍️ Generowanie draftu...")
            current_post = generate_post(args.topic, args.platform, "post", context, recent_topics)
        else:
            print(f"🔧 Poprawianie (feedback redaktora)...")
            last_eval = iteration_history[-1]['evaluation']
            last_fact_check = iteration_history[-1].get('fact_check_results')
            current_post = improve_post(current_post, last_eval, context, last_fact_check)

        # FACT-CHECKING STEP
        fact_check_results = None
        if ENABLE_FACT_CHECK:
            fact_check_results = fact_check_post(current_post, web_search_fn=web_search)
            print(f"   {fact_check_results['summary']}")
            if fact_check_results['suspicious_claims']:
                print(f"   ⚠️ Podejrzane twierdzenia:")
                for claim in fact_check_results['suspicious_claims']:
                    print(f"      • {claim['original_claim']['claim']}")
                    print(f"        → {claim['verdict']}: {claim['explanation']}")

        print("⚖️ Ocena jakości...")
        evaluation = evaluate_post(current_post, args.platform, context, fact_check_results)
        score = evaluation.get('total_score', 0)
        
        print(f"📊 WYNIK: {score}/100")
        bd = evaluation.get('breakdown', {})
        print(f"   Hook: {bd.get('hook')}/30 | E-E-A-T: {bd.get('eeat')}/40 | Logika: {bd.get('logic')}/20")
        print(f"   Feedback: {evaluation.get('feedback', '')}")

        iter_data = {
            "iteration": i,
            "score": score,
            "post_content": current_post,
            "evaluation": evaluation,
            "fact_check_results": fact_check_results
        }
        iteration_history.append(iter_data)

        if score > best_score:
            best_score = score
            best_post = current_post

        if score >= TARGET_SCORE:
            print(f"\n🎉 ZATWIERDZONO! Jakość {score}/100.")
            break
        
        if i == MAX_ITERATIONS:
            print(f"\n⚠️ Osiągnięto limit iteracji. Best attempt: {best_score}/100")

    save_iteration_history(args.topic, iteration_history)

    formatted_content = format_final_file(args.topic, best_post)

    print(f"\n{'='*60}")
    print(f"🏆 FINALNY PLIK:")
    print(f"{ '='*60}")
    print(formatted_content)
    print(f"{'='*60}")

    should_save = args.auto
    if not args.auto:
        choice = input("\nCzy zapisać wynik do pliku? (t/n): ")
        should_save = (choice.lower() == 't')

    if should_save:
        safe_filename = "".join([c if c.isalnum() else "_" for c in args.topic])[:50] + ".md"
        target_dir = os.path.join(BASE_DIR, "MARKETING", "02_PLAN_2026", "posty_luty_2026")
        
        os.makedirs(target_dir, exist_ok=True)
        
        # UŻYCIE WERSJONOWANIA
        final_path = get_unique_filepath(target_dir, safe_filename)
        
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"✅ Zapisano plik: {final_path}")
        
        if not args.auto:
            choice = input("\nCzy dodać do INDEX_POSTOW.md? (t/n): ")
            if choice.lower() == 't':
                append_data = {'date': datetime.now().strftime('%Y-%m-%d'), 'topic': args.topic, 'has_file': True, 'has_graphic': "PROMPT" in formatted_content}
                append_to_index(append_data)
                print("✅ Zaktualizowano indeks.")
        else:
            print("⚠️ Pamiętaj o dodaniu wpisu do INDEX_POSTOW.md po publikacji!")

if __name__ == "__main__":
    main()