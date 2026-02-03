# 🗺️ AI Content Factory - ROADMAP

**Projekt:** AI Content Factory - LinkedIn Post Generator
**Owner:** Łukasz Rymkowski / AgencjaOP
**Repo:** https://github.com/Brodno/AI-Content-Factory

---

## 🎯 WIZJA

Rozwijalna aplikacja SaaS dla content creatorów w B2B/Industrial:
- Prototyp → MVP → SaaS
- Możliwość sprzedaży jako white-label dla firm
- Cel: $5-10k MRR w 12 miesięcy

---

## 📍 OBECNY STAN

**Wersja:** v0.1.0 (Prototyp)
**Status:** ✅ Working Baseline
**Tech Stack:** Python + Streamlit + Gemini AI
**Deployment:** Localhost

### ✅ Co działa:
- Content Quality Loop (Generator + Evaluator + Improver + Fact-checker)
- Target: 95+ quality score
- Streamlit web UI
- 100 topics bank (tematy100.md)
- Image prompt generator (Industrial Raw Style)
- Save to file

### ❌ Co brakuje:
- Filtrowanie użytych tematów
- System statusów (Draft/Scheduled/Published)
- Kalendarz publikacji
- Historia i statystyki w UI
- Hosting online (obecnie tylko localhost)

---

## 🚀 FAZA 1: Prototyp v0.x (TERAZ - 2-4 tygodnie)

**Tech:** Streamlit + Python (bez zmian)
**Cel:** Testować funkcjonalność, dopracować UX, zdobyć feedback

### v0.2.0 - Content Queue System ⏳ IN PROGRESS
**ETA:** 1-2 dni

**Features:**
1. **System statusów postów**
   - 🟡 Draft (wygenerowany, do akceptacji)
   - 🔵 Scheduled (zaakceptowany, przypisana data)
   - 🟢 Published (opublikowany na LinkedIn)
   - ⚫ Archived (zarchiwizowany)

2. **Kolejka publikacji**
   - Tabela z zaplanowanymi postami
   - Przypisanie daty publikacji (date picker)
   - Sortowanie po dacie
   - Akcje: Edit, Publish, Delete

3. **Sidebar - Historia & Statystyki**
   - Last 10 publikacji (z linkami)
   - Statystyki:
     - Tematy wykorzystane: X/100
     - Posty scheduled: X
     - Posty published: X
     - Średni quality score
   - ⚠️ Alert: "Zostało tylko X tematów!"

4. **Filtrowanie tematów**
   - Losowanie pokazuje TYLKO niewykorzystane tematy
   - Możliwość "cofnięcia" publikacji (temat wraca do puli)
   - Integracja z INDEX_POSTOW.md

5. **UI/UX Improvements**
   - Custom CSS theme (ładniejszy design)
   - Better layouts (cards, colors, spacing)
   - Loading indicators
   - Success/error toasts

**Files to modify:**
- `code/app.py` - główny UI
- `code/modules/history_checker.py` - tracking tematów
- `code/modules/queue_manager.py` - NEW (zarządzanie kolejką)

---

### v0.3.0 - Performance & Polish
**ETA:** 1 tydzień

**Features:**
1. **Performance**
   - Caching (st.cache_data dla kontekstu)
   - Lazy loading tematów
   - Async fact-checking (szybsze generowanie)

2. **Export & Backup**
   - Eksport kolejki do CSV/Excel
   - Backup postów (JSON)
   - Import tematów z CSV

3. **Better prompts**
   - Refine generator prompts
   - Better fact-checking (więcej źródeł)
   - Quality score tweaks

**Deployment:**
- ✅ Deploy na Streamlit Cloud (FREE)
- URL: `https://ai-content-factory.streamlit.app`

---

### v0.4.0 - LinkedIn Integration (OPCJONALNE)
**ETA:** 2 tygodnie

**Features:**
1. **LinkedIn API**
   - OAuth authentication
   - Auto-publish scheduled posts
   - Pobieranie statystyk (views, reactions)

2. **Scheduler**
   - Cron job (publikacja o określonej godzinie)
   - Email notifications (post opublikowany)

**Tech:**
- LinkedIn API (python-linkedin-v2)
- APScheduler (cron jobs)

---

### v0.5.0 - Multi-user Ready
**ETA:** 2 tygodnie

**Features:**
1. **User Management**
   - Login/Password (streamlit-authenticator)
   - Każdy user osobny folder danych
   - User profiles (nazwa, firma, logo)

2. **Admin Panel**
   - Zarządzanie użytkownikami
   - Statystyki wszystkich userów
   - Usage limits (100 postów/msc na usera)

**Deployment:**
- Railway ($10/msc) - więcej RAM, szybsze

---

## 🎯 FAZA 2: MVP v1.0 (3-6 miesięcy)

**Tech:** Wciąż Streamlit (dopracowane)
**Cel:** 5-10 płacących klientów, $500-1000 MRR

### v1.0.0 - Production Ready
**Features:**
1. **Billing & Subscriptions**
   - Stripe integration
   - Plany: Solo ($29), Team ($99), Agency ($299)
   - Usage tracking & limits

2. **White-label**
   - Custom branding (logo, kolory)
   - Custom domain (client.agencjaop.pl)

3. **Analytics Dashboard**
   - LinkedIn stats tracking
   - Best performing posts
   - Topic recommendations

4. **Multi-platform**
   - LinkedIn (done)
   - Twitter/X support
   - Facebook support

**Deployment:**
- DigitalOcean ($20/msc) lub Railway Pro ($20/msc)
- Custom domain: contentfactory.agencjaop.pl
- SSL certificate

---

## 🚀 FAZA 3: SaaS v2.0 (6-12 miesięcy)

**Tech:** React + FastAPI + PostgreSQL (PRZEPISANIE)
**Cel:** 50+ klientów, $5-10k MRR

### Przepisanie na profesjonalny stack:

**Frontend:**
- React + Next.js (TypeScript)
- Tailwind CSS
- Shadcn/ui components
- Vercel deployment

**Backend:**
- FastAPI (Python) - REST API
- PostgreSQL (database)
- Redis (caching, queue)
- Railway/AWS deployment

**Features:**
- Multi-tenant architecture
- Advanced analytics
- API dla developerów
- Mobile app (React Native)
- Integrations marketplace (Zapier, Make)

**Pricing (przykład):**
- Solo: $29/msc (1 user, 100 posts/msc)
- Team: $99/msc (5 users, 500 posts/msc)
- Agency: $299/msc (unlimited)
- Enterprise: Custom pricing

---

## 📊 METRYKI SUKCESU

### v0.x (Prototyp)
- [ ] 3+ beta testerów (feedback)
- [ ] 50+ postów wygenerowanych
- [ ] <3s średni czas generowania
- [ ] 90%+ quality score average

### v1.0 (MVP)
- [ ] 5 płacących klientów
- [ ] $500+ MRR
- [ ] <5% churn rate
- [ ] 4.5+ rating (user feedback)

### v2.0 (SaaS)
- [ ] 50+ aktywnych klientów
- [ ] $5k+ MRR
- [ ] <2% churn rate
- [ ] 10+ integration partners

---

## 🛠️ TECH DEBT & NICE-TO-HAVE

### Low priority (może kiedyś):
- [ ] Tematy200.md, Tematy300.md (więcej tematów)
- [ ] Multi-language support (EN, DE, FR)
- [ ] AI voice-over (video posts)
- [ ] Competitor analysis (scraping LinkedIn)
- [ ] Content calendar view (Google Calendar style)
- [ ] Collaboration (team comments/reviews)
- [ ] Version control (post revisions)
- [ ] A/B testing (multiple variants)

---

## 📅 TIMELINE

| Milestone | ETA | Status |
|-----------|-----|--------|
| v0.1.0 - Baseline | ✅ 2026-02-03 | Done |
| v0.2.0 - Queue System | 2026-02-05 | In Progress |
| v0.3.0 - Performance | 2026-02-12 | Planned |
| v0.4.0 - LinkedIn API | 2026-02-26 | Optional |
| v0.5.0 - Multi-user | 2026-03-12 | Planned |
| v1.0.0 - Production | 2026-06-01 | Goal |
| v2.0.0 - SaaS | 2027-01-01 | Vision |

---

## 🤝 CONTRIBUTORS

- **Łukasz Rymkowski** - Owner, Product
- **Claude Sonnet 4.5** - AI Development Partner

---

**Last updated:** 2026-02-03
**Next review:** Co 2 tygodnie (aktualizacja statusu)
