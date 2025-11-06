"""
Database cleaner module
"""
from pathlib import Path
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:////home/ubuntu/burger-alert/instance/orders.db')

with engine.begin() as conn:
    conn.execute(text("DELETE FROM orders"))
    print("All rows deleted.")
