# Local Agentic On-Page SEO Analyzer & Optimizer

A fully local, free, agentic AI tool that crawls URLs or local HTML files/sitemaps, performs a complete 9+ factor on-page SEO audit, scores the content, and autonomously generates and applies fix recommendations directly to files in-place (with backup creation) or as copyable code snippets.

---

## Key Features

1. **Agentic Planner-Executor Loop**: Analyzes page structure (e.g. blog post vs. product page vs. homepage) and customizes check priorities and scoring weights.
2. **Comprehensive On-Page SEO Checks**:
   - **Title Tag**: Length (50-60 chars), keyword positioning, existence, uniqueness.
   - **Meta Description**: Length (150-160 chars), keyword presence, CTA detection.
   - **Headings Structure**: Single H1, H1→H2→H3 logical hierarchy, keyword presence.
   - **URL Structure**: Length, hyphens, clean query strings.
   - **Content & Readability**: Word count, keyword density (primary + LSI), Flesch reading ease score via `textstat`.
   - **Image Optimization**: Alt text audit, lazy-loading check, WebP format suggestion.
   - **Linking**: Internal link count, anchor text relevance, orphan page detection via `sitemap.xml`.
   - **Technical SEO**: Canonical links, meta robots (`noindex`), schema.org JSON-LD detection, mobile viewport tag, HTTPS check.
   - **Performance & Core Web Vitals**: Local `lighthouse` CLI audit for LCP, CLS, and INP metrics.
3. **Free Keyword & Ranking Research**:
   - Pytrends relative search volume trend integration.
   - Google Autosuggest scraping endpoint (`suggestqueries.google.com`).
   - People Also Ask (PAA) & Related Searches SERP extraction with rate-limiting.
   - Keyword Difficulty proxy formula.
4. **Autonomous In-Place Fix Engine & Self-Critique**:
   - Automatically creates `.bak` file backups in `/backups`.
   - Modifies HTML DOM directly in-place for local files.
   - Displays unified text diffs (`before` vs `after`) on the React dashboard.
   - Self-critique engine validates fix suggestions against character limits and keyword constraints.
5. **Score History & Report Export**:
   - Tracks audit scores over time in local SQLite database (`seo_analyzer.db`).
   - One-click Markdown audit report export.

---

## Tech Stack (100% Free & Open Source)

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (SQLite), BeautifulSoup4, Playwright, pytrends, textstat, lxml
- **Frontend**: React 18, Vite, Lucide Icons, Modern CSS Design System
- **Performance Audit**: Local Lighthouse CLI (`npm install -g lighthouse`)

---

## Local Setup & Quickstart Guide

### Step 1: Clone / Navigate to Workspace
```bash
cd "c:\Users\Naveen kumar\Downloads\Just"
```

### Step 2: Create Python Virtual Environment & Install Backend Dependencies
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r backend/requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application Locally

### Option A: Run Backend Server (FastAPI)
```bash
# From workspace root directory:
python -m uvicorn backend.main:app --reload --port 8000
```
- Interactive API Docs will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Option B: Run Frontend Dashboard (Vite + React)
```bash
# In a separate terminal tab inside /frontend directory:
cd frontend
npm run dev
```
- React Dashboard will open at: [http://localhost:3050](http://localhost:3050)

---

## How to Test

### 1. Test Audit on a Web URL
- Enter `https://example.com` into the dashboard URL field.
- Enter target keyword `seo optimization`.
- Click **RUN AGENT AUDIT**.

### 2. Test Autonomous In-Place Fix on a Local File
- Enter local file path (e.g. `c:\Users\Naveen kumar\Downloads\Just\sample.html`).
- Enter keyword `on-page seo guide`.
- Click **RUN AGENT AUDIT**.
- Click **Apply In-Place Fix** next to any failed check.
- Observe the created `.bak` file in `/backups` and view the unified diff in the pop-up modal!

---

## Running Unit Tests
```bash
python -m pytest tests/
```
