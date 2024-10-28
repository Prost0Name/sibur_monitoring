import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from .keyboards import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import Problems, Person
from datetime import datetime
from tortoise.expressions import Q
import os


from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
form_router = Router()
dp.include_router(form_router)

users = {}
statusik = {'START': 'НОВАЯ 💡', 'IN_PROGRESS': 'В ПРОЦЕССЕ ⏳', 'END': 'ЗАВЕРШЕННАЯ 🏁'}
vids = {'INFO': 'ℹ ИНФОРМАЦИОННЫЙ', 'WARN': '❗ПРЕДУПРЕЖДАЮЩИЙ', 'CRIT': '⚠ КРИТИЧЕСКИЙ'}

url_site = f"{os.getenv("WEB_URL")}"

typesss = {1: 'Общее',
           2: 'Химия',
           3: 'Электрика',
           4: 'Безопасность',
           5: 'Руководство',
           6: 'Охрана труда',
           7: 'Закупки',
           8: 'Программирование',
           9: 'Логистика',
           10: 'Сети, связи'}


class Form(StatesGroup):
    login = State()
    password = State()

    desc = State()
    message = State()

    number = State()
    fini = State()


@form_router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    users[str(msg.from_user.id)] = [None, [None, None, None, None]]

    pers = await Person.filter(tg_id=str(msg.from_user.id))
    if pers:
        person = pers[0]
        person.tg_id = None
        await person.save()

    await msg.answer(
        f'Привет, это бот для системы оповещения о проблемах в компании <u>"СИБУР"</u> 🛢\n\nНет учетной записи? Зарегистрируйтесь на сайте: {url_site}\nЧтобы начать использование введите свой логин, а затем пароль (разными сообщениями)🔐',
        parse_mode='html')
    await state.set_state(Form.login)


@form_router.message(Form.login)
async def login(msg: Message, state: FSMContext):
    await state.clear()
    data = await Person.filter(login=msg.text)
    if data:
        if msg.text == data[0].login:
            users[str(msg.from_user.id)][0] = msg.text
            await state.set_state(Form.password)
    else:
        await bot.send_message(msg.from_user.id, "Такого логина нет❌")


@form_router.message(Form.password)
async def password(msg: Message, state: FSMContext):
    await state.clear()
    pers = await Person.filter(login=users[str(msg.from_user.id)][0])
    person = pers[0]
    if person.check_password(msg.text):

        person.tg_id = str(msg.from_user.id)
        await person.save()

        await bot.send_message(msg.from_user.id,
                               f"{person.full_name} вы успешно авторизовались✅\n\nЧтобы выйти из учетной записи введите /log_out\nДля работы с проблемами введите /menu")
    else:
        await bot.send_message(msg.from_user.id, "Неверный пароль❌")


@form_router.message(Command('menu'))
async def menu(msg: Message, state: FSMContext):
    person = await Person.filter(tg_id=str(msg.from_user.id))
    if person:
        users[str(msg.from_user.id)] = [None, [None, None, None, None]]
        await bot.send_message(msg.from_user.id, 'Это меню для работы с проблемами, выбери необходимую функцию ⬇',
                               reply_markup=keyboard_menu)


@form_router.message(Command('log_out'))
async def log_out(msg: Message, state: FSMContext):
    users.pop(str(msg.from_user.id))
    pers = await Person.filter(tg_id=str(msg.from_user.id))
    if pers:
        person = pers[0]
        person.tg_id = None
        await person.save()
        await bot.send_message(msg.from_user.id, 'Вы успешно вышли из учетной записи↩')


@form_router.callback_query(F.data == 'problem')
async def problem(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await bot.send_message(call.from_user.id,
                               '<u><i>Если возникла проблема</i></u> - опиши ее и она добавиться в общий список проблем компании "Сибур" ⚠\n\nПроблема состоит из:\n   <b>·<u>Вида проблемы</u></b>\n   <b>·<u>Типа проблемы</u></b>\n   <b>·<u>Описания</u></b>\n   <b>·<u>Сообщения к проблеме</u></b>',
                               reply_markup=keyboard_add_prob, parse_mode='html')


@form_router.callback_query(F.data == 'contin_add')
async def contin_add(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await bot.send_message(call.from_user.id, "Выберите вид проблемы ниже 🔽", reply_markup=keyboard_vid)


@form_router.callback_query(F.data.startswith('vid '))
async def vid(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        ostatok = call.data.replace('vid ', '')
        users[str(call.from_user.id)][1][0] = ostatok

        await bot.send_message(call.from_user.id, 'Выберите тип проблемы ниже 🔽', reply_markup=keyboard_type)


@form_router.callback_query(F.data.startswith('type '))
async def type(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        ostatok = int(call.data.replace('type ', ''))
        users[str(call.from_user.id)][1][3] = ostatok

        await bot.send_message(call.from_user.id, 'Введите название проблемы:')
        await state.set_state(Form.desc)


@form_router.message(Form.desc)
async def desc(msg: Message, state: FSMContext):
    await state.clear()
    person = await Person.filter(tg_id=str(msg.from_user.id))
    if person:
        users[str(msg.from_user.id)][1][1] = msg.text

        await bot.send_message(msg.from_user.id, 'Введите описание проблемы:')
        await state.set_state(Form.message)


@form_router.message(Form.message)
async def message(msg: Message, state: FSMContext):
    await state.clear()
    person = await Person.filter(tg_id=str(msg.from_user.id))
    if person:
        users[str(msg.from_user.id)][1][2] = msg.text

        v = users[str(msg.from_user.id)][1][0]
        t = users[str(msg.from_user.id)][1][3]
        await bot.send_message(msg.from_user.id,
                               f'⚠ Ваша новая проблема:\n\n<b>Вид</b>:\n {vids[v]}\n\n<b>Тип</b>:\n {typesss[t]}\n\n<b>Название</b>:\n {users[str(msg.from_user.id)][1][1]}\n\n<b>Описание проблемы</b>:\n {users[str(msg.from_user.id)][1][2]}',
                               reply_markup=keyboard_adding, parse_mode='html')


@form_router.callback_query(F.data == 'wrong_add')
async def wrong_add(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await state.clear()
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@form_router.callback_query(F.data == 'adding')
async def adding(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        prior = users[str(call.from_user.id)][1][0]
        descript = users[str(call.from_user.id)][1][1]
        mess = users[str(call.from_user.id)][1][2]
        type_int = users[str(call.from_user.id)][1][3]

        await Problems.create(priority=prior, type_id=type_int, description=descript, message=mess, status="START",
                              time=datetime.now())
        users[str(call.from_user.id)][1] = [None, None, None, None]
        await bot.send_message(call.from_user.id,
                               'Проблема была добавлена в глобальный список📌✅\n\nДля редактирования сатуса проблемы через /menu перейдите во вкладку "Мои проблемы"')
        await asyncio.sleep(1)
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@form_router.callback_query(F.data == 'show')
async def show(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        data = await Problems.filter(Q(status='START') | Q(status='IN_PROGRESS'))

        str_update = "<b>СПИСОК ПРОБЛЕМ СЕЙЧАС📁:</b>\n\n"
        for val in data:
            str_update += f"<blockquote>Id: <b>{val.id}</b> Вид проблемы: <b>{vids[str(val.priority.value)]}</b>\nТип: <i>{typesss[val.type_id]}</i>\n<b>{val.description}</b>\nОписание: <i>{val.message}</i>\nСтатус: <u>{statusik[val.status.value]}</u></blockquote>\n\n"
        await bot.send_message(call.from_user.id, str_update, reply_markup=keyboard_myproblem, parse_mode='html')


@form_router.callback_query(F.data == 'take_problem')
async def take_problem(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await bot.send_message(call.from_user.id, 'Чтобы взять проблему на себя, введите <b><u>ID</u></b> проблемы 🔢:',
                               reply_markup=keyboard_wrong_add, parse_mode='html')
        await state.set_state(Form.number)


@form_router.callback_query(F.data == 'update')
async def update(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await show(call, state)


@form_router.message(Form.number)
async def number(msg: Message, state: FSMContext):
    await state.clear()
    person = await Person.filter(tg_id=str(msg.from_user.id))
    if person:
        data = await Problems.filter(id=int(msg.text))

        if data:

            keyboard_take_problem = InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Взять проблему 📎", callback_data=f'take {msg.text}')],
                [types.InlineKeyboardButton(text="Отменить взятие ❌", callback_data='wrong_add')]
            ])

            await bot.send_message(msg.from_user.id,
                                   f'<i>Проблема, которую вы хотите взять:</i>\n\n<blockquote>Id: <b>{data[0].id}</b> Вид проблемы: <b>{vids[str(data[0].priority.value)]}</b>\nТип: <i>{typesss[data[0].type_id]}</i>\n<b>{data[0].description}</b>\nОписание: <i>{data[0].message}</i>\nСтатус: <u>{statusik[data[0].status.value]}</u></blockquote>',
                                   reply_markup=keyboard_take_problem, parse_mode='html')
        else:
            await bot.send_message(msg.from_user.id,
                                   'Такого ID проблемы нет, введите <b><u>ID</u></b> проблемы числом еще раз 🔢:',
                                   reply_markup=keyboard_wrong_add, parse_mode='html')
            await state.set_state(Form.number)


@form_router.callback_query(F.data.startswith('take '))
async def take(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))

    if person:
        print(call.data)
        print(call.data.replace('take ', ''))
        id = int(call.data.replace('take ', ''))
        proble = await Problems.filter(id=id)
        if proble:
            problem = proble[0]
            problem.status = 'IN_PROGRESS'
            per = person[0]
            problem.responsible = per

            await problem.save()
            await bot.send_message(call.from_user.id,
                                   'Вы успешно взялись за решение проблемы ✅\n\nПосле ее завершения измените статус проблемы во вкладке "Мои проблемы 👀" в /menu')


@form_router.callback_query(F.data == 'my')
async def my(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        per = person[0]
        proble = await Problems.filter(responsible=per, status="IN_PROGRESS")
        if proble:
            str_update = "<b>СПИСОК ВАШИХ ПРОБЛЕМ👥:</b>\n\n"
            for problem in proble:
                str_update += f"<blockquote>Id: <b>{problem.id}</b> Вид проблемы: <b>{vids[str(problem.priority.value)]}</b>\nТип: <i>{typesss[problem.type_id]}</i>\n<b>{problem.description}</b>\nОписание: <i>{problem.message}</i>\nСтатус: <u>{statusik[problem.status.value]}</u></blockquote>\n\n"

            await bot.send_message(call.from_user.id, str_update, reply_markup=keyboard_my, parse_mode='html')


@form_router.callback_query(F.data == 'finish')
async def finish(call: CallbackQuery, state: FSMContext):
    person = await Person.filter(tg_id=str(call.from_user.id))
    if person:
        await bot.send_message(call.from_user.id, 'Чтобы завершить проблему, введите <b><u>ID</u></b> проблемы 🏁:',
                               reply_markup=keyboard_wrong_add, parse_mode='html')
        await state.set_state(Form.fini)


@form_router.message(Form.fini)
async def fini(msg: Message, state: FSMContext):
    await state.clear()
    person = await Person.filter(tg_id=str(msg.from_user.id))
    if person:
        per = person[0]
        proble = await Problems.filter(responsible=per)
        for i in proble:
            if str(i.id) == msg.text:
                i.status = 'END'
                i.responsible = None
                await i.save()
                await bot.send_message(msg.from_user.id, 'Вы успешно завершили эту проблему 🏁', parse_mode='html')
                break
            else:
                await bot.send_message(msg.from_user.id,
                                       'Такого ID нет\nЧтобы завершить проблему, введите <b><u>ID</u></b> проблемы 🏁:',
                                       reply_markup=keyboard_wrong_add, parse_mode='html')
                await state.set_state(Form.fini)
                break


async def setup():
    await dp.start_polling(bot)
