"""
AI Content Factory v0.2.0 - Streamlit Web UI
Panel do generowania postów LinkedIn z Content Queue System
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
from modules.queue_manager import get_queue_manager
from content_loop import web_search

# Konfiguracja strony
st.set_page_config(
    page_title="AI Content Factory v0.2",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Ładniejszy UI
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .metric-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }

    .metric-card p {
        margin: 0;
        opacity: 0.9;
    }

    /* Status badges */
    .status-draft {
        background-color: #ffd93d;
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    .status-scheduled {
        background-color: #6bcf7f;
        color: #fff;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    .status-published {
        background-color: #4dabf7;
        color: #fff;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.85rem;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Alert box */
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicjalizacja session state
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""
if 'context' not in st.session_state:
    st.session_state.context = None
if 'random_topics' not in st.session_state:
    st.session_state.random_topics = []
if 'topics_seed' not in st.session_state:
    st.session_state.topics_seed = 0

# Queue Manager
queue_manager = get_queue_manager()

# Funkcje tematów
def find_topic_files():
    """Znajduje wszystkie pliki tematy*.md"""
    code_dir = os.path.dirname(__file__)
    topic_files = []
    for filename in os.listdir(code_dir):
        if filename.startswith('tematy') and filename.endswith('.md'):
            topic_files.append(os.path.join(code_dir, filename))
    return sorted(topic_files)

def load_all_topics():
    """Wczytuje wszystkie tematy"""
    topic_files = find_topic_files()
    all_topics = []
    for filepath in topic_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            for line in content.split('\\n'):
                line = line.strip()
                if line and line[0].isdigit() and '. ' in line:
                    topic = line.split('. ', 1)[1].strip()
                    if topic and len(topic) > 10:
                        all_topics.append({
                            'text': topic,
                            'file': os.path.basename(filepath),
                            'full_line': line
                        })
        except Exception as e:
            st.error(f"Błąd wczytywania {filepath}: {e}")
    return all_topics

def get_used_topics():
    """Pobiera listę użytych tematów z INDEX i queue"""
    used = set()

    # Z INDEX_POSTOW.md
    history = parse_index()
    for item in history:
        used.add(item['topic'].lower())

    # Z kolejki (published)
    published = queue_manager.get_posts(status='published')
    for post in published:
        used.add(post['topic'].lower())

    return used

def get_random_topics(n=8, seed=None):
    """Zwraca N losowych NIEWYKORZYSTANYCH tematów"""
    import random

    all_topics = load_all_topics()
    used_topics = get_used_topics()

    # Filtruj użyte
    available = [t for t in all_topics if t['text'].lower() not in used_topics]

    if not available:
        st.warning("⚠️ Wszystkie tematy wykorzystane!")
        return []

    if seed is not None:
        random.seed(seed)

    if len(available) <= n:
        return available

    return random.sample(available, n)

# Callbacks
def refresh_topics():
    st.session_state.topics_seed += 1
    st.session_state.random_topics = get_random_topics(8, st.session_state.topics_seed)

def select_topic(topic_text):
    st.session_state.topic_input_field = topic_text
    st.session_state.current_topic = topic_text

# Funkcja generowania
def generate_post_with_progress(topic):
    """Generuje post z progress tracking"""
    TARGET_SCORE = 95
    MAX_ITERATIONS = 10

    if st.session_state.context is None:
        with st.spinner("📂 Ładowanie kontekstu..."):
            st.session_state.context = load_context()

    context = st.session_state.context
    recent_topics = get_recent_topics(10)

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

            with st.spinner("🔍 Fact-checking..."):
                fact_check_results = fact_check_post(current_post, web_search_fn=web_search)

            if fact_check_results['suspicious_claims']:
                st.warning(f"⚠️ {len(fact_check_results['suspicious_claims'])} podejrzanych twierdzeń")
            else:
                st.success("✅ Fact-check OK")

            with st.spinner("⚖️ Ocena jakości..."):
                evaluation = evaluate_post(current_post, "LinkedIn", context, fact_check_results)

            score = evaluation.get('total_score', 0)
            bd = evaluation.get('breakdown', {})

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Total", f"{score}/100")
            col2.metric("Hook", f"{bd.get('hook', 0)}/30")
            col3.metric("E-E-A-T", f"{bd.get('eeat', 0)}/25")
            col4.metric("Visual", f"{bd.get('visual', 0)}/20")
            col5.metric("Pain", f"{bd.get('pain', 0)}/15")
            col6.metric("CTA", f"{bd.get('cta', 0)}/10")

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
# SIDEBAR - Historia & Statystyki
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Dashboard")

    # Statystyki kolejki
    stats = queue_manager.get_statistics()

    st.markdown("### 📊 Statystyki")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Draft", stats['draft'])
        st.metric("✅ Published", stats['published'])
    with col2:
        st.metric("📅 Scheduled", stats['scheduled'])
        st.metric("⭐ Avg Score", f"{stats['avg_score']}/100")

    # Tematy - ile zostało
    all_topics_count = len(load_all_topics())
    used_topics_count = len(get_used_topics())
    remaining = all_topics_count - used_topics_count

    st.markdown("### 🎯 Tematy")
    st.metric("Wykorzystano", f"{used_topics_count}/{all_topics_count}")
    st.progress(used_topics_count / all_topics_count if all_topics_count > 0 else 0)

    if remaining < 10:
        st.markdown(f"""
        <div class="alert-warning">
            ⚠️ <strong>Uwaga!</strong><br/>
            Zostało tylko {remaining} tematów!
        </div>
        """, unsafe_allow_html=True)

    # Historia publikacji
    st.markdown("### 📜 Ostatnie publikacje")
    recent = queue_manager.get_recent_published(5)
    if recent:
        for post in recent:
            st.markdown(f"""
            <div style='padding: 0.5rem; background: #f8f9fa; border-radius: 5px; margin: 0.5rem 0;'>
                <strong>{post['topic'][:40]}...</strong><br/>
                <small>✅ {post.get('published_date', '')[:10]} | Score: {post.get('score', 0)}/100</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Brak opublikowanych postów")

    st.markdown("---")
    st.caption(f"v0.2.0 | {datetime.now().strftime('%Y-%m-%d')}")

# ============================================
# MAIN CONTENT
# ============================================

# Header
st.markdown('<p class="main-header">🚀 AI Content Factory v0.2</p>', unsafe_allow_html=True)
st.markdown("**Content Quality Loop + Queue System**")

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Nowy Post", "📅 Kolejka", "🎨 Obrazy"])

# TAB 1: Nowy Post
with tab1:
    st.markdown("## Generuj nowy post")

    col1, col2 = st.columns([3, 1])

    with col1:
        if 'topic_input_field' not in st.session_state:
            st.session_state.topic_input_field = st.session_state.current_topic

        topic_input = st.text_input(
            "Wpisz temat posta:",
            placeholder="np. Olej z logo producenta - marża OEM",
            key="topic_input_field"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🚀 Generuj Post", type="primary", use_container_width=True)

    # Losowe tematy
    st.markdown("### 💡 Losowe tematy (niewykorzystane)")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        st.button("🔄 Odśwież tematy", use_container_width=True, on_click=refresh_topics)
    with col3:
        st.metric("Dostępne", f"{len(load_all_topics()) - len(get_used_topics())}")

    if not st.session_state.random_topics:
        st.session_state.random_topics = get_random_topics(8, st.session_state.topics_seed)

    if st.session_state.random_topics:
        for idx, topic_data in enumerate(st.session_state.random_topics):
            topic_text = topic_data['text']
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
                st.caption(f"_{topic_data['file']}_")
    else:
        st.warning("⚠️ Wszystkie tematy wykorzystane! Dodaj nowe pliki tematy*.md")

    st.markdown("---")

    # Generowanie
    if generate_button and topic_input:
        st.session_state.current_topic = topic_input

        st.markdown("## 🔄 Generowanie...")

        try:
            result = generate_post_with_progress(topic_input)

            st.session_state.generated_post = result

            # Automatycznie dodaj do kolejki jako Draft
            post_id = queue_manager.add_post(
                topic=topic_input,
                content=result['post'],
                score=result['score'],
                status='draft'
            )

            st.balloons()
            st.success(f"✅ Post wygenerowany i dodany do kolejki (Draft)")

        except Exception as e:
            st.error(f"❌ Błąd podczas generowania: {e}")
            st.exception(e)

    # Wyświetlenie wyniku
    if st.session_state.generated_post:
        st.markdown("---")
        st.markdown("## 🏆 Wygenerowany Post")

        result = st.session_state.generated_post

        col1, col2, col3 = st.columns(3)
        col1.metric("Wynik", f"{result['score']}/100", delta=f"{result['score']-95:+d}")
        col2.metric("Iteracji", result['iterations'])
        col3.metric("Status", "✅ Draft" if result['score'] >= 95 else "⚠️ Do poprawy")

        st.markdown("### 📄 Treść posta:")
        st.text_area(
            "Post",
            value=result['post'],
            height=400,
            key="generated_post_display",
            label_visibility="collapsed"
        )

# TAB 2: Kolejka publikacji
with tab2:
    st.markdown("## 📅 Kolejka publikacji")

    # Filtr statusu
    filter_status = st.selectbox(
        "Filtruj po statusie:",
        ["Wszystkie", "Draft", "Scheduled", "Published"],
        index=0
    )

    status_map = {
        "Wszystkie": None,
        "Draft": "draft",
        "Scheduled": "scheduled",
        "Published": "published"
    }

    posts = queue_manager.get_posts(status=status_map[filter_status])

    if posts:
        for post in posts:
            with st.expander(f"📄 {post['topic']} - Score: {post.get('score', 0)}/100"):
                # Status badge
                status = post['status']
                badge_class = f"status-{status}"
                st.markdown(f'<span class="{badge_class}">{status.upper()}</span>', unsafe_allow_html=True)

                st.markdown(f"**Created:** {post.get('created_at', '')[:19]}")
                if post.get('scheduled_date'):
                    st.markdown(f"**Scheduled for:** {post['scheduled_date']}")
                if post.get('published_date'):
                    st.markdown(f"**Published:** {post.get('published_date', '')[:19]}")

                st.markdown("---")
                st.text_area("Content", post['content'], height=200, key=f"content_{post['id']}")

                # Akcje
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if status == 'draft':
                        scheduled_date = st.date_input(
                            "Data publikacji:",
                            value=datetime.now() + timedelta(days=1),
                            key=f"date_{post['id']}"
                        )
                        if st.button("📅 Zaplanuj", key=f"schedule_{post['id']}"):
                            queue_manager.update_status(post['id'], 'scheduled', str(scheduled_date))
                            st.success("✅ Zaplanowano!")
                            st.rerun()

                with col2:
                    if status in ['draft', 'scheduled']:
                        if st.button("✅ Opublikuj", key=f"publish_{post['id']}"):
                            queue_manager.update_status(post['id'], 'published')
                            st.success("✅ Opublikowano!")
                            st.rerun()

                with col3:
                    if status == 'published':
                        if st.button("🔄 Cofnij", key=f"unpublish_{post['id']}"):
                            queue_manager.update_status(post['id'], 'draft')
                            st.success("✅ Cofnięto do Draft!")
                            st.rerun()

                with col4:
                    if st.button("🗑️ Usuń", key=f"delete_{post['id']}"):
                        queue_manager.delete_post(post['id'])
                        st.success("✅ Usunięto!")
                        st.rerun()
    else:
        st.info("📭 Brak postów w kolejce")

# TAB 3: Generowanie obrazów
with tab3:
    st.markdown("## 🎨 Generuj prompt do obrazu")

    if st.session_state.generated_post:
        result = st.session_state.generated_post
        topic = st.session_state.current_topic

        st.info(f"🎯 Temat: **{topic}**")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📷 Close-up", use_container_width=True, key="img_closeup_tab"):
                st.session_state.image_variant = "closeup"
        with col2:
            if st.button("📷 Medium Shot", use_container_width=True, key="img_medium_tab"):
                st.session_state.image_variant = "medium"
        with col3:
            if st.button("📷 Wide Angle", use_container_width=True, key="img_wide_tab"):
                st.session_state.image_variant = "wide"

        if 'image_variant' not in st.session_state:
            st.session_state.image_variant = "medium"

        variants = generate_multiple_variants(result['post'], topic, count=3)
        variant_map = {"closeup": 0, "medium": 1, "wide": 2}
        selected_variant = variants[variant_map[st.session_state.image_variant]]

        st.info(f"🎯 Wybrany wariant: **{selected_variant['variant_name']}**")

        st.text_area(
            "Prompt do Imagen 4 / DALL-E 3:",
            value=selected_variant['prompt'],
            height=300,
            key="image_prompt_tab"
        )

        st.markdown("""
        **Jak użyć:**
        1. Skopiuj prompt (Ctrl+A, Ctrl+C)
        2. Wejdź na generator obrazów (Imagen, DALL-E, etc.)
        3. Wklej i wygeneruj
        4. Pobierz obraz i dodaj do posta LinkedIn
        """)
    else:
        st.warning("⚠️ Najpierw wygeneruj post w zakładce 'Nowy Post'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🤖 Powered by Gemini AI & AgencjaOP | v0.2.0 | Built with Streamlit
</div>
""", unsafe_allow_html=True)
