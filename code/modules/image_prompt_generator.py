"""
Image Prompt Generator - AgencjaOP Style
Generuje prompty do obrazów dla postów przemysłowych LinkedIn

Styl: RAW, AUTHENTIC, INDUSTRIAL
- Zdjęcia jak z iPhone'a (nie stock photos)
- Hala produkcyjna, brudne maszyny, smar
- Blue collar vibe, rzeczywisty przemysł
"""

import re

def generate_image_prompt(post_content, topic=""):
    """
    Generuje prompt do obrazu bazując na temacie posta

    Args:
        post_content (str): Treść wygenerowanego posta
        topic (str): Temat posta (opcjonalnie)

    Returns:
        dict: {
            'prompt': str - prompt po angielsku do Imagen/DALL-E/SD,
            'style_notes': str - dodatkowe wytyczne,
            'aspect_ratio': str - rekomendowany format
        }
    """

    # Analiza tematu - wykryj kluczowe słowa
    content_lower = (post_content + " " + topic).lower()

    # Określ główny temat wizualny
    visual_theme = detect_visual_theme(content_lower)

    # Buduj bazowy prompt (ZAWSZE w stylu industrial/authentic)
    base_style = """
Raw iPhone photography style, authentic industrial setting.
Factory floor environment. Real manufacturing scene.
Gritty, unpolished, documentary feel.
Natural lighting with some overhead factory lights.
Slight motion blur acceptable. Not a stock photo.
Blue collar aesthetic. Professional but not sterile.
    """.strip()

    # Główny obiekt zdjęcia (bazując na temacie)
    main_subject = get_main_subject(visual_theme, content_lower)

    # Kompozycja i szczegóły
    composition = get_composition_details(visual_theme)

    # Buduj finalny prompt
    prompt = f"""
{main_subject}

{composition}

Style: {base_style}

Technical: Shot on iPhone 15 Pro Max.
Slightly dirty lens. Real work environment.
Some machinery in soft focus background.
Visible wear and tear on equipment.
Safety markings partially worn off.
Oil stains, metal shavings, industrial dust visible.

Mood: Authentic, raw, real industrial workspace.
NOT glamorized. NOT stock photography.
This is how factories REALLY look.
    """.strip()

    # Rekomendowany format (LinkedIn preferuje 1:1 lub 4:5)
    aspect_ratio = "1:1"  # Square dla LinkedIn

    # Dodatkowe notatki
    style_notes = f"""
🎨 STYL AgencjaOP - Industrial Raw:
- Zdjęcie wykonane jakby z telefonu przez inżyniera na hali
- Brudne, autentyczne, bez retuszu
- Widać że to PRAWDZIWA fabryka (nie studio)
- Temat: {visual_theme}
    """

    return {
        'prompt': prompt,
        'style_notes': style_notes,
        'aspect_ratio': aspect_ratio,
        'theme': visual_theme
    }


def detect_visual_theme(text):
    """
    Wykrywa główny temat wizualny z tekstu
    """
    themes = {
        'maszyna': ['maszyn', 'robot', 'linia', 'prasa', 'tokarka', 'obrabiark'],
        'audyt': ['audyt', 'odbiór', 'fat', 'sat', 'inspekcj', 'kontrola'],
        'bezpieczeństwo': ['bezpieczeńst', 'osłon', 'safety', 'wypadek', 'guard'],
        'usterka': ['usterka', 'awaria', 'błąd', 'defekt', 'wada', 'problem'],
        'dokumentacja': ['dokument', 'specyfikacj', 'urs', 'certyfikat', 'deklaracj'],
        'serwis': ['serwis', 'naprawa', 'konserwacj', 'ur', 'utrzymani'],
        'przestój': ['przestój', 'postój', 'linia stoi', 'downtime'],
        'kosztorys': ['koszt', 'cena', 'budżet', 'oferta', 'wycena'],
        'integracja': ['integracja', 'połączen', 'komunikacj', 'interfejs'],
        'operator': ['operator', 'pracownik', 'obsługa', 'ekipa']
    }

    # Sprawdź który temat dominuje
    for theme_name, keywords in themes.items():
        for keyword in keywords:
            if keyword in text:
                return theme_name

    return 'maszyna'  # Default


def get_main_subject(theme, text):
    """
    Zwraca opis głównego obiektu na zdjęciu
    """
    subjects = {
        'maszyna': """
A large industrial CNC machine or production line equipment.
Close-up shot showing control panel with worn buttons, scratched metal surfaces.
Yellow safety markings partially faded.
        """.strip(),

        'audyt': """
Industrial engineer inspecting machine with clipboard and measuring tools.
Focus on hands holding digital caliper or inspection checklist.
Machine in background, slightly out of focus.
        """.strip(),

        'bezpieczeństwo': """
Safety guard or emergency stop button on industrial machine.
Red emergency stop prominent. Safety signage visible but weathered.
Yellow and black hazard stripes showing wear.
        """.strip(),

        'usterka': """
Damaged or malfunctioning machine component.
Visible wear, broken part, or leak. Oil stain on concrete floor.
Maintenance tag hanging from equipment.
        """.strip(),

        'dokumentacja': """
Technical documentation spread on work table in factory.
Blueprints or manuals with coffee stains and finger marks.
Machine visible in background. Pen and notes on documents.
        """.strip(),

        'serwis': """
Maintenance technician working on open machine panel.
Tools scattered around. Hydraulic lines and electrical cables visible.
Dirty work gloves and grease stains on surfaces.
        """.strip(),

        'przestój': """
Idle production line with red warning light or STOP sign.
Empty conveyor belt. Machinery silent. Clock or countdown timer visible.
Worker standing nearby looking frustrated.
        """.strip(),

        'kosztorys': """
Industrial equipment with visible price tag mockup or cost breakdown sheet.
Calculator and documents on workbench.
Machine in background showing scale of investment.
        """.strip(),

        'integracja': """
Multiple machines connected with cables, hoses, or conveyor systems.
Complex wiring or pneumatic connections visible.
Control cabinet with various cables and terminals.
        """.strip(),

        'operator': """
Factory worker in safety vest operating machine control panel.
Shot from behind or side. Focus on hands and controls.
Industrial setting with machines in background.
        """.strip()
    }

    return subjects.get(theme, subjects['maszyna'])


def get_composition_details(theme):
    """
    Zwraca szczegóły kompozycji i otoczenia
    """
    # Wspólne dla wszystkich tematów przemysłowych
    common_details = """
Composition:
- Slight Dutch angle (5-10 degrees) for dynamic feel
- Shallow depth of field (foreground sharp, background soft)
- Natural framing from machinery or structural elements

Environment Details:
- Concrete or epoxy-coated factory floor (scratched, stained)
- Overhead LED or fluorescent lighting creating harsh shadows
- Other machines visible in soft focus background
- Electrical conduits, cable trays on walls
- Yellow floor markings (faded, chipped)
- Safety notices on walls (slightly curled edges)
- Metal toolbox or cart visible nearby

Authenticity Markers:
- Fingerprints or smudges on control panels
- Coffee mug or water bottle in background
- Safety goggles hanging on equipment
- Oil or coolant puddles reflecting light
- Metal shavings on surfaces
- Worn instruction labels
- Grease stains on concrete
- Used shop towels visible
    """.strip()

    return common_details


def generate_multiple_variants(post_content, topic="", count=3):
    """
    Generuje kilka wariantów promptu do A/B testowania

    Returns:
        list: Lista dict z wariantami promptów
    """
    variants = []

    # Wariant 1: Close-up (szczegół)
    base_prompt = generate_image_prompt(post_content, topic)
    variant_1 = base_prompt.copy()
    variant_1['prompt'] = f"{base_prompt['prompt']}\n\nFRAMING: Extreme close-up. Fill frame with main subject."
    variant_1['variant_name'] = "Close-up Detail"
    variants.append(variant_1)

    # Wariant 2: Medium shot (kontekst)
    variant_2 = base_prompt.copy()
    variant_2['prompt'] = f"{base_prompt['prompt']}\n\nFRAMING: Medium shot showing subject with surrounding context."
    variant_2['variant_name'] = "Medium Context"
    variants.append(variant_2)

    # Wariant 3: Environmental (szerszy plan)
    variant_3 = base_prompt.copy()
    variant_3['prompt'] = f"{base_prompt['prompt']}\n\nFRAMING: Wide angle showing full production environment."
    variant_3['variant_name'] = "Wide Environmental"
    variants.append(variant_3)

    return variants[:count]


def format_prompt_for_imagen(prompt_dict):
    """
    Formatuje prompt specjalnie dla Google Imagen 4
    (optymalizacja pod Google Vision understanding)
    """
    # Imagen preferuje zwięzłe, ale opisowe prompty
    base = prompt_dict['prompt']

    # Uproszczenie (Imagen lepiej działa z krótszymi)
    simplified = f"""
{base}

Additional context for Google Imagen:
- Realistic photo, not illustration
- Industrial documentary style
- High detail on textures (metal, oil, rust)
- Natural color grading (slightly desaturated)
- 16:9 or 1:1 aspect ratio
    """.strip()

    return {
        'imagen_prompt': simplified,
        'parameters': {
            'aspectRatio': prompt_dict.get('aspect_ratio', '1:1'),
            'sampleCount': 1,
            'guidanceScale': 15  # Wyższa wartość = bardziej zgodny z promptem
        }
    }


# Przykładowe użycie (do testów)
if __name__ == "__main__":
    # Test 1
    test_post = """
    Odmówiłem podpisania odbioru maszyny dziś.

    Powód? Brak schematu elektrycznego w dokumentacji.

    Maszyna za 1.4M PLN, a my mamy działać "na czuja" przy awarii?

    Nie ma mowy.
    """

    test_topic = "Brak schematu elektrycznego = 3 dni przestoju przy awarii"

    result = generate_image_prompt(test_post, test_topic)

    print("="*60)
    print("GENERATED IMAGE PROMPT")
    print("="*60)
    print(f"\n📊 Wykryty temat: {result['theme']}")
    print(f"📐 Aspect ratio: {result['aspect_ratio']}")
    print(f"\n{result['style_notes']}")
    print(f"\n🎨 PROMPT DO IMAGEN/DALL-E:\n")
    print("-"*60)
    print(result['prompt'])
    print("-"*60)

    # Test 2: Warianty
    print("\n\n" + "="*60)
    print("TESTING VARIANTS")
    print("="*60)

    variants = generate_multiple_variants(test_post, test_topic, count=3)

    for i, variant in enumerate(variants, 1):
        print(f"\n🎨 WARIANT {i}: {variant['variant_name']}")
        print(f"Theme: {variant['theme']}")
        print(f"Aspect: {variant['aspect_ratio']}")
