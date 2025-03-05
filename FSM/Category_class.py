import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
PS_NAME = os.getenv('DB_NAME')
PS_USER = os.getenv('DB_USER')
PS_PASS = os.getenv('DB_PASS')


class Category:

    def __init__(self):
        self.connection = psycopg2.connect(database=PS_NAME,
                                           user=PS_USER,
                                           password=PS_PASS,
					   host='localhost')
        self.cursor = self.connection.cursor()

    def insert_category(self, data):
        with self.connection:
            query = "INSERT INTO category(user_id, title) VALUES (%s, %s);"
            self.cursor.execute(query, (data["user_id"], data["title"]))
            self.connection.commit()

    def update_category(self, data):
        with self.connection:
            query = "update category set title = %s where user_id = %s and id = %s;"
            self.cursor.execute(query, (data["new_title"], data["user_id"], data["id"]))
            self.connection.commit()

    def delete_category(self, data):
        with self.connection:
            query = "DELETE FROM category WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (data["user_id"], data["id"]))
            self.connection.commit()

    def select_categories(self, user_id):
        with self.connection:
            query = "SELECT * FROM category WHERE user_id = %s ORDER BY id DESC;"
            self.cursor.execute(query, (user_id,))
            res = self.cursor.fetchall()
            return res

    def get_title(self, data) -> bool:
        with self.connection:
            query = "SELECT title FROM category WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (data["user_id"], data["id"]))
            title = self.cursor.fetchone()
            return title[0] if title is not None else -1
        
    def is_exist_by_title(self, data) -> bool:
        with self.connection:
            query = "SELECT id FROM category WHERE user_id = %s and upper(title) = upper(%s);"
            self.cursor.execute(query, (data["user_id"], data["title"]))
            id = self.cursor.fetchone()
            return id[0] if id is not None else -1

    def is_exist_by_id(self, data) -> bool:
        with self.connection:
            query = "SELECT id FROM category WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (data["user_id"], data["id"]))
            id = self.cursor.fetchone()
            return id[0] if id is not None else -1


if __name__ == '__main__':
    obj = Category()
    print(str(obj.select_categories))
