from dotenv import load_dotenv
import os

load_dotenv()  # Tải các biến môi trường từ tệp .env

DATABASE_URI = os.getenv("DATABASE_URI")
DB_PASSWORD = os.getenv("DB_PASSWORD")

username = "admin_user"
password = "P@ssw0rd123!"
