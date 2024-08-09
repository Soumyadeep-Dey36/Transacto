import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'host')
    MYSQL_USER = os.getenv('MYSQL_USER', 'user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'user_db')
    PASS = os.getenv('PASS', 'email_pass')