class User:
    def __init__(self, first_name, second_name, user_id) -> None:
        self.first_name = first_name
        self.second_name = second_name
        self.user_id = user_id


class Chat:
    def __init__(self, chat_id: int, title: str) -> None:
        self.title = title
        self.chat_id = chat_id


class Record:
    def __init__(self, contribution: int, exercise_type_id: int, chat: Chat, user: User, record_id: int) -> None:
        self.record_id = record_id
        self.user = user
        self.chat = chat
        self.exercise_type_id = exercise_type_id
        self.contribution = contribution
