from flask import Flask, request, render_template
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def read_html():
    return render_template('index.html')
