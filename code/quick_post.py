"""
quick_post.py - Szybkie generowanie posta LinkedIn przez CLI
Uruchom: python quick_post.py "temat posta"
Lub:     python quick_post.py  (użyje tematu z dołu pliku)

Nie wymaga Streamlit - działa w terminalu.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from modules.context_loader import load_context
from modules.generator import generate_post
from modules.evaluator import evaluate_post
from modules.improver import improve_post
from modules.history_checker import get_recent_topics

# ============================================================
# KONFIGURACJA
# ============================================================
TARGET_SCORE = 90      # Próg akceptacji
MAX_ITERATIONS = 5     # Max prób ulepszenia

OUTPUT_DIR = Path(__file__).parent / "data" / "generated_posts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_cli(topic: str, verbose: bool = True):
    """
    Generuje i ulepsza post do osiągnięcia TARGET_SCORE.
    Zwraca finalny post i score.
    """
    print(f"\n{'='*60}")
    print(f"[POST] TEMAT: {topic}")
    print(f"{'='*60}\n")

    # Załaduj kontekst
    print("[...] Ladowanie kontekstu (ghost, persona, oferta)...")
    context = load_context()
    recent_topics = get_recent_topics(10)

    best_post = ""
    best_score = 0

    for i in range(1, MAX_ITERATIONS + 1):
        print(f"\n{'─'*50}")
        print(f"[{i}/{MAX_ITERATIONS}] Iteracja")

        if i == 1:
            print("[GEN] Generowanie draftu...")
            current_post = generate_post(topic, "LinkedIn", "post", context, recent_topics)
        else:
            print("[FIX] Ulepszanie posta...")
            current_post = improve_post(current_post, last_eval, context)

        # Ocena
        print("[EVA] Ocenianie jakosci...")
        evaluation = evaluate_post(current_post, "LinkedIn", context)

        score = evaluation.get('total_score', 0)
        bd = evaluation.get('breakdown', {})

        print(f"\n[SCORE] {score}/100")
        print(f"  Hook: {bd.get('hook',0)}/30 | E-E-A-T: {bd.get('eeat',0)}/25 | "
              f"Visual: {bd.get('visual',0)}/20 | Pain: {bd.get('pain',0)}/15 | CTA: {bd.get('cta',0)}/10")

        if verbose:
            feedback = evaluation.get('feedback', '')
            if feedback:
                # print only ASCII-safe part
                safe_feedback = feedback[:200].encode('ascii', errors='replace').decode('ascii')
                print(f"\n[FEEDBACK]: {safe_feedback}...")

        if score > best_score:
            best_score = score
            best_post = current_post

        last_eval = evaluation

        if score >= TARGET_SCORE:
            print(f"\n[OK] Osiagnieto cel ({score} >= {TARGET_SCORE})!")
            break

    # Podsumowanie
    print(f"\n{'='*60}")
    print(f"[DONE] GOTOWY POST (best score: {best_score}/100)")
    print(f"{'='*60}")
    print()
    # Wyswietl post bezpiecznie (Windows terminal moze nie obsluzyc polskich znakow)
    try:
        print(best_post)
    except UnicodeEncodeError:
        print(best_post.encode('ascii', errors='replace').decode('ascii'))
    print()
    print(f"{'='*60}")

    # Zapisz do pliku (zawsze UTF-8)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    safe_topic = topic[:50].replace(' ', '_').replace('/', '-')
    filepath = OUTPUT_DIR / f"{timestamp}_{safe_topic}.md"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Post LinkedIn\n")
        f.write(f"**Temat:** {topic}\n")
        f.write(f"**Wygenerowano:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Score:** {best_score}/100\n\n")
        f.write("---\n\n")
        f.write(best_post)

    print(f"[SAVE] Zapisano: {filepath}")

    return best_post, best_score


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        # DOMYŚLNY TEMAT - zmień tutaj
        topic = (
            "Kamera + AI na hali = koniec z mikrozestojami. "
            "Nowy pomysł na produkt: Edge AI Video Analytics dla MŚP "
            "bez drogich systemów MES"
        )

    generate_cli(topic)
