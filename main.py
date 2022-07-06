from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_manager, LoginManager
from flask_login import login_required, current_user
import json

# MY db connection
local_server = True
app = Flask(__name__)
app.secret_key = 'kusumachandashwini'


# this is for getting unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/inventory'
db = SQLAlchemy(app)

# here we will create db models that is tables


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))


class Department(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(100))


class Attendence(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    attendance = db.Column(db.Integer())


class Trig(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(100))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(50))
    sname = db.Column(db.String(50))
    sem = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    email = db.Column(db.String(50))
    number = db.Column(db.String(12))
    address = db.Column(db.String(100))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    desc = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    supplier = db.Column(db.String(50))
    timestamp = db.Column(db.String(100))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/itemdetails')
def itemdetails():
    query = db.engine.execute(f"SELECT * FROM `item`")
    return render_template('itemdetails.html', query=query)


@app.route('/triggers')
@login_required
def triggers():
    query = db.engine.execute(f"SELECT * FROM `trig`")
    return render_template('triggers.html', query=query)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == "POST":
        name = request.form.get('name')
        bio = Item.query.filter_by(name=name).first()
        return render_template('search.html', bio=bio)

    return render_template('search.html')


@app.route("/delete/<string:id>", methods=['POST', 'GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `item` WHERE `item`.`id`={id}")
    flash("Item Deleted Successfully", "danger")
    return redirect('/itemdetails')


@app.route("/edit/<string:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    posts = Item.query.filter_by(id=id).first()
    if request.method == "POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        supplier = request.form.get('supplier')

        query = db.engine.execute(
            f"UPDATE `item` SET `name`='{name}',`desc`='{desc}',`quantity`={quantity},`price`={price},`supplier`='{supplier}' WHERE `id`={id}")
        flash("Item updated", "success")
        return redirect('/itemdetails')

    return render_template('edititem.html', posts=posts)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist", "warning")
            return render_template('/signup.html')
        encpassword = generate_password_hash(password)

        new_user = db.engine.execute(
            f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Succes Please Login", "success")
        return render_template('login.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials", "danger")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('login'))


@app.route('/additem', methods=['POST', 'GET'])
@login_required
def additem():
    if request.method == "POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        supplier = request.form.get('supplier')

        query = db.engine.execute(
            f"INSERT INTO `item` (`name`, `desc`, `quantity`, `price`, `supplier`)  VALUES ('{name}', '{desc}', {quantity}, {price}, '{supplier}')")

        flash("Item added to inventory", "info")

    return render_template('item.html')


@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)
