import asyncio
from time import timezone

import database
from datetime import datetime, timezone, timedelta
from database.models import Problems, Person
from mailing.use_email import Email
from dotenv import load_dotenv

load_dotenv()

import bot
from aiogram.types import InlineKeyboardMarkup
from aiogram import types

rename_type = {
    "INFO": "Информационная",
    "CRIT": "Критическая",
    "WARN": "Предупреждающая"
}


async def check_and_send_emails():
    while True:
        recent_time = datetime.now(timezone(timedelta(hours=0)))
        await asyncio.sleep(10)

        problems = await Problems.all()
        persons = await Person.all()



        for problem in problems:

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Взять проблему 📎", callback_data=f'take {str(problem.id)}')]])

            if problem.time >= recent_time:

                for person in persons:
                    if (await problem.type.first()).id in [1, (await person.type.first()).id]:
                        email_message = Email(
                            priority=problem.priority,
                            receiver_email=person.email,
                            description=problem.description,
                            message=problem.message,
                            status=problem.status,
                            type=(await problem.type.first()).full_name,
                            # author=problem.responsible.full_name if problem.responsible else "Неизвестен",
                            time=problem.time
                        )

                        # Отправляем email (вызов send_new_email будет синхронным)
                        await asyncio.to_thread(email_message.send_new_email)
                        if person.tg_id:
                            temp = (await problem.type.first()).full_name

                            await bot.bot.send_message(chat_id=person.tg_id,
                                                       text=f'❗<u><b>ВНИМАНИЕ</b></u>❗:\n\n'
                                                            f'<b>Id: {problem.id}</b>\n'
                                                            f'<b>{problem.description}</b>\n'
                                                            f'{problem.message}\n\n'
                                                            f'Вид: <b>{rename_type[problem.priority.value]}</b>\n'
                                                            f'Тип: <b>{temp}</b>\n'
                                                            f'От: {problem.time.strftime('%Y-%m-%d %H:%M:%S')}\n\n'
                                                            f'Проблема появилась в списке всех проблем в /menu',
                                                       parse_mode='html',
                                                       reply_markup=keyboard)


async def main():
    await database.setup()
    await asyncio.gather(bot.setup(), check_and_send_emails())
    # await bot.setup()
    # await check_and_send_emails()


if __name__ == '__main__':
    asyncio.run(main())
