"""
History Checker - integracja z INDEX_POSTOW.md
"""
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
INDEX_PATH = os.path.join(BASE_DIR, os.getenv("INDEX_PATH", "MARKETING/05_PUBLIKACJE/INDEX_POSTOW.md"))

def parse_index():
    if not os.path.exists(INDEX_PATH): return []
    with open(INDEX_PATH, 'r', encoding='utf-8') as f: content = f.read()
    history = []
    pattern = r'|\s*([\d\-]+)\s*|\s*([^\|]+?)\s*|\s*([^\|]+?)\s*|\s*([^\|]+?)\s*|\s*([^\|]+?)\s*|'
    matches = re.findall(pattern, content)
    for date_str, topic, has_file, has_graphic, views_str in matches:
        if "Data" in date_str: continue
        history.append({'date': date_str.strip(), 'topic': topic.strip()})
    return history

def get_recent_topics(n=10):
    history = parse_index()
    return [item['topic'] for item in history[-n:]]

def check_uniqueness(new_topic, history=None, days_threshold=30):
    if history is None: history = parse_index()
    new_keywords = set(new_topic.lower().split())
    similar_posts = []
    today = datetime.now()
    for post in history:
        try:
            post_date = datetime.strptime(post['date'], '%Y-%m-%d')
        except ValueError: continue
        days_ago = (today - post_date).days
        post_keywords = set(post['topic'].lower().split())
        common = new_keywords & post_keywords
        similarity = len(common) / len(new_keywords) if new_keywords else 0
        if similarity > 0.5 and days_ago < days_threshold:
            similar_posts.append({'topic': post['topic'], 'days_ago': days_ago})
    if similar_posts:
        return {'is_unique': False, 'similar_posts': similar_posts, 'recommendation': f"Podobny post {similar_posts[0]['days_ago']} dni temu."}
    return {'is_unique': True, 'similar_posts': [], 'recommendation': "OK"}

def append_to_index(post_data):
    if not os.path.exists(INDEX_PATH): return False
    new_row = f"| {post_data['date']} | {post_data['topic']} | {'✅' if post_data.get('has_file', True) else '❌'} | {'✅' if post_data.get('has_graphic', False) else '❌'} | - |\n"
    with open(INDEX_PATH, 'r', encoding='utf-8') as f: content = f.read()
    
    # Marker bez polskich znaków do wyszukiwania
    for line in content.split('\n'):
        if "| Data | Temat |" in line and "MD" in line:
            marker_line = line
            break
    else:
        print("Nie znaleziono nagłówka")
        return False

    next_line = "|---|---|---|---|---|"
    marker = marker_line + "\n" + next_line + "\n"
    
    if marker in content:
        parts = content.split(marker, 1)
        updated = parts[0] + marker + new_row + parts[1]
        with open(INDEX_PATH, 'w', encoding='utf-8') as f: f.write(updated)
        return True
    return False