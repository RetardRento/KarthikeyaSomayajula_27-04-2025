import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_engine():
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")
    DB_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=prefer"
    if not DB_URL:
        raise ValueError("Database URL is missing")
    return create_engine(DB_URL)

def fetch_query(conn, query: str):
    return pd.read_sql(query, conn)

def get_max_timestamp(conn, table_name: str):
    query = f"SELECT MAX(timestamp_utc) as max_time FROM {table_name}"
    result = fetch_query(conn, query)
    return pd.to_datetime(result['max_time'][0])

def get_store_ids(conn, table_name: str):
    query = f"SELECT DISTINCT store_id FROM {table_name}"
    return fetch_query(conn, query)

def get_timezones(conn, table_name: str):
    query = f"SELECT * FROM {table_name}"
    return fetch_query(conn, query)

def fetch_data(query, conn):
    """Fetch data from the database."""
    return pd.read_sql(query, conn)
