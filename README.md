# AI Content Creator

Generator treści marketingowych oparty na AI. Automatyzuje tworzenie postów LinkedIn z integracją Notion i Google Drive.

## Co robi

- Generuje posty na podstawie podanego tematu (iteracyjnie, z oceną jakości)
- Pobiera tematy z kolejki w Notion
- Ładuje kontekst z Google Drive (styl, profil, oferta)
- Generuje obrazy przez Imagen 3 API
- Zapisuje historię wygenerowanych postów

## Stack

Python · Streamlit · Anthropic Claude API · Google Gemini API · Imagen 3 · Notion API · Google Drive API

## Uruchomienie

```bash
pip install -r code/requirements.txt
cp code/.env.example code/.env
streamlit run code/app.py
```

## Konfiguracja

```
ANTHROPIC_API_KEY=your-key
GEMINI_API_KEY=your-key
NOTION_TOKEN=your-token
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
```

## Status

Projekt w aktywnym rozwoju — v0.2.0.
