import pymysql.cursors

class Config:
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Replace with your actual MySQL root password
        'database': 'user_db',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor  # Use the actual class here
    }
    EXCEL_FILE = 'data/staff_feedback.xlsx'