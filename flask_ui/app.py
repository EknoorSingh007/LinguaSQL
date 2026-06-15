from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from math import ceil

API = "http://localhost:8000"  # FastAPI backend

app = Flask(__name__)
app.secret_key = "linguasql-secret"

@app.route("/")
def index():
    try:
        tables = requests.get(f"{API}/collections").json()
    except Exception:
        tables = []
    return render_template("index.html", collections=tables)

@app.route("/view/<collection>")
def view(collection):
    col_resp = requests.get(f"{API}/columns/{collection}")
    if col_resp.status_code != 200:
        flash(f"Failed to load schema for {collection}", "error")
        return redirect(url_for("index"))
    columns_dict = col_resp.json()
    columns = list(columns_dict.keys())

    prompt = f"SELECT * FROM {collection};"
    resp = requests.post(f"{API}/query", json={"prompt": prompt})
    data = resp.json()
    documents = data.get("result", []) if resp.status_code == 200 and data.get("status") == "success" else []

    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 20))
    total = len(documents)
    pages = ceil(total / limit) if limit else 1
    page = (skip // limit) + 1 if limit else 1
    docs_page = documents[skip: skip + limit]

    return render_template("view.html", collection=collection, columns=columns, documents=docs_page,
                           skip=skip, limit=limit, total=total, page=page, pages=pages)

@app.route("/nlq", methods=["GET", "POST"])
def nlq():
    prompt = ""
    result = None
    rows_affected = None
    error = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            try:
                resp = requests.post(f"{API}/query", json={"prompt": prompt})
                data = resp.json()
                if resp.status_code == 200 and data.get("status") == "success":
                    result = data.get("result")
                    rows_affected = data.get("rows_affected")
                else:
                    error = data.get("detail") or data.get("error") or resp.text
            except Exception as e:
                error = str(e)

    return render_template("nlq.html", prompt=prompt, result=result,
                           rows_affected=rows_affected, error=error)

@app.route("/insert/<collection>")
def insert(collection):
    flash("Use the NLQ page to insert records.", "info")
    return redirect(url_for("nlq"))

@app.route("/schema/<collection>")
def edit_schema(collection):
    flash("Use the NLQ page to define schemas.", "info")
    return redirect(url_for("nlq"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
