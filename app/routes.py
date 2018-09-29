import json
import uuid
from datetime import datetime

from app import app
from flask import render_template, request, make_response, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mongoengine import MongoEngine, Document
from flask import jsonify


app.config['MONGO_URI'] = "mongodb://localhost:27017/nachos"
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'cookie'

class User(db.Document):
    meta = {'collection': 'users'}
    membership_id = db.StringField(max_length=30)
    password = db.StringField()
    uuid = db.StringField()
    orders = db.ListField()

class Product(db.Document):
    meta = {'collection': 'products'}
    id = db.SequenceField(primary_key=True)
    name = db.StringField()
    category = db.ListField()
    content = db.StringField()
    price = db.StringField()
    miles = db.StringField()
    image = db.URLField()

class Order(db.Document): # ordered, packed, onboard, arrive, completed
    meta = {'collection': 'orders'}
    order_id = db.StringField()
    product = db.IntField()
    created = db.DateTimeField(default=datetime.utcnow)
    last_update = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField()
    user = db.StringField()

class Transaction(db.Document):
    meta = {'collection': 'transactions'}
    id = db.SequenceField(primary_key=True)
    order_id = db.StringField()
    action = db.StringField()
    datetime = db.DateTimeField(default=datetime.utcnow())
    actor = db.StringField()


def create_product_json(obj):
    if isinstance(obj, Product):
        product = obj
        return {
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'content': product.content,
            'price': product.price,
            'miles': product.miles,
            'image': product.image
        }
    elif isinstance(obj, Order):
        order = obj
        return {
            'id': order.order_id, 
            'product_id': order.product,
            'product': Product.objects(id=order.product).first()['name'],
            'last_update': str(order.last_update),
            'created': str(order.created),
            'status': order.status,
        }
    else:
        trans = obj
        return {
            'id': trans.id,
            'order_id': trans.order_id,
            'action': trans.action,
            'datetime': str(trans.datetime),
            'actor': trans.actor
        }

def no_user_with_session_id(uid=''):
    existing_user = User.objects(uuid=uid).first()
    return existing_user is None


@app.route('/login', methods=['POST'])
def login():
    # check if membership ID is valid
    check_user = User.objects(membership_id=request.form.get('mem_id'))
    if check_user:
        if check_password_hash(check_user.first()['password'], request.form.get('password')):
            uid = str(uuid.uuid4().int)
            check_user.update_one(uuid=uid)
            return uid
    return 'FAILED'

@app.route('/signup', methods=['POST'])
def sign_up():
    msg = 'SUCCESS'
    mem_id = request.form.get('mem_id')
    if not mem_id:
        return '404'
    try:
        existing_user = User.objects(membership_id=mem_id).first()
        if not existing_user:
            hash_pass = generate_password_hash(request.form.get('password'), method='sha256')
            user = User(request.form.get('mem_id'), hash_pass, None).save()
        else:
            msg = 'FAILED, USER ALREADY EXISTS'
    except Exception as e:
        msg = f'Failed with error response : {e}' 
    return msg

@app.route('/logout', methods=['POST'])
def logout():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    User.objects(uuid=request.form.get('uid')).update_one(uuid=None)

@app.route('/product/<pid>', methods = ['GET', 'POST'])
def product(pid):
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    products = Product.objects(id=pid).first()
    return json.dumps(create_product_json(products))


@app.route('/products', methods=['GET'])
def products():
    # if no_user_with_session_id(request.form.get('uid')):
    #     return 'Sorry, you are not authenticated.'
    products = Product.objects
    return json.dumps([create_product_json(product) for product in products])

@app.route('/add_product', methods=['POST'])
def add_product():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    form = request.form
    print (form.get('image'))
    product = Product(
        form.get('id'),
        form.get('name'),
        form.getlist("category"),
        form.get('content'),
        form.get('price'),
        form.get('miles'),
        form.get('image')
    ).save()
    print (Product.objects.count())
    return 'SAVED' if product else None

@app.route('/add_order', methods=['POST'])
def add_order():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    product_id = request.form.get('product_id')
    user = User.objects(uuid=request.form.get('uid'))
    if product_id and user.first():
        order_id = str(uuid.uuid4())[:8]
        order = Order(order_id=order_id, product=int(product_id), created=datetime.now(), status='ordered').save()
        user.update_one(orders=user.first()['orders'] + [order.id])
        return order_id
    return 'FAILED'

def get_order(order_id):
    return Order.objects(id=order_id).first()

@app.route('/view_order', methods=['POST'])
def view_order():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    orders = User.objects(uuid=request.form.get('uid')).first()['orders']
    return json.dumps([create_product_json(get_order(order)) for order in orders])

@app.route('/update_order', methods=['POST'])
def update_order():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    order_id = request.form.get('order_id')
    set_to = request.form.get('set_to')
    if order_id:
        datetime_now = datetime.utcnow
        order = Order.objects(order_id=request.form.get('order_id'))
        order.update_one(status=set_to)
        order.update_one(status=datetime_now)
        trans = add_transaction(order.order_id, order.status, request.form.get('uid'))
        if trans:
            return 'SUCCESS'

def add_transaction(order_id, status, actor):
    trans = Transaction(order_id=order_id, action=status, actor=actor).save()
    return trans
