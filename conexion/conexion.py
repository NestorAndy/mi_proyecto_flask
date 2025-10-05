import mysql.connector
from mysql.connector import Error

def connect_mysql(host='localhost', user='root', password='', database='mi_proyecto'):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        if conn.is_connected():
            return conn
    except Error as e:
        print("Error conexión MySQL:", e)
    return None