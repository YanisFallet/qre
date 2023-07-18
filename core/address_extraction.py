import re
import os
import pandas as pd
import sqlite3 as sql

pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

def load_description_where_lat_none():
    """
    Loads the description of the properties where the latitude and longitude are None
    """
    root = "/Users/yanisfallet/sql_server/jinka"
    description = pd.DataFrame(columns=['description'])
    for database in os.listdir(root):
        conn = sql.connect(os.path.join(root, database))
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        for table in tables['name']:
            df = pd.read_sql_query("SELECT description FROM {0} WHERE lat IS NULL".format(table), conn)
            description = pd.concat([description, df], axis = 0)
    return description

def load_all_description():
    root = "/Users/yanisfallet/sql_server/jinka"
    description = pd.DataFrame(columns=['description'])
    for database in os.listdir(root):
        conn = sql.connect(os.path.join(root, database))
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        for table in tables['name']:
            df = pd.read_sql_query("SELECT description FROM {0}".format(table), conn)
            description = pd.concat([description, df], axis = 0)
    return description

def load_description_where_lat_not_none():
    root = "/Users/yanisfallet/sql_server/jinka"
    description = pd.DataFrame(columns=['description'])
    for database in os.listdir(root):
        conn = sql.connect(os.path.join(root, database))
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        for table in tables['name']:
            df = pd.read_sql_query("SELECT description FROM {0} WHERE lat IS NOT NULL".format(table), conn)
            description = pd.concat([description, df], axis = 0)
    return description

def extract_address(text):
    # Define the list of keywords to look for
    keywords = ['quartier', 'rue', 'cours', 'allée', 'avenue', 'boulevard', 'place', 'quais', 'arrêt', 'quai', 'impasse', 'voie', 'secteur']
    
    # Convert all keywords to lowercase
    keywords = [keyword.lower() for keyword in keywords]
    
    # Define the regular expression pattern to match the keywords
    pattern_keywords = r"\b(?:{})\b".format('|'.join(keywords))
    
    # Use the regular expression to find all matches in the text
    matches = re.finditer(pattern_keywords, text, re.IGNORECASE)
    
    addresses = []
    # Iterate over all matches
    for match in matches:
        # Get the start position of the match
        start = match.start()
        
        not_valid_address = True
        address = ''
        i = 0
        counter = 0
        max_iter = 10
        while not_valid_address and max_iter > 0:
            words = text[start:].split()[0:4+(i*3)]
            
            flag = False
            
            for word in words:
                counter += 1
                # Check if the word starts with a capital letter
                if word[0].isupper():
                    address = ' '.join(text[start:].split()[0:counter])
                    i += 1
                    flag = True
                if word[-1] in [',', ':', '.', '\n', "-", '*', ';', '?'] or word[0] in [',', ':', '.', '\n', '-', '*', ';', '?']:
                    not_valid_address = False
                    break
            
            
            if flag :
                not_valid_address = False
            max_iter -= 1
        if address :        
            addresses.append(re.split(f"[.,;:]", address)[0])
    return addresses


if __name__ == "__main__":
    description = load_description_where_lat_none()
    description["addresses_v2"] = description['description'].apply(extract_address)
    print(description[description['addresses_v2'].apply(lambda x: len(x) > 0)].shape[0] / description.shape[0])
    print(description)
    