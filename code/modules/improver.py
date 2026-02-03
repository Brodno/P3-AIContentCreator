"""
Improver - poprawia post na podstawie feedbacku
"""
from config.gemini_config import generate_content_with_retry
from google.genai import types
from modules.prompt_loader import load_prompt, format_prompt

def improve_post(previous_draft, evaluation, context=None, fact_check_results=None):
    """
    Poprawia post na podstawie feedbacku z evaluatora

    Args:
        previous_draft (str): Obecna wersja posta
        evaluation (dict): Wynik z evaluate_post()
        context (dict): Kontekst (opcjonalny)
        fact_check_results (dict): Wyniki fact-checkingu (opcjonalne)

    Returns:
        str: Poprawiona wersja posta
    """

    # ===================================
    # WYCIĄGNIJ BŁĘDY Z EVALUATION
    # ===================================
    feedback = evaluation.get('feedback', 'Brak feedbacku')

    logic_errors = evaluation.get('logic_check', {}).get('errors', [])
    logic_errors_str = "\n".join([f"- {err}" for err in logic_errors]) if logic_errors else "Brak błędów logicznych"

    format_errors = evaluation.get('format_errors', [])
    format_errors_str = "\n".join([f"- {err}" for err in format_errors]) if format_errors else "Brak błędów formatowania"

    repetition_check = evaluation.get('repetition_check', {})
    repetition_errors_str = repetition_check.get('details', 'Brak powtórzeń') if repetition_check else 'Brak danych'

    # ===================================
    # WYCIĄGNIJ FACT-CHECK RESULTS
    # ===================================
    fact_check_str = ""
    if fact_check_results and fact_check_results.get('suspicious_claims'):
        fact_check_str = "NIEREALISTYCZNE TWIERDZENIA (z researchu internetowego):\n"
        for claim in fact_check_results['suspicious_claims']:
            fact_check_str += f"\n❌ TWIERDZENIE: {claim['original_claim']['claim']}\n"
            fact_check_str += f"   PROBLEM: {claim['verdict']} - {claim['explanation']}\n"
            fact_check_str += f"   REALNE DANE: {claim.get('real_range', 'N/A')}\n"
            if claim.get('correction_hint'):
                fact_check_str += f"   JAK POPRAWIĆ: {claim['correction_hint']}\n"
    else:
        fact_check_str = "Brak nierealistycznych twierdzeń"

    # ===================================
    # WCZYTAJ PROMPT Z PLIKU
    # ===================================
    prompt_template = load_prompt("improver.txt")

    # ===================================
    # FORMATUJ ZMIENNE
    # ===================================
    prompt = format_prompt(
        prompt_template,
        previous_draft=previous_draft,
        feedback=feedback,
        logic_errors=logic_errors_str,
        format_errors=format_errors_str,
        repetition_errors=repetition_errors_str,
        fact_check_errors=fact_check_str
    )

    # ===================================
    # WYWOŁAJ API
    # ===================================
    response = generate_content_with_retry(
        prompt=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="high"),
            temperature=0.7  # Średnia temperatura = kontrolowana poprawa
        )
    )

    return response.text.strip()
