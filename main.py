import json
from random import choice

from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.level_module_task import Progress
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from gen_equations import gen_lvl3, add_into_db, gen_message

app = Flask(__name__)
app.config["SECRET_KEY"] = "hackaton_cubes"
login_manager = LoginManager()
login_manager.init_app(app)


def get_data_json(num_level):
    path = 'levels/level' + str(num_level) + '.json'
    print(path)
    with open(path, 'r') as f:
        data = json.load(f)
        return data


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html", current_user=current_user)


@login_required
@app.route("/story")
def story():
    return render_template("story.html")


@login_required
@app.route('/profile')
def profile():
    db_sess = db_session.create_session()
    lvl1 = db_sess.query(Progress).filter(Progress.user_id == current_user.id, Progress.level_id == 1,
                                          Progress.completed == "completed").all()
    lvl2 = db_sess.query(Progress).filter(Progress.user_id == current_user.id, Progress.level_id == 2,
                                          Progress.completed == "completed").all()
    lvl3 = db_sess.query(Progress).filter(Progress.user_id == current_user.id, Progress.level_id == 3,
                                          Progress.completed == "completed").all()
    ur1, ur2, ur3 = round(len(lvl1) / 15 * 100, 1), round(len(lvl2) / 15 * 100, 1), round(len(lvl3) / 15 * 100, 1)
    return render_template('user_profile.html', ur1=ur1, ur2=ur2, ur3=ur3, current_user=current_user)


@login_required
@app.route("/map")
def map():
    db_sess = db_session.create_session()
    lvl_opened = 0
    for i in range(1, 3):
        tasks = [el.completed for el in
                 db_sess.query(Progress).filter(Progress.user_id == current_user.id, Progress.level_id == i)]
        if tasks.count('completed') >= 12:
            lvl_opened += 1
    return render_template("map.html", lvl_opened=lvl_opened)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect('/story')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            print(current_user.username)
            return redirect("/story")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/the_graphical_equation', methods=['GET', 'POST'])
@login_required
def level_flowers():
    global ans
    res = 'НЕ ПРАВИЛЬНО'
    if request.method == 'POST':
        res_x = request.form['ans_x']
        res_y = request.form['ans_y']
        print((int(res_x), int(res_y)), ans)
        if (int(res_x), int(res_y)) == ans:
            res = "ПРАВИЛЬНО"
        return render_template('level_flower_res.html', res=res)
    else:
        equations, answ = gen_lvl3()
        ans = answ
        return render_template('level_flovers.html', equations=equations)


@login_required
@app.route("/draft/<int:lvl><int:module><int:task>")
def draft(lvl, module, task):
    db_sess = db_session.create_session()
    eq = db_sess.query(Progress).filter(Progress.user_id == current_user.id,
                                        Progress.level_id == lvl,
                                        Progress.module_id == module,
                                        Progress.task_id == task).first()
    return render_template("draft.html", eq=eq.text_task, ids=str(lvl) + str(module) + str(task))


@app.route('/solv/<int:lvl><int:module><int:task>', methods=['GET', 'POST'])
@login_required
def solving_eq(lvl, module, task):
    if request.method == 'POST':
        ans = set(request.form.get('ans').split())
        result = set(request.form.get('result').split())
        if result == ans:
            db_sess = db_session.create_session()
            eq = db_sess.query(Progress).filter(Progress.user_id == current_user.id,
                                                Progress.level_id == lvl,
                                                Progress.module_id == module,
                                                Progress.task_id == task).first()
            eq.completed = 'completed'
            db_sess.commit()
            return render_template('check_answer.html', res=True,
                                   ids=(lvl, module, task), message=gen_message())
        return render_template('check_answer.html', res=False,
                               ids=(lvl, module, task))
    else:
        add_into_db(lvl, module, task, current_user.get_id())
        db_sess = db_session.create_session()
        eq = db_sess.query(Progress).filter(Progress.user_id == current_user.id,
                                            Progress.level_id == lvl,
                                            Progress.module_id == module,
                                            Progress.task_id == task).first()
        return render_template('solving_eq.html', eq=(eq.text_task, eq.answer), ids=(lvl, module, task))


@login_required
@app.route('/show_level<int:level_id>')
def show_level(level_id):
    db_sess = db_session.create_session()
    dict_progress_buttons = {"level": level_id}
    f = False
    for i in range(1, 4):
        g = [(el.task_id, el.completed) for el in db_sess.query(Progress).filter(Progress.user_id == current_user.id,
                                                                                 Progress.level_id == level_id,
                                                                                 Progress.module_id == i)]
        if i == 1 or g:
            temp = ['unblocked'] * 5
            for j in g:
                temp[j[0] - 1] = j[1]
            dict_progress_buttons[f'model{i}'] = temp
        elif dict_progress_buttons[f'model{i - 1}'].count('completed') >= 4:
            dict_progress_buttons[f'model{i}'] = ['unblocked'] * 5
        else:
            dict_progress_buttons[f'model{i}'] = ['blocked'] * 5
    return render_template('level.html', data=get_data_json(dict_progress_buttons["level"]),
                           dict_progress_buttons=dict_progress_buttons)


if __name__ == "__main__":
    db_session.global_init("db/hackathon.db")
    app.run()
