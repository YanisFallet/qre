import sqlite3 as sql

class UpdateMap:
    
    def __init__(self, path : str, name : str) -> None:
        self.conn = sql.connect(path)
        self.cursor = self.conn.cursor()
        self.name = name
        
    def if_exists(self, name : str) -> bool:
        return self.cursor.execute("SELECT * FROM update_map WHERE name = ?", (name,)).fetchone() is not None
    
    def read_index(self, name) -> int:
        if self.if_exists(name):
            return self.cursor.execute("SELECT index FROM update_map WHERE name = ?", (self.name,)).fetchone()[0]
        else :  
            return 0
    
    def update(self, index : int):
        if self.if_exists(self.name):
            self.cursor.execute("UPDATE update_map SET index = ? WHERE name = ?", (index, self.name))
        else :
            self.cursor.execute("INSERT INTO update_map VALUES (?, ?)", (self.name, index))
        self.conn.commit()
        
    def create_table(self):
        self.cursor.execute("""CREATE TABLE update_map (
            name TEXT, 
            index INTEGER)
        """)
        self.conn.commit()