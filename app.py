from flask import Flask, request, render_template
from flask_wtf import Form
from wtforms import FloatField
from .main import main





app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'stuff'

@app.route('/', methods=['GET', 'POST'])
def divide():

    class UrlLink(Form):
        webLink = FloatField("Albumn Name")


    form = UrlLink()
    result = None

    if form.validate_on_submit():
        result = form.webLink.data

    return render_template('divide.html', result=result, form=form)


if __name__ == '__main__':
    app.run(port=5000)
