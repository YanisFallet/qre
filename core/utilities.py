import os
import sqlite3
import numpy as np
from scipy import stats
import logging
from tqdm import tqdm

def connect_to_database(func):
    def wrapper(*args, **kwargs):
        root = "/Users/yanisfallet/sql_server/jinka"
        for database in tqdm(os.listdir(root)):
            with sqlite3.connect(os.path.join(root, database)) as conn:
                cursor = conn.cursor()
                tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                for table in tables:
                    func(cursor, table[0], *args, **kwargs)
                conn.commit()
    return wrapper

@connect_to_database
def clean_databases_outliers(cursor, table_name, feature):
    cursor.execute(f"SELECT id, {feature} FROM {table_name}")
    data = cursor.fetchall()
    x = np.array([row[0] for row in data], dtype=float)
    y = np.array([row[1] for row in data], dtype=float)
    z_scores = np.abs(stats.zscore(y))
    outliers = np.where(z_scores > 6)[0]
    for i in outliers:
        logging.info(f"Deleting {x[i]} from {table_name}")
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (x[i],))

@connect_to_database
def clean_databases_duplicates(cursor, table_name):
    cursor.execute(f"""
        DELETE FROM {table_name} WHERE id NOT IN (
            SELECT MIN(id) FROM {table_name} GROUP BY pm2, sendDate
        )
    """)
    logging.info(f"Deleted {cursor.rowcount} duplicates from {table_name}")


@connect_to_database
def clean_source(cursor, table_name, source):
    cursor.execute(f"""
        DELETE FROM '{table_name}' WHERE source = '{source}'
    """)
    logging.info(f"Deleted {cursor.rowcount} ads from {table_name} of source {source}")

if __name__ == "__main__":
    clean_databases_outliers("pm2")
    clean_databases_duplicates()
    clean_source('morningcroissant')