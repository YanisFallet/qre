import numpy as np
import sqlite3 as sql

class Point :
    def __init__(self, lat = None, lng = None):
        self.lat = lat
        self.lng = lng
    
    def __repr__(self):
        return f"Point({self.lat}, {self.lng})"
    
class Grid:
    def __init__(self, grid_format : tuple ,list_points : list[tuple]):
        self.grid_format = grid_format
        self.origin = Point(min(list_points, key = lambda p : p[0])[0], min(list_points, key = lambda p : p[1])[1])
        self.max_lat = Point(max(list_points, key = lambda p : p[0])[0], self.origin.lng)
        self.max_lng = Point(self.origin.lat, max(list_points, key = lambda p : p[1])[1])
        
        self.axis_lat = np.linspace(self.origin.lat, self.max_lat.lat, grid_format[0])
        self.axis_lng = np.linspace(self.origin.lng, self.max_lng.lng, grid_format[1])
        
    def __repr__(self):
        return f"Grid({self.origin}, {self.grid_format})"
    
    def place_one_point(self, point : tuple) -> int:
        i = 0
        while  i < self.axis_lat.shape[0] and point[0] >= self.axis_lat[i]:
            j = 0
            while  j < self.axis_lng.shape[0] and point[1] >= self.axis_lng[j]:
                j += 1
            i += 1
        return (i-1)*self.grid_format[1] + (j-1)

    def populate_the_grid(self, list_points : list[tuple]):
        return [self.place_one_point(point) for point in list_points]
        
def distance(p : tuple):
    return np.sqrt(p[0 ]**2 + p.y**2)


if __name__ == "__main__":
    conn = sql.connect("/Users/yanisfallet/sql_server/jinka/database_Bourgoin_Jallieu.db")
    c = conn.cursor()
    data = c.execute("SELECT lat, lng FROM ads_Bourgoin_Jallieu_for_invest WHERE lat != 'None'").fetchall()
    print(np.array(data).shape)
    g = Grid((2, 5), data)
    print(np.unique(g.populate_the_grid(data), return_counts=True))