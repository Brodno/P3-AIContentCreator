# 🔍 Google Custom Search API - Setup Guide

## Dlaczego Google Custom Search?

- ✅ **100 zapytań/dzień za darmo**
- ✅ Prawdziwe wyniki z Google
- ✅ Prosty REST API
- ✅ Bez karty kredytowej (dla free tier)

---

## 📋 Setup Krok po Kroku

### 1. Utwórz projekt Google Cloud

1. Idź do: https://console.cloud.google.com/
2. Kliknij **"New Project"** (górny pasek)
3. Nazwa projektu: `AI-OS-Personal-FactChecker`
4. Kliknij **"CREATE"**

### 2. Włącz Custom Search API

1. W Google Cloud Console, idź do: **"APIs & Services" → "Library"**
2. W wyszukiwarce wpisz: `Custom Search API`
3. Kliknij na **"Custom Search API"**
4. Kliknij **"ENABLE"**

### 3. Utwórz API Key

1. Idź do: **"APIs & Services" → "Credentials"**
2. Kliknij **"+ CREATE CREDENTIALS"**
3. Wybierz **"API Key"**
4. **Skopiuj klucz!** (np. `AIzaSyB...`)
5. **Opcjonalnie - zabezpiecz klucz:**
   - Kliknij **"Edit API key"**
   - W sekcji "API restrictions" wybierz **"Restrict key"**
   - Zaznacz tylko **"Custom Search API"**
   - Kliknij **"SAVE"**

### 4. Utwórz Custom Search Engine (Wyszukiwarkę)

1. Idź do: https://programmablesearchengine.google.com/
2. Kliknij **"Add"** (Create a new search engine)
3. Konfiguracja:
   - **Name your search engine:** `FactChecker`
   - **What to search:** Zaznacz **"Search the entire web"**
   - Kliknij checkbox: **"I have read and agree to the Terms of Service"**
4. Kliknij **"CREATE"**
5. **Skopiuj Search Engine ID** (cx):
   - Kliknij na swoją wyszukiwarkę
   - W sekcji "Basics" znajdziesz **"Search engine ID"** (np. `c1234567890abcdef`)

---

## 🔧 Konfiguracja w projekcie

### 1. Zainstaluj bibliotekę Google API

Otwórz terminal w folderze projektu:

```bash
cd "C:\Users\rymko\Desktop\CLAUDE\oferta kompletna\AOP+++\Projekty\AI_OS_Personal\code"
pip install google-api-python-client
```

### 2. Dodaj klucze do `.env`

Edytuj plik `.env` i zamień placeholdery:

```bash
# Google Custom Search API (Fact-checking)
GOOGLE_API_KEY=AIzaSyB...TWÓJ_KLUCZ
GOOGLE_CSE_ID=c1234567890abcdef...TWOJE_ID
```

**WAŻNE:** Nie commituj `.env` do repo!

### 3. Testuj konfigurację

Uruchom test:

```bash
python modules/google_search.py
```

**Oczekiwany output:**
```
🧪 Test Google Custom Search API

Zapytanie: cena oleju hydraulicznego HLP 46 Polska

Zapytanie: cena oleju hydraulicznego HLP 46 Polska
Znaleziono: 1250 wyników (czas: 0.32s)

Tytuł: Olej hydrauliczny HLP 46 - ceny i oferty
Opis: Cena oleju hydraulicznego HLP 46 w Polsce...
Źródło: https://...

============================================================

📊 Sprawdzam konfigurację:
   API Key: ✅ OK
   CSE ID: ✅ OK
   Google API Library: ✅ Zainstalowana
```

---

## 🚀 Użycie w Content Loop

System automatycznie użyje Google Search jeśli jest skonfigurowane:

```bash
python content_loop.py "Olej z logo producenta" --auto
```

**Output z prawdziwym wyszukiwaniem:**
```
🔍 Fact-checking: Wyciągam twierdzenia...
   Znaleziono 5 twierdzeń do sprawdzenia
   [1/5] Sprawdzam: Olej kosztuje 415 zł/L...
      🌐 Szukam: cena oleju hydraulicznego HLP 46 Polska
      [Prawdziwe wyniki z Google Search]
      ❌ ZAWYŻONE: Typowe ceny 30-50 PLN/L...
```

---

## 📊 Limity i koszty

### Free Tier (100 zapytań/dzień):
- **0 PLN/miesiąc**
- Wystarczy na ~3-5 postów dziennie (każdy post = ~5-10 zapytań)
- Brak karty kredytowej

### Paid Tier (jeśli potrzebujesz więcej):
- **$5 za 1000 zapytań** (powyżej 100/dzień)
- Max 10,000 zapytań/dzień

### Monitorowanie użycia:
1. Google Cloud Console → **"APIs & Services" → "Dashboard"**
2. Zobacz wykres zapytań do Custom Search API

---

## 🔒 Bezpieczeństwo

### Ogranicz API Key:
1. Google Cloud Console → **"Credentials"**
2. Edytuj swój API Key
3. **API restrictions:** Tylko Custom Search API
4. **Application restrictions (opcjonalnie):**
   - IP addresses: Twój serwer
   - Lub HTTP referrers

### Chroń `.env`:
Dodaj do `.gitignore`:
```
.env
.env.local
```

---

## ❓ Troubleshooting

### Błąd: "API Key not valid"
- Sprawdź czy API Key jest poprawny w `.env`
- Sprawdź czy Custom Search API jest włączone w Google Cloud
- Poczekaj 1-2 minuty po utworzeniu klucza

### Błąd: "Quota exceeded"
- Przekroczyłeś 100 zapytań/dzień
- Poczekaj do północy (UTC)
- Lub włącz płatny plan

### Błąd: "Search Engine ID not found"
- Sprawdź czy CSE ID jest poprawne
- Upewnij się że wyszukiwarka jest publiczna

### Brak wyników po polsku:
- W `google_search.py` jest ustawione `lr="lang_pl"`
- Możesz dodać `gl="pl"` (geolocation Poland)

---

## 📚 Przydatne linki

- Google Cloud Console: https://console.cloud.google.com/
- Programmable Search Engine: https://programmablesearchengine.google.com/
- API Documentation: https://developers.google.com/custom-search/v1/overview
- Pricing: https://developers.google.com/custom-search/v1/overview#pricing

---

## ✅ Checklist

- [ ] Utworzony projekt Google Cloud
- [ ] Włączone Custom Search API
- [ ] Utworzony API Key i skopiowany
- [ ] Utworzony Custom Search Engine i skopiowany CSE ID
- [ ] Zainstalowane `google-api-python-client`
- [ ] Dodane klucze do `.env`
- [ ] Przetestowane `python modules/google_search.py`
- [ ] Przetestowane fact-checking w content loop

---

Gotowe! Teraz twój fact-checker używa prawdziwych danych z Google 🎉
