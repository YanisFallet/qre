import os
import sqlite3
import numpy as np
from scipy import stats

def clean_databases_outliers():
    root = "/Users/yanisfallet/sql_server/jinka"
    for database in os.listdir(root):
        target = root + "/" + database
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            for table in tables:
                cursor.execute(f"SELECT id, pm2 FROM {table[0]}")
                data = cursor.fetchall()
                x = np.array([row[0] for row in data], dtype=float)
                y = np.array([row[1] for row in data], dtype=float)
                z_scores = np.abs(stats.zscore(y))
                outliers = np.where(z_scores > 5)[0]
                for i in outliers:
                    cursor.execute(f"DELETE FROM {table[0]} WHERE id = ?", (x[i],))
                conn.commit()

def clean_databases_duplicates():
    root = "/Users/yanisfallet/sql_server/jinka"
    for database in os.listdir(root):
        target = root + "/" + database
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            for table in tables:
                cursor.execute("""
                               DELETE FROM {0} WHERE id NOT IN (
                                   SELECT MIN(id) FROM {0} GROUP BY pm2
                                 )
                               """.format(table[0]))
                conn.commit()

if __name__ == "__main__":
    pass