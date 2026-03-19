"""
Image Generator - AgencjaOP
Generuje PRAWDZIWE obrazy przez Google AI Studio (Gemini / Imagen 3)

Modele:
  - imagen-3.0-generate-002      → Imagen 3 (najlepsza jakość, aspekt ratio)
  - gemini-2.0-flash-preview-image-generation → Gemini Flash (szybszy, fallback)
"""
import os
import base64
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY nie znaleziony w .env!")

# Output folder
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "generated_images"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_image_imagen3(prompt: str, filename: str = None, aspect_ratio: str = "1:1") -> dict:
    """
    Generuje obraz przez Imagen 3 (google-genai SDK).

    Args:
        prompt: Opis obrazu (po angielsku - najlepsze wyniki)
        filename: Nazwa pliku bez rozszerzenia (auto jeśli None)
        aspect_ratio: "1:1" | "16:9" | "9:16" | "4:3" | "3:4"

    Returns:
        dict: {success, filepath, model, error}
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_only_high",
            )
        )

        if not response.generated_images:
            return {"success": False, "error": "Brak wygenerowanych obrazów w odpowiedzi"}

        # Zapisz obraz
        image_bytes = response.generated_images[0].image.image_bytes
        filepath = _save_image(image_bytes, filename, "imagen3")

        return {
            "success": True,
            "filepath": str(filepath),
            "model": "imagen-3.0-generate-002",
            "error": None
        }

    except Exception as e:
        return {"success": False, "error": str(e), "filepath": None, "model": "imagen-3.0-generate-002"}


def generate_image_gemini_flash(prompt: str, filename: str = None) -> dict:
    """
    Generuje obraz przez Gemini 2.0 Flash (fallback).

    Args:
        prompt: Opis obrazu
        filename: Nazwa pliku bez rozszerzenia

    Returns:
        dict: {success, filepath, model, error}
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )

        # Szukaj danych obrazu w odpowiedzi
        image_bytes = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                raw = part.inline_data.data
                # Dane mogą być bytes lub base64 string
                if isinstance(raw, str):
                    image_bytes = base64.b64decode(raw)
                else:
                    image_bytes = raw
                break

        if not image_bytes:
            return {"success": False, "error": "Brak danych obrazu w odpowiedzi Gemini Flash"}

        filepath = _save_image(image_bytes, filename, "gemini_flash")

        return {
            "success": True,
            "filepath": str(filepath),
            "model": "gemini-2.0-flash-preview-image-generation",
            "error": None
        }

    except Exception as e:
        return {"success": False, "error": str(e), "filepath": None, "model": "gemini-2.0-flash-preview-image-generation"}


def generate_image(prompt: str, filename: str = None, aspect_ratio: str = "1:1",
                   prefer_model: str = "gemini_flash") -> dict:
    """
    Główna funkcja generowania obrazów z auto-fallback.

    Args:
        prompt: Opis obrazu
        filename: Nazwa pliku (opcjonalnie)
        aspect_ratio: Format obrazu
        prefer_model: "imagen3" | "gemini_flash"

    Returns:
        dict: {success, filepath, model, error}
    """
    if prefer_model == "gemini_flash":
        result = generate_image_gemini_flash(prompt, filename)
        if not result["success"]:
            print(f"⚠️ Gemini Flash failed: {result['error']}\n   Próbuję Imagen 3...")
            result = generate_image_imagen3(prompt, filename, aspect_ratio)
    else:
        result = generate_image_imagen3(prompt, filename, aspect_ratio)
        if not result["success"]:
            print(f"⚠️ Imagen 3 failed: {result['error']}\n   Próbuję Gemini Flash...")
            result = generate_image_gemini_flash(prompt, filename)

    return result


def _save_image(image_bytes: bytes, filename: str = None, model_tag: str = "") -> Path:
    """Zapisuje bytes obrazu do pliku PNG."""
    if filename is None:
        timestamp = int(time.time())
        filename = f"image_{model_tag}_{timestamp}"

    filepath = DEFAULT_OUTPUT_DIR / f"{filename}.png"

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    print(f"✅ Obraz zapisany: {filepath}")
    return filepath


# ============================================================
# CLI TEST
# ============================================================
if __name__ == "__main__":
    print("🎨 Test Image Generator - AgencjaOP")
    print("=" * 50)

    test_prompt = """
    Professional LinkedIn banner for industrial machinery audit consultant.
    Dark background, industrial factory setting.
    Polish engineer in safety vest inspecting large CNC machine.
    Text: 'AgencjaOP | Audyt Maszyn Przemysłowych'
    Blue and orange accent colors.
    Clean, professional, modern design.
    16:9 format, high quality.
    """

    print("▶ Testuję Imagen 3...")
    result = generate_image_imagen3(test_prompt, "test_banner", aspect_ratio="16:9")

    if result["success"]:
        print(f"✅ Sukces! Plik: {result['filepath']}")
    else:
        print(f"❌ Imagen 3 error: {result['error']}")
        print("▶ Próbuję Gemini Flash...")
        result = generate_image_gemini_flash(test_prompt, "test_banner_flash")
        if result["success"]:
            print(f"✅ Sukces z Gemini Flash! Plik: {result['filepath']}")
        else:
            print(f"❌ Gemini Flash error: {result['error']}")
