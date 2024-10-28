import database, web
import asyncio
from dotenv import load_dotenv
from database.models import Type

load_dotenv()


async def main():
    await database.setup()

    types = [
        "Общее",
        "Химия",
        "Электрика",
        "Безопасность",
        "Руководство",
        "Охрана труда",
        "Закупки",
        "Программирование",
        "Логистика",
        "Сети, связи"
    ]

    for type_name in types:
        if not await Type.exists(full_name=type_name):
            await Type.create(full_name=type_name)

    await web.setup()


if __name__ == '__main__':
    asyncio.run(main())
