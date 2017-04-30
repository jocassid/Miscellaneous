#!/usr/bin/env python3

from sqlite3 import connect, Cursor
from random import randint

class UnsafeCursor:
    """Wrapper around sqlite cursor to make it more susceptible to a basic
    SQL injection attack"""
    
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, sql, params=None):
        """Standard cursor.execute only allows a single SQL command to be run"""
        if params is None:
            for statement in sql.split(';'):
                self.cursor.execute(statement)
            return
        print('string parameters get escaped to guard against sql injection')
        print("resulting sql is " + \
            sql.replace("?", "'" + params[0].replace("'", "''") + "'"))
        self.cursor.execute(sql, params)
        
            
    def executemany(self, sql, params):
        self.cursor.executemany(sql, params)
        
    def __iter__(self):
        return self.cursor.__iter__()


with connect(':memory:') as conn:
    
    cursor = conn.cursor()
    
    # This is a hack to make it easy to perform the classic SQL injection hack
    cursor = UnsafeCursor(cursor)
    
    cursor.execute("CREATE TABLE Book(title text, author text)")

    books = [
        ("Pattern Recognition", "William Gibson"),
        ("Hitchhiker's Guide to the Galaxy", "Douglas Adams"),
        ("Witches Abroad", "Terry Pratchett")     
    ]

    cursor.executemany("INSERT INTO Book VALUES(?, ?)", books)
    
    cursor.execute("""CREATE TABLE User(username text, is_admin text)""")
    cursor.execute("""INSERT INTO User VALUES('hacker', 'N')""")
     
    conn.commit()                          

    print("Starting Contents of database")
    sql = "SELECT * FROM Book"
    print(sql)    
    cursor.execute(sql)
    for row in cursor:
        print(row)
        
    sql = "SELECT * FROM User"
    print("\n" + sql)
    cursor.execute(sql)
    for row in cursor:
        print(row)
        
    print("\nA harmless query using author value provided by user") 
    author = 'William Gibson'
    sql = "SELECT * FROM Book WHERE author='" + author + "'"
    print(sql)
    cursor.execute(sql)
    for row in cursor:
        print(row)
        
    print("\nNow the hacker enters a value for author to inject a 2nd statement separated by a semicolon")
    author = "'; UPDATE User SET is_admin='Y' WHERE username='hacker"
    sql = "SELECT * FROM Book WHERE author='" + author + "'"
    print(sql)
    cursor.execute(sql)
    
    print("\nThe hacker now has admin access")
    cursor.execute("SELECT * FROM User")
    for row in cursor:
        print(row)
        
    print("\nReset hacker account back to normal")
    cursor.execute("UPDATE User SET is_admin='N' WHERE username='hacker'")
    cursor.execute("SELECT * FROM User")
    for row in cursor:
        print(row)
    
    print("\nQuery written the safe way")
    cursor.execute(
        "SELECT * FROM Book WHERE author=?",
        (author,))

    
    


