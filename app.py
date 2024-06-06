import json

from flask import Flask, render_template


def get_data_json():
    with open('level1.json', 'r') as f:
        data = json.load(f)
        return data


app = Flask(__name__)


@app.route('/')
def show_level():
    dict_progress_buttons = {"model1": ["completed", "unblocked", "unblocked", "blocked"],
                             "model2": ["blocked", "blocked", "completed", "unblocked"],
                             "model3": ["completed", "completed", "blocked", "blocked"]}
    return render_template('level.html', data=get_data_json(), dict_progress_buttons=dict_progress_buttons)


if __name__ == '__main__':
    app.run()
