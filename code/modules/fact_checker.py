"""
Fact Checker - weryfikuje twierdzenia w poście przez WebSearch
"""
import json
from config.gemini_config import generate_content_with_retry
from google.genai import types

def extract_claims(draft):
    """
    Wyciąga twierdzenia do weryfikacji z draftu posta

    Args:
        draft (str): Treść posta

    Returns:
        list: Lista twierdzeń z query do wyszukania
    """
    prompt = f"""
Jesteś fact-checkerem technicznym. Wyciągnij WSZYSTKIE twierdzenia liczbowe i techniczne z posta, które można zweryfikować.

POST:
---
{draft}
---

SZUKAJ:
1. CENY (np. "olej kosztuje 125 zł", "maszyna za 1.47M")
2. ROI / ZWROTY (np. "zwrot w 3 miesiące", "oszczędność 46k")
3. PARAMETRY TECHNICZNE (np. "HLP 46", "OEE 85%")
4. PROPORCJE (np. "marża 400%", "4x droższe")

Dla każdego twierdzenia podaj:
- claim: dokładny cytat z posta
- type: "price" | "roi" | "technical" | "proportion"
- search_query: query do Google (po polsku, konkretne)
- context: co sprawdzamy (1-2 słowa)

Zwróć JSON:
{{
  "claims": [
    {{"claim": "...", "type": "...", "search_query": "...", "context": "..."}}
  ]
}}

WAŻNE:
- Nie wyciągaj każdego słowa, tylko KLUCZOWE liczby
- Max 5 najważniejszych twierdzeń
- Query musi być konkretne (np. "cena oleju hydraulicznego HLP 46 2026")
"""

    response = generate_content_with_retry(
        prompt=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3  # Niska temperatura = precyzja
        )
    )

    try:
        result = json.loads(response.text)
        return result.get('claims', [])
    except json.JSONDecodeError:
        return []


def verify_claim(claim, search_result):
    """
    Weryfikuje pojedyncze twierdzenie na podstawie wyników wyszukiwania

    Args:
        claim (dict): Twierdzenie do weryfikacji
        search_result (str): Wyniki z WebSearch

    Returns:
        dict: Wynik weryfikacji
    """
    prompt = f"""
Jesteś inżynierem weryfikującym twierdzenie techniczne.

TWIERDZENIE Z POSTA:
"{claim['claim']}"

TYP: {claim['type']}
KONTEKST: {claim['context']}

WYNIKI WYSZUKIWANIA:
---
{search_result}
---

ZADANIE:
Sprawdź czy twierdzenie jest REALISTYCZNE na podstawie wyników.

Zwróć JSON:
{{
  "is_realistic": true/false,
  "confidence": "high" | "medium" | "low",
  "real_range": "jaki jest realny zakres (np. 30-50 PLN/L)",
  "verdict": "REALISTYCZNE" | "ZAWYŻONE" | "ZANIŻONE" | "BŁĘDNE",
  "explanation": "krótkie wyjaśnienie (1-2 zdania)",
  "correction_hint": "jak poprawić (opcjonalne, jeśli błędne)"
}}

PRZYKŁAD OCENY:
- Claim: "olej 125 zł/L" + Search: "30-50 PLN typowo" → verdict: "ZAWYŻONE"
- Claim: "przestój 46k PLN dla linii 1.5M" + Search: "10-25k typowo" → verdict: "ZAWYŻONE"
- Claim: "marża 400%" + Search: "OEM markup 2-5x" → verdict: "ZAWYŻONE"

Bądź surowy ale sprawiedliwy. Jeśli liczba jest 2x poza zakresem → BŁĘDNE.
"""

    response = generate_content_with_retry(
        prompt=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3
        )
    )

    try:
        verification = json.loads(response.text)
        verification['original_claim'] = claim
        return verification
    except json.JSONDecodeError:
        return {
            'is_realistic': True,  # Domyślnie przepuszczamy
            'confidence': 'low',
            'verdict': 'NIEZNANE',
            'explanation': 'Błąd parsowania weryfikacji',
            'original_claim': claim
        }


def fact_check_post(draft, web_search_fn=None):
    """
    Główna funkcja fact-checkingu

    Args:
        draft (str): Treść posta do sprawdzenia
        web_search_fn (callable): Funkcja do wyszukiwania (WebSearch)

    Returns:
        dict: {
            'all_claims': [...],
            'suspicious_claims': [...],
            'verified_claims': [...],
            'summary': "..."
        }
    """
    print("🔍 Fact-checking: Wyciągam twierdzenia...")
    claims = extract_claims(draft)

    if not claims:
        return {
            'all_claims': [],
            'suspicious_claims': [],
            'verified_claims': [],
            'summary': 'Brak twierdzeń do weryfikacji'
        }

    print(f"   Znaleziono {len(claims)} twierdzeń do sprawdzenia")

    verifications = []

    for i, claim in enumerate(claims, 1):
        print(f"   [{i}/{len(claims)}] Sprawdzam: {claim['claim'][:50]}...")

        # Wyszukaj w internecie
        if web_search_fn:
            search_result = web_search_fn(claim['search_query'])
        else:
            search_result = "Brak dostępu do WebSearch"

        # Weryfikuj
        verification = verify_claim(claim, search_result)
        verifications.append(verification)

        verdict_emoji = "✅" if verification['is_realistic'] else "❌"
        print(f"      {verdict_emoji} {verification['verdict']}: {verification['explanation'][:60]}...")

    # Podziel na suspicious vs verified
    suspicious = [v for v in verifications if not v['is_realistic']]
    verified = [v for v in verifications if v['is_realistic']]

    # Podsumowanie
    if suspicious:
        summary = f"⚠️ Znaleziono {len(suspicious)} podejrzanych twierdzeń"
    else:
        summary = f"✅ Wszystkie twierdzenia ({len(verified)}) są realistyczne"

    return {
        'all_claims': verifications,
        'suspicious_claims': suspicious,
        'verified_claims': verified,
        'summary': summary
    }


# Test
if __name__ == "__main__":
    test_draft = """
Olej hydrauliczny z logo OEM kosztuje 545 zł za litr.
W hurtowni ten sam olej kosztuje 125 zł.
Przestój linii za 1.47M PLN = 46k PLN na godzinę.
"""

    result = fact_check_post(test_draft)
    print("\n📊 WYNIK FACT-CHECKINGU:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
