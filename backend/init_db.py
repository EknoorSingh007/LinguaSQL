# backend/init_db.py
from db.database import engine
from sqlalchemy import MetaData

MetaData().create_all(bind=engine)
print("DB initialized (no static tables).")
