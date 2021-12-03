import mysql.connector


class AbstractDataBase:
    DB_HOST = environ["DB_HOST"]
    DB_PORT = environ["DB_PORT"]
    DB_USER = environ["DB_USER"]
    DB_PASSWORD = environ["DB_PASS"]
    DB_NAME = environ["DB_NAME"]

    connection = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
                                         database=DB_NAME)


class UserDB(AbstractDataBase):
    def is_user_exist(self, user_id):
        sql = "SELECT * FROM users WHERE user_id=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            if cursor.fetchone() is None:
                return False
            else:
                return True

    def add_user(self, first_name, second_name, user_id):
        sql = "INSERT INTO users(first_name, second_name, user_id, registr_date)\
              SELECT * FROM (SELECT %s f_name, %s s_name, %s u_id, current_date()) AS tmp\
              WHERE NOT EXISTS(SELECT user_id FROM users WHERE user_id = tmp.u_id);"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (first_name, second_name, user_id))
            self.connection.commit()

    def add_city(self, user_id, city: str):
        sql = "UPDATE users SET city=%s WHERE user_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (city, user_id))
            self.connection.commit()

    def add_gender(self, user_id, gender: int):
        sql = "UPDATE users SET gender=%s WHERE user_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (gender, user_id))
            self.connection.commit()

    def add_age(self, user_id, age: int):
        sql = "UPDATE users SET age=%s WHERE user_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (age, user_id))
            self.connection.commit()

    def get_age(self, user_id):
        sql = "SELECT age FROM users WHERE user_id=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()

    def get_gender(self, user_id):
        sql = "SELECT gender FROM users WHERE user_id=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchone()

    def get_users_info(self):
        sql = "SELECT user_id,first_name, second_name, city, gender, age, registr_date FROM users ORDER BY registr_date"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def ban_user(self, user_id):
        sql = "UPDATE users SET is_baned=1 WHERE user_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            self.connection.commit()

    def unban_user(self, user_id):
        sql = "UPDATE users SET is_baned=0 WHERE user_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            self.connection.commit()


class ChatDB(AbstractDataBase):
    def add_chat(self, chat_id, title, gender):
        sql1 = "INSERT INTO chats(chat_id, title, gender) VALUES (%s, %s, %s)"
        sql2 = "UPDATE burpee_bot.chats SET title=%s, gender=%s  WHERE chat_id =%s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql1, (chat_id, title, gender))
            except mysql.connector.errors.IntegrityError:
                cursor.execute(sql2, (title, gender, chat_id))
            self.connection.commit()

    def get_all_chats(self) -> list:
        sql = "SELECT * FROM chats"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


class RecordDB(AbstractDataBase):
    def create_record(self, contribution, exercise_type_id, user_id, chat_id):
        sql = "INSERT INTO records (contribution, exercise_type_id, user_id, chat_id) VALUES (%s, %s, %s, %s)"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (contribution, exercise_type_id, user_id, chat_id))
            self.connection.commit()

    def get_common_user_result(self, user_id, exercise_type_id):
        sql = "SELECT SUM(contribution) FROM records WHERE user_id=%s and exercise_type_id=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id, exercise_type_id))
            return cursor.fetchall()

    def get_common_result(self, exercise_type_id):
        sql = "SELECT SUM(contribution) FROM records WHERE exercise_type_id=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (exercise_type_id,))
            return cursor.fetchall()

    def get_top(self, exercise_type_id, gender):
        sql = "SELECT r.user_id,u.first_name, u.second_name," \
              " SUM(contribution) AS c FROM records r, users u " \
              "WHERE exercise_type_id = %s " \
              "AND r.user_id = u.user_id " \
              "AND u.gender = %s " \
              "GROUP BY user_id " \
              "ORDER BY c DESC LIMIT 10"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (exercise_type_id, gender))
            return cursor.fetchall()

    def get_user_with_placement(self, exercise_type_id, gender, user_id) -> list:
        sql = "SELECT  r_num,fn,sn,c FROM(SELECT r.user_id as id," \
              "u.first_name as fn, u.second_name as sn,SUM(contribution) AS c, " \
              "row_number() over(ORDER BY SUM(contribution) DESC) as r_num " \
              "FROM records r, users u WHERE exercise_type_id = %s " \
              "AND r.user_id = u.user_id AND u.gender = %s " \
              "GROUP BY id ORDER BY c DESC) b " \
              "WHERE id = %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (exercise_type_id, gender, user_id))
            return cursor.fetchone()

    def delete_records_by_ex_type(self, exercise_type_id):
        sql = "DELETE FROM records WHERE exercise_type_id = %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (exercise_type_id,))
            self.connection.commit()
            return cursor.rowcount

    def delete_record_by_id(self, record_id):
        sql = "DELETE FROM records WHERE record_id = %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (record_id,))
            self.connection.commit()
            return cursor.rowcount

    def update_record(self, record_id, new_value):
        sql = "UPDATE records SET contribution=%s WHERE record_id = %s;"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (new_value, record_id))
            self.connection.commit()
            return cursor.rowcount

    def get_ex_type_buy_record_id(self, record_id):
        sql = "SELECT exercise_type_id FROM records WHERE record_id = %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (record_id,))
            return cursor.fetchone()

    def show_user_records(self, user_id, row_limit):
        sql = " SELECT record_id, u.first_name, u.second_name, r.exercise_type_id ," \
              " r.contribution, gender, u.user_id " \
              "FROM records r ,users u " \
              "WHERE r.user_id = u.user_id " \
              "AND r.user_id = %s " \
              "ORDER BY `date` DESC " \
              "LIMIT %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (user_id, row_limit))
            return cursor.fetchall()

    def show_all_records(self, row_limit):
        sql = " SELECT record_id, u.first_name, u.second_name, r.exercise_type_id ," \
              " r.contribution, gender, u.user_id " \
              "FROM records r ,users u " \
              "WHERE r.user_id = u.user_id " \
              "ORDER BY `date` DESC " \
              "LIMIT %s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (row_limit,))
            return cursor.fetchall()

    def set_autoincrement(self, new_value):
        sql = "ALTER TABLE records AUTO_INCREMENT=%s"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (new_value,))
            self.connection.commit()

    def get_records_by_date(self, exercise_type_id, gender, date_from, date_to):
        sql = "SELECT r.user_id as id, u.first_name as fn," \
              "u.second_name as sn,SUM(contribution) AS c " \
              "FROM records r, users u WHERE exercise_type_id = %s " \
              "AND r.user_id = u.user_id AND u.gender = %s " \
              "AND r.date BETWEEN %s and %s " \
              "GROUP BY id ORDER BY c DESC"
        self.connection.reconnect(attempts=2)
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (exercise_type_id, gender, date_from, date_to))
            return cursor.fetchall()
