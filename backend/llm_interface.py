import requests

LLM_URL = "http://localhost:8080/generate"

def parse_prompt(prompt: str, schema: str = "") -> str:
    schema_section = f"Database schema:\n{schema}\n\n" if schema else ""
    template = (
        "You are a helpful assistant that converts natural language into valid SQLite SQL queries.\n\n"
        f"{schema_section}"
        f"Prompt: {prompt}\n"
        "SQL:"
    )

    response = requests.post(LLM_URL, json={
        "inputs": template,
        "parameters": {"max_new_tokens": 100, "do_sample": False}
    })
    raw = response.json()["generated_text"]
    return extract_sql(raw)

import re

SQL_KEYWORDS = ("SELECT", "INSERT", "CREATE", "UPDATE", "DELETE", "DROP", "ALTER")

def extract_sql(text: str) -> str:
    lines = text.strip().splitlines()
    for line in lines:
        clean = line.strip()

        # Strip Python list brackets e.g. ['SELECT ...'] → SELECT ...
        if clean.startswith("['") and "']" in clean:
            clean = clean[2 : clean.rfind("']")].strip()
        elif clean.startswith('["') and '"]' in clean:
            clean = clean[2 : clean.rfind('"]')].strip()

        # Strip "SQL: " prefix if model echoes it
        if clean.upper().startswith("SQL:"):
            clean = clean[4:].strip()

        if clean.upper().startswith(SQL_KEYWORDS):
            return post_process(clean)

    raise ValueError("No valid SQL found in LLM output.")


def post_process(sql: str) -> str:
    # Take only the first statement — model often repeats the same INSERT many times
    sql = sql.split(";")[0].strip()

    # Normalize table name to lowercase so "Student" matches "students"
    sql = re.sub(r'(INSERT\s+INTO\s+)(\w+)',
                 lambda m: m.group(1) + m.group(2).lower(), sql, flags=re.IGNORECASE)
    sql = re.sub(r'(UPDATE\s+)(\w+)',
                 lambda m: m.group(1) + m.group(2).lower(), sql, flags=re.IGNORECASE)
    sql = re.sub(r'(FROM\s+)(\w+)',
                 lambda m: m.group(1) + m.group(2).lower(), sql, flags=re.IGNORECASE)
    sql = re.sub(r'(DELETE\s+FROM\s+)(\w+)',
                 lambda m: m.group(1) + m.group(2).lower(), sql, flags=re.IGNORECASE)

    # Fix INSERT column/value count mismatch
    insert_m = re.match(
        r'(INSERT\s+INTO\s+\w+\s*\()([^)]+)(\)\s*VALUES\s*\()([^)]+)(\))',
        sql, re.IGNORECASE
    )
    if insert_m:
        prefix   = insert_m.group(1)
        col_str  = insert_m.group(2)
        mid      = insert_m.group(3)
        val_str  = insert_m.group(4)

        columns = [c.strip() for c in col_str.split(",") if c.strip()]
        values  = _split_values(val_str)

        # Match lengths — trim whichever side is longer
        n = min(len(columns), len(values))
        columns, values = columns[:n], values[:n]

        sql = f"{prefix}{', '.join(columns)}{mid}{', '.join(values)})"

    # Fix CREATE TABLE: deduplicate repeated columns + close missing parenthesis
    if re.match(r'CREATE\s+TABLE', sql, re.IGNORECASE) and "(" in sql:
        paren_pos    = sql.index("(")
        prefix       = sql[:paren_pos + 1]
        columns_part = sql[paren_pos + 1:].rstrip(");,").strip()

        seen, unique_cols = set(), []
        for col in columns_part.split(","):
            col = col.strip()
            if not col:
                continue
            name = col.split()[0].lower()
            if name not in seen:
                seen.add(name)
                unique_cols.append(col)

        sql = prefix + ", ".join(unique_cols) + ")"

    return sql + ";"


def _split_values(val_str: str) -> list:
    """Split a VALUES string respecting single/double quoted strings."""
    values, current, in_quote, quote_char = [], "", False, None
    for ch in val_str:
        if in_quote:
            current += ch
            if ch == quote_char:
                in_quote = False
        elif ch in ("'", '"'):
            in_quote, quote_char, current = True, ch, current + ch
        elif ch == ",":
            values.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        values.append(current.strip())
    return values
