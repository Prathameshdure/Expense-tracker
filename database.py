import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    Configuration matches default XAMPP/WAMP settings.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",        # Default MySQL user
            password="Rahuldure@123",        # Default password is empty for XAMPP
            database="expense_db"
        )
        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_db_connection(connection, cursor=None):
    """
    Safely closes the database cursor and the connection to prevent memory leaks.
    """
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    except Error as e:
        print(f"Error closing connection: {e}")