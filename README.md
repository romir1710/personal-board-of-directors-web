# 🌐 Personal Board of Directors — Web Version

A premium, dark-themed web dashboard powered by **FastAPI**, **LangGraph**, and **multi-provider AI models**. Submit any idea, decision, or challenge and receive a structured multi-agent analysis from four distinct AI advisors — displayed in real-time on a beautiful single-page interface.

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

## ✨ Key Features

- **Multi-Agent AI Deliberation** — Four distinct AI personalities analyse your idea in parallel and deliver a structured Board Resolution.
- **User Authentication** — Sign in with email to save and resume your board sessions across devices. Session history is persisted via Supabase.
- **Bring Your Own API Key** — Use your own API key from **Gemini**, **OpenAI**, **Claude (Anthropic)**, or **OpenRouter** for unlimited turns and your preferred model.
- **Default Model (No Key Required)** — Try the board without an API key, limited to 5 total turns on a default model.
- **PDF Upload & Analysis** — Attach any text-based PDF document for the board to analyse alongside your question.
- **Session History & Sidebar** — Browse, resume, and manage past board sessions from the sidebar.
- **Parallelised Advisor Responses** — The three advisors run concurrently for significantly faster deliberation times.
- **Premium Dark UI** — A carefully crafted obsidian and champagne-gold design with smooth animations, a director carousel, and glassmorphism effects.

---

## 📁 Project Structure

```
personal-board-of-directors-web/
├── main.py           # FastAPI server — POST /api/debate endpoint
├── index.html        # Single-page frontend (served at /)
├── graph.py          # LangGraph state machine (4 board-member nodes)
├── prompts.py        # System prompts for each board member
├── llm_factory.py    # Builds the LLM (Gemini, OpenAI, Claude, or OpenRouter)
├── pdf_utils.py      # PDF text extraction via pypdf
├── config.py         # Centralised env-var loading
├── requirements.txt  # Python dependencies
├── .env.example      # Template for your .env file
└── .gitignore
```

---

## 🚀 Quick Start

You may of course just use the Live Link from the "About" section to directly access the Web App. Assuming you would like to run it locally, here's how:

### 1. Prerequisites

- Python 3.11+
- A Google AI Studio API key — [aistudio.google.com](https://aistudio.google.com/app/apikey) (or any supported provider key)

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

## 🔑 API Key Support

The board supports multiple AI providers. You can enter your own API key from the sidebar after signing in:

| Provider | Model Used |
|---|---|
| **Google Gemini** | Gemini 2.5 Flash |
| **OpenAI** | GPT-4o |
| **Anthropic (Claude)** | Claude Sonnet |
| **OpenRouter** | Any model via OpenRouter relay |

> **Note:** If no API key is provided, the board runs on a default model with a limit of 5 total turns. Responses may not always be accurate and may occasionally return errors.

---

## 🔌 API Reference

### `POST /api/debate`

Accepts `multipart/form-data` with either:
- `text` — a plain string idea/question
- `file` — a PDF file (takes precedence if both provided)

Optional headers for custom API keys:
- `X-Api-Provider` — one of `gemini`, `openai`, `claude`, `openrouter`
- `X-Api-Key` — your API key for the chosen provider

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

Upload any text-based PDF via the attach button. The server will:
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
    ├──► pragmatist_node  ──┼──► chairperson_node  (fan-out / fan-in)
    └──► advocate_node    ──┘
    │
    ▼
JSON response → UI cards
```

The three advisor nodes run **in parallel** using `ThreadPoolExecutor` for significantly faster response times.

---

## 📝 License

MIT License

Copyright (c) 2025 Romir

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
