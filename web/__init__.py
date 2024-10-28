import os

from flask import Flask, render_template, request, g, redirect, url_for, flash, session
from database.models import Problems, Person, Type
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'aP9*3xL0#VmZ!8pQ$7kFs'


def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in')
            return redirect(url_for('login'))
        return await f(*args, **kwargs)

    return decorated_function


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        type_id = request.form.get('type')

        # Проверяем, существует ли уже такой логин
        existing_user = await Person.filter(login=login).first()
        if existing_user:
            flash('Login already taken')
            return render_template('register.html', types=await Type.all())  # Передаем список типов

        # Создаем нового пользователя с выбранной должностью
        new_user = Person(
            login=login,
            full_name=full_name,
            email=email,
            type_id=type_id
        )
        new_user.set_password(password)
        await new_user.save()

        flash('Registration successful, please log in.')
        return redirect('/login')

    # Получаем список всех должностей для отображения
    types = await Type.all()
    return render_template('register.html', types=types)


@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        # Ищем пользователя по логину
        user = await Person.filter(login=login).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful')
            return redirect(url_for('home'))

        flash('Invalid credentials')

    return render_template('login.html')


@app.before_request
async def load_user():
    user_id = session.get('user_id')  # Берём id пользователя из сессии
    g.user_name = None  # Задаём значение по умолчанию
    if user_id:
        try:
            user = await Person.get(id=user_id)  # Ищем пользователя в базе данных
            if user:
                g.user_name = user.full_name  # Сохраняем имя пользователя в g
        except Exception as e:
            pass


@app.route('/')
async def home():
    return render_template('home.html')


@app.route('/form')
@login_required
async def form():
    types = await Type.all()
    return render_template('form.html', types=types)


@app.route('/submit', methods=['POST'])
@login_required
async def submit():
    priority = request.form.get('priority')
    description = request.form.get('description')
    message = request.form.get('message')
    type_id = request.form.get('type')

    await Problems.create(priority=priority, description=description, message=message, type_id=type_id, status="START")
    return render_template('success.html')


@app.route('/show')
async def show():
    tab = request.args.get('tab', 'start')  # Получаем вкладку, по умолчанию 'start'

    start_data = []
    in_progress_data = []
    end_data = []

    sorter = {
        "INFO": 0,
        "WARN": 1,
        "CRIT": 2,
    }

    if tab == 'start':
        problems = await Problems.filter(status='START')
        for v in problems:
            start_data.append([v.description, v.message, v.time, v.id, v.priority])
        start_data.sort(key=lambda x: (sorter[x[4]], x[2]), reverse=True)

    elif tab == 'in_progress':
        problems = await Problems.filter(status='IN_PROGRESS')
        for v in problems:
            in_progress_data.append([v.description, v.message, v.time, v.id, v.priority,
                                     "<no>" if not v.responsible else (await v.responsible.first()).full_name])
        in_progress_data.sort(key=lambda x: (sorter[x[4]], x[2]), reverse=True)

    elif tab == 'end':
        problems = await Problems.filter(status='END')
        for v in problems:
            end_data.append([v.description, v.message, v.time, v.id, v.priority,
                             "<no>" if not v.responsible else (await v.responsible.first()).full_name])
        end_data.sort(key=lambda x: x[2], reverse=True)

    return render_template('show.html',
                           start_data=start_data,
                           in_progress_data=in_progress_data,
                           end_data=end_data,
                           tab=tab)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
async def edit(id):
    problem = await Problems.get(id=id)
    if request.method == 'POST':
        problem.priority = request.form.get('priority')
        problem.description = request.form.get('description')
        problem.message = request.form.get('message')
        await problem.save()

        return redirect('/show')

    return render_template('edit.html', problem=problem)


@app.route('/take/<int:problem_id>', methods=['POST'])
@login_required
async def take_problem(problem_id):
    problem = await Problems.get(id=problem_id)
    if problem:
        problem.status = 'IN_PROGRESS'
        problem.responsible = await Person.get(id=session.get('user_id'))
        await problem.save()
    return redirect('/show?tab=start')  # Возвращаемся на вкладку "Ждут действий"


@app.route('/solve/<int:problem_id>', methods=['POST'])
@login_required
async def solve_problem(problem_id):
    problem = await Problems.get(id=problem_id)
    if problem:
        problem.status = 'END'  # Меняем статус задачи на "Решено"
        await problem.save()
    return redirect('/show?tab=in_progress')  # Возвращаемся на вкладку "В процессе"


@app.route('/reopen/<int:problem_id>', methods=['POST'])
@login_required
async def reopen_problem(problem_id):
    problem = await Problems.get(id=problem_id)
    if problem:
        problem.status = 'IN_PROGRESS'  # Меняем статус задачи на "Решено"
        problem.responsible = await Person.get(id=session.get('user_id'))
        await problem.save()
    return redirect('/show?tab=end')


def setup():
    app.run(host=os.getenv("URL"), port=os.getenv("PORT"), debug=True)
