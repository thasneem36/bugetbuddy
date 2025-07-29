import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'your_mysql_username'
    MYSQL_PASSWORD = 'your_mysql_password'
    MYSQL_DB = 'expense_tracker'
