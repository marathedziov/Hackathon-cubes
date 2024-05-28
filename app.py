from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    flags = {
        'module1_flag': False,
        'task1_1_flag': False,
        'task2_1_flag': False,
        'task3_1_flag': False,
        'task4_1_flag': False,
        'module2_flag': False,
        'task1_2_flag': False,
        'task2_2_flag': False,
        'task3_2_flag': False,
        'task4_2_flag': False,
        'module3_flag': False,
        'task1_3_flag': False,
        'task2_3_flag': False,
        'task3_3_flag': False,
        'task4_3_flag': False
    }
    return render_template('index.html', **flags)


if __name__ == '__main__':
    app.run()
