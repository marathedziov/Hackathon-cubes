import json

from flask import Flask, render_template


def data_json():
    with open('level1.json', 'r') as f:
        data = json.load(f)
        lst_for_btn = []
        for module in data['modules']:
            lst_for_btn.append((module['sizes'], module['coordinates']))
            for task in module['tasks']:
                lst_for_btn.append((task['sizes'], task['coordinates']))
        print(lst_for_btn)
        return lst_for_btn


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
    lst_for_btn = data_json()
    return render_template('index.html', lst_for_btn=lst_for_btn, **flags)


if __name__ == '__main__':
    app.run()
