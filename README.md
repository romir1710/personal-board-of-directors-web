# 🌐 Personal Board of Directors — Web Version

A premium, dark-themed web dashboard powered by **FastAPI**, **LangGraph**, and **Google Gemini 2.5 Flash**. Submit any idea, decision, or challenge and receive a structured multi-agent analysis from four distinct AI advisors — displayed in real-time on a beautiful single-page interface.

> 📱 **Looking for the Telegram bot version?**
> See [personal-board-of-directors](https://github.com/romir1710/personal-board-of-directors) for the original `python-telegram-bot` implementation.

---

## 🎭 The Board Members

| Member | Personality | Role |
|---|---|---|
| 🗣 **The Visionary** | Hyperactive, breathless, turbo-charged | Scales every idea into a global empire |
| 🛠 **The Pragmatist** | Slow, pedantic, methodical engineer | Grounds everything in cold, hard reality |
| ⚖️ **The Devil's Advocate** | Brash, blunt, zero diplomatic softening | Hunts for the one flaw that kills the whole plan |
| 📋 **The Chairperson** | Tired, exasperated, ultimately effective | Delivers the final actionable Board Resolution |

---

## 📁 Project Structure

```
personal-board-of-directors-web/
├── main.py           # FastAPI server — POST /api/debate endpoint
├── index.html        # Single-page frontend (served at /)
├── graph.py          # LangGraph state machine (4 board-member nodes)
├── prompts.py        # System prompts for each board member
├── llm_factory.py    # Builds the LLM (Gemini or OpenRouter)
├── pdf_utils.py      # PDF text extraction via pypdf
├── config.py         # Centralised env-var loading
├── requirements.txt  # Python dependencies
├── .env.example      # Template for your .env file
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- A Google AI Studio API key — [aistudio.google.com](https://aistudio.google.com/app/apikey)

### 2. Clone & install

```bash
git clone https://github.com/romir1710/personal-board-of-directors-web.git
cd personal-board-of-directors-web

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure your `.env`

```bash
cp .env.example .env
```

Open `.env` and set:

```env
GOOGLE_API_KEY=AIza...your-key-here
```

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open the app

Navigate to **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🔌 API Reference

### `POST /api/debate`

Accepts `multipart/form-data` with either:
- `text` — a plain string idea/question
- `file` — a PDF file (takes precedence if both provided)

Returns JSON:

```json
{
  "visionary":  "...",
  "pragmatist": "...",
  "advocate":   "...",
  "resolution": "..."
}
```

### `GET /health`

```json
{ "status": "ok", "service": "Personal Board of Directors" }
```

Interactive docs available at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---


## 📄 PDF Support

Upload any text-based PDF via the drag-and-drop interface. The server will:
1. Write the file to a temporary location
2. Extract all text using `pypdf`
3. Pass the extracted text through the Board of Directors graph
4. Delete the temp file immediately after processing

> **Note:** Scanned or image-only PDFs cannot be parsed — use text-based PDFs.

---

## 🏗️ Architecture

```
Browser (index.html)
    │  fetch() POST /api/debate
    ▼
FastAPI (main.py)
    │  asyncio.to_thread()
    ▼
LangGraph (graph.py)
    │
    ├──► visionary_node   ──┐
    ├──► pragmatist_node  ──┼──► chairperson_node
    └──► advocate_node    ──┘
    │
    ▼
JSON response → UI cards
```

---

## 📝 License

MIT
