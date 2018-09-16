from app import app 
from flask import render_template, request, make_response
from flask_pymongo import PyMongo 
from werkzeug.security import generate_password_hash, check_password_hash


app.config['MONGO_URI'] = "mongodb://localhost:27017/nachos"
mongo = PyMongo(app)

@app.route('/login', methods=['POST'])
def login():
    # check if membership ID is valid
    user = mongo.db.user.find(
        {
            'mem_id': request.form['mem_id'], 
            'password': request.form['password']
        }
    )
    return 'cookie' if user else 'invalid request'

@app.route('/signup', methods=['POST'])
def sign_up():
    # check if user exists already
    # check if password matches confirm password
    # check if membership ID is valid.
    msg = 'SUCCESS'
    try:
        mongo.db.user.insert({
            'mem_id': request.form['mem_id'],
            'password': request.form['password']
        })
    except Exception as e:
        msg = f'Failed with error response : {e}' 
    resp = make_response({'authentication': msg})
    resp.set_cookie()
    return resp

@app.route('/', methods=['GET'])
def main():
    # reading cookie
    cookie = request.cookies.get('session')
