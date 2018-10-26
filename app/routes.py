import json
import uuid
from datetime import datetime

from app import app
from flask import render_template, request, make_response, Flask, redirect
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
    name = db.StringField()
    auth = db.StringField(default='user')  # types include - employee, admin, user


class Product(db.Document):
    meta = {'collection': 'products'}
    id = db.SequenceField(primary_key=True)
    name = db.StringField()
    category = db.ListField()
    content = db.StringField()
    price = db.StringField()
    miles = db.StringField()
    image = db.URLField()
    best_seller = db.BooleanField()


class Order(db.Document):  # ordered, packed, onboard, arrive, completed
    meta = {'collection': 'orders'}
    order_id = db.StringField()
    product = db.ListField(db.DictField())
    created = db.DateTimeField(default=datetime.utcnow)
    last_update = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField()
    user = db.StringField()
    last_updated_by = db.StringField()
    color = db.StringField()
    flight_no = db.StringField()
    issue = db.StringField()
    message = db.StringField()
    fraudulent = db.IntField()

class Transaction(db.Document):
    meta = {'collection': 'transactions'}
    id = db.SequenceField(primary_key=True)
    order_id = db.StringField()
    action = db.StringField()
    datetime = db.DateTimeField(default=datetime.utcnow())
    actor = db.StringField()

def create_small_order_json(order):
    return {
        'id': order.id,
        'user': order.user,
        'created': order.created,
        'last_update': order.last_update,
        'last_updated_by': order.last_updated_by,
        'status': order.status, 
    }

def create_json(obj):
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
        products = [Product.objects(id=dict(product)['id']).first() for product in order.product]
        return {
            'id': order.order_id,
            'product_id': [prod.id for prod in products],
            'product_names': [prod.name for prod in products],
            'product_images': [prod.image for prod in products],
            'product_descr': [prod.content for prod in products],
            'product_prices': [prod.price for prod in products],
            'product_miles': [prod.miles for prod in products],
            'product_quantities': [product['quantity'] for product in order.product],
            'last_update': str(order.last_update),
            'created': str(order.created),
            'last_updated_by': order.last_updated_by,
            'status': order.status,
            'user': order.user,
            'color': order.color,
            'flight_no': order.flight_no,
            'price': sum([float(prod.price[1:]) for prod in products]),
            'issue': order.issue if order.issue else None,
            'message': order.message if order.message else None,
            'fraudulent': order.fraudulent if order.fraudulent else 0
        }
    elif isinstance(obj, User):
        user = obj
        return {
            'name': name
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
            return json.dumps({'success': True, 'message': '', 'session_id': uid, 'name':check_user.first()['name'], 'auth': check_user.first()["auth"]})
    return json.dumps({'success': False, 'message': 'Invalid Username or Password'})


@app.route('/signup', methods=['POST'])
def sign_up():
    msg = 'SUCCESS'
    name = request.form.get('name')
    mem_id = request.form.get('mem_id')
    if not mem_id:
        return '404'
    try:
        existing_user = User.objects(membership_id=mem_id).first()
        if not existing_user:
            hash_pass = generate_password_hash(request.form.get('password'), method='sha256')
            user = User(request.form.get('mem_id'), hash_pass, name=name).save()
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


@app.route('/product/<pid>', methods=['GET', 'POST'])
def product(pid):
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    products = Product.objects(id=pid).first()
    return json.dumps(create_json(products))


@app.route('/products', methods=['GET'])
def products():
    # if no_user_with_session_id(request.form.get('uid')):
    #     return 'Sorry, you are not authenticated.'
    products = Product.objects
    return json.dumps([create_json(product) for product in products][::-1])


@app.route('/add_product', methods=['POST'])
def add_product():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    form = request.form
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
        return {'order_id': order_id, 'success': False, 'message': 'Sorry, you are not authenticated.'}
    products = json.loads(request.form.get('products'))
    user_id = request.form.get('uid')
    user = User.objects(uuid=user_id)
    datetime_now = datetime.now()
    if products and user.first():
        order_id = str(uuid.uuid4())[:8]
        order = Order(
            order_id=order_id, product=products, 
            created=datetime_now, last_update=datetime_now, 
            status='Ordered', user=user.first()['membership_id'], 
            last_updated_by=user.first()['membership_id'], color=request.form.get('color'),
            flight_no=request.form.get('flight_no')
        ).save()
        user.update_one(orders=user.first()['orders'] + [order.id])
        trans = add_transaction(order_id, 'Ordered', user.first()['membership_id'])
        return json.dumps({'order_id': order_id, 'success': True, 'message': '', 'session_id':user_id})
    return 'FAILED'


def get_order(order_id):
    return Order.objects(id=order_id).first()


@app.route('/view_order', methods=['POST'])
def view_order():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    orders = User.objects(uuid=request.form.get('uid')).first()['orders'][::-1]
    return json.dumps([create_json(get_order(order)) for order in orders])


@app.route('/update_order', methods=['POST'])
def update_order():
    if no_user_with_session_id(request.form.get('uid')):
        return 'Sorry, you are not authenticated.'
    order_id = request.form.get('order_id')
    set_to = request.form.get('set_to')
    user = User.objects(uuid=request.form.get('uid')).first()
    if order_id:
        datetime_now = datetime.utcnow
        order = Order.objects(order_id=request.form.get('order_id'))
        order.update_one(status=set_to)
        order.update_one(last_update=datetime_now)
        order.update_one(last_updated_by=user['membership_id'])
        trans = add_transaction(order_id, set_to, user['membership_id'])
        if trans:
            return 'SUCCESS'
    return 'FAILED'


def add_transaction(order_id, status, actor):
    trans = Transaction(order_id=order_id, action=status, actor=actor).save()
    return trans


@app.route('/orders', methods=['GET', 'POST'])
def view_all_orders():
    # uuid = request.form.get('uid')
    # if uuid:
    #     admin = User.objects(uuid=uuid).first()
    #     if admin['auth'] == 'admin':
    orders = Order.objects
    return json.dumps([create_json(order) for order in orders])
    #     return 'NO ADMIN PRIVELEGES '
    # return 'FAILED'


@app.route('/transactions', methods=['POST'])
def view_all_transactions():
    #     uuid = request.form.get('uid')
    # if uuid:
    #     admin = User.objects(uuid=uuid).first()
    #     if admin['auth'] == 'admin':
    transactions = Transaction.objects
    return json.dumps([create_json(trans) for trans in transactions])
    #     return 'NO ADMIN PRIVELEGES '
    # return 'FAILED'

# endpoint to get employee by employee ID
# endpoint for krucible homepage
# endpoint for dashboard, employees and orders (krucible)


@app.route('/krucible/login', methods=['GET', 'POST'])
def krucible_login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin':
            if request.form.get('password') == 'password':
                return redirect('/krucible/dashboard')
        return render_template('login.html', msg="Error")
    return render_template('login.html')


@app.route('/krucible/dashboard', methods=['GET'])
def dashboard():
    return render_template('krucible.html')


@app.route('/bestsellers', methods=['GET'])
def bestsellers():
    # if no_user_with_session_id(request.form.get('uid')):
    #     return 'Sorry, you are not authenticated.'
    products = Product.objects
    best_sellers = []
    for product in products:
        try:
            if product.best_seller:
                best_sellers.append(product)
        except Exception as e:
            print (e)
    return json.dumps([create_json(product) for product in best_sellers])


@app.route('/transactions/<order_id>', methods=['GET'])
def all_transactions_for_order(order_id):
    print(order_id)
    transactions = Transaction.objects
    timeline = []
    for trans in transactions:
        if trans.order_id == order_id:
            timeline.append(trans)

    return json.dumps(
        {
            'transactions':[create_json(trans) for trans in timeline],
            'order': create_json(Order.objects(order_id=order_id).first())
        }
    )


@app.route('/employees', methods=['GET'])
def get_all_employees():
    users = User.objects
    employees = []
    for user in users:
        if user.auth == 'employee':
            employees.append(user)
    return json.dumps([emp.name for emp in employees])


@app.route('/unpacked_orders', methods=['GET'])
def get_all_unpacked_orders():
    orders = Order.objects
    unpacked_orders = []
    for order in orders:
        if order.status == "Ordered":
            unpacked_orders.append(order)
    return json.dumps([create_json(order) for order in unpacked_orders])


@app.route('/orders_by_flight/<flight_no>', methods=['GET'])
def get_orders_by_flight(flight_no):
    orders = Order.objects
    orders_by_flight = []
    for order in orders:
        if order.flight_no == flight_no:
            orders_by_flight.append(order)
    return json.dumps([create_json(order) for order in orders_by_flight][::-1])


@app.route('/issues', methods=['GET'])
def get_all_issues():
    orders = Order.objects
    order_w_issues = []
    for order in orders:
        if order.issue:
            order_w_issues.append(order)
    return json.dumps([create_json(order) for order in order_w_issues])

@app.route('/report_issue/<order_id>', methods=['POST'])
def report_issue(order_id):
    issue = request.form.get('issue')
    message = request.form.get('message')
    order = Order.objects(order_id=order_id)
    order.update_one(issue=issue)
    order.update_one(message=message)
    return 'SUCCESS'

@app.route('/report_message/<order_id>', methods=['GET']) 
def report_message(order_id):
    order = Order.objects(order_id=order_id).first()
    return order.message

@app.route('/transactions/<emp_id>', methods=['GET'])
def get_emp_trans(emp_id):
    trans = Transaction.objects(actor=emp_id).all()
    return json.dumps([create_json(transaction) for transaction in trans])
