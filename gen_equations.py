from random import randint, choice, shuffle

from data import db_session
from data.level_module_task import Progress


def fk(typ, koef):
    if typ == 1:
        if koef == -1:
            return '-'
        elif koef == 1:
            return ''
        else:
            return str(koef)
    elif typ == 2:
        if koef < 0:
            return f'- {abs(koef)}'
        elif koef >= 0:
            return f'+ {koef}'


def gen_lvl1(k=1, b=0):
    if k != 1:
        k = randint(-10, 10)
        while k == 0 or k == 1:
            k = randint(-10, 10)
    x = randint(-10, 10)
    if b:
        b = randint(-10, 10)
        while b == 0:
            b = randint(-10, 10)
    if b == 0:
        return {
            'k': k,
            'c': k * x,
            'x': x
        }
    return {
        "k": k,
        'b': b,
        'c': x * k + b,
        'x': x
    }


def gen_lvl2_module1():
    x = randint(1, 10)
    if choice([True, False]):
        return f'x² - {x ** 2} = 0', str(x) + ' ' + str(-x)
    else:
        g = randint(-(x ** 2), x ** 2)
        while g == 0 or g == x ** 2:
            g = randint(-(x ** 2), x ** 2)
        r = [g, x ** 2 - g]
        shuffle(r)
        return f'x² {fk(2, -r[0])} = {r[1]}', str(x) + ' ' + str(-x)


def gen_lvl2_module2(c=0):
    if c:
        x1, x2 = randint(-10, 10), randint(-10, 10)
        while x1 == x2:
            x1, x2 = randint(-10, 10), randint(-10, 10)
    else:
        x1, x2 = 0, randint(-10, 10)
        while x1 == x2:
            x2 = randint(-10, 10)

    a = randint(-3, 3)
    while a == 0:
        a = randint(-3, 3)
    b = -a * (x1 + x2)
    c = a * (x1 * x2)

    if c == 0:
        return {
            'a': a,
            'b': b,
            'x': str(x1) + ' ' + str(x2)
        }
    return {
        'a': a,
        'b': b,
        'c': c,
        'x': str(x1) + ' ' + str(x2)
    }


def gen_lvl2_module3():
    x = randint(-10, 10)
    b = -x
    return {
        'b': 2 * b,
        'c': b ** 2,
        'x': x
    }


def gen_lvl3():
    x = randint(1, 10)
    y = randint(1, 10)

    a1, b1 = randint(2, 3), 1
    c1 = a1 * x + y
    a2, b2 = 1, randint(2, 3)
    c2 = x + b2 * y
    print(f"{a1}x + y = {c1}")
    print(f"x + {b2}y = {c2}")
    print(f"Корни: x = {x}, y = {y}")
    lst = [
        ['x.png'] * a1 + ['y.png'] * b1 + [c1],
        ['x.png'] * a2 + ['y.png'] * b2 + [c2],
    ]
    return lst, str(x) + ' ' + str(y)


def gen_eq(typee):
    if typee == 11:
        koef = gen_lvl1(b=1)
        return f'x {fk(2, koef["b"])} = {koef["c"]}', koef["x"]
    elif typee == 12:
        koef = gen_lvl1(k=0)
        return f'{fk(1, koef["k"])}x = {koef["c"]}', koef["x"]
    elif typee == 13:
        koef = gen_lvl1(k=0, b=1)
        return f'{fk(1, koef["k"])}x {fk(2, koef["b"])} = {koef["c"]}', koef["x"]
    elif typee == 21:
        return gen_lvl2_module1()
    elif typee == 22:
        koef = gen_lvl2_module2()
        return f'{fk(1, koef["a"])}x² {fk(2, koef["b"])}x = 0', koef["x"]
    elif typee == 23:
        koef = gen_lvl2_module3()
        return f'x² {fk(2, koef["b"])}x {fk(2, koef["c"])} = 0', koef["x"]
    elif typee == 24:
        koef = gen_lvl2_module2(c=1)
        return f'{fk(1, koef["a"])}x² {fk(2, koef["b"])}x {fk(2, koef["c"])} = 0', koef["x"]


def add_into_db(lvl, module, task, current_user):
    equat = gen_eq(int(f'{lvl}{module}'))
    db_sess = db_session.create_session()
    temp = [i.text_task for i in db_sess.query(Progress).filter(Progress.user_id == current_user,
                                                                Progress.level_id == lvl,
                                                                Progress.module_id == module)]
    while equat[0] in temp:
        equat = gen_eq(int(f'{lvl}{module}'))
        print(equat)

    eqs = db_sess.query(Progress).filter(Progress.user_id == current_user,
                                         Progress.level_id == lvl,
                                         Progress.module_id == module,
                                         Progress.task_id == task).first()
    if not eqs:
        progress = Progress()
        progress.user_id = current_user
        progress.level_id = lvl
        progress.module_id = module
        progress.task_id = task
        progress.text_task = equat[0]
        progress.answer = equat[1]
        db_sess.add(progress)
        db_sess.commit()


def gen_message():
    return choice(["Ты настоящий нейронный гений!",
                   "Мозг как суперкомпьютер!",
                   "Ты вычислительный мастер!"
                   "У тебя мозги как у математического гуру!",
                   "Ты настоящий аналитический асс!",
                   "Твои нейронные сети работают на полную мощность!",
                   "Ты настоящий король математики!",
                   "Твои знания — это прямая трансляция из квантового компьютера!",
                   "Твои решения на уровне искусственного интеллекта!",
                   "Ты нейро-процессор в человеческом облике!",
                   "Ты словно ходячий алгоритм!",
                   "Твои мозги — настоящая фабрика идей!",
                   "Ты аналитический виртуоз!",
                   "Твоя интуиция на уровне машинного обучения!",
                   "Ты словно живой калькулятор!",
                   "Ты прям мозг!"])
