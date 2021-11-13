from data_base import UserDB, ChatDB, RecordDB
from models import User


class UserTransactions:
    users = UserDB()
    records = RecordDB()

    def add_user(self, user: User):
        self.users.add_user(user.first_name, user.second_name, user.user_id)

    def add_city(self, user_id, city: str):
        self.users.add_city(user_id, city)

    def add_gender(self, user_id, gender: int):
        self.users.add_gender(user_id, gender)

    def add_age(self, user_id, age: int):
        self.users.add_age(user_id, age)

    def get_user_age(self, user_id) -> tuple:
        return self.users.get_age(user_id)

    def get_user_gender(self, user_id) -> tuple:
        return self.users.get_gender(user_id)

    def get_users_info(self):
        return self.users.get_users_info()

    def ban_user(self, user_id):
        self.users.ban_user(user_id)

    def unban_user(self, user_id):
        self.users.unban_user(user_id)


class ChatTransactions:
    chats = ChatDB()

    def add_chat(self, chat_id, title, gender=1):
        self.chats.add_chat(chat_id, title, gender)

    def get_all_chats(self):
        return self.chats.get_all_chats()


class TransactionUtils:
    def prepare_user_not_in_top(self, exercise_type_id, gender, user_id, records_db):
        line = "-" * 20 + "\n"
        user_result = records_db.get_user_with_placement(exercise_type_id, gender, user_id)
        if user_result:
            placement = user_result[0]
            contribution = self.prepare_result(user_result[3], exercise_type_id)
            if user_result[2]:
                name = user_result[1] + " " + user_result[2]
            else:
                name = user_result[1]
            line = line + str(placement) + ". " + name + " " + str(contribution)
            return "<b><i>" + line + "</i></b>"
        else:
            return ""

    def prepare_result(self, unconverted_result, exercise_type_id):
        if exercise_type_id == 1:
            return unconverted_result
        elif exercise_type_id == 2:
            return round(unconverted_result / 1000, 3)

    def prepare_top(self, exercise_type_id, unsorted_top, user_id, gender, records_db):
        user_tr = UserTransactions()
        text_result = ""
        user_in_top = False
        counter = 1
        for tuple_line in unsorted_top:
            top_user_id = tuple_line[0]
            contribution = self.prepare_result(tuple_line[3], exercise_type_id)
            if tuple_line[2]:
                name = tuple_line[1] + " " + tuple_line[2]
            else:
                name = tuple_line[1]
            if user_id == top_user_id:
                user_in_top = True
                line = self.prepare_line_for_top(contribution, counter, exercise_type_id, name)
                counter += 1
            else:
                line = self.prepare_line_for_top(contribution, counter, exercise_type_id, name, False)
                counter += 1
            text_result = text_result + line
        user_gender = user_tr.get_user_gender(user_id)
        if user_gender:
            user_gender = user_gender[0]
        if user_in_top or user_gender != gender:
            return text_result
        else:
            return text_result + self.prepare_user_not_in_top(exercise_type_id, gender, user_id, records_db)

    def prepare_line_for_top(self, contribution, counter, exercise_type_id, name, with_user=True):
        line = str(counter) + ". " + name + " " + str(contribution)
        if exercise_type_id == 2:
            line = line + "км\n"
        else:
            line = line + "\n"
        if with_user:
            return "<b><i>" + line + "</i></b>"
        else:
            return line


class RecordTransactions:
    records = RecordDB()
    utils = TransactionUtils()

    def create_record(self, contribution, exercise_type_id, user_id, chat_id):
        self.records.create_record(contribution, exercise_type_id, user_id, chat_id)

    def get_common_user_result(self, user_id, exercise_type_id):
        unconverted_result = self.records.get_common_user_result(user_id, exercise_type_id)
        return self.utils.prepare_result(unconverted_result[0][0], exercise_type_id)

    def get_common_result(self, exercise_type_id):
        unconverted_result = self.records.get_common_result(exercise_type_id)
        return self.utils.prepare_result(unconverted_result[0][0], exercise_type_id)

    def get_top(self, user_id, exercise_type_id, gender):
        unsorted_top = self.records.get_top(exercise_type_id, gender)
        text_result = self.utils.prepare_top(exercise_type_id, unsorted_top, user_id, gender, self.records)
        return text_result

    def delete_records_by_ex_type(self, exercise_type_id):
        return self.records.delete_records_by_ex_type(exercise_type_id)

    def delete_record(self, record_id):
        return self.records.delete_record_by_id(record_id)

    def update_record(self, record_id, new_value):
        return self.records.update_record(record_id, new_value)

    def get_ex_type_buy_record_id(self, record_id):
        exec_type = self.records.get_ex_type_buy_record_id(record_id)
        if exec_type:
            return exec_type[0]

    def show_user_records(self, user_id, row_limit):
        return self.records.show_user_records(user_id, row_limit)

    def show_all_records(self, row_limit):
        return self.records.show_all_records(row_limit)

    def set_autoincrement(self, new_value):
        self.records.set_autoincrement(new_value)

    def get_records_by_date(self, exercise_type_id, gender, date_from, date_to):
        records_list = self.records.get_records_by_date(exercise_type_id, gender, date_from, date_to)
        formatted_result = ""
        counter = 1
        for tuple_line in records_list:
            user_id = tuple_line[0]
            contribution = self.utils.prepare_result(tuple_line[3], exercise_type_id)
            if exercise_type_id == 2:
                contribution = str(contribution) + " км."
            if tuple_line[2]:
                name = tuple_line[1] + " " + tuple_line[2]
            else:
                name = tuple_line[1]
            name = '<a href="tg://user?id=' + str(user_id) + '">' + name + '</a>'
            formatted_result = formatted_result + str(counter) + ". " + name + " " + str(contribution) + "\n"
            counter += 1
        return formatted_result

