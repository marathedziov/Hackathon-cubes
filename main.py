import json

from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.level_module_task import Progress
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from gen_equations import gen_lvl3, add_into_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "hackaton_cubes"
login_manager = LoginManager()
login_manager.init_app(app)


def get_data_json():
    with open('/level1.json', 'r') as f:
        data = json.load(f)
        return data


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@login_required
@app.route("/story")
def story():
    return render_template("story.html")


@login_required
@app.route("/user_profile")
def user_profile():
    return render_template("user_profile.html")


@login_required
@app.route("/map")
def map():
    return render_template("map.html")


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
            return redirect("/story")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/the_graphical_equation', methods=['GET', 'POST'])
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


@app.route('/solv/<int:lvl><int:module><int:task>', methods=['GET', 'POST'])
def solving_eq(lvl, module, task):
    if request.method == 'POST':
        ans = request.form.get('ans')
        result = request.form.get('result')
        if result == ans:
            return render_template('level_flower_res.html', res="ПРАВИЛЬНО")
        return render_template('level_flower_res.html', res="НЕПРАВИЛЬНО")
    else:
        add_into_db(lvl, module, task, current_user)
        db_sess = db_session.create_session()
        eq = db_sess.query(Progress).filter(Progress.level_id == lvl,
                                            Progress.module_id == module,
                                            Progress.task_id == task).first()
        return render_template('solving_eq.html', eq=(eq.text_task, eq.answer))


@login_required
@app.route('/show_level')
def show_level():
    dict_progress_buttons = {"model1": ["completed", "unblocked", "unblocked", "blocked"],
                             "model2": ["blocked", "blocked", "completed", "unblocked"],
                             "model3": ["completed", "completed", "blocked", "blocked"]}
    return render_template('level.html', data=get_data_json(), dict_progress_buttons=dict_progress_buttons)


if __name__ == "__main__":
    db_session.global_init("db/hackathon.db")
    app.run(debug=True)
