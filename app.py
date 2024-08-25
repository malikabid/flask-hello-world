from flask import Flask, request, jsonify, render_template, send_file
app = Flask(__name__)

@app.route('/')
def hello_world():
    # return 'Hello, World! I am coming...'
    return render_template('index.html')
