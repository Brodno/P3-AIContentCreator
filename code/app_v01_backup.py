"""
AI Content Factory - Streamlit Web UI
Panel do generowania postów LinkedIn
"""
import streamlit as st
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(__file__))

from modules.context_loader import load_context, BASE_DIR
from modules.generator import generate_post
from modules.evaluator import evaluate_post
from modules.improver import improve_post
from modules.fact_checker import fact_check_post
from modules.history_checker import parse_index, get_recent_topics
from modules.image_prompt_generator import generate_image_prompt, generate_multiple_variants
from content_loop import web_search

# Konfiguracja strony
st.set_page_config(
    page_title="AI Content Factory",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicjalizacja session state
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None
if 'generation_log' not in st.session_state:
    st.session_state.generation_log = []
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""
if 'context' not in st.session_state:
    st.session_state.context = None
if 'random_topics' not in st.session_state:
    st.session_state.random_topics = []
if 'topics_seed' not in st.session_state:
    st.session_state.topics_seed = 0

# Funkcje do wczytywania tematów z plików tematy*.md
def find_topic_files():
    """Znajduje wszystkie pliki tematy*.md w folderze code"""
    code_dir = os.path.dirname(__file__)
    topic_files = []

    for filename in os.listdir(code_dir):
        if filename.startswith('tematy') and filename.endswith('.md'):
            topic_files.append(os.path.join(code_dir, filename))

    return sorted(topic_files)

def load_all_topics():
    """Wczytuje wszystkie tematy ze wszystkich plików tematy*.md"""
    topic_files = find_topic_files()
    all_topics = []

    for filepath in topic_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Wyciągnij tematy (linie zaczynające się od cyfry i kropki)
            for line in content.split('\n'):
                line = line.strip()
                # Sprawdź czy linia zaczyna się od numeru (np. "1. " lub "100. ")
                if line and line[0].isdigit() and '. ' in line:
                    # Wyciągnij temat po numerze
                    topic = line.split('. ', 1)[1].strip()
                    if topic and len(topic) > 10:  # Pomijamy za krótkie
                        all_topics.append({
                            'text': topic,
                            'file': os.path.basename(filepath),
                            'full_line': line
                        })
        except Exception as e:
            st.error(f"Błąd wczytywania {filepath}: {e}")

    return all_topics

def get_random_topics(n=8, seed=None):
    """Zwraca n losowych tematów"""
    import random

    all_topics = load_all_topics()

    if not all_topics:
        return []

    if seed is not None:
        random.seed(seed)

    # Jeśli jest mniej tematów niż n, zwróć wszystkie
    if len(all_topics) <= n:
        return all_topics

    return random.sample(all_topics, n)

# Funkcja generowania posta (z progress)
def generate_post_with_progress(topic):
    """Generuje post z wyświetlaniem postępu"""

    TARGET_SCORE = 95
    MAX_ITERATIONS = 10

    # Wczytaj kontekst (cache w session_state)
    if st.session_state.context is None:
        with st.spinner("📂 Ładowanie kontekstu..."):
            st.session_state.context = load_context()

    context = st.session_state.context
    recent_topics = get_recent_topics(10)

    # Kontenery dla postępu
    progress_bar = st.progress(0)
    status_text = st.empty()
    iteration_container = st.container()

    current_post = ""
    best_post = ""
    best_score = 0
    iteration_history = []

    for i in range(1, MAX_ITERATIONS + 1):
        progress = i / MAX_ITERATIONS
        progress_bar.progress(progress)
        status_text.text(f"🔄 Iteracja {i}/{MAX_ITERATIONS}")

        with iteration_container:
            st.markdown(f"### Iteracja {i}")

            # Generowanie/Poprawianie
            if i == 1:
                with st.spinner("✍️ Generowanie draftu..."):
                    current_post = generate_post(topic, "LinkedIn", "post", context, recent_topics)
                st.success("✅ Draft wygenerowany")
            else:
                with st.spinner("🔧 Poprawianie posta..."):
                    last_eval = iteration_history[-1]['evaluation']
                    last_fact_check = iteration_history[-1].get('fact_check_results')
                    current_post = improve_post(current_post, last_eval, context, last_fact_check)
                st.success("✅ Post poprawiony")

            # Fact-checking
            with st.spinner("🔍 Fact-checking..."):
                fact_check_results = fact_check_post(current_post, web_search_fn=web_search)

            if fact_check_results['suspicious_claims']:
                st.warning(f"⚠️ {len(fact_check_results['suspicious_claims'])} podejrzanych twierdzeń")
                for claim in fact_check_results['suspicious_claims']:
                    st.text(f"  • {claim['original_claim']['claim']}")
                    st.text(f"    → {claim['verdict']}: {claim['explanation']}")
            else:
                st.success("✅ Fact-check OK")

            # Evaluacja
            with st.spinner("⚖️ Ocena jakości..."):
                evaluation = evaluate_post(current_post, "LinkedIn", context, fact_check_results)

            score = evaluation.get('total_score', 0)
            bd = evaluation.get('breakdown', {})

            # Wyświetl wynik
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Total", f"{score}/100")
            col2.metric("Hook", f"{bd.get('hook', 0)}/30")
            col3.metric("E-E-A-T", f"{bd.get('eeat', 0)}/25")
            col4.metric("Visual", f"{bd.get('visual', 0)}/20")
            col5.metric("Pain", f"{bd.get('pain', 0)}/15")
            col6.metric("CTA", f"{bd.get('cta', 0)}/10")

            st.info(f"💬 Feedback: {evaluation.get('feedback', '')}")

            # Zapisz historię
            iter_data = {
                'iteration': i,
                'score': score,
                'post_content': current_post,
                'evaluation': evaluation,
                'fact_check_results': fact_check_results
            }
            iteration_history.append(iter_data)

            if score > best_score:
                best_score = score
                best_post = current_post

            # Sprawdź czy osiągnięto cel
            if score >= TARGET_SCORE:
                st.success(f"🎉 SUKCES! Jakość {score}/100 osiągnięta!")
                break

            st.markdown("---")

    progress_bar.progress(1.0)
    status_text.text(f"✅ Zakończono! Best score: {best_score}/100")

    return {
        'post': best_post,
        'score': best_score,
        'iterations': len(iteration_history),
        'history': iteration_history
    }

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### ⚙️ Ustawienia")

    # Limity
    target_score = st.slider("Cel jakości", 80, 100, 95, 5)
    max_iterations = st.slider("Max iteracji", 1, 10, 10)

    st.markdown("---")

    # Fact-checking status
    st.markdown("### 🔍 Fact-checking")
    if os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE") != "YOUR_API_KEY_HERE":
        st.success("✅ Google Search API")
    else:
        st.warning("⚠️ Mock Data (fallback)")

    st.markdown("---")

    # Baza tematów
    st.markdown("### 📚 Baza tematów")
    topic_files = find_topic_files()
    if topic_files:
        for filepath in topic_files:
            filename = os.path.basename(filepath)
            st.text(f"✅ {filename}")
    else:
        st.text("❌ Brak plików")

    st.markdown("---")

    # Historia
    st.markdown("### 📊 Historia")
    history_index = parse_index()
    if history_index:
        st.text(f"Postów w bazie: {len(history_index)}")
        recent = get_recent_topics(5)
        if recent:
            st.text("Ostatnie tematy:")
            for topic in recent[:3]:
                st.text(f"• {topic[:30]}...")
    else:
        st.text("Brak historii")

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown('<p class="main-header">🚀 AI Content Factory</p>', unsafe_allow_html=True)
st.markdown("**Content Quality Loop** - Generator postów LinkedIn z fact-checkingiem")

st.markdown("---")

# Główna sekcja - Input
st.markdown("## 📝 Nowy Post")

col1, col2 = st.columns([3, 1])

with col1:
    # Inicjalizuj pole jeśli nie istnieje
    if 'topic_input_field' not in st.session_state:
        st.session_state.topic_input_field = st.session_state.current_topic

    topic_input = st.text_input(
        "Wpisz temat posta:",
        placeholder="np. Olej z logo producenta - marża OEM",
        key="topic_input_field"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    generate_button = st.button("🚀 Generuj Post", type="primary", use_container_width=True)

# System tematów z tematy*.md
st.markdown("### 💡 Losowe tematy z bazy")

# Funkcje callback
def refresh_topics():
    """Callback dla odświeżenia tematów"""
    st.session_state.topics_seed += 1
    st.session_state.random_topics = get_random_topics(8, st.session_state.topics_seed)

def select_topic(topic_text):
    """Callback dla wyboru tematu"""
    st.session_state.topic_input_field = topic_text
    st.session_state.current_topic = topic_text

# Przyciski akcji
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("Wybierz temat z listy lub kliknij Odśwież dla nowych propozycji")

with col2:
    st.button("🔄 Odśwież tematy", use_container_width=True, on_click=refresh_topics)

with col3:
    # Statystyka
    all_topics_count = len(load_all_topics())
    st.metric("Baza tematów", all_topics_count)

# Wczytaj tematy jeśli jeszcze nie ma
if not st.session_state.random_topics:
    st.session_state.random_topics = get_random_topics(8, st.session_state.topics_seed)

# Wyświetl tematy
if st.session_state.random_topics:
    st.markdown("**Kliknij na temat, aby go użyć:**")

    for idx, topic_data in enumerate(st.session_state.random_topics):
        topic_text = topic_data['text']
        topic_file = topic_data['file']

        # Twórz button dla każdego tematu
        col1, col2 = st.columns([5, 1])

        with col1:
            st.button(
                f"📌 {topic_text}",
                key=f"topic_btn_{idx}",
                use_container_width=True,
                on_click=select_topic,
                args=(topic_text,)
            )

        with col2:
            st.caption(f"_{topic_file}_")

else:
    st.warning("⚠️ Nie znaleziono plików tematy*.md w folderze code/")
    st.info("💡 Utwórz plik tematy100.md z listą tematów")

st.markdown("---")

# Generowanie
if generate_button and topic_input:
    st.session_state.current_topic = topic_input

    st.markdown("## 🔄 Generowanie...")

    try:
        result = generate_post_with_progress(topic_input)

        st.session_state.generated_post = result
        st.session_state.generation_log.append({
            'topic': topic_input,
            'timestamp': datetime.now(),
            'score': result['score']
        })

        st.balloons()

    except Exception as e:
        st.error(f"❌ Błąd podczas generowania: {e}")
        st.exception(e)

# Wyświetlenie wyniku
if st.session_state.generated_post:
    st.markdown("---")
    st.markdown("## 🏆 Wygenerowany Post")

    result = st.session_state.generated_post

    # Metryki
    col1, col2, col3 = st.columns(3)
    col1.metric("Wynik", f"{result['score']}/100", delta=f"{result['score']-95:+d}")
    col2.metric("Iteracji", result['iterations'])
    col3.metric("Status", "✅ Zatwierdzone" if result['score'] >= 95 else "⚠️ Do poprawy")

    # Post
    st.markdown("### 📄 Treść posta:")
    st.text_area(
        "Post",
        value=result['post'],
        height=400,
        key="generated_post_display",
        label_visibility="collapsed"
    )

    # Akcje
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Zapisz do pliku", use_container_width=True):
            # Zapisz post do folderu generated_posts
            from datetime import datetime
            import os

            # Folder na wygenerowane posty
            output_dir = Path(BASE_DIR) / "MARKETING" / "05_PUBLIKACJE" / "generated"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Nazwa pliku z datą
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            topic_slug = st.session_state.current_topic[:50].replace(" ", "_").replace("/", "-")
            filename = f"post_{timestamp}_{topic_slug}.txt"

            filepath = output_dir / filename

            # Zapisz post
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Post LinkedIn - AgencjaOP\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Temat: {st.session_state.current_topic}\n")
                f.write(f"Wynik: {result['score']}/100\n")
                f.write(f"Iteracji: {result['iterations']}\n")
                f.write(f"\n{'='*60}\n")
                f.write(f"TREŚĆ POSTA:\n")
                f.write(f"{'='*60}\n\n")
                f.write(result['post'])
                f.write(f"\n\n{'='*60}\n")
                f.write(f"KONIEC\n")
                f.write(f"{'='*60}\n")

            st.success(f"✅ Post zapisany!\n\n📁 {filepath}")
            st.caption(f"Plik: {filename}")

    with col2:
        if st.button("🔄 Regeneruj", use_container_width=True):
            st.session_state.generated_post = None
            st.rerun()

    with col3:
        if st.button("📋 Kopiuj do schowka", use_container_width=True):
            st.code(result['post'])
            st.info("💡 Zaznacz i skopiuj powyższy tekst (Ctrl+C)")

    # Sekcja: Prompt do obrazu
    st.markdown("---")
    st.markdown("## 🎨 Prompt do obrazu (Industrial Raw Style)")
    st.markdown("**Styl:** Autentyczny przemysł - jak z iPhone'a, brudne maszyny, hala produkcyjna, smar")

    # Generuj prompty
    topic_used = st.session_state.current_topic
    post_content = result['post']

    # Warianty
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📷 Close-up", use_container_width=True, key="img_closeup"):
            st.session_state.image_variant = "closeup"

    with col2:
        if st.button("📷 Medium Shot", use_container_width=True, key="img_medium"):
            st.session_state.image_variant = "medium"

    with col3:
        if st.button("📷 Wide Angle", use_container_width=True, key="img_wide"):
            st.session_state.image_variant = "wide"

    # Domyślny wariant
    if 'image_variant' not in st.session_state:
        st.session_state.image_variant = "medium"

    # Generuj warianty
    variants = generate_multiple_variants(post_content, topic_used, count=3)

    # Mapowanie wariantów
    variant_map = {
        "closeup": 0,
        "medium": 1,
        "wide": 2
    }

    selected_variant = variants[variant_map[st.session_state.image_variant]]

    st.info(f"🎯 Wybrany wariant: **{selected_variant['variant_name']}**")

    # Wyświetl prompt
    st.text_area(
        "Prompt do Imagen 4 / DALL-E 3:",
        value=selected_variant['prompt'],
        height=300,
        key="image_prompt_display"
    )

    st.markdown("""
    **Jak użyć:**
    1. Skopiuj powyższy prompt (Ctrl+A, Ctrl+C)
    2. Wejdź na: [Google AI Studio - Imagen](https://aistudio.google.com/app/prompts/new_freeform) lub inny generator
    3. Wklej prompt i wygeneruj obraz
    4. Pobierz i dodaj do posta na LinkedIn

    **Rekomendowany format:** Square (1:1) lub Portrait (4:5) dla LinkedIn
    """)

elif not generate_button:
    st.info("👆 Wpisz temat posta i kliknij 'Generuj Post' aby rozpocząć")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🤖 Powered by Gemini AI & AgencjaOP | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
