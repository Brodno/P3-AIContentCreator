"""
generate_banner.py - AgencjaOP LinkedIn Banner Generator
Czyta _KONTEKST/profil.md i generuje profesjonalny baner LinkedIn.

Użycie:
    python generate_banner.py
    python generate_banner.py --model gemini_flash
    python generate_banner.py --variant dark
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from modules.image_generator import generate_image

# ============================================================
# ŚCIEŻKI
# ============================================================
BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parent.parent.parent  # AOP+++/
PROFIL_PATH = REPO_ROOT / "_KONTEKST" / "profil.md"
OUTPUT_DIR = BASE_DIR / "data" / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PROMPTY NA BANERY
# ============================================================

BANNER_PROMPTS = {
    "dark": """
Professional LinkedIn banner image, 1584x396 pixels (horizontal panoramic format, very wide).
Dark industrial background: steel factory floor at night, dramatic lighting.
Silhouette of large industrial machinery (CNC machine, production line) in background.
Left side: Bold white text 'AgencjaOP' in modern sans-serif font, large.
Below main text: smaller text 'Audyt Maszyn Przemysłowych | Inwestycje 500k-2M PLN'.
Right side: Orange accent line or geometric element.
Color palette: Deep navy #0d1117, electric blue #1f77b4, orange #ff7f0e, white.
Tagline at bottom: 'Wiem gdzie maszyna nie dowiezie. Zanim ją kupisz.'
Style: Corporate-industrial, serious, premium quality.
No people visible. Clean typography. Professional and trustworthy.
Horizontal banner format 4:1 ratio.
""".strip(),

    "light": """
Clean professional LinkedIn banner, horizontal format 4:1.
Light grey background #f5f5f5 with subtle industrial texture.
Left side: Company logo area - 'AgencjaOP' bold navy blue text.
Center: Icon of industrial machine gear combined with magnifying glass (audit concept).
Right side: Key stats in boxes:
  - '10 lat' / 'doświadczenia'
  - '500k-2M PLN' / 'wartość inwestycji'
  - 'Audyt w 10 dni'
Color palette: Navy #0a2342, orange #ff6b35, light grey, white.
Bottom bar: Orange gradient strip with text 'www.audytmaszyn.pl'.
Professional, minimalist, B2B corporate style.
No photos, icon-based design.
""".strip(),

    "photo": """
LinkedIn banner with authentic industrial photography as background.
Wide panoramic format (4:1 ratio, very horizontal).
Background: Real factory floor photo, production line with machines, slightly blurred/darkened.
Dark overlay gradient from left (80% opacity) to right (transparent).
On dark left section, white text:
  Title: 'Łukasz Rymkowski' (medium size)
  Subtitle: 'Audytor Maszyn Przemysłowych | AgencjaOP'
  Small text below: 'Chronię producentów przed błędnymi zakupami maszyn'
Orange accent line (3px) between title and subtitle.
Bottom right: 'audytmaszyn.pl' in orange.
Raw, authentic industrial feel. Real factory environment.
Professional LinkedIn cover photo style.
""".strip(),
}


def load_profil():
    """Wczytuje profil.md dla kontekstu."""
    if PROFIL_PATH.exists():
        with open(PROFIL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # Wyciągnij kluczowe info
        print(f"✅ Wczytano profil z: {PROFIL_PATH}")
        return content[:500]  # Pierwsze 500 znaków jako kontekst
    else:
        print(f"⚠️ Nie znaleziono profil.md w {PROFIL_PATH}")
        return ""


def generate_linkedin_banner(variant: str = "dark", model: str = "imagen3") -> str:
    """
    Generuje baner LinkedIn.

    Args:
        variant: "dark" | "light" | "photo"
        model: "imagen3" | "gemini_flash"

    Returns:
        str: Ścieżka do wygenerowanego pliku
    """
    profil_info = load_profil()

    prompt = BANNER_PROMPTS.get(variant, BANNER_PROMPTS["dark"])

    # Dodaj kontekst z profilu (opcjonalnie)
    if profil_info:
        prompt += f"\n\nContext: This is for Łukasz Rymkowski, industrial machinery audit consultant from Warsaw, Poland."

    print(f"\n🎨 Generuję baner LinkedIn...")
    print(f"   Wariant: {variant}")
    print(f"   Model: {model}")
    print(f"   Prompt (pierwsze 100 znaków): {prompt[:100]}...")
    print()

    filename = f"baner_linkedin_{variant}"

    result = generate_image(
        prompt=prompt,
        filename=filename,
        aspect_ratio="16:9",  # Najbliższy do LinkedIn banner ratio
        prefer_model=model
    )

    if result["success"]:
        filepath = result["filepath"]
        print(f"\n{'='*50}")
        print(f"✅ BANER WYGENEROWANY!")
        print(f"   Model: {result['model']}")
        print(f"   Plik: {filepath}")
        print(f"{'='*50}")
        print(f"\n📋 Jak dodać baner na LinkedIn:")
        print(f"   1. Otwórz LinkedIn → swój profil")
        print(f"   2. Kliknij ikonę ołówka na tle profilu")
        print(f"   3. Załaduj plik: {filepath}")
        print(f"   4. Przytnij do formatu 1584x396px")
        return filepath
    else:
        print(f"\n❌ BŁĄD generowania: {result['error']}")
        return None


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgencjaOP LinkedIn Banner Generator")
    parser.add_argument(
        "--variant",
        choices=["dark", "light", "photo"],
        default="dark",
        help="Styl banera: dark (ciemny/industrial), light (jasny/clean), photo (zdjęcie tła)"
    )
    parser.add_argument(
        "--model",
        choices=["imagen3", "gemini_flash"],
        default="imagen3",
        help="Model AI: imagen3 (lepsza jakość) lub gemini_flash (szybszy)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Wygeneruj wszystkie 3 warianty"
    )

    args = parser.parse_args()

    print("🚀 AgencjaOP - LinkedIn Banner Generator")
    print("=" * 50)

    if args.all:
        print("Generuję wszystkie 3 warianty...")
        for v in ["dark", "light", "photo"]:
            print(f"\n--- Wariant: {v} ---")
            generate_linkedin_banner(variant=v, model=args.model)
    else:
        generate_linkedin_banner(variant=args.variant, model=args.model)
