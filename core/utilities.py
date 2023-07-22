import os
import sqlite3
import numpy as np
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w', filename='cleaning.log')

def clean_databases_outliers(feature):
    root = "/Users/yanisfallet/sql_server/jinka"
    for database in os.listdir(root):
        target = root + "/" + database
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            for table in tables:
                cursor.execute(f"SELECT id, {feature} FROM {table[0]}")
                data = cursor.fetchall()
                x = np.array([row[0] for row in data], dtype=float)
                y = np.array([row[1] for row in data], dtype=float)
                z_scores = np.abs(stats.zscore(y))
                outliers = np.where(z_scores > 6)[0]
                for i in outliers:
                    logging.info(f"Deleting {x[i]} from {table[0]}")
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
                                   SELECT MIN(id) FROM {0} GROUP BY pm2, sendDate
                                 )
                               """.format(table[0]))
                logging.info(f"Deleted {cursor.rowcount} duplicates from {table[0]}")
                conn.commit()

def clean_source(source : str):
    root = "/Users/yanisfallet/sql_server/jinka"
    for database in os.listdir(root):
        target = root + "/" + database
        with sqlite3.connect(target) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            for table in tables:
                cursor.execute("""
                    DELETE FROM {0} WHERE source = '{1}'
                """.format(table[0], source))
                logging.info(f"Deleted {cursor.rowcount} ads from {table[0]} of source {source}")

if __name__ == "__main__":
    clean_databases_outliers("pm2")
    clean_databases_duplicates()
    clean_source('morningcroissant')