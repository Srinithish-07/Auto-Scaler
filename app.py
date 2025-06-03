from flask import Flask, render_template, request
import os

app = Flask(__name__)

electives = ["Machine Learning", "Cyber Security", "Cloud Computing", "Data Science"]

@app.route('/')
def index():

    
    
    return render_template('index.html', electives=electives)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    elective = request.form['elective']
    return render_template('success.html', name=name, elective=elective)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Changed from 5000 to 5001

