# LinguaSQL — LLM-Powered SQL Database Interface

A Natural Language Interface to a SQL database, powered by a fine-tuned Large Language Model. Type plain English — LinguaSQL converts it to SQL and executes it against a live SQLite database.

---

## Features

- Natural language to SQL conversion using a fine-tuned LLM
- SQLite backend for persistence
- Schema-aware prompting — model is given the live database schema at inference time
- Web UI to view, filter, and manage tables
- Supports CREATE, INSERT, SELECT, UPDATE, DELETE via natural language
- Runs locally — no external API calls

---

## Project Structure

```
LinguaSQL/
├── backend/
│   ├── main.py              # FastAPI — query endpoints + schema fetching
│   ├── llm_interface.py     # Prompt construction + SQL extraction
│   ├── llm_server.py        # LLM inference server (GPU with 8-bit / CPU fallback)
│   └── db/
│       ├── engine.py        # SQLAlchemy CRUD operations
│       └── database.py      # DB connection
├── flask_ui/
│   ├── app.py               # Flask routes
│   └── templates/           # Jinja2 HTML templates
├── models/
│   └── finetune.py          # Fine-tuning script (Google Colab)
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
```

Run three services simultaneously:

```bash
# Terminal 1 — LLM inference server (port 8080)
python backend/llm_server.py

# Terminal 2 — FastAPI backend (port 8000)
uvicorn backend.main:app --reload --port 8000

# Terminal 3 — Flask frontend (port 5000)
python flask_ui/app.py
```

Visit **http://localhost:5000**

---

## Fine-tuning

The LLM is fine-tuned on a text-to-SQL dataset using parameter-efficient techniques (LoRA + quantization) to reduce compute requirements. Training can be done on a free cloud GPU (e.g. Google Colab T4). A larger base model or more training steps will improve SQL accuracy.

See `models/finetune.py` for the training script.

---

## Example Prompts

```
Create a table called students with name, age, and city.
Insert a student named Eknoor, age 21, from Ganganagar.
Show all students from Ganganagar.
Delete all students older than 30.
```

---

## How It Works

```
Natural language input
        ↓
llm_interface.py  →  builds prompt with live DB schema
        ↓
llm_server.py     →  fine-tuned GPT-2 generates SQL
        ↓
main.py           →  executes SQL on SQLite
        ↓
Flask UI          →  displays results
```

---

## Tech Stack

| Layer       | Technology                         |
|-------------|------------------------------------|
| LLM         | Fine-tuned GPT-2 (HuggingFace)     |
| Fine-tuning | 8-bit quantization + LoRA (PEFT)   |
| Backend     | FastAPI + SQLite                   |
| Frontend    | Flask + Jinja2                     |
| Dataset     | gretelai/synthetic_text_to_sql     |

---

## Collaborators

- Eknoor Singh
- Vipul
- Tarun Gupta
