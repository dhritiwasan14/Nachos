from app import app 
from flask import render_template, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mongoengine import MongoEngine, Document


app.config['MONGO_URI'] = "mongodb://localhost:27017/nachos"
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'cookie'

class User(db.Document):
    meta = {'collection': 'users'}
    membership_id = db.StringField(max_length=30)
    password = db.StringField()


@app.route('/login', methods=['POST'])
def login():
    # check if membership ID is valid
    check_user = User.objects(membership_id=request.form.get('mem_id')).first()
    if check_user:
        if check_password_hash(check_user['password'], request.form.get('password')):
            return 'SUCCESS'
    return 'FAILED'

@app.route('/signup', methods=['POST'])
def sign_up():
    # check if user exists already
    # check if password matches confirm password
    # check if membership ID is valid.
    msg = 'SUCCESS'
    try:
        existing_user = User.objects(membership_id=request.form.get('mem_id')).first()
        if not existing_user:
            hash_pass = generate_password_hash(request.form.get('password'), method='sha256')
            user = User(request.form.get('mem_id'), hash_pass).save()
        else:
            msg = 'FAILED, USER ALREADY EXISTS'
    except Exception as e:
        msg = f'Failed with error response : {e}' 
    resp = make_response(msg)
    resp.set_cookie(request.form.get('mem_id'))
    return resp

# @app.route('/', methods=['GET'])
# def main():
#     # reading cookie
#     cookie = request.cookies.get('session')
