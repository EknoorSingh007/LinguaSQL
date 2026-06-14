# 🧠 LLM-Powered SQL Database Interface

This is a Natural Language Interface to a SQL database, powered by a Large Language Model (LLM). It allows users to **create tables**, **insert data**, **query**, **update**, and **delete** records using plain English commands.

---

## ✨ Features

- ✅ Natural language to SQL conversion using LLM
- ✅ SQLite backend for persistence
- ✅ View and edit tables using a web UI
- ✅ Dynamic schema creation via NLQ
- ✅ Query results displayed in a clean tabular format
- ✅ Edit and delete rows from UI
- ✅ Works entirely locally

---

## 📂 Project Structure

```
LLM_DBMS/
│
├── backend/                 # FastAPI backend
│   ├── main.py              # Core API endpoints
│   ├── db/engine.py         # SQL handling (insert, find, delete)
│   ├── llm_interface.py     # Sends prompts to LLM server
│   └── llm_server.py        # Local LLM inference endpoint
│
├── flask_ui/                # Flask + Jinja2 frontend
│   ├── app.py               # Routes and rendering
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── nlq.html
│       └── view.html
│
└── README.md                # This file
```

---

## 🚀 Getting Started

### 1. Set up the environment

```bash
conda create -n tfgpu python=3.10
conda activate tfgpu
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:

```txt
fastapi
uvicorn
flask
jinja2
requests
sqlite3       # comes built-in
transformers
torch
```

---

### 2. Start the LLM server

```bash
cd backend
python llm_server.py
```

This will launch the text generation model (e.g., GPT2 or similar).

---

### 3. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8000
```

---

### 4. Start the Flask frontend

```bash
cd flask_ui
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🧪 Example Prompts

Try these in the **NLQ page**:

- `Create a table called users with name, age, and city.`
- `Insert a user named Alice, 25 years old, from Delhi.`
- `Show all users from Delhi.`
- `Delete all users over 60 years old.`

---

## 💡 How it Works

1. You enter a **natural language prompt**
2. `llm_interface.py` converts it to SQL using the LLM
3. `main.py` parses and executes it using `sqlite3`
4. Results are returned and displayed in a table

---

## 📌 Notes

- This is a prototype, not production-ready.
- You can fine-tune your own LLM to improve prompt-to-SQL accuracy.
- Add authentication if deploying publicly.

---

## 📷 Screenshots

> Add screenshots of the UI here

---

## 📃 License

MIT License
