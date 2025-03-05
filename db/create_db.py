import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
PS_NAME = os.getenv('DB_NAME')
PS_USER = os.getenv('DB_USER')
PS_PASS = os.getenv('DB_PASS')

class DB_Create:

    def __init__(self):
        # подключение к базе данных
        self.connection = psycopg2.connect(database=PS_NAME,
                                           user=PS_USER,
                                           password=PS_PASS,
					   host='localhost')
        self.cursor = self.connection.cursor()
    
    def create_table_category(self):
        with self.connection:
            query = "CREATE TABLE category ( "\
                    "id SERIAL PRIMARY KEY NOT NULL, "\
                    "user_id bigint NOT NULL,"\
                    "title TEXT NOT NULL);"
            self.cursor.execute(query)
            self.connection.commit()
    
    def create_table_spend(self):
        with self.connection:
            query = "CREATE TABLE spend ( "\
                    "id SERIAL PRIMARY KEY NOT NULL, "\
                    "category_id INTEGER NOT NULL, "\
                    "amount INTEGER NOT NULL, "\
                    "user_id bigint, "\
                    "descs text DEFAULT 'empty', "\
                    "datetime date DEFAULT CURRENT_DATE); "
            self.cursor.execute(query)
            self.connection.commit()


if __name__ == '__main__':
    obj = DB_Create()
    obj.create_table_category()
    obj.create_table_spend()
