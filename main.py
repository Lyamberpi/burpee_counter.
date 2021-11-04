from aiogram.utils import executor

from initializer import Initializer

if __name__ == "__main__":
    initializer = Initializer()
    executor.start_polling(initializer.dp)
