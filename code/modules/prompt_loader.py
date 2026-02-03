"""
Prompt Loader - wczytuje prompty z plików .txt
"""
import os

# Ścieżka do folderu z promptami
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # code/
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

def load_prompt(filename):
    """
    Wczytaj prompt z pliku .txt

    Args:
        filename (str): Nazwa pliku (np. "generator.txt")

    Returns:
        str: Treść promptu
    """
    filepath = os.path.join(PROMPTS_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Nie znaleziono promptu: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return content

def format_prompt(template, **kwargs):
    """
    Formatuj prompt z zmiennymi

    Args:
        template (str): Template promptu (z {placeholders})
        **kwargs: Zmienne do wstawienia

    Returns:
        str: Sformatowany prompt
    """
    return template.format(**kwargs)

# Test
if __name__ == "__main__":
    try:
        generator_prompt = load_prompt("generator.txt")
        print(f"✅ Wczytano generator.txt ({len(generator_prompt)} znaków)")
    except FileNotFoundError as e:
        print(e)
