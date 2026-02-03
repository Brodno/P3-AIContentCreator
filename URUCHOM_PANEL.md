# 🚀 Jak uruchomić AI Content Factory - Panel Streamlit

## Uruchomienie panelu:

### Krok 1: Otwórz terminal w folderze projektu

```bash
cd "C:\Users\rymko\Desktop\CLAUDE\oferta kompletna\AOP+++\Projekty\AI_OS_Personal\code"
```

### Krok 2: Uruchom Streamlit

```bash
streamlit run app.py
```

### Krok 3: Otworzy się przeglądarka

Panel automatycznie otworzy się w przeglądarce pod adresem:
```
http://localhost:8501
```

Jeśli nie otworzył się automatycznie - wklej ten adres do przeglądarki.

---

## 🎯 Jak używać panelu:

### 1. Wpisz temat posta
- W polu "Wpisz temat posta" wpisz temat (np. "Olej z logo producenta")
- Kliknij **"Generuj Post"**

### 2. Lub wybierz z sugestii
- Kliknij **"Pokaż sugestie z banku pomysłów"**
- Zaznacz temat z listy
- Kliknij **"Generuj wybrane"**

### 3. Obserwuj postęp
- Zobaczysz na żywo:
  - Iteracje (1-10)
  - Fact-checking wyników
  - Oceny jakości (hook, E-E-A-T, etc.)
  - Feedback od evaluatora

### 4. Gotowy post
- Zobaczysz finalny post
- Wynik (np. 100/100)
- Możesz: Zapisać / Regenerować / Skopiować

---

## 📊 Sidebar (lewy panel):

- **Ustawienia:** Cel jakości, Max iteracji
- **Fact-checking status:** Mock Data lub Google API
- **Historia:** Ostatnie wygenerowane posty

---

## 🔧 Troubleshooting:

### "ModuleNotFoundError"
```bash
pip install streamlit
```

### "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### Zmiana portu domyślnie
Utwórz plik `.streamlit/config.toml`:
```toml
[server]
port = 8501
```

---

## 🎨 Funkcje panelu:

✅ Wpisywanie własnych tematów
✅ Sugestie z BANK_POMYSLOW.md
✅ Live progress (iteracje, fact-checking)
✅ Wyświetlanie wyników na żywo
✅ Metryki jakości (breakdown)
✅ Zapisywanie/kopiowanie postów
✅ Historia wygenerowanych postów

---

## 🚀 Gotowe!

Teraz masz profesjonalny panel webowy do generowania postów LinkedIn!

**Enjoy! 🎉**
