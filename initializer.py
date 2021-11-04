from os import environ

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters

import states
from states import states_set
from handlers.admin_handlers import AdminHandlers
from handlers.client_util_handlers import ClientUtilsHandler
from handlers.exercise_handlers import ExerciseHandler
from handlers.registration_handlers import RegistrationHandler

run_goal = environ["RUN_GOAL"]
burpee_goal = environ["BURPEE_GOAL"]
super_admin = environ["SUPER_ADMIN"]


class Initializer:

    def __init__(self) -> None:
        self.bot = Bot(token=environ['BOT_TOKEN'])
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        exercise_handler = ExerciseHandler()
        registration_handler = RegistrationHandler()
        client_utils_handler = ClientUtilsHandler()
        admin_handler = AdminHandlers()
        self.register_exercise_handlers(exercise_handler)
        self.register_registration_handlers(registration_handler)
        self.register_client_utils_handler(client_utils_handler)
        self.register_admin_handlers(admin_handler, exercise_handler)

    def register_exercise_handlers(self, exercise_handler):
        self.dp.register_message_handler(exercise_handler.add_run_handler,
                                         filters.Text(startswith=["Бег", "Run"], ignore_case=True))
        self.dp.register_message_handler(exercise_handler.add_burpee_handler,
                                         filters.Text(startswith=["Берпи", "Бёрпи", "Burpee"], ignore_case=True))

    def register_registration_handlers(self, registration_handler):
        self.dp.register_message_handler(registration_handler.start_handler, commands=["start"])
        self.dp.register_message_handler(registration_handler.add_city_handler, state=states_set.Registration.add_city)
        self.dp.register_callback_query_handler(registration_handler.add_gender_handler,
                                                state=states_set.Registration.add_gender)
        self.dp.register_message_handler(registration_handler.add_age_handler, state=states_set.Registration.add_age)

    def register_client_utils_handler(self, client_utils_handler):
        self.dp.register_message_handler(client_utils_handler.help_command_handler, commands=["help"])
        self.dp.register_message_handler(client_utils_handler.my_statistic_handler, commands=["my_statistic"])
        self.dp.register_message_handler(client_utils_handler.statistic_handler, commands=["statistic"])
        self.dp.register_callback_query_handler(client_utils_handler.burpee_men, text="top_b_men")
        self.dp.register_callback_query_handler(client_utils_handler.burpee_women, text="top_b_women")
        self.dp.register_callback_query_handler(client_utils_handler.run_men, text="top_r_men")
        self.dp.register_callback_query_handler(client_utils_handler.run_women, text="top_r_women")

    def register_admin_handlers(self, admin_handler, exercise_handler):
        self.dp.register_message_handler(admin_handler.set_zero_run_handler, user_id=super_admin,
                                         commands=["set_zero_run"])
        self.dp.register_message_handler(admin_handler.set_zero_burpee_handler, user_id=super_admin,
                                         commands=["set_zero_burpee"])
        self.dp.register_message_handler(admin_handler.ban_user, user_id=super_admin, commands=["ban"])
        self.dp.register_message_handler(admin_handler.unban_user, user_id=super_admin, commands=["unban"])
        self.dp.register_message_handler(admin_handler.show_records_handler, user_id=super_admin,
                                         commands=["show_records"])
        self.dp.register_message_handler(admin_handler.stop_edit_handler, user_id=super_admin,
                                         commands=["stop_edit"], state=states.AdminStates.editing_records)
        self.dp.register_message_handler(admin_handler.editing_records, user_id=super_admin,
                                         state=states.AdminStates.editing_records)
        self.dp.register_message_handler(exercise_handler.add_team_result_handler, user_id=super_admin,
                                         commands=["add_team_result"])
        self.dp.register_message_handler(admin_handler.help_admin_handler, user_id=super_admin,
                                         commands=["help_admin"])
        self.dp.register_callback_query_handler(admin_handler.delete_records_handler, user_id=super_admin,
                                                state=states.DeleteStates.deleting)
