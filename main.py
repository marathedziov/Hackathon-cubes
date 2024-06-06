from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.level_module_task import Module, Progress
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import gen_equations

app = Flask(__name__)
app.config["SECRET_KEY"] = "hackaton_cubes"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("base.html")


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
            name=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('log     in.html', title='Авторизация', form=form)


@app.route('/flowers', methods=['GET', 'POST'])
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
    equations, answ = gen_equations.gen_lvl3()
    ans = answ
    return render_template('level_flowers.html', equations=equations)


def solving_eq(eq):
    if request.method == 'POST':
        ans = request.form.get('ans')
        result = request.form.get('result')
        if result == ans:
            return render_template('level_flower_res.html', res="ПРАВИЛЬНО")
        return render_template('level_flower_res.html', res="НЕПРАВИЛЬНО")
    else:
        return render_template('solving_eq.html', eq=eq)


@app.route('/solv/<int:lvl><int:module><int:task>', methods=['GET', 'POST'])
def genering(lvl, module, task):
    equat = gen_equations.gen_eq(int(f'{lvl}{module}'))
    db_sess = db_session.create_session()
    eqs = db_sess.query(Progress).filter(Progress.id == (lvl - 1) * 12 * (module - 1) * 4 + (task)).first()
    if eqs:
        solving_eq((eqs.text_task, eqs.answer))
    else:
        progress = Progress()
        progress.user_id = current_user
        progress.level_id = lvl
        progress.module_id = module
        progress.text_task = equat[0]
        progress.answer = equat[1]
        db_sess.add(progress)
        db_sess.commit()
        solving_eq(equat)


if __name__ == "__main__":
    db_session.global_init("db/hackathon")
    app.run(debug=True)
