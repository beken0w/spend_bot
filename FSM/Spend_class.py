import os
import psycopg2
from dotenv import load_dotenv


PERIODS = {
    "curr":("date_trunc('month', current_date)::date",
            "current_date"),
    "1m"  :("date_trunc('month', current_date-interval '1 month')::date", 
            "date_trunc('month', current_date)::date-1"),
    "2m"  :("date_trunc('month', current_date-interval '2 month')::date",
            "date_trunc('month', current_date-interval '1 month')::date-1"),
    "3m"  :("date_trunc('month', current_date-interval '3 month')::date",
            "date_trunc('month', current_date-interval '2 month')::date-1"),
}

load_dotenv()
PS_NAME = os.getenv('DB_NAME')
PS_USER = os.getenv('DB_USER')
PS_PASS = os.getenv('DB_PASS')


class Spend:

    def __init__(self):
        self.connection = psycopg2.connect(database=PS_NAME,
                                           user=PS_USER,
                                           password=PS_PASS,
					   host='localhost')
        self.cursor = self.connection.cursor()

    def __markup_spend(self, rows):
        res = []
        for rec in rows:
            res.append((rec[0], f"📂 {rec[4]}\n"\
                                f"🔤 {rec[2]}\n"\
                                f"💶 {rec[1]}\n"\
                                f"🕖 {rec[3]}"))
        return res


    def __my_markup_report_period(self, rows):
        total = sum([int(rec[1]) for rec in rows])
        output = [f"[ {rec[0]} ]\n"\
                  f"Sum: {int(rec[1])}\n"\
                  f"Avg: {int(rec[2])}\n"\
                  f"Count: {int(rec[3])}\n" for rec in rows]
        return "---------------------\n" + "\n".join(output) + f"\nTotal: {total}"

    def __my_markup_report_category(self, title, d):
        output = f"[ {title} ]\n\n"\
                  "[ TODAY ]\n"\
                  f"Sum: {int(d[0])}\n"\
                  f"Avg: {int(d[1])}\n"\
                  f"Count: {int(d[2])}\n\n"\
                  "[ 7 DAYS ]\n"\
                  f"Sum: {int(d[3])}\n"\
                  f"Avg: {int(d[4])}\n"\
                  f"Count: {int(d[5])}\n\n"\
                  "[ 30 DAYS ]\n"\
                  f"Sum: {int(d[6])}\n"\
                  f"Avg: {int(d[7])}\n"\
                  f"Count: {int(d[8])}\n\n"\
                  "[ 90 DAYS ]\n"\
                  f"Sum: {int(d[9])}\n"\
                  f"Avg: {int(d[10])}\n"\
                  f"Count: {int(d[11])}\n\n"\
                  "[ ALL TIME ]\n"\
                  f"Sum: {int(d[12])}\n"\
                  f"Avg: {int(d[13])}\n"\
                  f"Count: {int(d[14])}\n\n"
        return "---------------------\n" + output

    def update_category(self, new_id, old_id):
        with self.connection:
            query = "UPDATE spend "\
                    "SET category_id = %s "\
                    "where category_id = %s;"
            self.cursor.execute(query, (new_id, old_id))
            self.connection.commit()


    def change_spend(self, data):
        with self.connection:
            query = "UPDATE spend "\
                    "SET category_id = %s "\
                    ", amount = %s "\
                    ", descs = %s "\
                    "where id = %s;"
            self.cursor.execute(query, (data['category_id'],
                                        data['amount'],
                                        data['descs'],
                                        data['id']))
            self.connection.commit()


    def is_exist_by_id(self, data) -> bool:
        with self.connection:
            query = "SELECT id FROM spend "\
                    "WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (data["user_id"], data["id"]))
            id = self.cursor.fetchone()
            return id[0] if id is not None else -1


    def is_exist_by_category_id(self, id) -> bool:
        with self.connection:
            query = "SELECT id FROM spend "\
                    "WHERE category_id = %s;"
            self.cursor.execute(query, (id,))
            id = self.cursor.fetchone()
            return id[0] if id is not None else -1
        

    def insert_spend(self, d):
        with self.connection:
            query = "INSERT INTO spend(category_id, amount, user_id, descs) "\
                    "VALUES (%s, %s, %s, %s);"
            self.cursor.execute(query, (d["category_id"], 
                                        d["amount"], 
                                        d['user_id'], 
                                        d['descs']))
            self.connection.commit()


    def delete_spend(self, d):
        with self.connection:
            query = "DELETE FROM spend "\
                    "WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (d["user_id"], d["id"]))
            self.connection.commit()

    def get_title(self, user_id, category_id) -> bool:
        with self.connection:
            query = "SELECT title FROM category WHERE user_id = %s and id = %s;"
            self.cursor.execute(query, (user_id, category_id))
            title = self.cursor.fetchone()
            return title

    def admstatusers(self) -> bool:
        with self.connection:
            query = "select count(id), user_id from spend "\
                    "group by user_id"
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            return res
        
    def select_spend_by_category(self, d):
        title = self.get_title(d['user_id'], d["category_id"])[0]
        if title:
            with self.connection:
                query = "SELECT "\
                        "coalesce(sum(case when datetime = current_date then amount end),0) as res_sum1, "\
                        "coalesce(avg(case when datetime = current_date then amount end),0) as res_avg1, "\
                        "coalesce(count(case when datetime = current_date then amount end),0) as res_cnt1, "\
                        "coalesce(sum(case when datetime >= current_date-6 then amount end),0) as res_sum7, "\
                        "coalesce(avg(case when datetime >= current_date-6 then amount end),0) as res_avg7, "\
                        "coalesce(count(case when datetime >= current_date-6 then amount end),0) as res_cnt7, "\
                        "coalesce(sum(case when datetime >= current_date-29 then amount end),0) as res_sum30, "\
                        "coalesce(avg(case when datetime >= current_date-29 then amount end),0) as res_avg30, "\
                        "coalesce(count(case when datetime >= current_date-29 then amount end),0) as res_cnt30, "\
                        "coalesce(sum(case when datetime >= current_date-89 then amount end),0) as res_sum90, "\
                        "coalesce(avg(case when datetime >= current_date-89 then amount end),0) as res_avg90, "\
                        "coalesce(count(case when datetime >= current_date-89 then amount end),0) as res_cnt90, "\
                        "coalesce(sum(amount),0) as res_sum_all, "\
                        "coalesce(avg(amount),0) as res_avg_all, "\
                        "coalesce(count(amount),0) as res_cnt_all "\
                        "FROM spend "\
                        "WHERE user_id = %s "\
                        "and category_id = %s; "
                self.cursor.execute(query, (d['user_id'], d["category_id"]))
                curs = self.cursor.fetchall()[0]
                res = len([i for i in curs if i == 0])
                return self.__my_markup_report_category(title, curs) if res != 15 else -1
        else:
            return -1


    def select_spend_by_id(self, id):
        with self.connection:
            query = "SELECT category_id, amount, descs "\
                    "FROM spend WHERE id = %s "
            self.cursor.execute(query, (id,))
            res = self.cursor.fetchall()[0]
            return res


    def select_all_spend(self, d):
        with self.connection:
            query = "SELECT sp.id, sp.amount, sp.descs, sp.datetime, ct.title " \
                    "FROM spend sp " \
                    "left join category ct "\
                    "on ct.id = sp.category_id "\
                    "WHERE sp.user_id = %s " \
                    "ORDER BY sp.id DESC, sp.datetime DESC; "
            self.cursor.execute(query, (d['user_id'],))
            curs = self.cursor.fetchall()
            return self.__markup_spend(curs) if curs else -1


    def select_last_5_spend(self, d):
        with self.connection:
            query = "SELECT sp.id, sp.amount, sp.descs, sp.datetime, ct.title " \
                    "FROM spend sp " \
                    "left join category ct "\
                    "on ct.id = sp.category_id "\
                    "WHERE sp.user_id = %s " \
                    "ORDER BY sp.id DESC, sp.datetime DESC "\
                    "LIMIT 5;"
            self.cursor.execute(query, (d['user_id'],))
            curs = self.cursor.fetchall()
            return self.__markup_spend(curs) if curs else -1


    def select_spend_by_period(self, d):
        with self.connection:
            query = "SELECT ct.title, "\
                    "    sum(sp.amount) as sum_amt, "\
                    "    avg(sp.amount) as avg_amt, "\
                    "    count(1) "\
                    "FROM spend sp "\
                    "left join category ct "\
                    "                on ct.id = sp.category_id "\
                    "WHERE sp.datetime > current_date-%s and "\
                    "sp.datetime <= current_date and sp.user_id = %s "\
                    "group by ct.title; "
            self.cursor.execute(query, (d['period'], d['user_id']))
            curs = self.cursor.fetchall()
            return self.__my_markup_report_period(curs) if curs else -1


    def select_spend_by_period_curr_1m_2m_3m(self, d):
        start, end = PERIODS[d['period']]
        with self.connection:
            query = "SELECT ct.title, "\
                    "    sum(sp.amount) as sum_amt, "\
                    "    avg(sp.amount) as avg_amt, "\
                    "    count(1) "\
                    "FROM spend sp "\
                    "left join category ct "\
                    "                on ct.id = sp.category_id "\
                    f"WHERE sp.datetime BETWEEN {start} and {end} "\
                    "and sp.user_id = %s "\
                    "group by ct.title; "
            self.cursor.execute(query, (d['user_id'],))
            curs = self.cursor.fetchall()
            return self.__my_markup_report_period(curs) if curs else -1
